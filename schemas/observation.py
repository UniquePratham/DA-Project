"""Observation models for Level 2 deterministic measurements and Level 3 derived classifications."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any
import uuid

from pydantic import BaseModel, Field, field_validator


class PageRole(str, Enum):
    HOMEPAGE = "homepage"
    ABOUT = "about"
    CONTACT = "contact"
    PUBLIC_SERVICE = "public_service"
    CITIZEN_FORM = "citizen_form"
    SEARCH = "search"
    DOCUMENT_REPOSITORY = "document_repository"
    LANGUAGE_SWITCHER = "language_switcher"
    SITEMAP_DIRECTORY = "sitemap_directory"
    OTHER = "other"


class ArchitectureType(str, Enum):
    STATIC_HTML = "static_html"
    WORDPRESS = "wordpress"
    DRUPAL = "drupal"
    ANGULAR_SPA = "angular_spa"
    REACT_SPA = "react_spa"
    NEXTJS = "nextjs"
    LEGACY_DYNAMIC = "legacy_dynamic"
    CUSTOM_PORTAL = "custom_portal"
    UNKNOWN = "unknown"


# Level 2: Deterministic Measurement Models

class AccessibilityMeasurements(BaseModel):
    """Deterministic accessibility audit metrics from axe-core."""
    axe_violations_count: int = Field(ge=0, default=0)
    critical_violations: int = Field(ge=0, default=0)
    serious_violations: int = Field(ge=0, default=0)
    moderate_violations: int = Field(ge=0, default=0)
    minor_violations: int = Field(ge=0, default=0)
    accessibility_score: Optional[float] = Field(ge=0.0, le=100.0, default=None)
    has_missing_alts: bool = False
    has_form_label_violations: bool = False
    has_aria_violations: bool = False
    has_contrast_violations: bool = False
    raw_evidence_id: Optional[str] = None


class PerformanceMeasurements(BaseModel):
    """Deterministic Core Web Vitals and Lighthouse metrics."""
    lcp_ms: Optional[float] = Field(ge=0.0, default=None, description="Largest Contentful Paint in ms")
    cls: Optional[float] = Field(ge=0.0, default=None, description="Cumulative Layout Shift")
    fcp_ms: Optional[float] = Field(ge=0.0, default=None, description="First Contentful Paint in ms")
    ttfb_ms: Optional[float] = Field(ge=0.0, default=None, description="Time to First Byte in ms")
    tbt_ms: Optional[float] = Field(ge=0.0, default=None, description="Total Blocking Time in ms")
    speed_index: Optional[float] = Field(ge=0.0, default=None)
    page_weight_bytes: int = Field(ge=0, default=0)
    js_weight_bytes: int = Field(ge=0, default=0)
    css_weight_bytes: int = Field(ge=0, default=0)
    image_weight_bytes: int = Field(ge=0, default=0)
    request_count: int = Field(ge=0, default=0)
    lighthouse_performance_score: Optional[float] = Field(ge=0.0, le=100.0, default=None)
    raw_evidence_id: Optional[str] = None


class MobileReadinessMeasurements(BaseModel):
    """Deterministic mobile readiness checks."""
    has_viewport_meta: bool = True
    is_mobile_responsive: bool = True
    has_horizontal_overflow: bool = False
    mobile_score: Optional[float] = Field(ge=0.0, le=100.0, default=None)


class ReliabilityMeasurements(BaseModel):
    """Deterministic network, TLS, and availability metrics."""
    http_status_code: int = Field(ge=100, le=599)
    response_latency_ms: float = Field(ge=0.0)
    is_reachable: bool = True
    dns_resolution_time_ms: Optional[float] = Field(ge=0.0, default=None)
    tls_valid: bool = True
    tls_version: Optional[str] = None
    certificate_expiry_days: Optional[int] = None
    redirect_hops: int = Field(ge=0, default=0)
    redirect_chain: List[str] = Field(default_factory=list)


class LanguageMeasurements(BaseModel):
    """Deterministic language and multilingual detection."""
    detected_primary_language: str = "en"
    detected_secondary_languages: List[str] = Field(default_factory=list)
    has_language_selector: bool = False
    is_multilingual: bool = False
    supported_indian_languages: List[str] = Field(default_factory=list)


class WebStructureMeasurements(BaseModel):
    """DOM tree and structural composition metrics."""
    dom_node_count: int = Field(ge=0, default=0)
    max_dom_depth: int = Field(ge=0, default=0)
    links_count: int = Field(ge=0, default=0)
    internal_links_count: int = Field(ge=0, default=0)
    external_links_count: int = Field(ge=0, default=0)
    forms_count: int = Field(ge=0, default=0)
    tables_count: int = Field(ge=0, default=0)
    images_count: int = Field(ge=0, default=0)
    pdf_links_count: int = Field(ge=0, default=0)
    script_tags_count: int = Field(ge=0, default=0)
    stylesheet_tags_count: int = Field(ge=0, default=0)
    detected_frameworks: List[str] = Field(default_factory=list)
    # GIGW & Public Service Feature Flags
    has_font_resize_buttons: bool = False
    has_contrast_toggle: bool = False
    has_skip_to_content: bool = False
    has_screen_reader_access: bool = False
    gigw_accessibility_score: float = Field(ge=0.0, le=100.0, default=0.0)
    has_search_bar: bool = False
    has_grievance_portal: bool = False
    has_payment_gateway: bool = False
    has_mobile_app_links: bool = False
    has_social_media_links: bool = False
    aria_landmarks_count: int = Field(ge=0, default=0)


class SecurityHygieneMeasurements(BaseModel):
    """Publicly observable HTTP and security configuration signals."""
    has_https: bool = True
    has_hsts: bool = False
    has_csp: bool = False
    has_x_frame_options: bool = False
    has_x_content_type_options: bool = False
    has_referrer_policy: bool = False
    has_mixed_content: bool = False
    security_headers_score: float = Field(ge=0.0, le=100.0, default=0.0)


# Level 3: Derived Classifications (with Provenance)

class ProvenanceRecord(BaseModel):
    """Grounding provenance for every AI-derived classification."""
    field_name: str
    derived_value: str
    method: str = "agentic_classification"
    model: str = "qwen3:4b"
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: List[str] = Field(min_length=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DerivedClassifications(BaseModel):
    """Level 3: Classifications grounded in deterministic evidence."""
    website_category: str = "general_portal"
    architecture_type: ArchitectureType = ArchitectureType.UNKNOWN
    page_role: PageRole = PageRole.HOMEPAGE
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    provenances: List[ProvenanceRecord] = Field(default_factory=list)


# Master Observation Record

class ObservationRecord(BaseModel):
    """Unified master record combining Level 1 refs, Level 2 measurements, and Level 3 classifications."""
    observation_id: str = Field(default_factory=lambda: f"obs-{uuid.uuid4().hex[:12]}")
    crawl_id: str
    dataset_version: str = "0.1.0"
    domain_id: str
    source_url: str
    canonical_url: str
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    page_role: PageRole = PageRole.HOMEPAGE
    browser_rendered: bool = True

    # Level 1 Raw Evidence IDs
    raw_evidence_ids: List[str] = Field(default_factory=list)

    # Level 2 Deterministic Measurements
    accessibility: AccessibilityMeasurements = Field(default_factory=AccessibilityMeasurements)
    performance: PerformanceMeasurements = Field(default_factory=PerformanceMeasurements)
    mobile: MobileReadinessMeasurements = Field(default_factory=MobileReadinessMeasurements)
    reliability: ReliabilityMeasurements
    language: LanguageMeasurements = Field(default_factory=LanguageMeasurements)
    structure: WebStructureMeasurements = Field(default_factory=WebStructureMeasurements)
    security_hygiene: SecurityHygieneMeasurements = Field(default_factory=SecurityHygieneMeasurements)

    # Level 3 Derived Classifications
    classifications: DerivedClassifications = Field(default_factory=DerivedClassifications)

    # Validation Status
    is_validated: bool = False
    validation_notes: List[str] = Field(default_factory=list)
