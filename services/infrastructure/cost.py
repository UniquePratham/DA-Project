"""Cost model for ephemeral instances.

Vultr bills per hour, but not in a way that makes "destroy it and you pay
nothing" true. This module makes the real charges explicit so the budget guard
is checking a number that reflects the invoice rather than the marketing page.

What is modelled:

* **Hourly compute.** Billed from creation to destruction, rounded up to the
  provider's billing granularity. Vultr rounds to the hour for instances
  destroyed within the first billing period, so a 12-minute job can cost a full
  hour.
* **Attached storage.** Block storage is billed separately and survives the
  instance unless it is explicitly deleted.
* **Snapshots.** Billed per GB-month while they exist.
* **Bandwidth.** Vultr includes a monthly allowance per plan; overage is billed
  per GB. We model the allowance and the overage rate.
* **Backups.** A percentage surcharge on the plan price when enabled.

The model is deliberately conservative: it rounds up, and it assumes the
minimum billing period rather than the actual runtime.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class InstancePrice:
    """The price of one plan in one region."""

    plan_id: str
    region_id: str
    hourly_usd: float
    monthly_usd: float
    vcpu: int = 0
    ram_mb: int = 0
    disk_gb: int = 0
    bandwidth_gb: int = 0

    @property
    def bandwidth_overage_per_gb(self) -> float:
        """Vultr charges roughly $0.01/GB beyond the plan allowance."""
        return 0.01


@dataclass(frozen=True)
class CostEstimate:
    """A pre-provisioning estimate, itemised so it can be audited."""

    compute_usd: float
    storage_usd: float
    snapshot_usd: float
    bandwidth_usd: float
    backup_usd: float
    billed_hours: float

    @property
    def total_usd(self) -> float:
        return round(
            self.compute_usd
            + self.storage_usd
            + self.snapshot_usd
            + self.bandwidth_usd
            + self.backup_usd,
            4,
        )

    def as_dict(self) -> dict[str, float]:
        return {
            "compute_usd": round(self.compute_usd, 4),
            "storage_usd": round(self.storage_usd, 4),
            "snapshot_usd": round(self.snapshot_usd, 4),
            "bandwidth_usd": round(self.bandwidth_usd, 4),
            "backup_usd": round(self.backup_usd, 4),
            "billed_hours": round(self.billed_hours, 2),
            "total_usd": self.total_usd,
        }


class CostModel:
    """Turns a plan, a region and an expected runtime into a dollar figure."""

    #: Vultr bills a minimum of one hour for short-lived instances.
    MIN_BILLED_HOURS = 1.0

    #: Block storage is billed per GB-month; we convert to the job's share.
    STORAGE_USD_PER_GB_MONTH = 0.10

    #: Snapshots are billed per GB-month.
    SNAPSHOT_USD_PER_GB_MONTH = 0.05

    #: Backups add 20% to the plan price when enabled.
    BACKUP_SURCHARGE = 0.20

    def __init__(self, prices: dict[tuple[str, str], InstancePrice] | None = None):
        self._prices = prices or {}

    def register(self, price: InstancePrice) -> None:
        self._prices[(price.plan_id, price.region_id)] = price

    def price_for(self, plan_id: str, region_id: str) -> InstancePrice | None:
        return self._prices.get((plan_id, region_id))

    def billed_hours(self, expected_runtime_seconds: float) -> float:
        """Hours the provider will actually charge for.

        Rounds up to the billing granularity, with a one-hour floor, because a
        short job still costs an hour.
        """
        raw = expected_runtime_seconds / 3600.0
        return max(self.MIN_BILLED_HOURS, math.ceil(raw * 100) / 100)

    def estimate(
        self,
        price: InstancePrice,
        expected_runtime_seconds: float,
        *,
        extra_storage_gb: float = 0.0,
        snapshot_gb: float = 0.0,
        egress_gb: float = 0.0,
        backups: bool = False,
    ) -> CostEstimate:
        """Estimate the full cost of one job, not just the compute line."""
        hours = self.billed_hours(expected_runtime_seconds)
        compute = price.hourly_usd * hours

        # Storage and snapshots are billed monthly; charge the job its share.
        month_fraction = hours / (24 * 30)
        storage = extra_storage_gb * self.STORAGE_USD_PER_GB_MONTH * month_fraction
        snapshot = snapshot_gb * self.SNAPSHOT_USD_PER_GB_MONTH * month_fraction

        overage = max(0.0, egress_gb - price.bandwidth_gb)
        bandwidth = overage * price.bandwidth_overage_per_gb

        backup = compute * self.BACKUP_SURCHARGE if backups else 0.0

        return CostEstimate(
            compute_usd=compute,
            storage_usd=storage,
            snapshot_usd=snapshot,
            bandwidth_usd=bandwidth,
            backup_usd=backup,
            billed_hours=hours,
        )

    def actual(
        self,
        price: InstancePrice,
        started_at_epoch: float,
        destroyed_at_epoch: float,
        *,
        egress_gb: float = 0.0,
    ) -> CostEstimate:
        """Cost actually incurred, from real timestamps."""
        runtime = max(0.0, destroyed_at_epoch - started_at_epoch)
        return self.estimate(price, runtime, egress_gb=egress_gb)
