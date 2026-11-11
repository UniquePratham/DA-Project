"""Build the final dataset from real measurements only.

Inputs:
  data/real/real_full.csv   - pass 1 measurements (9,066 domains)
  data/real/real_rest.csv   - pass 2 measurements (4,237 domains)
  data/fixtures/registry_full.json - tier/state metadata

Outputs:
  resources/bharatgov_access_clean.csv
  resources/bharatgov_access_clean.parquet
  resources/bharatgov_access_clean.json
  dashboard/static/dataset.json
  dashboard/static/dataset.js

Every measurement column comes from an actual HTTP response. The only derived
column is `observatory_maturity_score`, which applies the published formula to
measured inputs. No value is sampled, imputed, or synthesised.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

REAL_DIR = Path("data/real")
REGISTRY = Path("data/fixtures/registry_full.json")
OUT_CSV = Path("resources/bharatgov_access_clean.csv")
OUT_PARQUET = Path("resources/bharatgov_access_clean.parquet")
OUT_JSON = Path("resources/bharatgov_access_clean.json")
DASH_JSON = Path("dashboard/static/dataset.json")
DASH_JS = Path("dashboard/static/dataset.js")

COLUMNS = [
    "domain_name",
    "entity_name",
    "government_level",
    "state_or_ut",
    "district",
    "final_url",
    "http_status_code",
    "is_reachable",
    "measurement_reason",
    "sub_accessibility_score",
    "sub_has_gigw_toolbar",
    "sub_response_latency_ms",
    "sub_lcp_est_sec",
    "sub_https_enforced",
    "sub_security_headers_score",
    "sub_is_multilingual",
    "sub_mobile_responsive",
    "sub_cms_architecture",
    "sub_has_citizen_services",
    "observatory_maturity_score",
]


def load_measurements() -> pd.DataFrame:
    frames = []
    for name in ("real_full.csv", "real_rest.csv"):
        p = REAL_DIR / name
        if not p.exists():
            print(f"  {name}: missing, skipped")
            continue
        df = pd.read_csv(p)
        print(f"  {name}: {len(df):,} rows")
        frames.append(df)
    if not frames:
        raise SystemExit("no measurement files found")
    df = pd.concat(frames, ignore_index=True)
    # A domain measured twice keeps its first successful observation.
    df["_ok"] = df["is_reachable"].fillna(False).astype(bool)
    df = df.sort_values("_ok", ascending=False).drop_duplicates("domain_name", keep="first")
    return df.drop(columns=["_ok"])


def main() -> int:
    print("loading real measurements...")
    meas = load_measurements()
    print(f"  unique domains measured: {len(meas):,}")

    reg = pd.DataFrame(json.loads(REGISTRY.read_text(encoding="utf-8")))
    print(f"  registry entries: {len(reg):,}")

    df = reg.merge(meas, on="domain_name", how="left", suffixes=("", "_m"))

    # The crawler writes `status_code`; the published schema calls it
    # `http_status_code`.
    if "http_status_code" not in df.columns and "status_code" in df.columns:
        df["http_status_code"] = df["status_code"]

    # Domains in the registry that were never measured are excluded, not faked.
    unmeasured = df["is_reachable"].isna().sum()
    if unmeasured:
        print(f"  dropping {unmeasured:,} registry entries with no measurement")
        df = df[df["is_reachable"].notna()].copy()

    df["is_reachable"] = df["is_reachable"].astype(bool)
    df["http_status_code"] = pd.to_numeric(df["http_status_code"], errors="coerce")

    # Normalise booleans that came back as strings from CSV.
    for col in (
        "sub_has_gigw_toolbar",
        "sub_https_enforced",
        "sub_is_multilingual",
        "sub_mobile_responsive",
        "sub_has_citizen_services",
    ):
        df[col] = df[col].map(
            lambda v: True if str(v).lower() in ("true", "1", "1.0") else (False if str(v).lower() in ("false", "0", "0.0") else None)
        )

    df["measurement_reason"] = df["measurement_reason"].fillna("Not measured")
    df["final_url"] = df["final_url"].fillna("")
    df["sub_cms_architecture"] = df["sub_cms_architecture"].fillna("indeterminate_unreachable")

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[COLUMNS]

    df = df.sort_values("domain_name").reset_index(drop=True)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    df.to_parquet(OUT_PARQUET, index=False)
    df.to_json(OUT_JSON, orient="records", indent=2)

    reach = df[df.is_reachable]
    print(f"\nwrote {len(df):,} rows")
    print(f"  reachable: {len(reach):,} ({len(reach)/len(df)*100:.1f}%)")
    print(f"  unreachable: {len(df)-len(reach):,}")
    print("\nreal measured means (reachable only):")
    for col, label in [
        ("sub_accessibility_score", "accessibility"),
        ("sub_security_headers_score", "security headers"),
        ("observatory_maturity_score", "maturity"),
        ("sub_response_latency_ms", "latency ms"),
        ("sub_lcp_est_sec", "LCP sec"),
    ]:
        s = reach[col].dropna()
        print(f"  {label:18s} mean={s.mean():8.2f}  median={s.median():8.2f}  n={len(s):,}")

    print("\nby tier:")
    for tier, g in reach.groupby("government_level"):
        print(f"  {tier:22s} n={len(g):5,}  acc={g.sub_accessibility_score.mean():5.1f}  mat={g.observatory_maturity_score.mean():5.1f}")

    # Dashboard bundle
    dash = []
    for _, r in df.iterrows():
        dash.append(
            {
                "domain": r["domain_name"],
                "entity": r["entity_name"],
                "level": r["government_level"],
                "state": r["state_or_ut"],
                "district": r["district"],
                "final_url": r["final_url"],
                "status_code": int(r["http_status_code"]) if pd.notna(r["http_status_code"]) else None,
                "reachable": bool(r["is_reachable"]),
                "meas_reason": r["measurement_reason"],
                "acc_score": None if pd.isna(r["sub_accessibility_score"]) else round(float(r["sub_accessibility_score"]), 1),
                "has_gigw_toolbar": bool(r["sub_has_gigw_toolbar"]) if r["sub_has_gigw_toolbar"] is not None else False,
                "latency_ms": None if pd.isna(r["sub_response_latency_ms"]) else round(float(r["sub_response_latency_ms"]), 1),
                "lcp_sec": None if pd.isna(r["sub_lcp_est_sec"]) else round(float(r["sub_lcp_est_sec"]), 2),
                "has_https": bool(r["sub_https_enforced"]) if r["sub_https_enforced"] is not None else False,
                "sec_score": None if pd.isna(r["sub_security_headers_score"]) else round(float(r["sub_security_headers_score"]), 1),
                "multilingual": bool(r["sub_is_multilingual"]) if r["sub_is_multilingual"] is not None else False,
                "mobile_responsive": bool(r["sub_mobile_responsive"]) if r["sub_mobile_responsive"] is not None else False,
                "arch": r["sub_cms_architecture"],
                "has_citizen_services": bool(r["sub_has_citizen_services"]) if r["sub_has_citizen_services"] is not None else False,
                "maturity_score": None if pd.isna(r["observatory_maturity_score"]) else round(float(r["observatory_maturity_score"]), 1),
            }
        )

    DASH_JSON.write_text(json.dumps(dash, separators=(",", ":")), encoding="utf-8")
    DASH_JS.write_text(
        "window.RAW_DATASET=" + json.dumps(dash, separators=(",", ":")) + ";",
        encoding="utf-8",
    )
    print(f"\nwrote dashboard bundle: {len(dash):,} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
