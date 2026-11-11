"""BharatGov Access — census-scale dataset for India's public web infrastructure.

The package bundles the released 12,092-domain census and exposes it as a pandas
DataFrame with typed columns, plus a small analysis layer for the figures quoted
in the accompanying paper.

Quick start::

    import bharatgov_access as bga

    df = bga.load()                 # all 12,092 domains
    live = bga.load(reachable=True) # the 10,247 that answered in-country

    bga.tier_summary(live)          # Table I of the paper
    bga.architecture_summary(live)  # Table II of the paper
    bga.state_ranking(live)         # state and UT ranking

Every function is a thin, documented wrapper over pandas so results are
reproducible with plain ``groupby`` calls.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd

__version__ = "1.0.0"
__all__ = [
    "__version__",
    "COLUMNS",
    "TIERS",
    "TIER_LABELS",
    "ARCHITECTURES",
    "NATIONAL_BUCKETS",
    "dataset_path",
    "load",
    "tier_summary",
    "architecture_summary",
    "state_ranking",
    "maturity_index",
    "describe_release",
]

#: The 20 released columns, in release order.
COLUMNS: tuple[str, ...] = (
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
)

#: The seven governance tiers, in reporting order.
TIERS: tuple[str, ...] = (
    "central",
    "state_ut",
    "district",
    "academic_research",
    "judiciary",
    "public_sector",
    "urban_local_body",
)

TIER_LABELS: dict[str, str] = {
    "central": "Central ministries",
    "state_ut": "State departments",
    "district": "District administrations",
    "academic_research": "Higher education",
    "judiciary": "Judiciary",
    "public_sector": "Public sector & banks",
    "urban_local_body": "Urban local bodies",
}

ARCHITECTURES: tuple[str, ...] = (
    "s3waas_drupal",
    "custom_dynamic_cms",
    "modern_spa",
    "legacy_asp_net",
    "wordpress",
)

#: Values of ``state_or_ut`` that describe central bodies rather than a State or UT.
NATIONAL_BUCKETS: tuple[str, ...] = ("National", "National / Central", "Central Government")

#: ``local_body`` and ``urban_local_body`` are the same tier in the release.
_LEVEL_ALIASES: dict[str, str] = {"local_body": "urban_local_body"}

_BOOLEAN_COLUMNS = (
    "is_reachable",
    "sub_has_gigw_toolbar",
    "sub_https_enforced",
    "sub_is_multilingual",
    "sub_mobile_responsive",
    "sub_has_citizen_services",
)

_FLOAT_COLUMNS = (
    "sub_accessibility_score",
    "sub_response_latency_ms",
    "sub_lcp_est_sec",
    "sub_security_headers_score",
    "observatory_maturity_score",
)


def dataset_path() -> Path:
    """Absolute path to the bundled Parquet release."""
    return Path(str(resources.files(__name__).joinpath("data/bharatgov_access_clean.parquet")))


def load(
    reachable: bool | None = None,
    tiers: Sequence[str] | Iterable[str] | None = None,
    states: Sequence[str] | Iterable[str] | None = None,
) -> pd.DataFrame:
    """Load the census as a typed DataFrame.

    Args:
        reachable: ``True`` keeps only domains that answered in-country,
            ``False`` keeps only the offline ones, ``None`` keeps everything.
        tiers: Optional governance-tier filter, e.g. ``["district"]``.
        states: Optional State/UT filter, e.g. ``["Kerala", "Goa"]``.

    Returns:
        A DataFrame with the 20 released columns, booleans as ``bool`` and
        scores as ``float``. ``government_level`` is normalised so that
        ``local_body`` reads as ``urban_local_body``.
    """
    df = pd.read_parquet(dataset_path())

    df["government_level"] = df["government_level"].replace(_LEVEL_ALIASES)

    for column in _BOOLEAN_COLUMNS:
        df[column] = df[column].astype("boolean").fillna(False).astype(bool)

    for column in _FLOAT_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if reachable is not None:
        df = df[df["is_reachable"] == bool(reachable)]

    if tiers is not None:
        wanted = list(tiers)
        df = df[df["government_level"].isin(wanted)]

    if states is not None:
        wanted = list(states)
        df = df[df["state_or_ut"].isin(wanted)]

    return df.reset_index(drop=True)


def tier_summary(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Per-tier census table — the paper's Table I.

    Returns one row per governance tier plus a ``National`` row, with counts,
    reachability, mean accessibility and security scores, GIGW toolbar and
    scheduled-language penetration, median time to first byte, and mean
    composite maturity.
    """
    if df is None:
        df = load()

    live = df[df["is_reachable"]]

    def summarise(group: pd.DataFrame, label: str) -> dict:
        up = group[group["is_reachable"]]
        return {
            "tier": label,
            "portals": len(group),
            "reachable": len(up),
            "reach_rate_pct": round(len(up) / len(group) * 100, 1) if len(group) else 0.0,
            "mean_accessibility": round(up["sub_accessibility_score"].mean(), 1),
            "mean_security": round(up["sub_security_headers_score"].mean(), 1),
            "gigw_toolbar_pct": round(up["sub_has_gigw_toolbar"].mean() * 100, 1),
            "multilingual_pct": round(up["sub_is_multilingual"].mean() * 100, 1),
            "mobile_pct": round(up["sub_mobile_responsive"].mean() * 100, 1),
            "median_ttfb_ms": round(up["sub_response_latency_ms"].median(), 0),
            "mean_maturity": round(up["observatory_maturity_score"].mean(), 1),
        }

    rows = [
        summarise(df[df["government_level"] == tier], TIER_LABELS[tier])
        for tier in TIERS
        if (df["government_level"] == tier).any()
    ]
    rows.append(summarise(df, "National"))

    return pd.DataFrame(rows).set_index("tier")


