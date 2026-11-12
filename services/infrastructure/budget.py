"""Spending limits.

The budget guard is the last line of defence before an API call that costs
money. It is deliberately simple and deliberately pessimistic: it refuses when
it cannot prove the spend is affordable, rather than assuming it is.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


class BudgetExceeded(RuntimeError):
    """Raised when a provisioning request would breach a configured limit."""


@dataclass
class SpendRecord:
    job_id: str
    instance_id: str
    region_id: str
    plan_id: str
    estimated_usd: float
    actual_usd: float | None = None
    recorded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class BudgetGuard:
    """Tracks spend and refuses requests that would breach a ceiling.

    Two ceilings apply: a per-job cap, which stops a single runaway job, and a
    monthly cap, which stops a runaway month. Both are checked before the
    provider is called.

    The ledger is written to disk so a restart does not reset the month's
    spend. That matters: a process that forgets what it already spent will
    happily spend it again.
    """

    def __init__(
        self,
        per_job_usd: float,
        monthly_usd: float,
        ledger_path: Path | None = None,
        kill_switch: bool = False,
    ):
        self.per_job_usd = per_job_usd
        self.monthly_usd = monthly_usd
        self.ledger_path = ledger_path
        self.kill_switch = kill_switch
        self._lock = threading.Lock()
        self._records: list[SpendRecord] = []
        self._load()

    # ---------------------------------------------------------------- ledger

    def _load(self) -> None:
        if not self.ledger_path or not self.ledger_path.exists():
            return
        try:
            raw = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            # A corrupt ledger must not silently reset the budget to zero.
            raise BudgetExceeded(
                f"spend ledger at {self.ledger_path} is unreadable; refusing to "
                "provision until it is repaired or removed deliberately"
            )
        self._records = [SpendRecord(**r) for r in raw.get("records", [])]

    def _persist(self) -> None:
        if not self.ledger_path:
            return
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "per_job_usd": self.per_job_usd,
            "monthly_usd": self.monthly_usd,
            "records": [r.__dict__ for r in self._records],
        }
        self.ledger_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # ----------------------------------------------------------------- spend

    def _month_prefix(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m")

    def month_spend(self) -> float:
        """Committed spend this calendar month, estimated plus actual."""
        prefix = self._month_prefix()
        total = 0.0
        for r in self._records:
            if not r.recorded_at.startswith(prefix):
                continue
            total += r.actual_usd if r.actual_usd is not None else r.estimated_usd
        return round(total, 4)

    def check(self, estimated_usd: float, job_id: str = "") -> None:
        """Raise if this spend is not allowed. Call before provisioning."""
        if self.kill_switch:
            raise BudgetExceeded(
                "infrastructure kill switch is engaged; no provisioning permitted"
            )
        if estimated_usd < 0:
            raise BudgetExceeded(f"negative estimate {estimated_usd} is not valid")
        if estimated_usd > self.per_job_usd:
            raise BudgetExceeded(
                f"job {job_id or '<unnamed>'} estimated at ${estimated_usd:.4f} "
                f"exceeds the per-job cap of ${self.per_job_usd:.2f}"
            )
        projected = self.month_spend() + estimated_usd
        if projected > self.monthly_usd:
            raise BudgetExceeded(
                f"projected month spend ${projected:.4f} would exceed the "
                f"monthly cap of ${self.monthly_usd:.2f} "
                f"(already committed ${self.month_spend():.4f})"
            )

    def commit(
        self,
        job_id: str,
        instance_id: str,
        region_id: str,
        plan_id: str,
        estimated_usd: float,
    ) -> SpendRecord:
        """Record an authorised spend."""
        with self._lock:
            record = SpendRecord(
                job_id=job_id,
                instance_id=instance_id,
                region_id=region_id,
                plan_id=plan_id,
                estimated_usd=estimated_usd,
            )
            self._records.append(record)
            self._persist()
            return record

    def settle(self, instance_id: str, actual_usd: float) -> None:
        """Replace the estimate with the real cost once the instance is gone."""
        with self._lock:
            for r in self._records:
                if r.instance_id == instance_id:
                    r.actual_usd = round(actual_usd, 4)
                    self._persist()
                    return

    def records(self) -> list[SpendRecord]:
        return list(self._records)
