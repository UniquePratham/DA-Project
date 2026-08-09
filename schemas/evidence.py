"""Raw evidence schema definitions for Level 1 observations."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid

from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    HTML = "html"
    SCREENSHOT = "screenshot"
    AXE_JSON = "axe_json"
    LIGHTHOUSE_JSON = "lighthouse_json"
    HEADERS_JSON = "headers_json"
    DNS_JSON = "dns_json"
    DOM_TREE = "dom_tree"


class RawEvidenceRecord(BaseModel):
    """Level 1: Raw Evidence record with cryptographic integrity."""
    evidence_id: str = Field(default_factory=lambda: f"ev-{uuid.uuid4().hex[:12]}")
    crawl_id: str
    domain_id: str
    source_url: str
    evidence_type: EvidenceType
    file_path: str
    sha256_hash: str = Field(min_length=64, max_length=64, description="Cryptographic SHA256 integrity hash")
    byte_size: int = Field(ge=0)
    content_type: str
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = Field(default_factory=dict)
