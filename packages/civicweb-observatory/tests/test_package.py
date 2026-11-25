"""Tests for the civicweb-observatory package.

These assert the published figures, so a regression in the loader or the
aggregation layer fails loudly rather than silently changing a paper table.
"""

from __future__ import annotations

import pandas as pd
import pytest

import civicweb_observatory as cwo


def test_release_shape():
    df = cwo.load()
    assert len(df) == 2011
    assert list(df.columns) == list(cwo.COLUMNS)


def test_reachability_split():
    df = cwo.load()
    live = cwo.load(reachable=True)
    offline = cwo.load(reachable=False)

    assert len(live) == 573
    assert len(offline) == 1438
    assert len(live) + len(offline) == len(df)
    assert live["is_reachable"].all()
    assert not offline["is_reachable"].any()


def test_namibia_survives_the_reader():
    """``NA`` is Namibia's ISO code and pandas' default missing-value token.

    A default ``read_csv`` silently drops all ten Namibian rows, which is how
    the country vanished from the first build of these aggregates.
    """
    df = cwo.load()
    namibia = df[df["probe_country"] == "NA"]
    assert len(namibia) == 10
    assert df["probe_country"].notna().all()
    assert df["probe_country"].nunique() == 82


def test_dtypes_are_typed():
    df = cwo.load()
    assert str(df["is_reachable"].dtype) == "boolean"
    assert str(df["domestic_probe"].dtype) == "boolean"
    assert pd.api.types.is_float_dtype(df["sub_accessibility_score"])
    assert pd.api.types.is_float_dtype(df["observatory_maturity_score"])


def test_unmeasured_metrics_stay_null():
    """An unreachable host must not carry a zero score."""
    df = cwo.load(reachable=False)
    assert df["sub_accessibility_score"].isna().all()
    assert df["sub_security_headers_score"].isna().all()
    assert df["observatory_maturity_score"].isna().all()


def test_vantage_comparison_matches_paper():
    table = cwo.vantage_comparison()

    assert table.loc["domestic", "domains"] == 1360
    assert table.loc["domestic", "reachable"] == 398
    assert table.loc["domestic", "reach_pct"] == pytest.approx(29.3, abs=0.05)
    assert table.loc["domestic", "accessibility"] == pytest.approx(87.0, abs=0.05)
    assert table.loc["domestic", "security"] == pytest.approx(44.2, abs=0.05)
    assert table.loc["domestic", "median_ttfb_ms"] == 478

    assert table.loc["nearest", "domains"] == 651
    assert table.loc["nearest", "reachable"] == 175
    assert table.loc["nearest", "accessibility"] == pytest.approx(84.0, abs=0.05)
    assert table.loc["nearest", "security"] == pytest.approx(33.2, abs=0.05)
    assert table.loc["nearest", "median_ttfb_ms"] == 1156

    # The paper's headline: distance costs 680 ms.
    assert table.loc["nearest", "median_ttfb_ms"] - table.loc["domestic", "median_ttfb_ms"] == 678


def test_domestic_only_filter_is_exact():
    df = cwo.load(domestic_only=True)
    assert len(df) == 1360
    assert df["domestic_probe"].all()

    # A domestic row's probe region must be inside the target country.
    assert (df["probe_region_country"] == df["probe_country"]).all()


def test_nearest_rows_are_never_domestic():
    df = cwo.load()
    near = df[~df["domestic_probe"].fillna(False).astype(bool)]
    assert len(near) == 651
    assert (near["probe_region_country"] != near["probe_country"]).all()


def test_sector_summary_matches_paper_table():
    table = cwo.sector_summary()

    assert table.loc["education", "domains"] == 420
    assert table.loc["education", "reachable"] == 129
    assert table.loc["education", "security"] == pytest.approx(26.6, abs=0.05)

    assert table.loc["general", "domains"] == 1354
    assert table.loc["general", "security"] == pytest.approx(44.9, abs=0.05)

    assert table.loc["health", "accessibility"] == pytest.approx(88.1, abs=0.05)
    assert table.loc["judiciary", "accessibility"] == pytest.approx(81.8, abs=0.05)

    # A sector with fewer than ten reachable domains must not appear.
    assert "finance" not in table.index
    assert "police" not in table.index
    assert (table["reachable"] >= cwo.MIN_SECTOR_LIVE).all()


def test_country_summary_is_complete_and_sorted():
    table = cwo.country_summary()
    assert len(table) == 82
    assert list(table["rank"]) == list(range(1, len(table) + 1))

    scored = table["accessibility"].dropna()
    assert scored.is_monotonic_decreasing

    # A country with no reachable domain keeps its row with null means.
    unscored = table[table["accessibility"].isna()]
    assert (unscored["reachable"] == 0).all()


def test_architecture_summary_matches_paper_table():
    table = cwo.architecture_summary()

    assert table.loc["custom_dynamic_cms", "portals"] == 318
    assert table.loc["custom_dynamic_cms", "share_pct"] == pytest.approx(55.5, abs=0.05)
    assert table.loc["wordpress", "portals"] == 93
    assert table.loc["modern_spa", "mean_security"] == pytest.approx(69.9, abs=0.05)
    assert table.loc["s3waas_drupal", "portals"] == 12

    # Unreachable hosts must not appear as a platform.
    assert table["portals"].sum() == 573


def test_filters_compose():
    df = cwo.load(reachable=True, countries=["NL"], domestic_only=True)
    assert len(df) > 0
    assert (df["probe_country"] == "NL").all()
    assert df["is_reachable"].all()
    assert df["domestic_probe"].all()


def test_maturity_index_reproduces_release_values():
    df = cwo.load(reachable=True)

    import numpy as np

    recomputed = [
        cwo.maturity_index(
            accessibility=row.sub_accessibility_score,
            security=row.sub_security_headers_score,
            lcp_sec=row.sub_lcp_est_sec,
            multilingual=bool(row.sub_is_multilingual),
            mobile=bool(row.sub_mobile_responsive),
            citizen_services=bool(row.sub_has_citizen_services),
            s3waas=row.sub_cms_architecture == "s3waas_drupal",
        )
        for row in df.itertuples()
    ]

    err = np.abs(np.array(recomputed) - df["observatory_maturity_score"].values)
    assert (err <= 0.15).mean() > 0.999


def test_describe_release():
    info = cwo.describe_release()
    assert info["domains"] == 2011
    assert info["reachable"] == 573
    assert info["countries"] == 82
    assert info["countries_reachable"] == 72
    assert info["domestic_domains"] == 1360
    assert info["reach_rate_pct"] == pytest.approx(28.5, abs=0.05)


def test_cli_info(capsys):
    from civicweb_observatory.cli import main

    assert main(["info"]) == 0
    out = capsys.readouterr().out
    assert "2,011" in out or "2011" in out


def test_cli_vantage(capsys):
    from civicweb_observatory.cli import main

    assert main(["vantage"]) == 0
    out = capsys.readouterr().out
    assert "domestic" in out and "nearest" in out


def test_cli_query(capsys):
    from civicweb_observatory.cli import main

    assert main(["query", "--country", "NL", "--limit", "5"]) == 0
    out = capsys.readouterr().out
    assert "matching domains" in out


def test_cli_export(tmp_path):
    from civicweb_observatory.cli import main

    target = tmp_path / "measurements.csv"
    assert main(["export", "--format", "csv", "--out", str(target), "--reachable-only"]) == 0
    assert target.exists()
    assert len(pd.read_csv(target)) == 573
