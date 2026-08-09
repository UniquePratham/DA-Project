"""Coverage Audit and Registry Statistics Calculator (Section 8)."""

from __future__ import annotations

from typing import List, Dict, Any
from schemas.domain import GovernmentEntityRecord, DomainStatus
from schemas.observation import ObservationRecord


class CoverageAuditor:
    """Generates Section 8 verified coverage reports."""

    @staticmethod
    def calculate_coverage(
        registry_records: List[GovernmentEntityRecord],
        observations: List[ObservationRecord],
    ) -> Dict[str, Any]:
        total_candidates = len(registry_records)
        status_counts: Dict[str, int] = {}

        for r in registry_records:
            st = r.status.value
            status_counts[st] = status_counts.get(st, 0) + 1

        observed_domain_ids = set(o.domain_id for o in observations)
        successfully_observed = len(observed_domain_ids)

        return {
            "total_candidates": total_candidates,
            "verified_government_domains": status_counts.get(DomainStatus.VERIFIED.value, 0) + status_counts.get(DomainStatus.ACTIVE.value, 0),
            "successfully_observed": successfully_observed,
            "active": status_counts.get(DomainStatus.ACTIVE.value, 0),
            "temporarily_unavailable": status_counts.get(DomainStatus.TEMPORARILY_UNAVAILABLE.value, 0),
            "robots_restricted": status_counts.get(DomainStatus.ROBOTS_RESTRICTED.value, 0),
            "blocked_or_tls_error": status_counts.get(DomainStatus.BLOCKED.value, 0) + status_counts.get(DomainStatus.TLS_ERROR.value, 0),
            "unresolved": status_counts.get(DomainStatus.UNRESOLVED.value, 0),
            "coverage_percentage": round((successfully_observed / total_candidates * 100.0), 2) if total_candidates > 0 else 0.0,
        }
