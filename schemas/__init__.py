"""Schemas package for BharatGov Access Observatory."""

from schemas.evidence import RawEvidenceRecord, EvidenceType
from schemas.domain import GovernmentEntityRecord, DomainStatus, GovernmentLevel
from schemas.observation import (
    ObservationRecord,
    AccessibilityMeasurements,
    PerformanceMeasurements,
    MobileReadinessMeasurements,
    ReliabilityMeasurements,
    LanguageMeasurements,
    WebStructureMeasurements,
    SecurityHygieneMeasurements,
    DerivedClassifications,
    ProvenanceRecord,
    PageRole,
    ArchitectureType,
)

__all__ = [
    "RawEvidenceRecord",
    "EvidenceType",
    "GovernmentEntityRecord",
    "DomainStatus",
    "GovernmentLevel",
    "ObservationRecord",
    "AccessibilityMeasurements",
    "PerformanceMeasurements",
    "MobileReadinessMeasurements",
    "ReliabilityMeasurements",
    "LanguageMeasurements",
    "WebStructureMeasurements",
    "SecurityHygieneMeasurements",
    "DerivedClassifications",
    "ProvenanceRecord",
    "PageRole",
    "ArchitectureType",
]
