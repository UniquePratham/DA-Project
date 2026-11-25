"""CivicWeb Observatory — cross-country measurement of public-sector web.

The package bundles the released measurement table: 2,143 government domains
across 82 countries, each row carrying the vantage point that produced it.

Quick start::

    import civicweb_observatory as cwo

    df = cwo.load()                    # all 2,143 measured domains
    live = cwo.load(reachable=True)    # the 648 that answered

    cwo.country_summary()              # one row per country
    cwo.sector_summary()               # one row per sector
    cwo.vantage_comparison()           # domestic vs nearest

The vantage distinction is the point of the dataset. A cloud provider operates
in 20 countries, so a domestic probe is impossible in most of the world. Rather
than exclude those countries or pretend a foreign probe is domestic, every row
records ``domestic_probe``: true only when the probe's region country equals the
target country. Any claim about what a citizen experiences must filter on it.

Every function is a thin, documented wrapper over pandas so results are
reproducible with plain ``groupby`` calls.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd

__version__ = "2.0.0"
__all__ = [
    "__version__",
    "COLUMNS",
    "BOOLEAN_COLUMNS",
    "SECTORS",
    "dataset_path",
    "load",
    "country_summary",
    "sector_summary",
    "vantage_comparison",
    "architecture_summary",
    "classify_sector",
    "maturity_index",
    "describe_release",
]

#: The released columns, in release order.
COLUMNS: tuple[str, ...] = (
    "domain_name",
    "final_url",
    "status_code",
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
    "html_bytes",
    "sha256",
    "blocked_by_waf",
    "robots_disallowed",
    "probe_country",
    "probe_region",
    "probe_region_country",
    "domestic_probe",
    "measured_at",
    "job_id",
)

#: Columns written as ``True``/``False``. Read as nullable so an unmeasured
#: value is distinguishable from ``False``.
BOOLEAN_COLUMNS: tuple[str, ...] = (
    "is_reachable",
    "blocked_by_waf",
    "domestic_probe",
    "sub_has_gigw_toolbar",
    "sub_https_enforced",
    "sub_is_multilingual",
    "sub_mobile_responsive",
    "sub_has_citizen_services",
    "robots_disallowed",
)

#: Sector classification by hostname marker. A domain is assigned to the first
#: sector whose marker appears, so the order matters: health before education,
#: because ``health.edu`` is a health site.
SECTORS: dict[str, tuple[str, ...]] = {
    "health": (
        "health", "nhs", "hospital", "medic", "clinic", "doh", "moh",
        "sante", "santé", "salud", "sanidad", "salute", "gesundheit",
        "zdrowie", "zdrav", "saude", "saúde", "sanita", "gezondheid",
        "sundhed", "hälsa", "helse", "terveys", "egeszseg",
    ),
    "judiciary": (
        "court", "justice", "judic", "tribunal", "supreme", "leg.",
        "senat", "parliament", "congress", "assembly", "corte", "gerichte",
        "rechtspraak", "domstol", "sud", "soud",
    ),
    "finance": (
        "fin", "tax", "revenue", "treasur", "budget", "bank", "fisco",
        "hacienda", "impots", "finanz", "skatt", "podatki",
    ),
    "police": ("police", "policia", "polizei", "policie", "politi", "policja"),
    "defence": ("defen", "army", "navy", "airforce", "military", "mod.", "mil."),
    "transport": (
        "transport", "rail", "road", "highway", "traffic", "metro",
        "aviation", "airport", "port", "shipping", "verkehr",
    ),
    "environment": (
        "environment", "climate", "forest", "wildlife", "pollution",
        "ecology", "umwelt", "ambiente", "milieu",
    ),
    "agriculture": (
        "agric", "farming", "farmers", "crop", "livestock", "fisheries",
        "landwirtschaft", "rolnictwo",
    ),
    "social": (
        "social", "welfare", "pension", "benefit", "disability", "family",
        "children", "youth", "elderly", "sozial", "previdencia",
    ),
    "education": (
        "edu", "ac.", "univ", "school", "college", "institute", "research",
        "student", "campus", "library", "bildung", "onderwijs",
    ),
}

#: A sector mean is only reported when at least this many of its domains
#: answered. Below that the mean is one or two portals wearing a sector label.
MIN_SECTOR_LIVE = 10

_FLOAT_COLUMNS = (
    "sub_accessibility_score",
    "sub_response_latency_ms",
    "sub_lcp_est_sec",
    "sub_security_headers_score",
    "observatory_maturity_score",
)


def dataset_path() -> Path:
    """Absolute path to the bundled Parquet release."""
    return Path(
        str(resources.files(__name__).joinpath("data/civicweb_observatory_global.parquet"))
    )


def classify_sector(host: str) -> str:
    """Assign a domain to a sector by hostname marker, or ``general``."""
    h = str(host).lower()
    for sector, markers in SECTORS.items():
        if any(m in h for m in markers):
            return sector
    return "general"


def load(
    reachable: bool | None = None,
    countries: Sequence[str] | Iterable[str] | None = None,
    domestic_only: bool = False,
    sectors: Sequence[str] | Iterable[str] | None = None,
) -> pd.DataFrame:
    """Load the measurement table as a typed DataFrame.

    Args:
        reachable: ``True`` keeps only domains that answered, ``False`` keeps
            only the ones that did not, ``None`` keeps everything.
        countries: Optional ISO-3166 alpha-2 filter, e.g. ``["NL", "DE"]``.
        domestic_only: Keep only rows measured from a probe inside the target
            country. Use this for any claim about what a citizen experiences.
        sectors: Optional sector filter, e.g. ``["education"]``.

    Returns:
        A DataFrame with the released columns, booleans as nullable ``boolean``
        and scores as ``float``. Unmeasured metrics stay ``NaN``; they are never
        filled with zero.
    """
    df = pd.read_parquet(dataset_path())

    for column in BOOLEAN_COLUMNS:
        if column in df.columns:
            df[column] = df[column].astype("boolean")

    for column in _FLOAT_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    if reachable is not None:
        mask = df["is_reachable"].fillna(False).astype(bool)
        df = df[mask == bool(reachable)]

    if domestic_only:
        df = df[df["domestic_probe"].fillna(False).astype(bool)]

    if countries is not None:
        df = df[df["probe_country"].isin(list(countries))]

    if sectors is not None:
        wanted = set(sectors)
        df = df[df["domain_name"].map(classify_sector).isin(wanted)]

    return df.reset_index(drop=True)


def _block(group: pd.DataFrame) -> dict:
    """Counts and pillar means for one group of rows."""
    up = group[group["is_reachable"].fillna(False).astype(bool)]
    return {
        "domains": len(group),
        "reachable": len(up),
        "reach_pct": round(len(up) / len(group) * 100, 1) if len(group) else 0.0,
        "accessibility": round(float(up["sub_accessibility_score"].mean()), 1) if len(up) else None,
        "security": round(float(up["sub_security_headers_score"].mean()), 1) if len(up) else None,
        "maturity": round(float(up["observatory_maturity_score"].mean()), 1) if len(up) else None,
        "median_ttfb_ms": int(up["sub_response_latency_ms"].median()) if len(up) else None,
        "multilingual_pct": round(float(up["sub_is_multilingual"].mean() * 100), 1) if len(up) else None,
        "mobile_pct": round(float(up["sub_mobile_responsive"].mean() * 100), 1) if len(up) else None,
    }


def country_summary(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per measured country, ranked by mean accessibility.

    A country with no reachable domain keeps its row with ``None`` pillar means
    rather than zeros, so "not measured" is never read as "measured and bad".
    """
    if df is None:
        df = load()

    rows = []
    for code, group in df.groupby("probe_country"):
        row = {"country": code, **_block(group)}
        row["domestic_probe"] = bool(group["domestic_probe"].fillna(False).astype(bool).all())
        row["probe_region"] = group["probe_region"].iloc[0]
        rows.append(row)

    table = pd.DataFrame(rows)
    table = table.sort_values(
        ["accessibility", "domains"], ascending=[False, False], na_position="last"
    )
    table.insert(0, "rank", range(1, len(table) + 1))
    return table.set_index("country")


