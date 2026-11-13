"""Instance lifecycle manager.

This is the state machine that decides when to spend money and when to stop.
It is the most dangerous code in the project, because it can destroy cloud
resources, so the safety rules are enforced structurally rather than by
convention:

* Every instance we create carries :data:`OWNERSHIP_TAG`. The reaper only ever
  considers instances that carry it. An instance without the tag is invisible,
  which means a bug cannot delete a user's unrelated server.
* Destruction is gated on a verified result upload. The manager will refuse to
  destroy an instance whose job has not been confirmed persisted.
* Provisioning is idempotent on the job id, so a retry or a duplicate scheduler
  tick cannot create a second instance for the same work.

The state machine is::

    IDLE -> PROVISIONING -> INITIALIZING -> READY -> RUNNING
         -> UPLOADING_RESULTS -> VERIFYING_RESULTS -> TERMINATING -> DESTROYED

Any state can transition to FAILED. FAILED preserves the instance so logs can
be recovered; it is never auto-destroyed.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

from .budget import BudgetExceeded, BudgetGuard
from .cost import CostModel, InstancePrice
from .provider import (
    CloudProvider,
    InstanceSpec,
    ProviderError,
    ProvisionedInstance,
)

log = logging.getLogger(__name__)

#: The tag that marks an instance as ours. Nothing without it is ever touched.
OWNERSHIP_TAG = "bharatgov-ephemeral"

#: A second, more specific tag so a future project sharing the account cannot
#: collide with ours.
PROJECT_TAG = "project:bharatgov-access"


class LifecycleError(RuntimeError):
    """Raised when the state machine is asked to do something unsafe."""


class OwnershipError(LifecycleError):
    """Raised when an instance cannot be proven to belong to this project."""


class InstanceState(str, Enum):
    IDLE = "idle"
    PROVISIONING = "provisioning"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    UPLOADING_RESULTS = "uploading_results"
    VERIFYING_RESULTS = "verifying_results"
    TERMINATING = "terminating"
    DESTROYED = "destroyed"
    FAILED = "failed"


#: Legal transitions. Anything not listed here is a bug in the caller.
TRANSITIONS: dict[InstanceState, set[InstanceState]] = {
    InstanceState.IDLE: {InstanceState.PROVISIONING},
    InstanceState.PROVISIONING: {InstanceState.INITIALIZING, InstanceState.FAILED},
    InstanceState.INITIALIZING: {InstanceState.READY, InstanceState.FAILED},
    InstanceState.READY: {InstanceState.RUNNING, InstanceState.TERMINATING, InstanceState.FAILED},
    InstanceState.RUNNING: {
        InstanceState.UPLOADING_RESULTS,
        # A running instance may be terminated directly when it has outlived
        # its maximum lifetime or an operator forces cleanup after recovering
        # the data by hand.
        InstanceState.TERMINATING,
        InstanceState.FAILED,
    },
    InstanceState.UPLOADING_RESULTS: {
        InstanceState.VERIFYING_RESULTS,
        InstanceState.FAILED,
    },
    InstanceState.VERIFYING_RESULTS: {
        InstanceState.TERMINATING,
        InstanceState.FAILED,
    },
    InstanceState.TERMINATING: {InstanceState.DESTROYED, InstanceState.FAILED},
    InstanceState.DESTROYED: set(),
    InstanceState.FAILED: {InstanceState.TERMINATING},
}


@dataclass
class JobRecord:
    """One measurement job and the instance running it."""

    job_id: str
    country_code: str
    region_id: str
    plan_id: str
    instance_id: str | None = None
    state: InstanceState = InstanceState.IDLE
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    destroyed_at: float | None = None
    estimated_usd: float = 0.0
    actual_usd: float | None = None
    results_verified: bool = False
    error: str = ""
    history: list[tuple[str, str]] = field(default_factory=list)

    def transition(self, new: InstanceState, note: str = "") -> None:
        allowed = TRANSITIONS.get(self.state, set())
        if new not in allowed:
            raise LifecycleError(
                f"job {self.job_id}: illegal transition {self.state.value} -> "
                f"{new.value}"
            )
        self.history.append(
            (datetime.now(timezone.utc).isoformat(), f"{self.state.value}->{new.value} {note}".strip())
        )
        self.state = new


class InfrastructureManager:
    """Provisions, runs and destroys ephemeral measurement workers."""

    def __init__(
        self,
        provider: CloudProvider,
        budget: BudgetGuard,
        cost_model: CostModel,
        *,
        os_id: int = 1743,  # Ubuntu 22.04 x64 on Vultr
        max_concurrent_instances: int = 2,
        max_instance_lifetime_seconds: float = 3600.0,
        idle_timeout_seconds: float = 300.0,
        state_path: Path | None = None,
        dry_run: bool = False,
        clock: Callable[[], float] = time.time,
    ):
        self.provider = provider
        self.budget = budget
        self.cost_model = cost_model
        self.os_id = os_id
        self.max_concurrent_instances = max_concurrent_instances
        self.max_instance_lifetime_seconds = max_instance_lifetime_seconds
        self.idle_timeout_seconds = idle_timeout_seconds
        self.state_path = state_path
        self.dry_run = dry_run
        self._clock = clock
        self._jobs: dict[str, JobRecord] = {}
        self._lock = threading.Lock()
        self._audit: list[dict] = []
        self._load_state()

    # ----------------------------------------------------------------- audit

    def _record(self, action: str, **fields) -> None:
        entry = {
            "at": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "dry_run": self.dry_run,
            **fields,
        }
        self._audit.append(entry)
        log.info("infra %s %s", action, fields)

    def audit_log(self) -> list[dict]:
        return list(self._audit)

    # ----------------------------------------------------------------- state

    def _load_state(self) -> None:
        if not self.state_path or not self.state_path.exists():
            return
        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            log.warning("infra state at %s unreadable; starting empty", self.state_path)
            return
        for j in raw.get("jobs", []):
            try:
                rec = JobRecord(
                    job_id=j["job_id"],
                    country_code=j["country_code"],
                    region_id=j["region_id"],
                    plan_id=j["plan_id"],
                    instance_id=j.get("instance_id"),
                    state=InstanceState(j.get("state", "idle")),
                    created_at=j.get("created_at", time.time()),
                    started_at=j.get("started_at"),
                    destroyed_at=j.get("destroyed_at"),
                    estimated_usd=j.get("estimated_usd", 0.0),
                    actual_usd=j.get("actual_usd"),
                    results_verified=j.get("results_verified", False),
                    error=j.get("error", ""),
                )
                self._jobs[rec.job_id] = rec
            except (KeyError, ValueError):
                continue

    def _persist_state(self) -> None:
        if not self.state_path:
            return
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "jobs": [
                {
                    "job_id": r.job_id,
                    "country_code": r.country_code,
                    "region_id": r.region_id,
                    "plan_id": r.plan_id,
                    "instance_id": r.instance_id,
                    "state": r.state.value,
                    "created_at": r.created_at,
                    "started_at": r.started_at,
                    "destroyed_at": r.destroyed_at,
                    "estimated_usd": r.estimated_usd,
                    "actual_usd": r.actual_usd,
                    "results_verified": r.results_verified,
                    "error": r.error,
                }
                for r in self._jobs.values()
            ]
        }
        self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # ------------------------------------------------------------- ownership

    def _assert_owned(self, instance: ProvisionedInstance) -> None:
        """Refuse to act on an instance we cannot prove is ours."""
        if OWNERSHIP_TAG not in instance.tags:
            raise OwnershipError(
                f"instance {instance.id} does not carry the ownership tag "
                f"{OWNERSHIP_TAG!r}; refusing to touch it"
            )

    def owned_instances(self) -> list[ProvisionedInstance]:
        """Every instance in the account that belongs to this project."""
        return self.provider.list_instances(tag=OWNERSHIP_TAG)

    # ------------------------------------------------------------ provisioning

    def _active_count(self) -> int:
        return sum(
            1
            for r in self._jobs.values()
            if r.state
            in {
                InstanceState.PROVISIONING,
                InstanceState.INITIALIZING,
                InstanceState.READY,
                InstanceState.RUNNING,
                InstanceState.UPLOADING_RESULTS,
                InstanceState.VERIFYING_RESULTS,
            }
        )

    def provision(
        self,
        job_id: str,
        country_code: str,
        region_id: str,
        plan_id: str,
        expected_runtime_seconds: float = 900.0,
        label: str | None = None,
    ) -> JobRecord:
        """Create one worker for one job, or return the existing one.

        Idempotent on ``job_id``: calling twice returns the same record rather
        than provisioning a second instance.
        """
        with self._lock:
            existing = self._jobs.get(job_id)
            if existing and existing.state not in {
                InstanceState.DESTROYED,
                InstanceState.FAILED,
            }:
                self._record("provision.skip_existing", job_id=job_id,
                             state=existing.state.value)
                return existing

            if self._active_count() >= self.max_concurrent_instances:
                raise LifecycleError(
                    f"refusing to provision: {self._active_count()} instances "
                    f"already active (cap {self.max_concurrent_instances})"
                )

            price = self.cost_model.price_for(plan_id, region_id)
            if price is None:
                raise LifecycleError(
                    f"no price registered for plan {plan_id} in region {region_id}; "
                    "refusing to provision without a cost estimate"
                )

            estimate = self.cost_model.estimate(price, expected_runtime_seconds)
            self.budget.check(estimate.total_usd, job_id=job_id)

            record = JobRecord(
                job_id=job_id,
                country_code=country_code,
                region_id=region_id,
                plan_id=plan_id,
                estimated_usd=estimate.total_usd,
            )
            record.transition(InstanceState.PROVISIONING, "budget approved")
            self._jobs[job_id] = record
            self._persist_state()

        spec = InstanceSpec(
            region_id=region_id,
            plan_id=plan_id,
            os_id=self.os_id,
            label=label or f"bga-{job_id}"[:60],
            tags=(OWNERSHIP_TAG, PROJECT_TAG),
        )

        try:
            instance = self.provider.create_instance(spec)
        except ProviderError as exc:
            record.error = str(exc)
            record.transition(InstanceState.FAILED, "provider error")
            self._persist_state()
            self._record("provision.failed", job_id=job_id, error=str(exc))
            raise

        record.instance_id = instance.id
        record.transition(InstanceState.INITIALIZING, f"instance {instance.id}")
        self.budget.commit(
            job_id=job_id,
            instance_id=instance.id,
            region_id=region_id,
            plan_id=plan_id,
            estimated_usd=estimate.total_usd,
        )
        self._persist_state()
        self._record(
            "provision.created",
            job_id=job_id,
            instance_id=instance.id,
            region=region_id,
            plan=plan_id,
            estimated_usd=estimate.total_usd,
        )
        return record

    def wait_until_ready(
        self, job_id: str, timeout_seconds: float = 600.0, poll_seconds: float = 5.0
    ) -> JobRecord:
        """Block until the instance reports active, or fail the job."""
        record = self._jobs[job_id]
        if record.instance_id is None:
            raise LifecycleError(f"job {job_id} has no instance")

        deadline = self._clock() + timeout_seconds
        while self._clock() < deadline:
            inst = self.provider.get_instance(record.instance_id)
            if inst is None:
                record.error = "instance disappeared during initialisation"
                record.transition(InstanceState.FAILED)
                self._persist_state()
                raise LifecycleError(record.error)
            if inst.is_running:
                record.transition(InstanceState.READY, "instance active")
                self._persist_state()
                self._record("provision.ready", job_id=job_id,
                             instance_id=record.instance_id)
                return record
            time.sleep(poll_seconds)

        record.error = f"instance not ready within {timeout_seconds:.0f}s"
        record.transition(InstanceState.FAILED)
        self._persist_state()
        self._record("provision.timeout", job_id=job_id)
        raise LifecycleError(record.error)

    # ------------------------------------------------------------- execution

    def mark_running(self, job_id: str) -> JobRecord:
        record = self._jobs[job_id]
        record.started_at = self._clock()
        record.transition(InstanceState.RUNNING, "job dispatched")
        self._persist_state()
        self._record("job.running", job_id=job_id)
        return record

    def mark_uploading(self, job_id: str) -> JobRecord:
        record = self._jobs[job_id]
        record.transition(InstanceState.UPLOADING_RESULTS)
        self._persist_state()
        return record

    def mark_verified(self, job_id: str, verified: bool, note: str = "") -> JobRecord:
        """Record the result-verification outcome.

        A failed verification is not fatal to the instance: the manager keeps
        it alive so the data can be recovered, which is the whole point of the
        rule that we never destroy before persistence is confirmed.
        """
        record = self._jobs[job_id]
        record.results_verified = verified
        if verified:
            record.transition(InstanceState.VERIFYING_RESULTS, note or "results verified")
        else:
            record.error = note or "result verification failed"
            record.transition(InstanceState.FAILED, record.error)
        self._persist_state()
        self._record("results.verified", job_id=job_id, verified=verified, note=note)
        return record

    # ------------------------------------------------------------ destruction

    def destroy(self, job_id: str, force: bool = False) -> JobRecord:
        """Destroy the instance for a job.

        Refuses unless the results were verified, because destroying an
        instance whose data has not been persisted loses the measurement. The
        ``force`` escape hatch exists for the case where the instance is
        wedged and the operator has already recovered the data by hand; it is
        logged loudly.
        """
        record = self._jobs[job_id]
        if record.instance_id is None:
            record.transition(InstanceState.DESTROYED, "no instance to destroy")
            self._persist_state()
            return record

        if not record.results_verified and not force:
            raise LifecycleError(
                f"refusing to destroy instance {record.instance_id}: results for "
                f"job {job_id} are not verified. Recover the data first, or pass "
                "force=True after doing so deliberately."
            )
        if force and not record.results_verified:
            self._record("destroy.forced", job_id=job_id,
                         instance_id=record.instance_id)

        inst = self.provider.get_instance(record.instance_id)
        if inst is not None:
            self._assert_owned(inst)

        record.transition(InstanceState.TERMINATING, "destroy requested")
        self._persist_state()

        try:
            ok = self.provider.destroy_instance(record.instance_id)
        except ProviderError as exc:
            # A transient provider failure must not leave the record claiming
            # the instance is gone. Mark it failed so the reaper retries.
            record.error = f"destroy failed: {exc}"
            record.transition(InstanceState.FAILED, record.error)
            self._persist_state()
            self._record("destroy.failed", job_id=job_id,
                         instance_id=record.instance_id, error=str(exc))
            raise LifecycleError(record.error) from None

        if not ok:
            record.error = "provider did not confirm destruction"
            record.transition(InstanceState.FAILED, record.error)
            self._persist_state()
            self._record("destroy.failed", job_id=job_id,
                         instance_id=record.instance_id)
            raise LifecycleError(record.error)

        record.destroyed_at = self._clock()
        record.transition(InstanceState.DESTROYED, "instance gone")

        price = self.cost_model.price_for(record.plan_id, record.region_id)
        if price and record.started_at:
            actual = self.cost_model.actual(price, record.started_at, record.destroyed_at)
            record.actual_usd = actual.total_usd
            self.budget.settle(record.instance_id, actual.total_usd)

        self._persist_state()
        self._record(
            "destroy.done",
            job_id=job_id,
            instance_id=record.instance_id,
            actual_usd=record.actual_usd,
        )
        return record

    # --------------------------------------------------------------- reaping

    def reap_orphans(self, dry_run: bool | None = None) -> list[str]:
        """Destroy project-owned instances that no live job accounts for.

        This is the safety net for a crashed process. It only ever considers
        instances carrying the ownership tag, so an unrelated server in the
        same account is never a candidate.
        """
        dry = self.dry_run if dry_run is None else dry_run
        live_ids = {
            r.instance_id
            for r in self._jobs.values()
            if r.instance_id
            and r.state
            not in {InstanceState.DESTROYED, InstanceState.FAILED}
        }
        reaped: list[str] = []
        for inst in self.owned_instances():
            if inst.id in live_ids:
                continue
            if dry:
                self._record("reap.would_destroy", instance_id=inst.id)
                reaped.append(inst.id)
                continue
            try:
                self._assert_owned(inst)
                if self.provider.destroy_instance(inst.id):
                    reaped.append(inst.id)
                    self._record("reap.destroyed", instance_id=inst.id)
            except (OwnershipError, ProviderError) as exc:
                self._record("reap.failed", instance_id=inst.id, error=str(exc))
        return reaped

    def reap_expired(self, dry_run: bool | None = None) -> list[str]:
        """Destroy instances that have outlived the maximum lifetime."""
        dry = self.dry_run if dry_run is None else dry_run
        now = self._clock()
        expired: list[str] = []
        for record in self._jobs.values():
            if record.state in {InstanceState.DESTROYED, InstanceState.FAILED}:
                continue
            if record.started_at is None:
                continue
            if now - record.started_at < self.max_instance_lifetime_seconds:
                continue
            if dry:
                self._record("expire.would_destroy", job_id=record.job_id)
                expired.append(record.job_id)
                continue
            try:
                self.destroy(record.job_id, force=True)
                expired.append(record.job_id)
            except LifecycleError as exc:
                self._record("expire.failed", job_id=record.job_id, error=str(exc))
        return expired

    # ------------------------------------------------------------ reporting

    def summary(self) -> dict:
        """A snapshot for the dashboard's infrastructure panel."""
        active = [
            r for r in self._jobs.values()
            if r.state not in {InstanceState.DESTROYED, InstanceState.FAILED}
        ]
        destroyed = [
            r for r in self._jobs.values() if r.state is InstanceState.DESTROYED
        ]
        failed = [r for r in self._jobs.values() if r.state is InstanceState.FAILED]
        actual = [r.actual_usd for r in destroyed if r.actual_usd is not None]
        runtimes = [
            (r.destroyed_at - r.started_at)
            for r in destroyed
            if r.started_at and r.destroyed_at
        ]
        return {
            "active_instances": len(active),
            "completed_jobs": len(destroyed),
            "failed_jobs": len(failed),
            "estimated_active_usd": round(sum(r.estimated_usd for r in active), 4),
            "actual_total_usd": round(sum(actual), 4) if actual else 0.0,
            "month_spend_usd": self.budget.month_spend(),
            "monthly_cap_usd": self.budget.monthly_usd,
            "per_job_cap_usd": self.budget.per_job_usd,
            "avg_runtime_seconds": round(sum(runtimes) / len(runtimes), 1) if runtimes else 0.0,
            "instances": [
                {
                    "job_id": r.job_id,
                    "instance_id": r.instance_id,
                    "country": r.country_code,
                    "region": r.region_id,
                    "plan": r.plan_id,
                    "state": r.state.value,
                    "estimated_usd": r.estimated_usd,
                    "actual_usd": r.actual_usd,
                }
                for r in self._jobs.values()
            ],
        }
