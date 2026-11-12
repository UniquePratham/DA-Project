"""Load the real Vultr catalogue into the cost model.

The region and plan tables are fetched from the live API and cached to
``data/fixtures/vultr_catalog.json``. The cache exists so the dashboard and the
tests work offline, but the cache is regenerated from the API whenever a key is
available, so prices never drift from the invoice.

Nothing here invents a price. If the catalogue is missing, the loader raises
rather than falling back to a guess, because a guessed price would silently
break the budget guard.
"""

from __future__ import annotations

import json
from pathlib import Path

from services.infrastructure.cost import CostModel, InstancePrice
from services.infrastructure.provider import Region

CATALOG = Path(__file__).resolve().parent.parent.parent / "data" / "fixtures" / "vultr_catalog.json"


class CatalogMissing(RuntimeError):
    """Raised when the Vultr catalogue has not been fetched yet."""


def load_catalog(path: Path | None = None) -> dict:
    p = path or CATALOG
    if not p.exists():
        raise CatalogMissing(
            f"no Vultr catalogue at {p}. Run scripts/fetch_vultr_catalog.py with "
            "VULTR_API_KEY set to populate it."
        )
    return json.loads(p.read_text(encoding="utf-8"))


def regions_from_catalog(catalog: dict) -> list[Region]:
    return [
        Region(
            id=r["id"],
            city=r.get("city", r["id"]),
            country=(r.get("country") or "").upper(),
            continent=r.get("continent", ""),
        )
        for r in catalog.get("regions", [])
    ]


def cost_model_from_catalog(catalog: dict) -> CostModel:
    """Build a cost model whose prices are the real API prices."""
    model = CostModel()
    regions = [r["id"] for r in catalog.get("regions", [])]
    for plan in catalog.get("plans", []):
        hourly = plan.get("hourly_cost")
        monthly = plan.get("monthly_cost")
        if hourly is None or monthly is None:
            continue
        # A plan is priced per region; register it for every region it can
        # deploy into. Vultr exposes `locations` on some plans and not others,
        # so we fall back to all regions when the list is absent.
        locations = plan.get("locations") or regions
        for region_id in locations:
            model.register(
                InstancePrice(
                    plan_id=plan["id"],
                    region_id=region_id,
                    hourly_usd=float(hourly),
                    monthly_usd=float(monthly),
                    vcpu=int(plan.get("vcpu_count") or 0),
                    ram_mb=int(plan.get("ram") or 0),
                    disk_gb=int(plan.get("disk") or 0),
                    bandwidth_gb=int(plan.get("bandwidth") or 0),
                )
            )
    return model


def cheapest_plan_for(catalog: dict, region_id: str, min_ram_mb: int = 1024) -> dict | None:
    """The cheapest plan in a region that can run a headless browser.

    axe-core in Chromium needs roughly 1 GB to be reliable, so the default
    floor is 1 GB rather than the absolute cheapest 512 MB plan.
    """
    candidates = [
        p
        for p in catalog.get("plans", [])
        if int(p.get("ram") or 0) >= min_ram_mb
        and (not p.get("locations") or region_id in p["locations"])
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda p: float(p.get("hourly_cost") or 1e9))
