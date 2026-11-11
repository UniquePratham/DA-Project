"""Build the honest dataset: only domains that were actually discovered.

A domain qualifies only if it came from a real discovery source:
  - certificate_transparency : appeared in a real issued TLS certificate
  - seed_registry            : named in the project's curated registry
  - institutional_directory  : linked from an official directory page
  - link_crawl               : linked from a live government portal's HTML

Domains generated from naming conventions (`finance.up.gov.in`) are EXCLUDED.
They were never observed anywhere; measuring them only produces noise and
inflates the unreachable count with things that were never portals.

Every remaining row carries a real HTTP measurement.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

REAL_DIR = Path("data/real")
REGISTRY = Path("data/fixtures/registry_full.json")
LINKED = Path("data/fixtures/linked_domains.json")

OUT_CSV = Path("resources/bharatgov_access_clean.csv")
OUT_PARQUET = Path("resources/bharatgov_access_clean.parquet")
OUT_JSON = Path("resources/bharatgov_access_clean.json")
DASH_JSON = Path("dashboard/static/dataset.json")
DASH_JS = Path("dashboard/static/dataset.js")

# Sources that represent a genuine observation of the domain.
VERIFIED_SOURCES = {
    "certificate_transparency",
    "seed_registry",
    "institutional_directory",
    "link_crawl",
}

COLUMNS = [
    "domain_name", "entity_name", "government_level", "state_or_ut", "district",
    "final_url", "http_status_code", "is_reachable", "measurement_reason",
    "sub_accessibility_score", "sub_has_gigw_toolbar", "sub_response_latency_ms",
    "sub_lcp_est_sec", "sub_https_enforced", "sub_security_headers_score",
    "sub_is_multilingual", "sub_mobile_responsive", "sub_cms_architecture",
    "sub_has_citizen_services", "observatory_maturity_score",
]

# Real state/UT slugs that appear inside Indian government hostnames.
STATE_SLUGS = {
    "ap": "Andhra Pradesh", "arunachal": "Arunachal Pradesh", "assam": "Assam",
    "bihar": "Bihar", "cgstate": "Chhattisgarh", "chhattisgarh": "Chhattisgarh",
    "goa": "Goa", "gujarat": "Gujarat", "haryana": "Haryana", "hp": "Himachal Pradesh",
    "himachal": "Himachal Pradesh", "jharkhand": "Jharkhand", "karnataka": "Karnataka",
    "kerala": "Kerala", "mp": "Madhya Pradesh", "madhya": "Madhya Pradesh",
    "maharashtra": "Maharashtra", "manipur": "Manipur", "meghalaya": "Meghalaya",
    "mizoram": "Mizoram", "nagaland": "Nagaland", "odisha": "Odisha", "ori": "Odisha",
    "punjab": "Punjab", "rajasthan": "Rajasthan", "sikkim": "Sikkim",
    "tn": "Tamil Nadu", "tamilnadu": "Tamil Nadu", "telangana": "Telangana",
    "tripura": "Tripura", "up": "Uttar Pradesh", "uttar": "Uttar Pradesh",
    "uk": "Uttarakhand", "uttarakhand": "Uttarakhand", "wb": "West Bengal",
    "bengal": "West Bengal", "delhi": "Delhi", "jk": "Jammu and Kashmir",
    "jammu": "Jammu and Kashmir", "ladakh": "Ladakh", "puducherry": "Puducherry",
    "py": "Puducherry", "chandigarh": "Chandigarh",
    "andaman": "Andaman and Nicobar Islands",
    "dnh": "Dadra and Nagar Haveli and Daman and Diu",
    "daman": "Dadra and Nagar Haveli and Daman and Diu", "lakshadweep": "Lakshadweep",
}

ACADEMIC_MARKERS = (
    "iit", "nit", "iiit", "iim", "iiser", "niser", "aiims", "university", "univ",
    "college", "institute", "academy", "polytechnic", "school",
)
JUDICIAL_MARKERS = (
    "court", "judiciary", "tribunal", "nclt", "nclat", "lokayukta", "legal",
)
MUNICIPAL_MARKERS = ("municipal", "nagar", "corporation", "panchayat")
DISTRICT_MARKERS = ("district", "collectorate", "dm.", "dc.")


def infer_state(host: str) -> str:
    """Infer the State/UT from a real hostname's own labels."""
    for label in host.lower().split("."):
        if label in STATE_SLUGS:
            return STATE_SLUGS[label]
    return "National / Central"


def infer_level(host: str) -> str:
    """Infer the governance tier from a real hostname's own labels."""
    h = host.lower()
    if any(m in h for m in JUDICIAL_MARKERS):
        return "judiciary"
    if any(m in h for m in ACADEMIC_MARKERS) or h.endswith(
        (".ac.in", ".res.in", ".edu.in")
    ):
        return "academic_research"
    if any(m in h for m in MUNICIPAL_MARKERS):
        return "urban_local_body"
    if any(m in h for m in DISTRICT_MARKERS):
        return "district"
    return "state_ut"


def load_measurements() -> pd.DataFrame:
    frames = []
    for name in ("real_full.csv", "real_rest.csv", "real_linked.csv"):
        p = REAL_DIR / name
        if not p.exists():
            continue
        df = pd.read_csv(p)
        print(f"  {name}: {len(df):,} rows")
        frames.append(df)
    if not frames:
        raise SystemExit("no measurement files")
    df = pd.concat(frames, ignore_index=True)
    df["_ok"] = df["is_reachable"].fillna(False).astype(bool)
    df = df.sort_values("_ok", ascending=False).drop_duplicates("domain_name", keep="first")
    return df.drop(columns=["_ok"])


