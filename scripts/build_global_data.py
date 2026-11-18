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

    payload = {
        "generated_from": "data/real/global_measurements.csv",
        "total_rows": int(len(df)),
        "countries_measured": len(countries),
        "all_domestic": bool(df.domestic_probe.all()),
        "overall_reach_pct": round(len(live) / len(df) * 100, 1),
        "countries": countries,
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
