"""Data Quality & Integrity Validation Engine for BharatGov Access."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any

from schemas.observation import ObservationRecord
from schemas.evidence import RawEvidenceRecord


class ValidationError(Exception):
    """Raised when an observation fails strict quality validation."""
    pass


class ValidationResult:
    def __init__(self, is_valid: bool, issues: List[str]):
        self.is_valid = is_valid
        self.issues = issues

    def __repr__(self) -> str:
        return f"<ValidationResult valid={self.is_valid} issues={len(self.issues)}>"


class DataQualityValidator:
    """Multi-layer validation engine enforcing Section 37 quality rules."""

    @staticmethod
    def validate_observation(
        observation: ObservationRecord,
        available_evidence: List[RawEvidenceRecord] | None = None,
    ) -> ValidationResult:
        issues: List[str] = []

        # 1. Range Validation
        rel = observation.reliability
        if not (100 <= rel.http_status_code <= 599):
            issues.append(f"Invalid HTTP status code: {rel.http_status_code}")

        if rel.response_latency_ms < 0:
            issues.append(f"Negative latency: {rel.response_latency_ms}")

        perf = observation.performance
        if perf.cls is not None and perf.cls < 0:
            issues.append(f"Invalid negative CLS: {perf.cls}")

        if perf.lighthouse_performance_score is not None:
            if not (0.0 <= perf.lighthouse_performance_score <= 100.0):
                issues.append(f"Lighthouse score out of range: {perf.lighthouse_performance_score}")

        acc = observation.accessibility
        if acc.accessibility_score is not None:
            if not (0.0 <= acc.accessibility_score <= 100.0):
                issues.append(f"Accessibility score out of range: {acc.accessibility_score}")

        if acc.axe_violations_count < (acc.critical_violations + acc.serious_violations + acc.moderate_violations + acc.minor_violations):
            issues.append("Total axe violations is less than sum of severity breakdown")

        # 2. Cross-Field Consistency Validation
        if not observation.browser_rendered:
            if perf.lcp_ms is not None or perf.cls is not None:
                issues.append("Browser-only metrics (LCP/CLS) present on non-browser rendered observation")
            if acc.axe_violations_count > 0 and acc.raw_evidence_id is None:
                issues.append("Axe violations reported on non-browser observation without evidence reference")

        if not rel.is_reachable and rel.http_status_code < 400:
            issues.append("Observation marked unreachable but status code is successful (<400)")

        # 3. Provenance Grounding Validation (Section 36 & 39)
        known_evidence_ids = set(observation.raw_evidence_ids)
        if available_evidence:
            known_evidence_ids.update(e.evidence_id for e in available_evidence)

        for prov in observation.classifications.provenances:
            if not prov.evidence_ids:
                issues.append(f"Provenance for field '{prov.field_name}' contains empty evidence list")
            for eid in prov.evidence_ids:
                if eid not in known_evidence_ids:
                    issues.append(f"Provenance evidence ID '{eid}' not found in observation raw_evidence_ids")

        # 4. Temporal Validation
        now = datetime.now(timezone.utc)
        if observation.observed_at > now:
            issues.append("Observation timestamp is in the future")

        is_valid = len(issues) == 0
        observation.is_validated = is_valid
        observation.validation_notes = issues

        return ValidationResult(is_valid=is_valid, issues=issues)
