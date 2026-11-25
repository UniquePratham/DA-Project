"""Build the canonical released dataset from the raw measurement log.

The raw log is append-only: every measurement job appends its rows, so a host
measured twice appears twice. Two defects follow from releasing it as-is, and
both are fixed here rather than papered over downstream.

**Duplicate hosts.** 128 hosts were measured in more than one job, giving 2,143
rows for 2,011 distinct domains. A duplicate double-counts a domain in every
mean and inflates the population. The canonical release keeps the **latest**
measurement per host, because a later observation supersedes an earlier one.

**Empty bodies scored as accessible.** A host that returns ``HTTP 200`` with a
zero-byte body has no DOM to audit. The crawler's heuristic gave it
``alt_cov = 1.0`` and ``label_cov = 1.0`` because there were no images and no
form fields to fail, so an empty page scored 90.0 on accessibility — higher than
the population mean. An empty document is not accessible; it is unmeasurable.
Those rows keep their latency and status but lose every content score.

Usage:
    python scripts/build_canonical_dataset.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import pandas as pd  # noqa: E402

from global_dataset import GLOBAL_CSV, read_global, reachable  # noqa: E402

OUT = REPO / "data" / "real" / "global_measurements_canonical.csv"

#: A body smaller than this cannot contain a document worth auditing. The
#: smallest real government homepage in the release is several kilobytes; a
#: body under 200 bytes is an empty shell, a redirect stub, or a bot-check page.
MIN_AUDITABLE_BYTES = 200

#: Content metrics that require a real document. They are nulled when the body
#: is too small to audit.
CONTENT_COLUMNS = (
    "sub_accessibility_score",
    "sub_has_gigw_toolbar",
    "sub_lcp_est_sec",
    "sub_security_headers_score",
    "sub_is_multilingual",
    "sub_mobile_responsive",
    "sub_cms_architecture",
    "sub_has_citizen_services",
    "observatory_maturity_score",
)


def main() -> int:
    raw = read_global(GLOBAL_CSV)
    print(f"raw rows            {len(raw):,}")
    print(f"raw distinct hosts  {raw['domain_name'].nunique():,}")

    # ---- 1. keep the latest measurement per host -------------------------
    df = (
        raw.sort_values(["domain_name", "measured_at"])
        .drop_duplicates("domain_name", keep="last")
        .reset_index(drop=True)
    )
    dropped = len(raw) - len(df)
    print(f"duplicates dropped  {dropped:,}")
    print(f"canonical rows      {len(df):,}")

    # ---- 2. an empty body is not an auditable document -------------------
    live = df["is_reachable"].fillna(False).astype(bool)
    empty = live & (df["html_bytes"].fillna(0) < MIN_AUDITABLE_BYTES)
    print(f"empty-body rows     {int(empty.sum()):,}")

    if empty.any():
        df.loc[empty, "is_reachable"] = False
        df.loc[empty, "measurement_reason"] = "HTTP 200 with an empty body"
        for column in CONTENT_COLUMNS:
            df.loc[empty, column] = pd.NA

    # ---- 3. verify the result -------------------------------------------
    live_after = reachable(df)
    assert not df["domain_name"].duplicated().any(), "duplicates survived"
    assert (live_after["html_bytes"] >= MIN_AUDITABLE_BYTES).all(), "an empty body is still scored"
    assert live_after["sub_accessibility_score"].notna().all(), "a scored row lost its score"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    print()
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")
    print(f"  rows        {len(df):,}")
    print(f"  reachable   {len(live_after):,} ({len(live_after) / len(df) * 100:.1f}%)")
    print(f"  countries   {df['probe_country'].nunique()}")
    print(f"  acc         {live_after['sub_accessibility_score'].mean():.1f}")
    print(f"  sec         {live_after['sub_security_headers_score'].mean():.1f}")
    print(f"  maturity    {live_after['observatory_maturity_score'].mean():.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
