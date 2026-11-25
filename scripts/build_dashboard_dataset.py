"""Build the dashboard dataset bundle from the canonical measurements.

Reads ``data/real/global_measurements_canonical.csv`` — one row per host, latest
measurement wins, no content score on a body too small to audit — and emits the
per-domain bundle the dashboard renders.

Output: ``dashboard/static/dataset.js`` and ``dataset.json``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import pandas as pd  # noqa: E402

from global_dataset import GLOBAL_CSV as CSV  # noqa: E402
from global_dataset import country_name, read_global  # noqa: E402

OUT_JS = REPO / "dashboard" / "static" / "dataset.js"
OUT_JSON = REPO / "dashboard" / "static" / "dataset.json"


def main() -> int:
    if not CSV.exists():
        print(f"missing {CSV}", file=sys.stderr)
        return 1

    df = read_global(CSV)
    print(f"source rows: {len(df)}")

    records = []
    for _, r in df.iterrows():
        code = str(r.get("probe_country") or "")
        records.append(
            {
                "domain": r["domain_name"],
                "entity": r["domain_name"],
                "level": "public_sector",
                "state": country_name(code),
                "country": code,
                "district": "N/A",
                "final_url": r.get("final_url") if pd.notna(r.get("final_url")) else "",
                "status_code": int(r["status_code"]) if pd.notna(r.get("status_code")) else None,
                "reachable": bool(r["is_reachable"]),
                "meas_reason": r.get("measurement_reason") if pd.notna(r.get("measurement_reason")) else "",
                "acc_score": round(float(r["sub_accessibility_score"]), 1) if pd.notna(r.get("sub_accessibility_score")) else None,
                "has_gigw_toolbar": bool(r["sub_has_gigw_toolbar"]) if pd.notna(r.get("sub_has_gigw_toolbar")) else False,
                "latency_ms": round(float(r["sub_response_latency_ms"]), 1) if pd.notna(r.get("sub_response_latency_ms")) else None,
                "lcp_sec": round(float(r["sub_lcp_est_sec"]), 2) if pd.notna(r.get("sub_lcp_est_sec")) else None,
                "has_https": bool(r["sub_https_enforced"]) if pd.notna(r.get("sub_https_enforced")) else False,
                "sec_score": round(float(r["sub_security_headers_score"]), 1) if pd.notna(r.get("sub_security_headers_score")) else None,
                "multilingual": bool(r["sub_is_multilingual"]) if pd.notna(r.get("sub_is_multilingual")) else False,
                "mobile_responsive": bool(r["sub_mobile_responsive"]) if pd.notna(r.get("sub_mobile_responsive")) else False,
                "arch": r.get("sub_cms_architecture") if pd.notna(r.get("sub_cms_architecture")) else "unknown",
                "has_citizen_services": bool(r["sub_has_citizen_services"]) if pd.notna(r.get("sub_has_citizen_services")) else False,
                "maturity_score": round(float(r["observatory_maturity_score"]), 1) if pd.notna(r.get("observatory_maturity_score")) else None,
                "probe_region": r.get("probe_region") if pd.notna(r.get("probe_region")) else "",
                "domestic_probe": bool(r["domestic_probe"]) if pd.notna(r.get("domestic_probe")) else False,
                "distance_km": int(r["distance_km"]) if "distance_km" in df.columns and pd.notna(r.get("distance_km")) else None,
            }
        )

    OUT_JSON.write_text(json.dumps(records, separators=(",", ":")), encoding="utf-8")
    OUT_JS.write_text(
        "window.RAW_DATASET=" + json.dumps(records, separators=(",", ":")) + ";",
        encoding="utf-8",
    )

    print(f"wrote {len(records)} records")
    print(f"  countries: {len({r['country'] for r in records})}")
    print(f"  reachable: {sum(1 for r in records if r['reachable'])}")
    print(f"  domestic:  {sum(1 for r in records if r['domestic_probe'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
