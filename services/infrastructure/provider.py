"""Provider-neutral cloud interface.

The lifecycle manager talks only to this interface. Adding a second cloud means
writing one more adapter, not touching the state machine, the budget guard or
the ownership checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Protocol, runtime_checkable


class ProviderError(RuntimeError):
    """Raised when a provider call fails in a way the caller must handle."""


@dataclass(frozen=True)
class Region:
    """A physical cloud region.

    ``country`` is the ISO-3166 alpha-2 code of the country the datacentre is
    actually in. It is never inferred from the region's marketing name, because
    a region called ``eu-central`` may sit in any of several countries.
    """

    id: str
    city: str
    country: str
    continent: str = ""

    def __str__(self) -> str:  # pragma: no cover - display only
        return f"{self.city}, {self.country} ({self.id})"


@dataclass(frozen=True)
class InstanceSpec:
    """What to provision."""

    region_id: str
    plan_id: str
    os_id: int
    label: str
    tags: tuple[str, ...] = ()
    ssh_key_ids: tuple[str, ...] = ()
    user_data: str = ""


@dataclass
class ProvisionedInstance:
    """A live instance as the provider reports it."""

    id: str
    region_id: str
    plan_id: str
    label: str
    status: str
    main_ip: Optional[str] = None
    tags: tuple[str, ...] = ()
    created_at: Optional[datetime] = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def is_running(self) -> bool:
        return self.status == "active"


@runtime_checkable
class CloudProvider(Protocol):
    """The narrow surface the lifecycle manager needs."""

    name: str

    def list_regions(self) -> list[Region]:
        """Every region the account can actually deploy into."""

    def list_plans(self, region_id: str) -> list[dict[str, Any]]:
        """Plans available in a region, with hourly price where known."""

    def create_instance(self, spec: InstanceSpec) -> ProvisionedInstance:
        """Provision one instance. Must be idempotent on ``spec.label``."""

    def get_instance(self, instance_id: str) -> Optional[ProvisionedInstance]:
        """Return the instance, or ``None`` if it no longer exists."""

    def list_instances(self, tag: Optional[str] = None) -> list[ProvisionedInstance]:
        """All instances, optionally filtered by an ownership tag."""

    def destroy_instance(self, instance_id: str) -> bool:
        """Destroy one instance. Returns True when it is gone."""

    def account_balance(self) -> Optional[float]:
        """Remaining account credit, if the provider exposes it."""
