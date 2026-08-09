"""Provenance tracker ensuring 100% of AI-derived claims are grounded."""

from __future__ import annotations

from typing import List
from schemas.observation import ProvenanceRecord


class ProvenanceTracker:
    """Generates immutable provenance links between derived classifications and raw evidence."""

    @staticmethod
    def create_provenance(
        field_name: str,
        derived_value: str,
        evidence_ids: List[str],
        confidence: float = 1.0,
        model: str = "qwen3:4b",
        method: str = "deterministic_rule",
    ) -> ProvenanceRecord:
        if not evidence_ids:
            raise ValueError(f"Cannot create provenance for '{field_name}' without evidence IDs")

        return ProvenanceRecord(
            field_name=field_name,
            derived_value=derived_value,
            evidence_ids=evidence_ids,
            confidence=max(0.0, min(1.0, confidence)),
            model=model,
            method=method,
        )
