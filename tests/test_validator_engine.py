"""Unit tests for the Data Quality Validation Engine."""

from datetime import datetime, timezone, timedelta
import pytest
from pydantic import ValidationError

from schemas.observation import (
    ObservationRecord,
    ReliabilityMeasurements,
    PerformanceMeasurements,
    AccessibilityMeasurements,
    DerivedClassifications,
    ProvenanceRecord,
    PageRole,
    ArchitectureType,
)
from schemas.evidence import RawEvidenceRecord, EvidenceType
from services.validator.engine import DataQualityValidator


def test_valid_observation():
    evidence = RawEvidenceRecord(
        crawl_id="crawl-001",
        domain_id="dom-001",
        source_url="https://india.gov.in",
        evidence_type=EvidenceType.HTML,
        file_path="data/raw/html/test.html",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        byte_size=1024,
        content_type="text/html",
    )

    obs = ObservationRecord(
        crawl_id="crawl-001",
        domain_id="dom-001",
        source_url="https://india.gov.in",
        canonical_url="https://india.gov.in/",
        page_role=PageRole.HOMEPAGE,
        browser_rendered=True,
        raw_evidence_ids=[evidence.evidence_id],
        reliability=ReliabilityMeasurements(
            http_status_code=200,
            response_latency_ms=150.5,
            is_reachable=True,
            tls_valid=True,
        ),
        performance=PerformanceMeasurements(
            lcp_ms=1200.0,
            cls=0.05,
            lighthouse_performance_score=85.0,
        ),
        accessibility=AccessibilityMeasurements(
            axe_violations_count=5,
            critical_violations=1,
            serious_violations=2,
            moderate_violations=2,
            minor_violations=0,
            accessibility_score=92.0,
        ),
        classifications=DerivedClassifications(
            website_category="national_portal",
            architecture_type=ArchitectureType.STATIC_HTML,
            provenances=[
                ProvenanceRecord(
                    field_name="website_category",
                    derived_value="national_portal",
                    confidence=0.95,
                    evidence_ids=[evidence.evidence_id],
                )
            ],
        ),
    )

    result = DataQualityValidator.validate_observation(obs, [evidence])
    assert result.is_valid is True
    assert len(result.issues) == 0
    assert obs.is_validated is True


def test_schema_range_validation_rejection():
    # Verify Pydantic rejects out of range numbers
    with pytest.raises(ValidationError):
        ReliabilityMeasurements(
            http_status_code=999,
            response_latency_ms=-10.0,
            is_reachable=False,
        )


def test_cross_field_and_provenance_validation():
    # Valid schema fields, but cross-field / provenance inconsistencies
    obs = ObservationRecord(
        crawl_id="crawl-001",
        domain_id="dom-001",
        source_url="https://india.gov.in",
        canonical_url="https://india.gov.in/",
        page_role=PageRole.HOMEPAGE,
        browser_rendered=False,  # NOT rendered in browser
        raw_evidence_ids=[],
        reliability=ReliabilityMeasurements(
            http_status_code=200,
            response_latency_ms=100.0,
            is_reachable=False,  # Inconsistency: reachable=False but status=200
        ),
        performance=PerformanceMeasurements(
            lcp_ms=1000.0,  # Inconsistency: LCP on non-browser observation
        ),
        accessibility=AccessibilityMeasurements(
            axe_violations_count=2,
            critical_violations=3,  # Inconsistency: breakdown > total
        ),
        classifications=DerivedClassifications(
            provenances=[
                ProvenanceRecord(
                    field_name="category",
                    derived_value="portal",
                    confidence=0.9,
                    evidence_ids=["missing-ev-id"],  # Inconsistency: unlinked evidence
                )
            ]
        ),
    )

    result = DataQualityValidator.validate_observation(obs)
    assert result.is_valid is False
    assert any("marked unreachable but status code is successful" in issue for issue in result.issues)
    assert any("Browser-only metrics" in issue for issue in result.issues)
    assert any("Total axe violations is less than sum" in issue for issue in result.issues)
    assert any("Provenance evidence ID 'missing-ev-id' not found" in issue for issue in result.issues)
