"""Build the worldwide coverage model from the vantage selector.

Every country gets one of three honest states, derived from what Vultr can
actually do rather than from a theoretical multi-cloud union:

* **domestic** — a Vultr region inside the country. Supports a citizen's-eye claim.
* **nearest** — no domestic region, but a Vultr region close enough that the
  measurement is meaningful. Supports a foreign-client claim, and is the only
  honest way to cover these countries with the account we have.
* **unmeasurable** — the nearest region is too far for the number to describe
  the portal.

The distinction is the research contribution. A portal measured from both
inside and outside its country tells you how much of its measured quality is
the portal and how much is the path to it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pycountry

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from services.infrastructure.catalog import load_catalog, regions_from_catalog
from services.infrastructure.vantage import VantageClass, VantageSelector

OUT = REPO / "dashboard" / "static" / "world.json"


def build() -> dict:
    catalog = load_catalog()
    regions = regions_from_catalog(catalog)
    selector = VantageSelector(regions)

    measured: set[str] = set()
    csv = REPO / "data" / "real" / "global_measurements.csv"
    if csv.exists():
        import pandas as pd

        df = pd.read_csv(csv, usecols=["probe_country"])
        measured = set(df["probe_country"].dropna().unique())

    countries = []
    for c in pycountry.countries:
        code = c.alpha_2
        v = selector.select(code)
        d = v.as_dict()

        if v.vantage_class is VantageClass.DOMESTIC:
            status = "operational" if code in measured else "domestic_ready"
            note = (
                f"Measured from {v.region.city}."
                if code in measured
                else f"Domestic region in {v.region.city}; not yet measured."
            )
        elif v.vantage_class is VantageClass.NEAREST:
            status = "nearest_available"
            note = (
                f"No domestic region. Nearest probe is {v.region.city}, "
                f"{v.region.country}, {d['distance_km']} km away. Measures a "
                "foreign client's view, not a citizen's."
            )
        else:
            status = "unmeasurable"
            note = v.reason

        countries.append(
            {
                "code": code,
                "name": c.name,
                "status": status,
                "vantage_class": d["vantage_class"],
                "probe_region": d["region_id"],
                "probe_city": d["region_city"],
                "probe_country": d["region_country"],
                "distance_km": d["distance_km"],
                "can_claim_domestic": d["can_claim_domestic"],
                "measured": code in measured,
                "note": note,
            }
        )

    countries.sort(key=lambda x: x["name"])

    from collections import Counter

    counts = Counter(x["status"] for x in countries)
    vantage_counts = Counter(x["vantage_class"] for x in countries)

    return {
        "generated_from": "Vultr region catalogue + country centroids",
        "total_countries": len(countries),
        "status_counts": dict(counts),
        "vantage_counts": dict(vantage_counts),
        "countries": countries,
        "regions_total": len(regions),
        "regions_countries": len({r.country for r in regions}),
        "max_nearest_km": 6000,
    }


def main() -> int:
    payload = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    OUT.with_suffix(".js").write_text(
        "window.WORLD_DATA=" + json.dumps(payload, separators=(",", ":")) + ";",
        encoding="utf-8",
    )

    print(f"wrote {OUT}")
    print(f"  countries: {payload['total_countries']}")
    print("  by status:")
    for k, v in sorted(payload["status_counts"].items()):
        print(f"    {k:20s} {v}")
    print("  by vantage class:")
    for k, v in sorted(payload["vantage_counts"].items()):
        print(f"    {k:20s} {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
