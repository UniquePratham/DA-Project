"""Fetch the live Vultr region and plan catalogue.

Run with ``VULTR_API_KEY`` set. Writes ``data/fixtures/vultr_catalog.json``,
which the cost model and the Future dashboard read.

The key is read from the environment and never written anywhere.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx

OUT = Path(__file__).resolve().parent.parent / "data" / "fixtures" / "vultr_catalog.json"
API = "https://api.vultr.com/v2"


def main() -> int:
    key = os.environ.get("VULTR_API_KEY", "")
    if not key:
        print("VULTR_API_KEY is not set", file=sys.stderr)
        return 1

    headers = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
    with httpx.Client(timeout=60) as client:
        regions_resp = client.get(f"{API}/regions?per_page=500", headers=headers)
        regions_resp.raise_for_status()
        regions = regions_resp.json().get("regions", [])

        plans_resp = client.get(f"{API}/plans?per_page=500&type=vc2", headers=headers)
        plans_resp.raise_for_status()
        plans = plans_resp.json().get("plans", [])

    payload = {
        "fetched_from": API,
        "regions": [
            {
                "id": r["id"],
                "city": r.get("city", ""),
                "country": r.get("country", ""),
                "continent": r.get("continent", ""),
            }
            for r in regions
        ],
        "plans": [
            {
                "id": p["id"],
                "vcpu_count": p.get("vcpu_count"),
                "ram": p.get("ram"),
                "disk": p.get("disk"),
                "bandwidth": p.get("bandwidth"),
                "monthly_cost": p.get("monthly_cost"),
                "hourly_cost": p.get("hourly_cost"),
                "locations": p.get("locations", []),
            }
            for p in plans
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")

    countries = sorted({r["country"] for r in payload["regions"]})
    print(f"wrote {OUT}")
    print(f"  regions: {len(payload['regions'])} across {len(countries)} countries")
    print(f"  plans:   {len(payload['plans'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
