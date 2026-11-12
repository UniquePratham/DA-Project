"""Tests for the ephemeral infrastructure manager.

These tests never touch the network and never spend money. They use a fake
provider that records calls, so the safety rules can be proven rather than
asserted:

* an instance without the ownership tag is never destroyed
* an instance is never destroyed before its results are verified
* a duplicate scheduler tick does not provision twice
* a budget breach stops provisioning before the API call
* a restart recovers state instead of re-provisioning
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from services.infrastructure.budget import BudgetExceeded, BudgetGuard
from services.infrastructure.cost import CostModel, InstancePrice
from services.infrastructure.lifecycle import (
    OWNERSHIP_TAG,
    InfrastructureManager,
    InstanceState,
    LifecycleError,
    OwnershipError,
)
from services.infrastructure.provider import (
    InstanceSpec,
    ProviderError,
    ProvisionedInstance,
    Region,
)
from services.infrastructure.regions import ProbeRegistry, ProbeStatus
from services.infrastructure.vultr import VULTR_REGIONS


class FakeProvider:
    """Records every call so the tests can assert on behaviour."""

    name = "fake"

    def __init__(self, fail_create: bool = False, fail_destroy: bool = False):
        self.instances: dict[str, ProvisionedInstance] = {}
        self.created: list[InstanceSpec] = []
        self.destroyed: list[str] = []
        self.fail_create = fail_create
        self.fail_destroy = fail_destroy
        self._n = 0

    def list_regions(self) -> list[Region]:
        return list(VULTR_REGIONS)

    def list_plans(self, region_id: str):
        return [{"id": "vc2-1c-1gb", "hourly_cost": 0.007}]

    def create_instance(self, spec: InstanceSpec) -> ProvisionedInstance:
        if self.fail_create:
            raise ProviderError("simulated create failure")
        self._n += 1
        inst = ProvisionedInstance(
            id=f"inst-{self._n}",
            region_id=spec.region_id,
            plan_id=spec.plan_id,
            label=spec.label,
            status="active",
            tags=spec.tags,
        )
        self.instances[inst.id] = inst
        self.created.append(spec)
        return inst

    def get_instance(self, instance_id: str):
        return self.instances.get(instance_id)

    def list_instances(self, tag=None):
        vals = list(self.instances.values())
        return [i for i in vals if tag is None or tag in i.tags]

    def destroy_instance(self, instance_id: str) -> bool:
        if self.fail_destroy:
            return False
        self.destroyed.append(instance_id)
        self.instances.pop(instance_id, None)
        return True

    def account_balance(self):
        return 100.0


def make_manager(tmp_path: Path, provider=None, **kwargs) -> InfrastructureManager:
    provider = provider or FakeProvider()
    budget = BudgetGuard(
        per_job_usd=kwargs.pop("per_job_usd", 1.0),
        monthly_usd=kwargs.pop("monthly_usd", 20.0),
        ledger_path=tmp_path / "ledger.json",
        kill_switch=kwargs.pop("kill_switch", False),
    )
    cost = CostModel()
    cost.register(InstancePrice("vc2-1c-1gb", "bom", 0.007, 5.0, 1, 1024, 25, 1000))
    cost.register(InstancePrice("vc2-1c-1gb", "lhr", 0.007, 5.0, 1, 1024, 25, 1000))
    return InfrastructureManager(
        provider=provider,
        budget=budget,
        cost_model=cost,
        state_path=tmp_path / "state.json",
        dry_run=True,
        **kwargs,
    )


# ------------------------------------------------------------------ lifecycle


def test_provision_creates_one_instance_with_ownership_tag(tmp_path):
    provider = FakeProvider()
    mgr = make_manager(tmp_path, provider)

    rec = mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)

    assert rec.instance_id == "inst-1"
    assert rec.state is InstanceState.INITIALIZING
    assert len(provider.created) == 1
    assert OWNERSHIP_TAG in provider.created[0].tags


def test_provision_is_idempotent_on_job_id(tmp_path):
    provider = FakeProvider()
    mgr = make_manager(tmp_path, provider)

    first = mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)
    second = mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)

    assert first.instance_id == second.instance_id
    assert len(provider.created) == 1, "a duplicate tick must not provision twice"


def test_concurrency_cap_blocks_extra_instances(tmp_path):
    provider = FakeProvider()
    mgr = make_manager(tmp_path, provider, max_concurrent_instances=1)

    mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)
    with pytest.raises(LifecycleError, match="already active"):
        mgr.provision("job-2", "IN", "bom", "vc2-1c-1gb", 900)


def test_provision_fails_without_a_registered_price(tmp_path):
    mgr = make_manager(tmp_path)
    with pytest.raises(LifecycleError, match="no price registered"):
        mgr.provision("job-1", "IN", "unknown-region", "vc2-1c-1gb", 900)


def test_provider_failure_marks_job_failed(tmp_path):
    provider = FakeProvider(fail_create=True)
    mgr = make_manager(tmp_path, provider)

    with pytest.raises(ProviderError):
        mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)

    assert mgr._jobs["job-1"].state is InstanceState.FAILED


# --------------------------------------------------------------------- budget


def test_budget_blocks_provisioning_before_the_api_call(tmp_path):
    provider = FakeProvider()
    mgr = make_manager(tmp_path, provider, per_job_usd=0.001)

    with pytest.raises(BudgetExceeded):
        mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)

    assert provider.created == [], "no instance may be created after a budget refusal"


def test_kill_switch_blocks_everything(tmp_path):
    provider = FakeProvider()
    mgr = make_manager(tmp_path, provider, kill_switch=True)

    with pytest.raises(BudgetExceeded, match="kill switch"):
        mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)

    assert provider.created == []


def test_monthly_cap_accumulates_across_jobs(tmp_path):
    provider = FakeProvider()
    # Each job costs one billed hour at $0.007, so a $0.01 monthly cap allows
    # exactly one job and refuses the second.
    mgr = make_manager(tmp_path, provider, per_job_usd=1.0, monthly_usd=0.01)

    mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)
    with pytest.raises(BudgetExceeded, match="monthly cap"):
        mgr.provision("job-2", "IN", "bom", "vc2-1c-1gb", 900)


def test_corrupt_ledger_refuses_rather_than_resetting(tmp_path):
    ledger = tmp_path / "ledger.json"
    ledger.write_text("{not json", encoding="utf-8")
    with pytest.raises(BudgetExceeded, match="unreadable"):
        BudgetGuard(per_job_usd=1.0, monthly_usd=10.0, ledger_path=ledger)


# ---------------------------------------------------------------- destruction


def test_destroy_refuses_before_results_are_verified(tmp_path):
    provider = FakeProvider()
    mgr = make_manager(tmp_path, provider)
    mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)
    mgr.wait_until_ready("job-1", timeout_seconds=1, poll_seconds=0)
    mgr.mark_running("job-1")

    with pytest.raises(LifecycleError, match="not verified"):
        mgr.destroy("job-1")

    assert provider.destroyed == [], "data must not be lost to an early destroy"


def test_destroy_succeeds_after_verification(tmp_path):
    provider = FakeProvider()
    mgr = make_manager(tmp_path, provider)
    mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)
    mgr.wait_until_ready("job-1", timeout_seconds=1, poll_seconds=0)
    mgr.mark_running("job-1")
    mgr.mark_uploading("job-1")
    mgr.mark_verified("job-1", True, "checksum matched")

    rec = mgr.destroy("job-1")

    assert rec.state is InstanceState.DESTROYED
    assert provider.destroyed == ["inst-1"]
    assert rec.actual_usd is not None


def test_destroy_refuses_an_instance_without_the_ownership_tag(tmp_path):
    provider = FakeProvider()
    mgr = make_manager(tmp_path, provider)
    mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)
    mgr.wait_until_ready("job-1", timeout_seconds=1, poll_seconds=0)
    mgr.mark_running("job-1")
    mgr.mark_uploading("job-1")
    mgr.mark_verified("job-1", True)

    # Simulate the tag being stripped, or a foreign instance being substituted.
    provider.instances["inst-1"].tags = ("someone-elses-server",)

    with pytest.raises(OwnershipError):
        mgr.destroy("job-1")

    assert provider.destroyed == []


def test_failed_destroy_is_reported_not_swallowed(tmp_path):
    provider = FakeProvider(fail_destroy=True)
    mgr = make_manager(tmp_path, provider)
    mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)
    mgr.wait_until_ready("job-1", timeout_seconds=1, poll_seconds=0)
    mgr.mark_running("job-1")
    mgr.mark_uploading("job-1")
    mgr.mark_verified("job-1", True)

    with pytest.raises(LifecycleError, match="did not confirm"):
        mgr.destroy("job-1")

    assert mgr._jobs["job-1"].state is InstanceState.FAILED


# -------------------------------------------------------------------- reaping


def test_reaper_ignores_instances_it_does_not_own(tmp_path):
    provider = FakeProvider()
    provider.instances["foreign"] = ProvisionedInstance(
        id="foreign", region_id="bom", plan_id="x", label="user-db",
        status="active", tags=("production",),
    )
    mgr = make_manager(tmp_path, provider)

    reaped = mgr.reap_orphans(dry_run=False)

    assert reaped == []
    assert "foreign" in provider.instances, "an unrelated server must survive"


def test_reaper_destroys_orphaned_project_instances(tmp_path):
    provider = FakeProvider()
    mgr = make_manager(tmp_path, provider)
    mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)
    # Simulate a crash: the job record is gone but the instance is not.
    mgr._jobs.clear()

    reaped = mgr.reap_orphans(dry_run=False)

    assert reaped == ["inst-1"]
    assert provider.destroyed == ["inst-1"]


def test_reaper_dry_run_destroys_nothing(tmp_path):
    provider = FakeProvider()
    mgr = make_manager(tmp_path, provider)
    mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)
    mgr._jobs.clear()

    reaped = mgr.reap_orphans(dry_run=True)

    assert reaped == ["inst-1"]
    assert provider.destroyed == []


def test_expired_instance_is_reaped(tmp_path):
    provider = FakeProvider()
    now = [1000.0]
    mgr = make_manager(
        tmp_path, provider,
        max_instance_lifetime_seconds=60,
        clock=lambda: now[0],
    )
    mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)
    mgr.wait_until_ready("job-1", timeout_seconds=1, poll_seconds=0)
    mgr.mark_running("job-1")

    now[0] += 120
    expired = mgr.reap_expired(dry_run=False)

    assert expired == ["job-1"]
    assert provider.destroyed == ["inst-1"]


# ------------------------------------------------------------------ restart


def test_state_survives_a_restart(tmp_path):
    provider = FakeProvider()
    mgr = make_manager(tmp_path, provider)
    mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)

    # A new manager reading the same state file must not re-provision.
    mgr2 = make_manager(tmp_path, provider)
    rec = mgr2.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)

    assert rec.instance_id == "inst-1"
    assert len(provider.created) == 1


def test_illegal_transition_is_rejected(tmp_path):
    mgr = make_manager(tmp_path)
    rec = mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)
    with pytest.raises(LifecycleError, match="illegal transition"):
        rec.transition(InstanceState.DESTROYED)


# ------------------------------------------------------------------- regions


def test_probe_registry_marks_countries_without_a_region_unsupported():
    regions = [Region("bom", "Mumbai", "IN", "Asia")]
    reg = ProbeRegistry(regions)

    india = reg.probe_for("IN", "India")
    japan = reg.probe_for("JP", "Japan")

    assert india.status is ProbeStatus.OPERATIONAL
    assert india.can_claim_domestic is True
    assert japan.status is ProbeStatus.UNSUPPORTED
    assert japan.can_claim_domestic is False


def test_probe_registry_never_claims_a_foreign_region_as_domestic():
    regions = [Region("bom", "Mumbai", "IN", "Asia")]
    reg = ProbeRegistry(regions)
    japan = reg.probe_for("JP", "Japan")

    assert japan.domestic_region is None
    assert japan.nearest_region is not None
    assert japan.nearest_region.country == "IN"
    assert japan.can_claim_domestic is False


def test_all_target_countries_have_a_real_domestic_region():
    reg = ProbeRegistry(VULTR_REGIONS)
    for probe in reg.all_probes():
        assert probe.domestic_region is not None, probe.country_code
        assert probe.domestic_region.country == probe.country_code


# --------------------------------------------------------------------- cost


def test_cost_model_charges_a_minimum_hour():
    cost = CostModel()
    price = InstancePrice("p", "r", 0.10, 72.0)
    est = cost.estimate(price, expected_runtime_seconds=120)
    assert est.billed_hours == 1.0
    assert est.compute_usd == pytest.approx(0.10)


def test_cost_model_includes_bandwidth_overage():
    cost = CostModel()
    price = InstancePrice("p", "r", 0.10, 72.0, bandwidth_gb=100)
    est = cost.estimate(price, 3600, egress_gb=150)
    assert est.bandwidth_usd == pytest.approx(0.50)


def test_cost_model_includes_backup_surcharge():
    cost = CostModel()
    price = InstancePrice("p", "r", 0.10, 72.0)
    est = cost.estimate(price, 3600, backups=True)
    assert est.backup_usd == pytest.approx(0.02)


# ------------------------------------------------------------------- summary


def test_summary_reports_real_numbers(tmp_path):
    provider = FakeProvider()
    mgr = make_manager(tmp_path, provider)
    mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)
    mgr.wait_until_ready("job-1", timeout_seconds=1, poll_seconds=0)
    mgr.mark_running("job-1")
    mgr.mark_uploading("job-1")
    mgr.mark_verified("job-1", True)
    mgr.destroy("job-1")

    s = mgr.summary()
    assert s["completed_jobs"] == 1
    assert s["active_instances"] == 0
    assert s["actual_total_usd"] > 0
    assert s["monthly_cap_usd"] == 20.0


def test_audit_log_records_every_action(tmp_path):
    provider = FakeProvider()
    mgr = make_manager(tmp_path, provider)
    mgr.provision("job-1", "IN", "bom", "vc2-1c-1gb", 900)

    actions = [e["action"] for e in mgr.audit_log()]
    assert "provision.created" in actions
