"""Tests for the bharatgov-access package.

These assert the published figures, so a regression in the loader or the
aggregation layer fails loudly rather than silently changing a paper table.
"""

from __future__ import annotations

import pandas as pd
import pytest

import bharatgov_access as bga


def test_release_shape():
    df = bga.load()
    assert len(df) == 12092
    assert list(df.columns) == list(bga.COLUMNS)


def test_reachability_split():
    df = bga.load()
    live = bga.load(reachable=True)
    offline = bga.load(reachable=False)

    assert len(live) == 10247
    assert len(offline) == 1845
    assert len(live) + len(offline) == len(df)
    assert live["is_reachable"].all()
    assert not offline["is_reachable"].any()


def test_dtypes_are_typed():
    df = bga.load()
    assert df["is_reachable"].dtype == bool
    assert df["sub_has_gigw_toolbar"].dtype == bool
    assert pd.api.types.is_float_dtype(df["sub_accessibility_score"])
    assert pd.api.types.is_float_dtype(df["observatory_maturity_score"])


def test_local_body_is_normalised():
    df = bga.load()
    assert "local_body" not in set(df["government_level"])
    assert set(df["government_level"]) == set(bga.TIERS)


def test_tier_summary_matches_paper_table_one():
    table = bga.tier_summary()

    assert table.loc["National", "portals"] == 12092
    assert table.loc["National", "reachable"] == 10247
    assert table.loc["National", "reach_rate_pct"] == pytest.approx(84.7, abs=0.05)
    assert table.loc["National", "mean_accessibility"] == pytest.approx(93.8, abs=0.05)
    assert table.loc["National", "mean_security"] == pytest.approx(68.0, abs=0.05)
    assert table.loc["National", "gigw_toolbar_pct"] == pytest.approx(91.0, abs=0.05)
    assert table.loc["National", "multilingual_pct"] == pytest.approx(86.0, abs=0.05)
    assert table.loc["National", "mean_maturity"] == pytest.approx(78.8, abs=0.05)

    assert table.loc["District administrations", "portals"] == 7468
    assert table.loc["District administrations", "mean_accessibility"] == pytest.approx(95.0, abs=0.05)
    assert table.loc["Central ministries", "portals"] == 645
    assert table.loc["Urban local bodies", "portals"] == 140


def test_architecture_summary_matches_paper_table_two():
    table = bga.architecture_summary()

    assert table.loc["s3waas_drupal", "portals"] == 6480
    assert table.loc["s3waas_drupal", "share_pct"] == pytest.approx(63.2, abs=0.05)
    assert table.loc["s3waas_drupal", "mean_accessibility"] == pytest.approx(95.2, abs=0.05)
    assert table.loc["s3waas_drupal", "gigw_toolbar_pct"] == pytest.approx(100.0, abs=0.05)

    assert table.loc["legacy_asp_net", "portals"] == 399
    assert table.loc["legacy_asp_net", "mean_accessibility"] == pytest.approx(84.3, abs=0.05)

    assert table.loc["modern_spa", "portals"] == 651
    assert table.loc["modern_spa", "mean_security"] == pytest.approx(85.1, abs=0.05)

    # Unreachable hosts must not appear as a platform.
    assert "indeterminate_unreachable" not in table.index


def test_state_ranking_is_sorted_and_complete():
    table = bga.state_ranking()
    assert len(table) == 36
    assert list(table["rank"]) == list(range(1, 37))
    assert table["mean_maturity"].is_monotonic_decreasing
    assert table.index[0] == "Meghalaya"


def test_filters_compose():
    df = bga.load(reachable=True, tiers=["district"], states=["Kerala"])
    assert len(df) > 0
    assert (df["government_level"] == "district").all()
    assert (df["state_or_ut"] == "Kerala").all()
    assert df["is_reachable"].all()


def test_maturity_index_reproduces_release_values():
    df = bga.load(reachable=True)

    sample = df.sample(200, random_state=7)
    for _, row in sample.iterrows():
        recomputed = bga.maturity_index(
            accessibility=row["sub_accessibility_score"],
            security=row["sub_security_headers_score"],
            lcp_sec=row["sub_lcp_est_sec"],
            multilingual=row["sub_is_multilingual"],
            mobile=row["sub_mobile_responsive"],
            citizen_services=row["sub_has_citizen_services"],
            s3waas=row["sub_cms_architecture"] == "s3waas_drupal",
        )
        # The release clamps at a 45.0 floor, so a handful of very low scores
        # legitimately differ; everything else must match to rounding.
        if row["observatory_maturity_score"] > 45.0:
            assert recomputed == pytest.approx(row["observatory_maturity_score"], abs=0.15)


def test_maturity_index_is_exact_for_almost_every_row():
    df = bga.load(reachable=True)

    recomputed = [
        bga.maturity_index(
            accessibility=row.sub_accessibility_score,
            security=row.sub_security_headers_score,
            lcp_sec=row.sub_lcp_est_sec,
            multilingual=row.sub_is_multilingual,
            mobile=row.sub_mobile_responsive,
            citizen_services=row.sub_has_citizen_services,
            s3waas=row.sub_cms_architecture == "s3waas_drupal",
        )
        for row in df.itertuples()
    ]

    import numpy as np

    err = np.abs(np.array(recomputed) - df["observatory_maturity_score"].values)
    assert (err <= 0.15).mean() > 0.999


def test_describe_release():
    info = bga.describe_release()
    assert info["portals"] == 12092
    assert info["reachable"] == 10247
    assert info["tiers"] == 7
    # 36 States and UTs plus the national buckets used for central bodies.
    assert info["states_and_uts"] >= 36


def test_cli_info(capsys):
    from bharatgov_access.cli import main

    assert main(["info"]) == 0
    out = capsys.readouterr().out
    assert "12,092" in out or "12092" in out


def test_cli_query(capsys):
    from bharatgov_access.cli import main

    assert main(["query", "--tier", "district", "--state", "Kerala", "--limit", "5"]) == 0
    out = capsys.readouterr().out
    assert "matching domains" in out


def test_cli_export(tmp_path):
    from bharatgov_access.cli import main

    target = tmp_path / "census.csv"
    assert main(["export", "--format", "csv", "--out", str(target), "--reachable-only"]) == 0
    assert target.exists()
    assert len(pd.read_csv(target)) == 10247
