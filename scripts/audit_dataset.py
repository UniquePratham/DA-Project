"""Audit the released dataset for internal consistency.

Checks that every value is in range, that the composite index reproduces from
its own components, that provenance is structurally sound, and that no row
claims a measurement it does not have.

Usage:
    python scripts/audit_dataset.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import pandas as pd  # noqa: E402

from global_dataset import read_global, reachable  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def main() -> int:
    df = read_global()
    live = reachable(df)

    print(f"rows {len(df):,}  reachable {len(live):,}  countries {df['probe_country'].nunique()}")
    print()

    # ---------------------------------------------------------------- identity
    check("no duplicate hostnames", not df["domain_name"].duplicated().any(),
          f"{int(df['domain_name'].duplicated().sum())} duplicates")
    check("every hostname is a bare host", df["domain_name"].str.contains("/").sum() == 0)
    check("every row has a country", df["probe_country"].notna().all())
    check("every row has a job id", df["job_id"].notna().all())
    check("every row has a timestamp", df["measured_at"].notna().all())

    # -------------------------------------------------------------- provenance
    dom = df[df["domestic_probe"].fillna(False).astype(bool)]
    check("domestic rows have probe region == country",
          (dom["probe_region_country"] == dom["probe_country"]).all())
    near = df[~df["domestic_probe"].fillna(False).astype(bool)]
    check("nearest rows have probe region != country",
          (near["probe_region_country"] != near["probe_country"]).all())
    check("domestic + nearest == all rows", len(dom) + len(near) == len(df))

    # ------------------------------------------------------------------ ranges
    for column, low, high in (
        ("sub_accessibility_score", 0, 100),
        ("sub_security_headers_score", 0, 100),
        ("observatory_maturity_score", 0, 100),
    ):
        values = live[column].dropna()
        check(f"{column} within [{low}, {high}]",
              bool(values.between(low, high).all()),
              f"min {values.min():.1f} max {values.max():.1f}")

    check("latency is positive", bool((live["sub_response_latency_ms"].dropna() > 0).all()))
    check("lcp is positive", bool((live["sub_lcp_est_sec"].dropna() > 0).all()))
    check("html_bytes is positive", bool((live["html_bytes"].dropna() > 0).all()))

    # ------------------------------------------------- reachable rows are whole
    for column in (
        "sub_accessibility_score",
        "sub_security_headers_score",
        "observatory_maturity_score",
        "sub_response_latency_ms",
        "sub_lcp_est_sec",
        "html_bytes",
        "sha256",
        "final_url",
        "status_code",
    ):
        check(f"reachable rows all have {column}", live[column].notna().all(),
              f"{int(live[column].isna().sum())} null")

    # ------------------------------------------- unreachable rows carry no score
    down = df[~df["is_reachable"].fillna(False).astype(bool)]
    for column in (
        "sub_accessibility_score",
        "sub_security_headers_score",
        "observatory_maturity_score",
        "sub_lcp_est_sec",
    ):
        check(f"unreachable rows have no {column}", down[column].isna().all(),
              f"{int(down[column].notna().sum())} filled")

    # A row that received a response but no auditable document keeps its
    # evidence (the byte count and the hash of what arrived) and loses only the
    # content scores. A row that never connected has neither.
    empty_body = down[down["measurement_reason"] == "HTTP 200 with an empty body"]
    check("empty-body rows keep their byte count",
          bool((empty_body["html_bytes"] < 200).all()),
          f"{len(empty_body)} rows, max {empty_body['html_bytes'].max():.0f} bytes")
    check("empty-body rows keep their hash", empty_body["sha256"].notna().all())

    never_connected = down[down["measurement_reason"] != "HTTP 200 with an empty body"]
    check("rows that never served a page have no html_bytes",
          never_connected["html_bytes"].isna().all(),
          f"{int(never_connected['html_bytes'].notna().sum())} filled")

    # ------------------------------------------------ composite reproduces
    speed = (100.0 - 15.0 * live["sub_lcp_est_sec"]).clip(lower=0.0)
    recomputed = (
        0.30 * live["sub_accessibility_score"]
        + 0.25 * live["sub_security_headers_score"]
        + 0.20 * speed
        + 10.0 * live["sub_is_multilingual"].fillna(False).astype(float)
        + 5.0 * live["sub_mobile_responsive"].fillna(False).astype(float)
        + 5.0 * live["sub_has_citizen_services"].fillna(False).astype(float)
        + 5.0 * (live["sub_cms_architecture"] == "s3waas_drupal").astype(float)
    ).clip(0.0, 100.0)

    err = (recomputed - live["observatory_maturity_score"]).abs()
    check("composite reproduces from its components", bool((err <= 0.15).all()),
          f"max error {err.max():.3f}, {int((err > 0.15).sum())} rows off")

    # ------------------------------------------------------- outcome flags
    check("waf and robots are disjoint",
          not (df["blocked_by_waf"].fillna(False).astype(bool)
               & df["robots_disallowed"].fillna(False).astype(bool)).any())
    check("a waf-blocked row is not reachable",
          not (df["blocked_by_waf"].fillna(False).astype(bool)
               & df["is_reachable"].fillna(False).astype(bool)).any())

    # ------------------------------------------------------------ coverage
    print()
    print(f"domestic rows      {len(dom):,} across {dom['probe_country'].nunique()} countries")
    print(f"nearest rows       {len(near):,} across {near['probe_country'].nunique()} countries")
    print(f"reachable          {len(live):,} ({len(live) / len(df) * 100:.1f}%)")
    print(f"waf blocked        {int(df['blocked_by_waf'].fillna(False).astype(bool).sum())}")
    print(f"robots disallowed  {int(df['robots_disallowed'].fillna(False).astype(bool).sum())}")

    print()
    if FAILURES:
        print(f"{len(FAILURES)} CHECK(S) FAILED:")
        for name in FAILURES:
            print(f"  - {name}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