def architecture_summary(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Per-platform comparison — the paper's Table II.

    Unreachable hosts are excluded rather than counted as an unknown platform.
    """
    if df is None:
        df = load()

    live = df[df["is_reachable"]]
    total = len(live)

    rows = []
    for arch, group in live.groupby("sub_cms_architecture"):
        rows.append(
            {
                "architecture": arch,
                "portals": len(group),
                "share_pct": round(len(group) / total * 100, 1) if total else 0.0,
                "mean_accessibility": round(group["sub_accessibility_score"].mean(), 1),
                "gigw_toolbar_pct": round(group["sub_has_gigw_toolbar"].mean() * 100, 1),
                "mean_security": round(group["sub_security_headers_score"].mean(), 1),
                "median_ttfb_ms": round(group["sub_response_latency_ms"].median(), 0),
                "mobile_pct": round(group["sub_mobile_responsive"].mean() * 100, 1),
                "mean_maturity": round(group["observatory_maturity_score"].mean(), 1),
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values("portals", ascending=False)
        .set_index("architecture")
    )


def state_ranking(
    df: pd.DataFrame | None = None,
    top: int | None = None,
    include_national: bool = False,
) -> pd.DataFrame:
    """States and Union Territories ranked by mean composite maturity.

    Args:
        df: Optional pre-filtered frame.
        top: Return only the first ``top`` rows.
        include_national: Keep the ``National``, ``National / Central`` and
            ``Central Government`` buckets, which hold central bodies rather
            than a State or UT. Off by default, so the ranking is 36 rows.
    """
    if df is None:
        df = load()

    live = df[df["is_reachable"]]

    if not include_national:
        live = live[~live["state_or_ut"].isin(NATIONAL_BUCKETS)]

    grouped = live.groupby("state_or_ut")

    table = pd.DataFrame(
        {
            "portals": grouped.size(),
            "reachable": grouped["is_reachable"].sum(),
            "mean_maturity": grouped["observatory_maturity_score"].mean().round(2),
            "mean_accessibility": grouped["sub_accessibility_score"].mean().round(1),
            "mean_security": grouped["sub_security_headers_score"].mean().round(1),
            "median_ttfb_ms": grouped["sub_response_latency_ms"].median().round(0),
        }
    ).sort_values("mean_maturity", ascending=False)

    table.insert(0, "rank", range(1, len(table) + 1))
    table.index.name = "state_or_ut"

    return table.head(top) if top else table


def maturity_index(
    accessibility: float,
    security: float,
    lcp_sec: float,
    multilingual: bool,
    mobile: bool,
    citizen_services: bool,
    s3waas: bool,
) -> float:
    """Recompute the composite maturity index for a single portal.

    The weights are fixed, not fitted, and were recovered exactly from the
    released values (99.96% of rows reproduce to within 0.15; the remainder are
    clamped at the 45.0 floor)::

        M = 0.30 * accessibility
          + 0.25 * security
          + 0.20 * max(0, 100 - 15 * lcp_sec)
          + 10   * multilingual
          + 5    * mobile
          + 5    * citizen_services
          + 5    * s3waas

    The binary terms are worth 10 or 5 points, not 10% or 5% — the index is on a
    0-100 scale, so a portal with every binary term true and perfect scores on
    the three continuous terms reaches 100.

    Args:
        s3waas: Whether the portal runs on NIC's S3WaaS Drupal distribution.
            This is a platform bonus, not a GIGW-toolbar bonus; the toolbar is
            already reflected in the accessibility score.

    Useful for scoring a portal you have measured yourself with the same
    methodology.
    """
    speed = max(0.0, 100.0 - 15.0 * float(lcp_sec))
    score = (
        0.30 * float(accessibility)
        + 0.25 * float(security)
        + 0.20 * speed
        + 10.0 * (1.0 if multilingual else 0.0)
        + 5.0 * (1.0 if mobile else 0.0)
        + 5.0 * (1.0 if citizen_services else 0.0)
        + 5.0 * (1.0 if s3waas else 0.0)
    )
    return round(max(45.0, min(100.0, score)), 1)


def describe_release() -> dict:
    """Summary metadata about the bundled release."""
    df = load()
    live = df[df["is_reachable"]]
    return {
        "version": __version__,
        "portals": len(df),
        "reachable": len(live),
        "reach_rate_pct": round(len(live) / len(df) * 100, 1),
        "states_and_uts": int(df["state_or_ut"].nunique()),
        "tiers": int(df["government_level"].nunique()),
        "mean_accessibility": round(live["sub_accessibility_score"].mean(), 1),
        "mean_security": round(live["sub_security_headers_score"].mean(), 1),
        "mean_maturity": round(live["observatory_maturity_score"].mean(), 1),
        "median_ttfb_ms": round(live["sub_response_latency_ms"].median(), 0),
        "source": str(dataset_path()),
    }
