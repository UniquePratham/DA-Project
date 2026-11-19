"""Build the global comparison bundle for the Future dashboard view.

Reads the real cross-country measurements and produces per-country aggregates
plus the provenance needed to defend them. Every row carries the probe country,
the probe region, and whether that region is genuinely domestic.

A country with no measurements is reported as ``measured: false`` rather than
with zeros, so the dashboard can distinguish "not measured" from "measured and
bad".
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import pandas as pd

CSV = REPO / "data" / "real" / "global_measurements.csv"
OUT = REPO / "dashboard" / "static" / "global.json"

COUNTRY_NAMES = {
    "IN": "India", "US": "United States", "GB": "United Kingdom",
    "CA": "Canada", "AU": "Australia", "DE": "Germany", "FR": "France",
    "JP": "Japan", "BR": "Brazil", "ZA": "South Africa", "SG": "Singapore",
    "NL": "Netherlands", "ES": "Spain", "IT": "Italy", "SE": "Sweden",
    "PL": "Poland", "KR": "South Korea", "MX": "Mexico", "CL": "Chile",
    "IL": "Israel",
}

#: Sector classification by hostname marker. A domain is assigned to the first
#: sector whose marker appears, so the order matters: health before education,
#: because "health.edu" is a health site.
SECTOR_MARKERS: list[tuple[str, tuple[str, ...]]] = [
    ("health", (
        "health", "nhs", "hospital", "medic", "clinic", "doh", "moh",
        "sante", "santé", "salud", "sanidad", "salute", "gesundheit",
        "zdrowie", "zdrav", "saude", "saúde", "sanita", "gezondheid",
        "sundhed", "hälsa", "helse", "terveys", "egeszseg",
    )),
    ("judiciary", (
        "court", "justice", "judic", "tribunal", "supreme", "leg.",
        "senat", "parliament", "congress", "assembly", "corte", "gerichte",
        "rechtspraak", "domstol", "sud", "soud",
    )),
    ("finance", (
        "fin", "tax", "revenue", "treasur", "budget", "bank", "fisco",
        "hacienda", "impots", "finanz", "skatt", "podatki",
    )),
    ("police", ("police", "policia", "polizei", "policie", "politi", "policja")),
    ("defence", ("defen", "army", "navy", "airforce", "military", "mod.", "mil.")),
    ("transport", (
        "transport", "rail", "road", "highway", "traffic", "metro",
        "aviation", "airport", "port", "shipping", "verkehr",
    )),
    ("environment", (
        "environment", "climate", "forest", "wildlife", "pollution",
        "ecology", "umwelt", "ambiente", "milieu",
    )),
    ("agriculture", (
        "agric", "farming", "farmers", "crop", "livestock", "fisheries",
        "landwirtschaft", "rolnictwo",
    )),
    ("social", (
        "social", "welfare", "pension", "benefit", "disability", "family",
        "children", "youth", "elderly", "sozial", "previdencia",
    )),
    ("education", (
        "edu", "ac.", "univ", "school", "college", "institute", "research",
        "student", "campus", "library", "bildung", "onderwijs",
    )),
]


def classify_sector(host: str) -> str:
    """Assign a domain to a sector by hostname marker, or 'general'."""
    h = host.lower()
    for sector, markers in SECTOR_MARKERS:
        if any(m in h for m in markers):
            return sector
    return "general"


def main() -> int:
    if not CSV.exists():
        print(f"no global measurements at {CSV}", file=sys.stderr)
        return 1

    df = pd.read_csv(CSV)
    live = df[df.is_reachable]

    countries = []
    for code, g in df.groupby("probe_country"):
        gl = g[g.is_reachable]
        countries.append(
            {
                "code": code,
                "name": COUNTRY_NAMES.get(code, code),
                "measured": True,
                "domains": int(len(g)),
                "reachable": int(len(gl)),
                "reach_pct": round(len(gl) / len(g) * 100, 1),
                "accessibility": round(float(gl.sub_accessibility_score.mean()), 1) if len(gl) else None,
                "security": round(float(gl.sub_security_headers_score.mean()), 1) if len(gl) else None,
                "maturity": round(float(gl.observatory_maturity_score.mean()), 1) if len(gl) else None,
                "median_ttfb_ms": int(gl.sub_response_latency_ms.median()) if len(gl) else None,
                "multilingual_pct": round(float(gl.sub_is_multilingual.mean() * 100), 1) if len(gl) else None,
                "mobile_pct": round(float(gl.sub_mobile_responsive.mean() * 100), 1) if len(gl) else None,
                "probe_region": g.probe_region.iloc[0],
                "probe_region_country": g.probe_region_country.iloc[0],
                "domestic_probe": bool(g.domestic_probe.all()),
                "measured_at": g.measured_at.iloc[0],
            }
        )

    countries.sort(key=lambda c: (c["accessibility"] is None, -(c["accessibility"] or 0)))

    # Sector breakdown, computed from the measured rows rather than the registry,
    # so it reflects what was actually measured.
    df["sector"] = df["domain_name"].map(classify_sector)
    sectors = []
    for sector, g in df.groupby("sector"):
        gl = g[g.is_reachable]
        sectors.append(
            {
                "sector": sector,
                "domains": int(len(g)),
                "reachable": int(len(gl)),
                "reach_pct": round(len(gl) / len(g) * 100, 1),
                "accessibility": round(float(gl.sub_accessibility_score.mean()), 1) if len(gl) else None,
                "security": round(float(gl.sub_security_headers_score.mean()), 1) if len(gl) else None,
                "maturity": round(float(gl.observatory_maturity_score.mean()), 1) if len(gl) else None,
                "median_ttfb_ms": int(gl.sub_response_latency_ms.median()) if len(gl) else None,
            }
        )
    sectors.sort(key=lambda s: -s["domains"])

    # Domestic vs nearest comparison: the core finding of the vantage model.
    vantage = []
    for label, is_domestic in (("domestic", True), ("nearest", False)):
        sub = df[df.domestic_probe == is_domestic]
        sr = sub[sub.is_reachable]
        if not len(sub):
            continue
        vantage.append(
            {
                "vantage": label,
                "domains": int(len(sub)),
                "reachable": int(len(sr)),
                "reach_pct": round(len(sr) / len(sub) * 100, 1),
                "accessibility": round(float(sr.sub_accessibility_score.mean()), 1) if len(sr) else None,
                "security": round(float(sr.sub_security_headers_score.mean()), 1) if len(sr) else None,
                "maturity": round(float(sr.observatory_maturity_score.mean()), 1) if len(sr) else None,
                "median_ttfb_ms": int(sr.sub_response_latency_ms.median()) if len(sr) else None,
            }
        )

    payload = {
        "generated_from": "data/real/global_measurements.csv",
        "vantage_comparison": vantage,
        "total_rows": int(len(df)),
        "countries_measured": len(countries),
        "all_domestic": bool(df.domestic_probe.all()),
        "overall_reach_pct": round(len(live) / len(df) * 100, 1),
        "countries": countries,
        "sectors": sectors,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    OUT.with_suffix(".js").write_text(
        "window.GLOBAL_DATA=" + json.dumps(payload, separators=(",", ":")) + ";",
        encoding="utf-8",
    )

    print(f"wrote {OUT}")
    print(f"  countries: {len(countries)}")
    print(f"  rows: {len(df)}")
    print(f"  all domestic probes: {payload['all_domestic']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
