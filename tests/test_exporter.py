"""Unit tests for the DataHub KGP Dataset Exporter."""

import json
from pathlib import Path
import pytest
import pandas as pd

from schemas.observation import (
    ObservationRecord,
    ReliabilityMeasurements,
    AccessibilityMeasurements,
    PerformanceMeasurements,
    PageRole,
)
from schemas.domain import GovernmentEntityRecord, GovernmentLevel, DomainStatus
from services.analytics.exporter import DatasetExporter
from services.analytics.coverage import CoverageAuditor


def test_coverage_auditor():
    registry = [
        GovernmentEntityRecord(domain_name="site1.gov.in", base_url="https://site1.gov.in", entity_name="Site 1", status=DomainStatus.ACTIVE),
        GovernmentEntityRecord(domain_name="site2.gov.in", base_url="https://site2.gov.in", entity_name="Site 2", status=DomainStatus.TEMPORARILY_UNAVAILABLE),
        GovernmentEntityRecord(domain_name="site3.gov.in", base_url="https://site3.gov.in", entity_name="Site 3", status=DomainStatus.ROBOTS_RESTRICTED),
    ]

    obs = [
        ObservationRecord(
            crawl_id="crawl-1",
            domain_id=registry[0].domain_id,
            source_url="https://site1.gov.in",
            canonical_url="https://site1.gov.in/",
            reliability=ReliabilityMeasurements(http_status_code=200, response_latency_ms=100.0, is_reachable=True),
        )
    ]

    report = CoverageAuditor.calculate_coverage(registry, obs)
    assert report["total_candidates"] == 3
    assert report["successfully_observed"] == 1
    assert report["temporarily_unavailable"] == 1
    assert report["robots_restricted"] == 1
    assert report["coverage_percentage"] == 33.33


def test_dataset_exporter(tmp_path):
    exporter = DatasetExporter(releases_dir=tmp_path)

    registry = [
        GovernmentEntityRecord(domain_name="india.gov.in", base_url="https://india.gov.in", entity_name="India Portal", status=DomainStatus.ACTIVE)
    ]

    obs = [
        ObservationRecord(
            crawl_id="crawl-exp-1",
            domain_id=registry[0].domain_id,
            source_url="https://india.gov.in",
            canonical_url="https://india.gov.in/",
            page_role=PageRole.HOMEPAGE,
            reliability=ReliabilityMeasurements(http_status_code=200, response_latency_ms=120.0, is_reachable=True),
            accessibility=AccessibilityMeasurements(accessibility_score=95.0),
            performance=PerformanceMeasurements(lcp_ms=1100.0, cls=0.01),
        )
    ]

    out = exporter.export_release("v0.1.0", obs, registry)
    assert out["parquet"].exists()
    assert out["csv"].exists()
    assert out["jsonl"].exists()
    assert out["coverage"].exists()
    assert out["benchmarks"].exists()
    assert out["manifest"].exists()

    # Read back parquet and verify website-level row
    df = pd.read_parquet(out["parquet"])
    assert len(df) == 1
    assert df["domain_name"].iloc[0] == "india.gov.in"
    assert df["subdomain"].iloc[0] == "root"
    assert df["root_domain"].iloc[0] == "india.gov.in"
    assert df["tld_type"].iloc[0] == ".gov.in"
    assert df["domain_depth"].iloc[0] == 0
    assert df["overall_accessibility_score"].iloc[0] == 95.0
    assert df["reachability_status"].iloc[0] == "REACHABLE_200"
    assert "feature_richness_score" in df.columns
    assert df["total_pages_audited"].iloc[0] == 1
    assert df["homepage_url"].iloc[0] == "https://india.gov.in/"