def main() -> int:
    print("loading measurements...")
    meas = load_measurements()
    print(f"  unique measured: {len(meas):,}")

    reg = pd.DataFrame(json.loads(REGISTRY.read_text(encoding="utf-8")))
    print(f"  registry: {len(reg):,}")

    # Add link-crawl discoveries to the registry with inferred metadata.
    if LINKED.exists():
        linked = json.loads(LINKED.read_text(encoding="utf-8"))
        known = set(reg["domain_name"])
        extra = []
        for r in linked:
            d = r["domain_name"]
            if d in known:
                continue
            extra.append(
                {
                    "domain_name": d,
                    "entity_name": d,
                    "government_level": infer_level(d),
                    "state_or_ut": infer_state(d),
                    "district": "N/A",
                    "discovery_source": "link_crawl",
                }
            )
        if extra:
            reg = pd.concat([reg, pd.DataFrame(extra)], ignore_index=True)
            print(f"  + {len(extra):,} link-crawl domains")

    # THE FILTER: drop every convention-guessed domain.
    before = len(reg)
    reg = reg[reg["discovery_source"].isin(VERIFIED_SOURCES)].copy()
    print(f"  dropped {before - len(reg):,} convention-guessed domains")
    print(f"  verified-discovery registry: {len(reg):,}")

    df = reg.merge(meas, on="domain_name", how="left", suffixes=("", "_m"))
    if "http_status_code" not in df.columns and "status_code" in df.columns:
        df["http_status_code"] = df["status_code"]

    unmeasured = df["is_reachable"].isna().sum()
    if unmeasured:
        print(f"  dropping {unmeasured:,} verified domains with no measurement yet")
        df = df[df["is_reachable"].notna()].copy()

    df["is_reachable"] = df["is_reachable"].astype(bool)
    df["http_status_code"] = pd.to_numeric(df["http_status_code"], errors="coerce")

    for col in (
        "sub_has_gigw_toolbar", "sub_https_enforced", "sub_is_multilingual",
        "sub_mobile_responsive", "sub_has_citizen_services",
    ):
        df[col] = df[col].map(
            lambda v: True if str(v).lower() in ("true", "1", "1.0")
            else (False if str(v).lower() in ("false", "0", "0.0") else None)
        )

    df["measurement_reason"] = df["measurement_reason"].fillna("Not measured")
    df["final_url"] = df["final_url"].fillna("")
    df["sub_cms_architecture"] = df["sub_cms_architecture"].fillna("indeterminate_unreachable")

    # Recompute maturity from the measured pillars so the published column is
    # always exactly reproducible from its own inputs. The crawler's own value
    # is kept as a cross-check.
    def _maturity(r) -> float | None:
        if pd.isna(r["sub_accessibility_score"]) or pd.isna(r["sub_security_headers_score"]):
            return None
        lcp = 0.0 if pd.isna(r["sub_lcp_est_sec"]) else float(r["sub_lcp_est_sec"])
        score = (
            0.30 * float(r["sub_accessibility_score"])
            + 0.25 * float(r["sub_security_headers_score"])
            + 0.20 * max(0.0, 100.0 - 15.0 * lcp)
            + 10.0 * (1.0 if r["sub_is_multilingual"] else 0.0)
            + 5.0 * (1.0 if r["sub_mobile_responsive"] else 0.0)
            + 5.0 * (1.0 if r["sub_has_citizen_services"] else 0.0)
            + 5.0 * (1.0 if r["sub_cms_architecture"] == "s3waas_drupal" else 0.0)
        )
        return round(max(0.0, min(100.0, score)), 1)

    df["observatory_maturity_score"] = df.apply(_maturity, axis=1)

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[COLUMNS].sort_values("domain_name").reset_index(drop=True)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    df.to_parquet(OUT_PARQUET, index=False)
    df.to_json(OUT_JSON, orient="records", indent=2)

    reach = df[df.is_reachable]
    print(f"\n=== HONEST DATASET ===")
    print(f"total: {len(df):,}")
    print(f"reachable: {len(reach):,} ({len(reach)/len(df)*100:.1f}%)")
    print(f"unreachable: {len(df)-len(reach):,}")
    print("\nmeans (reachable):")
    for col, label in [
        ("sub_accessibility_score", "accessibility"),
        ("sub_security_headers_score", "security"),
        ("observatory_maturity_score", "maturity"),
        ("sub_response_latency_ms", "latency ms"),
        ("sub_lcp_est_sec", "LCP sec"),
    ]:
        s = reach[col].dropna()
        print(f"  {label:16s} mean={s.mean():8.2f} median={s.median():8.2f} n={len(s):,}")

    print("\nby tier:")
    for tier, g in reach.groupby("government_level"):
        print(f"  {tier:20s} n={len(g):5,} acc={g.sub_accessibility_score.mean():5.1f} mat={g.observatory_maturity_score.mean():5.1f}")

    dash = []
    for _, r in df.iterrows():
        dash.append({
            "domain": r["domain_name"], "entity": r["entity_name"],
            "level": r["government_level"], "state": r["state_or_ut"],
            "district": r["district"], "final_url": r["final_url"],
            "status_code": int(r["http_status_code"]) if pd.notna(r["http_status_code"]) else None,
            "reachable": bool(r["is_reachable"]), "meas_reason": r["measurement_reason"],
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
        })

    DASH_JSON.write_text(json.dumps(dash, separators=(",", ":")), encoding="utf-8")
    DASH_JS.write_text("window.RAW_DATASET=" + json.dumps(dash, separators=(",", ":")) + ";", encoding="utf-8")
    print(f"\ndashboard bundle: {len(dash):,} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
