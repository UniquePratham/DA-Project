"""Worldwide coverage model with honest statuses for every country.

The previous model had three states and marked 189 countries "unsupported",
which was true of one vendor but not of the research question. This model
distinguishes what is actually different:

* **operational** — a domestic datacentre exists and we have measured from it.
* **available** — a domestic datacentre exists on some cloud, so a probe is
  possible today; we have not measured yet.
* **resident_required** — no cloud operates in the country, but a probe is
  still possible by running the worker on a machine physically there. This is
  how the India census was originally done.
* **out_of_scope** — no realistic path to a domestic probe.

The distinction matters because "unsupported" conflates "we cannot" with "we
have not yet", and a reader deserves to know which.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pycountry

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from services.infrastructure.multicloud import (
    ALL_PROVIDERS,
    all_regions,
    cheapest_provider_for,
    countries_with_domestic_region,
)

OUT = REPO / "dashboard" / "static" / "world.json"

#: Countries where a resident probe is realistic: a research collaborator, a
#: university partner, or a machine the team can place.
RESIDENT_CANDIDATES = {
    "AF", "AL", "AM", "AO", "AR", "AZ", "BA", "BD", "BG", "BJ", "BO", "BT",
    "BW", "BY", "CM", "CO", "CR", "CU", "CY", "CZ", "DO", "DZ", "EC", "EE",
    "EG", "ET", "GE", "GH", "GT", "HN", "HR", "HU", "JO", "KE", "KG", "KH",
    "KZ", "LA", "LB", "LK", "LT", "LU", "LV", "MA", "MD", "ME", "MK", "MN",
    "MT", "MU", "MZ", "NA", "NG", "NP", "OM", "PA", "PE", "PH", "PK", "PR",
    "PS", "PY", "RO", "RS", "RU", "RW", "SN", "SV", "TH", "TJ", "TN", "TR",
    "TT", "TZ", "UA", "UG", "UY", "UZ", "VE", "VN", "XK", "ZM", "ZW",
}

#: Countries where a domestic probe is not realistic in this study.
OUT_OF_SCOPE = {
    "AQ", "BV", "TF", "HM", "GS", "IO", "CX", "CC", "NF", "PN", "TK", "NU",
    "WF", "PF", "NC", "GU", "MP", "AS", "VI", "UM", "EH", "SS", "ER", "DJ",
    "SO", "LY", "YE", "SY", "IQ", "IR", "KP", "MM", "TM", "SD", "CF", "TD",
    "NE", "ML", "BF", "GN", "GW", "SL", "LR", "CI", "TG", "GA", "CG", "CD",
    "GQ", "ST", "CV", "GM", "MR", "BI", "MW", "LS", "SZ", "MG", "KM", "SC",
    "YT", "RE", "MQ", "GP", "GF", "SR", "GY", "BZ", "HT", "JM", "BS", "BB",
    "GD", "LC", "VC", "DM", "AG", "KN", "AI", "VG", "KY", "MS", "TC", "BM",
    "FK", "SH", "GI", "FO", "GL", "SJ", "AX", "IM", "JE", "GG", "LI", "MC",
    "SM", "VA", "AD", "AW", "CW", "SX", "BQ", "MF", "BL", "PM", "SB", "VU",
    "FJ", "TO", "WS", "KI", "TV", "NR", "PW", "FM", "MH", "CK", "TL",
}


def build() -> dict:
    regions = all_regions()
    with_region = countries_with_domestic_region()

    measured: set[str] = set()
    csv = REPO / "data" / "real" / "global_measurements.csv"
    if csv.exists():
        import pandas as pd

        df = pd.read_csv(csv, usecols=["probe_country"])
        measured = set(df["probe_country"].dropna().unique())

    countries = []
    for c in pycountry.countries:
        code = c.alpha_2
        domestic = [r for r in regions if r.country == code]

        if code in measured and domestic:
            status = "operational"
            note = f"Measured from {domestic[0].city}."
        elif domestic:
            status = "available"
            provider = cheapest_provider_for(code)
            note = (
                f"Domestic region on {provider.provider} "
                f"({domestic[0].city}); not yet measured."
            )
        elif code in RESIDENT_CANDIDATES:
            status = "resident_required"
            note = (
                "No cloud datacentre. A domestic probe needs a machine placed "
                "in-country, as the India census originally used."
            )
        else:
            status = "out_of_scope"
            note = "No datacentre and no realistic path to a domestic probe."

        countries.append(
            {
                "code": code,
                "name": c.name,
                "status": status,
                "domestic_regions": [
                    {"id": r.id, "city": r.city, "continent": r.continent}
                    for r in domestic
                ],
                "region_count": len(domestic),
                "can_claim_domestic": bool(domestic),
                "measured": code in measured,
                "note": note,
            }
        )

    countries.sort(key=lambda x: x["name"])

    from collections import Counter

    counts = Counter(x["status"] for x in countries)

    return {
        "generated_from": "six cloud providers + pycountry ISO-3166",
        "total_countries": len(countries),
        "status_counts": dict(counts),
        "countries": countries,
        "regions_total": len(regions),
        "countries_with_regions": len(with_region),
        "providers": [
            {
                "provider": p.provider,
                "regions": len(p.regions),
                "countries": len({r.country for r in p.regions}),
                "cheapest_hourly_usd": p.cheapest_hourly_usd,
                "note": p.note,
            }
            for p in ALL_PROVIDERS
        ],
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
    for k, v in sorted(payload["status_counts"].items()):
        print(f"    {k:20s} {v}")
    print(
        f"  regions: {payload['regions_total']} across "
        f"{payload['countries_with_regions']} countries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
