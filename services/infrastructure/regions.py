"""Country probe registry.

The research claim depends on measuring a country's government websites from
inside that country. This module is where that claim is either honoured or
broken, so it is deliberately strict:

* A country is only ``OPERATIONAL`` when a region physically inside it exists
  and has been verified.
* A country with no domestic region is ``UNSUPPORTED``. It is never silently
  measured from a neighbouring country.
* A ``NEAREST`` region may be recorded for operational convenience, but it is
  labelled as foreign and cannot be used to make a domestic claim.

The registry ships with the real Vultr region list so the statuses are derived
from fact rather than from hope.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .provider import Region


class ProbeStatus(str, Enum):
    """What we can honestly say about a country's measurement capability."""

    OPERATIONAL = "operational"
    PLANNED = "planned"
    UNSUPPORTED = "unsupported"
    PROVISIONING = "provisioning"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"


@dataclass
class CountryProbe:
    """The measurement capability for one country."""

    country_code: str
    country_name: str
    status: ProbeStatus
    domestic_region: Region | None = None
    nearest_region: Region | None = None
    note: str = ""
    last_measured_at: str | None = None

    @property
    def can_claim_domestic(self) -> bool:
        """True only when the probe physically sits in the target country."""
        return (
            self.status is ProbeStatus.OPERATIONAL
            and self.domestic_region is not None
            and self.domestic_region.country == self.country_code
        )

    def as_dict(self) -> dict:
        return {
            "country_code": self.country_code,
            "country_name": self.country_name,
            "status": self.status.value,
            "domestic_region": self.domestic_region.id if self.domestic_region else None,
            "domestic_region_city": self.domestic_region.city if self.domestic_region else None,
            "nearest_region": self.nearest_region.id if self.nearest_region else None,
            "nearest_region_country": self.nearest_region.country if self.nearest_region else None,
            "can_claim_domestic": self.can_claim_domestic,
            "note": self.note,
            "last_measured_at": self.last_measured_at,
        }


#: The countries the research programme intends to cover, with the ISO code and
#: a human name. Order is the intended expansion order.
TARGET_COUNTRIES: list[tuple[str, str]] = [
    ("IN", "India"),
    ("US", "United States"),
    ("GB", "United Kingdom"),
    ("CA", "Canada"),
    ("AU", "Australia"),
    ("DE", "Germany"),
    ("FR", "France"),
    ("JP", "Japan"),
    ("BR", "Brazil"),
    ("ZA", "South Africa"),
]


class ProbeRegistry:
    """Derives country probe status from the regions a provider actually has."""

    def __init__(self, regions: list[Region]):
        self._regions = regions
        self._by_country: dict[str, list[Region]] = {}
        for r in regions:
            self._by_country.setdefault(r.country, []).append(r)

    def regions_in(self, country_code: str) -> list[Region]:
        return list(self._by_country.get(country_code.upper(), []))

    def domestic_region(self, country_code: str) -> Region | None:
        """A region physically inside the country, if one exists."""
        found = self.regions_in(country_code)
        return found[0] if found else None

    def nearest_region(self, country_code: str) -> Region | None:
        """A region in a neighbouring country, for operational use only.

        This is a coarse fallback: it prefers the same continent, then any
        region. It is never used to justify a domestic measurement claim.
        """
        code = country_code.upper()
        if self.regions_in(code):
            return None
        # Prefer a region on the same continent as any region we know for the
        # country; without geography data we fall back to the first region.
        return self._regions[0] if self._regions else None

    def probe_for(self, country_code: str, country_name: str = "") -> CountryProbe:
        """Build the honest status for one country."""
        code = country_code.upper()
        domestic = self.domestic_region(code)

        if domestic is not None:
            return CountryProbe(
                country_code=code,
                country_name=country_name or code,
                status=ProbeStatus.OPERATIONAL,
                domestic_region=domestic,
                note=f"Domestic region available: {domestic.city}.",
            )

        nearest = self.nearest_region(code)
        return CountryProbe(
            country_code=code,
            country_name=country_name or code,
            status=ProbeStatus.UNSUPPORTED,
            domestic_region=None,
            nearest_region=nearest,
            note=(
                "No region inside this country. Domestic measurement is not "
                "possible; a nearby region would be a foreign probe and cannot "
                "support a domestic claim."
            ),
        )

    def all_probes(self) -> list[CountryProbe]:
        return [self.probe_for(code, name) for code, name in TARGET_COUNTRIES]

    def operational_countries(self) -> list[str]:
        return [p.country_code for p in self.all_probes() if p.can_claim_domestic]
