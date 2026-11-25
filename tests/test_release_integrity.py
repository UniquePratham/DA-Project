"""Guards on the released dataset and the artefacts built from it.

These tests exist because two real defects shipped silently:

* Namibia's ISO code is ``NA``, which pandas treats as a missing value by
  default, so ten rows and one whole country vanished from every aggregate.
* The deck and the paper were built from different sector classifiers, so the
  same sector had two different security scores.

Each test here fails if either defect returns.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from global_dataset import GLOBAL_CSV, read_global, reachable  # noqa: E402

import civicweb_observatory as cwo  # noqa: E402


def test_released_csv_exists():
    assert GLOBAL_CSV.exists(), f"missing released dataset at {GLOBAL_CSV}"


def test_default_reader_loses_namibia_and_ours_does_not():
    """The bug this module exists to prevent, demonstrated both ways."""
    naive = pd.read_csv(GLOBAL_CSV)
    assert naive["probe_country"].isna().sum() == 10, (
        "the default reader no longer drops Namibia; the guard below may be stale"
    )

    safe = read_global()
    assert safe["probe_country"].isna().sum() == 0
    assert (safe["probe_country"] == "NA").sum() == 10


def test_every_row_has_a_country():
    df = read_global()
    assert df["probe_country"].notna().all()
    assert df["probe_country"].nunique() == 82


def test_domestic_flag_is_structurally_true():
    """A row may only claim domestic when the probe region is in the country."""
    df = read_global()
    dom = df[df["domestic_probe"].fillna(False).astype(bool)]
    assert len(dom) > 0
    assert (dom["probe_region_country"] == dom["probe_country"]).all()


def test_unreachable_rows_carry_no_scores():
    """A host that did not serve an auditable page must not carry a content score.

    Latency is different: a host that answered ``HTTP 404`` or a WAF challenge
    has a real round-trip time even though there is no page to score. Those rows
    keep their latency and leave every content metric null.

    A host that returned ``HTTP 200`` with a body under 200 bytes is a third
    case: it answered, so it keeps its status, latency, byte count and hash, but
    there is no DOM to audit, so every content score is null. Scoring it would
    give an empty page 90.0 on accessibility, above the population mean.
    """
    df = read_global()
    down = df[~df["is_reachable"].fillna(False).astype(bool)]
    assert len(down) > 0

    for column in (
        "sub_accessibility_score",
        "sub_security_headers_score",
        "observatory_maturity_score",
        "sub_lcp_est_sec",
    ):
        assert down[column].isna().all(), f"{column} was filled for an unreachable host"

    # A latency is only present when the host actually answered.
    with_latency = down[down["sub_response_latency_ms"].notna()]
    assert len(with_latency) > 0
    assert with_latency["status_code"].notna().all()
    assert (with_latency["measurement_reason"] != "DNS or connection failure").all()

    # An empty body is recorded as such, not scored.
    empty = down[down["measurement_reason"] == "HTTP 200 with an empty body"]
    assert len(empty) > 0
    assert (empty["html_bytes"] < 200).all()
    assert empty["sha256"].notna().all()


def test_package_and_csv_agree():
    """The bundled Parquet must be the same release as the CSV."""
    csv = read_global()
    pkg = cwo.load()

    assert len(csv) == len(pkg)
    assert set(csv["domain_name"]) == set(pkg["domain_name"])
    assert csv["probe_country"].nunique() == pkg["probe_country"].nunique()


def test_package_vantage_matches_csv():
    csv = read_global()
    live = reachable(csv)
    dom = csv[csv["domestic_probe"].fillna(False).astype(bool)]
    dom_live = reachable(dom)

    table = cwo.vantage_comparison()
    assert table.loc["domestic", "domains"] == len(dom)
    assert table.loc["domestic", "reachable"] == len(dom_live)
    assert table.loc["domestic", "median_ttfb_ms"] == int(
        dom_live["sub_response_latency_ms"].median()
    )
    assert table.loc["nearest", "domains"] == len(csv) - len(dom)
    assert live["probe_country"].nunique() == cwo.describe_release()["countries_reachable"]


def test_sector_classifier_is_shared():
    """The deck and the package must not disagree about a sector."""
    from build_deck import classify as deck_classify

    for host in (
        "health.gov.example",
        "courts.gov.example",
        "education.gov.example",
        "gov.example",
        "police.gov.example",
    ):
        assert deck_classify(host) == cwo.classify_sector(host)


def test_deck_figures_match_the_dataset():
    """Every headline on the deck is computed, so it must equal the dataset."""
    from build_deck import figures

    f = figures()
    df = read_global()
    live = reachable(df)

    assert f["total"] == len(df)
    assert f["live"] == len(live)
    assert f["countries"] == df["probe_country"].nunique()
    assert f["reach"] == pytest.approx(len(live) / len(df) * 100, abs=0.05)
    assert f["acc"] == pytest.approx(live["sub_accessibility_score"].mean(), abs=0.05)
    assert f["sec"] == pytest.approx(live["sub_security_headers_score"].mean(), abs=0.05)


def test_deck_has_no_stale_india_figures():
    """The deck was rebuilt for the global release; old figures must not return."""
    from build_deck import build, figures

    html = build(figures())
    for stale in ("14,489", "12,092", "10,247", "7,542", "BharatGov", "36 States"):
        assert stale not in html, f"stale figure {stale!r} is back in the deck"


def test_dashboard_bundle_counts_rows_not_percentages():
    """A count must be counted, never derived by rounding a percentage.

    The dashboard once reported 647 reachable domains because it computed
    ``round(30.2 / 100 * 2143)`` instead of counting the rows. The deck said 648
    and the two artefacts disagreed on the same page.
    """
    import json

    bundle = json.loads((REPO / "dashboard" / "static" / "global.json").read_text(encoding="utf-8"))
    df = read_global()
    live = reachable(df)

    assert bundle["total_rows"] == len(df)
    assert bundle["reachable_rows"] == len(live)
    assert bundle["reachable_rows"] == 573
    assert bundle["overall_reach_pct"] == pytest.approx(len(live) / len(df) * 100, abs=0.05)

    # The bundle must carry an explicit count, and the dashboard must read it
    # rather than re-deriving it from the percentage.
    assert "reachable_rows" in bundle
    app_js = (REPO / "dashboard" / "static" / "app.js").read_text(encoding="utf-8")
    assert "g.reachable_rows" in app_js, "the dashboard stopped reading the counted field"
    assert "overall_reach_pct / 100" not in app_js, (
        "the dashboard is deriving a count from a percentage again"
    )


def test_world_bundle_agrees_with_the_dataset():
    """Every measured country must be marked measured in the world bundle."""
    import json

    world = json.loads((REPO / "dashboard" / "static" / "world.json").read_text(encoding="utf-8"))
    df = read_global()
    measured = set(df["probe_country"].dropna().unique())

    flagged = {c["code"] for c in world["countries"] if c["measured"]}
    assert flagged == measured
    assert len(flagged) == 82

    # A country with rows must carry its counts, not zeros.
    for c in world["countries"]:
        if c["code"] in measured:
            assert c["domains"] > 0, f"{c['code']} is measured but reports 0 domains"


def test_world_map_covers_every_measured_country():
    """A measured country must be clickable: a polygon or a centroid marker."""
    import json

    raw = (REPO / "dashboard" / "static" / "world_map.js").read_text(encoding="utf-8")
    payload = json.loads(raw[raw.index("=") + 1:].rstrip().rstrip(";"))

    drawn = {c["code"] for c in payload["countries"]}
    marked = {m["code"] for m in payload.get("markers", [])}

    df = read_global()
    measured = set(df["probe_country"].dropna().unique())
    missing = measured - drawn - marked
    assert not missing, f"measured countries with no geometry and no marker: {sorted(missing)}"


def test_canonical_release_has_one_row_per_host():
    """The raw log is append-only; the release must be deduplicated.

    128 hosts were measured in more than one job, giving 2,143 rows for 2,011
    domains. Aggregating the raw log double-counts them in every mean.
    """
    from global_dataset import RAW_CSV

    raw = read_global(RAW_CSV)
    canonical = read_global()

    assert len(raw) > len(canonical), "the raw log is no longer larger than the release"
    assert raw["domain_name"].duplicated().any(), "the raw log no longer has duplicates"
    assert not canonical["domain_name"].duplicated().any(), "the release has duplicate hosts"
    assert len(canonical) == canonical["domain_name"].nunique()


def test_canonical_release_refuses_to_score_an_empty_body():
    """An empty document is unmeasurable, not accessible.

    The crawler's coverage terms scored a zero-byte body at 90.0 because there
    were no images and no form fields to fail. That is above the population
    mean, so an empty page outranked a real one.
    """
    df = read_global()
    live = reachable(df)

    assert (live["html_bytes"] >= 200).all(), "a body under 200 bytes is still scored"
    assert live["sub_accessibility_score"].notna().all()

    empty = df[df["measurement_reason"] == "HTTP 200 with an empty body"]
    assert len(empty) > 0
    assert empty["sub_accessibility_score"].isna().all()
    assert empty["observatory_maturity_score"].isna().all()


def test_dataset_audit_passes():
    """Run the full consistency audit as a test."""
    import subprocess

    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "audit_dataset.py")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(REPO),
    )
    assert result.returncode == 0, f"audit failed:\n{result.stdout[-3000:]}"
