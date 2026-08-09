"""Domain registry and government hierarchy schema definitions."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List
import uuid

from pydantic import BaseModel, Field, HttpUrl


class DomainStatus(str, Enum):
    VERIFIED = "VERIFIED"
    ACTIVE = "ACTIVE"
    TEMPORARILY_UNAVAILABLE = "TEMPORARILY_UNAVAILABLE"
    PERMANENTLY_UNAVAILABLE = "PERMANENTLY_UNAVAILABLE"
    REDIRECTED = "REDIRECTED"
    ROBOTS_RESTRICTED = "ROBOTS_RESTRICTED"
    BLOCKED = "BLOCKED"
    TLS_ERROR = "TLS_ERROR"
    TIMEOUT = "TIMEOUT"
    REQUIRES_AUTH = "REQUIRES_AUTH"
    UNRESOLVED = "UNRESOLVED"
    RETIRED = "RETIRED"


class GovernmentLevel(str, Enum):
    CENTRAL = "central"
    STATE_UT = "state_ut"
    DISTRICT = "district"
    LOCAL_BODY = "local_body"
    OTHER_PUBLIC = "other_public"


class GovernmentEntityRecord(BaseModel):
    """Registry entry for an Indian government web domain."""
    domain_id: str = Field(default_factory=lambda: f"dom-{uuid.uuid4().hex[:10]}")
    domain_name: str
    base_url: str
    canonical_url: Optional[str] = None
    government_level: GovernmentLevel = GovernmentLevel.CENTRAL
    state_or_ut: Optional[str] = None
    district: Optional[str] = None
    ministry_or_department: Optional[str] = None
    entity_name: str
    status: DomainStatus = DomainStatus.VERIFIED
    last_observed_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