def sector_summary(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per sector, with sectors below ``MIN_SECTOR_LIVE`` excluded.

    Sector is inferred from the hostname, so it is reliable for dedicated
    domains (``health.``, ``court.``) and puts everything else in ``general``.
    """
    if df is None:
        df = load()

    df = df.copy()
    df["sector"] = df["domain_name"].map(classify_sector)

    rows = []
    for sector, group in df.groupby("sector"):
        block = _block(group)
        if block["reachable"] < MIN_SECTOR_LIVE:
            continue
        rows.append({"sector": sector, **block})

    return (
        pd.DataFrame(rows)
        .sort_values("domains", ascending=False)
        .set_index("sector")
    )


def vantage_comparison(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Domestic versus nearest probes — the paper's main result.

    The same kind of portal answers in 471 ms from inside its country and
    1,151 ms from the nearest foreign region. The gap is the cost of distance,
    not a difference in the portals.
    """
    if df is None:
        df = load()

    rows = []
    for label, is_domestic in (("domestic", True), ("nearest", False)):
        mask = df["domestic_probe"].fillna(False).astype(bool) == is_domestic
        group = df[mask]
        if not len(group):
            continue
        rows.append({"vantage": label, **_block(group)})

    return pd.DataFrame(rows).set_index("vantage")


def architecture_summary(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Per-platform comparison. Unreachable hosts are excluded."""
    if df is None:
        df = load()

    live = df[df["is_reachable"].fillna(False).astype(bool)]
    total = len(live)

    rows = []
    for arch, group in live.groupby("sub_cms_architecture"):
        rows.append(
            {
                "architecture": arch,
                "portals": len(group),
                "share_pct": round(len(group) / total * 100, 1) if total else 0.0,
                "mean_accessibility": round(float(group["sub_accessibility_score"].mean()), 1),
                "mean_security": round(float(group["sub_security_headers_score"].mean()), 1),
                "median_ttfb_ms": int(group["sub_response_latency_ms"].median()),
                "mean_maturity": round(float(group["observatory_maturity_score"].mean()), 1),
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values("portals", ascending=False)
        .set_index("architecture")
    )


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

    The weights are fixed, not fitted::

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

    The result is clamped to ``[0, 100]``. It is **not** floored: an earlier
    release applied a 45.0 floor, which silently inflated the worst portals and
    made the index non-reproducible from its own inputs. The floor has been
    removed so that ``maturity_index`` always returns exactly what the published
    formula produces.

    Args:
        s3waas: Whether the portal runs on NIC's S3WaaS Drupal distribution.
            This is a platform bonus, not a GIGW-toolbar bonus; the toolbar is
            already reflected in the accessibility score.
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
    return round(max(0.0, min(100.0, score)), 1)


def describe_release() -> dict:
    """Summary metadata about the bundled release."""
    df = load()
    live = df[df["is_reachable"].fillna(False).astype(bool)]
    dom = df[df["domestic_probe"].fillna(False).astype(bool)]
    dom_live = dom[dom["is_reachable"].fillna(False).astype(bool)]

    return {
        "version": __version__,
        "domains": len(df),
        "reachable": len(live),
        "reach_rate_pct": round(len(live) / len(df) * 100, 1),
        "countries": int(df["probe_country"].nunique()),
        "countries_reachable": int(live["probe_country"].nunique()),
        "domestic_domains": len(dom),
        "domestic_reachable": len(dom_live),
        "mean_accessibility": round(float(live["sub_accessibility_score"].mean()), 1),
        "mean_security": round(float(live["sub_security_headers_score"].mean()), 1),
        "mean_maturity": round(float(live["observatory_maturity_score"].mean()), 1),
        "median_ttfb_ms": int(live["sub_response_latency_ms"].median()),
        "source": str(dataset_path()),
    }
