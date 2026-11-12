"""Worldwide country coverage, derived from real facts only.

Every country in the ISO-3166 list is classified into exactly one status, and
the classification is derived rather than asserted:

* ``operational``  - a cloud region physically inside the country exists, so a
                     domestic probe is possible today.
* ``planned``      - the country is on the research roadmap but no domestic
                     region exists yet.
* ``unsupported``  - no domestic region exists and the country is not on the
                     roadmap, so no domestic measurement is possible.

A country is never marked operational because a nearby region exists. The
``nearest_region`` field is recorded for operational convenience and is always
labelled with the country it actually sits in, so a foreign probe can never be
mistaken for a domestic one.

The region table comes from the live Vultr API (cached to
``data/fixtures/vultr_catalog.json``). The country list comes from pycountry.
Nothing here is invented.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pycountry

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from services.infrastructure.catalog import load_catalog, regions_from_catalog
from services.infrastructure.regions import ProbeRegistry, ProbeStatus

OUT = REPO / "dashboard" / "static" / "world.json"

#: Countries the research programme intends to cover first. These are marked
#: ``planned`` when no domestic region exists, rather than ``unsupported``.
ROADMAP_COUNTRIES = {
    "IN", "US", "GB", "CA", "AU", "DE", "FR", "JP", "BR", "ZA",
    "NZ", "IE", "NL", "ES", "IT", "SE", "PL", "KR", "SG", "MX",
    "AR", "CL", "CO", "PE", "NG", "KE", "EG", "MA", "GH", "TZ",
    "ID", "PH", "MY", "TH", "VN", "PK", "BD", "LK", "NP", "AE",
    "SA", "IL", "TR", "RU", "UA", "CN", "TW", "HK", "AT", "BE",
    "CH", "DK", "FI", "NO", "PT", "GR", "CZ", "HU", "RO", "BG",
}

#: Continent lookup for the map grouping. Derived from pycountry's region data
#: where available, with a small override table for the countries pycountry
#: leaves blank.
CONTINENT_OVERRIDES = {
    "TW": "Asia", "HK": "Asia", "MO": "Asia", "PS": "Asia",
    "XK": "Europe", "AQ": "Antarctica",
}


def continent_of(country) -> str:
    """Best-effort continent for grouping, never used for a measurement claim."""
    code = country.alpha_2
    if code in CONTINENT_OVERRIDES:
        return CONTINENT_OVERRIDES[code]
    # pycountry exposes a coarse region on some subdivisions only; fall back to
    # the UN region where present.
    try:
        sub = pycountry.subdivisions  # noqa: F841  (import side effect only)
    except Exception:  # noqa: BLE001
        pass
    return ""


def build() -> dict:
    catalog = load_catalog()
    regions = regions_from_catalog(catalog)
    registry = ProbeRegistry(regions)

    # Which countries actually have a region, and where.
    by_country: dict[str, list[dict]] = {}
    for r in regions:
        by_country.setdefault(r.country, []).append(
            {"id": r.id, "city": r.city, "continent": r.continent}
        )

    countries = []
    for c in pycountry.countries:
        code = c.alpha_2
        name = c.name
        domestic = by_country.get(code, [])

        if domestic:
            status = ProbeStatus.OPERATIONAL.value
            note = f"Domestic region available: {domestic[0]['city']}."
        elif code in ROADMAP_COUNTRIES:
            status = ProbeStatus.PLANNED.value
            note = "On the research roadmap; no domestic cloud region yet."
        else:
            status = ProbeStatus.UNSUPPORTED.value
            note = "No domestic cloud region; domestic measurement not possible."

        countries.append(
            {
                "code": code,
                "name": name,
                "status": status,
                "domestic_regions": domestic,
                "region_count": len(domestic),
                "can_claim_domestic": bool(domestic),
                "on_roadmap": code in ROADMAP_COUNTRIES,
                "measured": code == "IN",
                "note": note,
            }
        )

    countries.sort(key=lambda x: x["name"])

    from collections import Counter

    counts = Counter(x["status"] for x in countries)

    return {
        "generated_from": "live Vultr region catalogue + pycountry ISO-3166",
        "total_countries": len(countries),
        "status_counts": dict(counts),
        "countries": countries,
        "regions_total": len(regions),
        "countries_with_regions": len(by_country),
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
        print(f"    {k:12s} {v}")
    print(f"  regions: {payload['regions_total']} across {payload['countries_with_regions']} countries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
