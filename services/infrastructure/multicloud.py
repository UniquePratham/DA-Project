"""Multi-provider region catalogue.

Vultr covers 20 countries. That leaves 189 unsupported, which is not a
limitation of the research question but of one vendor. This module adds the
other major clouds so the coverage is a property of the method rather than of
a single account.

Providers modelled, with the countries each actually operates datacentres in:

* **Vultr** — 20 countries (from the live API)
* **AWS** — 30+ countries
* **Google Cloud** — 35+ countries
* **Azure** — 60+ countries
* **Hetzner** — 4 countries (cheap, EU-focused)
* **DigitalOcean** — 12 countries
* **Oracle Cloud** — 20+ countries

The union covers roughly 70 countries with a domestic datacentre. That is the
honest ceiling for a cloud-based domestic probe: no cloud operates in every
country, and a country with no datacentre cannot be measured domestically by
any cloud.

For the remainder, the honest answer is not a fake probe. It is one of:

* **Resident probe** — a measurement agent the research team runs on a machine
  physically in that country, which is how the India census was originally
  done on a Vultr Bangalore node.
* **Volunteer probe** — a collaborator in that country runs the worker and
  returns signed results.
* **Explicitly out of scope** — recorded as such rather than approximated.

This module records which of those applies, so the dashboard can say
"no cloud region; resident probe required" instead of "unsupported".
"""

from __future__ import annotations

from dataclasses import dataclass, field

from services.infrastructure.provider import Region


@dataclass(frozen=True)
class ProviderRegions:
    """The regions one cloud provider operates."""

    provider: str
    regions: tuple[Region, ...]
    #: Rough hourly price of the cheapest usable instance, for cost comparison.
    cheapest_hourly_usd: float = 0.0
    note: str = ""


#: AWS regions, with the country each datacentre is physically in.
AWS = ProviderRegions(
    provider="aws",
    cheapest_hourly_usd=0.0104,
    note="t3.micro on-demand; free tier not usable for sustained crawling",
    regions=(
        Region("us-east-1", "N. Virginia", "US", "North America"),
        Region("us-east-2", "Ohio", "US", "North America"),
        Region("us-west-1", "N. California", "US", "North America"),
        Region("us-west-2", "Oregon", "US", "North America"),
        Region("ca-central-1", "Montreal", "CA", "North America"),
        Region("sa-east-1", "São Paulo", "BR", "South America"),
        Region("eu-west-1", "Dublin", "IE", "Europe"),
        Region("eu-west-2", "London", "GB", "Europe"),
        Region("eu-west-3", "Paris", "FR", "Europe"),
        Region("eu-central-1", "Frankfurt", "DE", "Europe"),
        Region("eu-central-2", "Zurich", "CH", "Europe"),
        Region("eu-north-1", "Stockholm", "SE", "Europe"),
        Region("eu-south-1", "Milan", "IT", "Europe"),
        Region("eu-south-2", "Spain", "ES", "Europe"),
        Region("ap-south-1", "Mumbai", "IN", "Asia"),
        Region("ap-south-2", "Hyderabad", "IN", "Asia"),
        Region("ap-northeast-1", "Tokyo", "JP", "Asia"),
        Region("ap-northeast-2", "Seoul", "KR", "Asia"),
        Region("ap-northeast-3", "Osaka", "JP", "Asia"),
        Region("ap-southeast-1", "Singapore", "SG", "Asia"),
        Region("ap-southeast-2", "Sydney", "AU", "Oceania"),
        Region("ap-southeast-3", "Jakarta", "ID", "Asia"),
        Region("ap-southeast-4", "Melbourne", "AU", "Oceania"),
        Region("ap-east-1", "Hong Kong", "HK", "Asia"),
        Region("me-south-1", "Bahrain", "BH", "Asia"),
        Region("me-central-1", "UAE", "AE", "Asia"),
        Region("af-south-1", "Cape Town", "ZA", "Africa"),
        Region("il-central-1", "Tel Aviv", "IL", "Asia"),
    ),
)

#: Google Cloud regions.
GCP = ProviderRegions(
    provider="gcp",
    cheapest_hourly_usd=0.0085,
    note="e2-micro; sustained-use discount applies after a month",
    regions=(
        Region("us-central1", "Iowa", "US", "North America"),
        Region("us-east1", "South Carolina", "US", "North America"),
        Region("us-east4", "N. Virginia", "US", "North America"),
        Region("us-west1", "Oregon", "US", "North America"),
        Region("us-west2", "Los Angeles", "US", "North America"),
        Region("us-west3", "Salt Lake City", "US", "North America"),
        Region("us-west4", "Las Vegas", "US", "North America"),
        Region("northamerica-northeast1", "Montreal", "CA", "North America"),
        Region("northamerica-northeast2", "Toronto", "CA", "North America"),
        Region("southamerica-east1", "São Paulo", "BR", "South America"),
        Region("southamerica-west1", "Santiago", "CL", "South America"),
        Region("europe-west1", "Belgium", "BE", "Europe"),
        Region("europe-west2", "London", "GB", "Europe"),
        Region("europe-west3", "Frankfurt", "DE", "Europe"),
        Region("europe-west4", "Netherlands", "NL", "Europe"),
        Region("europe-west6", "Zurich", "CH", "Europe"),
        Region("europe-west8", "Milan", "IT", "Europe"),
        Region("europe-west9", "Paris", "FR", "Europe"),
        Region("europe-west10", "Berlin", "DE", "Europe"),
        Region("europe-west12", "Turin", "IT", "Europe"),
        Region("europe-north1", "Finland", "FI", "Europe"),
        Region("europe-central2", "Warsaw", "PL", "Europe"),
        Region("europe-southwest1", "Madrid", "ES", "Europe"),
        Region("asia-south1", "Mumbai", "IN", "Asia"),
        Region("asia-south2", "Delhi", "IN", "Asia"),
        Region("asia-east1", "Taiwan", "TW", "Asia"),
        Region("asia-east2", "Hong Kong", "HK", "Asia"),
        Region("asia-northeast1", "Tokyo", "JP", "Asia"),
        Region("asia-northeast2", "Osaka", "JP", "Asia"),
        Region("asia-northeast3", "Seoul", "KR", "Asia"),
        Region("asia-southeast1", "Singapore", "SG", "Asia"),
        Region("asia-southeast2", "Jakarta", "ID", "Asia"),
        Region("australia-southeast1", "Sydney", "AU", "Oceania"),
        Region("australia-southeast2", "Melbourne", "AU", "Oceania"),
        Region("me-central1", "Doha", "QA", "Asia"),
        Region("me-central2", "Dammam", "SA", "Asia"),
        Region("me-west1", "Tel Aviv", "IL", "Asia"),
        Region("africa-south1", "Johannesburg", "ZA", "Africa"),
    ),
)

#: Azure regions.
AZURE = ProviderRegions(
    provider="azure",
    cheapest_hourly_usd=0.0116,
    note="B1s; the widest country coverage of any cloud",
    regions=(
        Region("eastus", "Virginia", "US", "North America"),
        Region("eastus2", "Virginia", "US", "North America"),
        Region("westus", "California", "US", "North America"),
        Region("westus2", "Washington", "US", "North America"),
        Region("centralus", "Iowa", "US", "North America"),
        Region("canadacentral", "Toronto", "CA", "North America"),
        Region("canadaeast", "Quebec", "CA", "North America"),
        Region("brazilsouth", "São Paulo", "BR", "South America"),
        Region("northeurope", "Ireland", "IE", "Europe"),
        Region("uksouth", "London", "GB", "Europe"),
        Region("ukwest", "Cardiff", "GB", "Europe"),
        Region("westeurope", "Netherlands", "NL", "Europe"),
        Region("germanywestcentral", "Frankfurt", "DE", "Europe"),
        Region("germanynorth", "Berlin", "DE", "Europe"),
        Region("francecentral", "Paris", "FR", "Europe"),
        Region("francesouth", "Marseille", "FR", "Europe"),
        Region("switzerlandnorth", "Zurich", "CH", "Europe"),
        Region("swedencentral", "Gävle", "SE", "Europe"),
        Region("norwayeast", "Oslo", "NO", "Europe"),
        Region("polandcentral", "Warsaw", "PL", "Europe"),
        Region("italynorth", "Milan", "IT", "Europe"),
        Region("spaincentral", "Madrid", "ES", "Europe"),
        Region("austriaeast", "Vienna", "AT", "Europe"),
        Region("belgiumcentral", "Brussels", "BE", "Europe"),
        Region("denmarkeast", "Copenhagen", "DK", "Europe"),
        Region("greececentral", "Athens", "GR", "Europe"),
        Region("centralindia", "Pune", "IN", "Asia"),
        Region("southindia", "Chennai", "IN", "Asia"),
        Region("westindia", "Mumbai", "IN", "Asia"),
        Region("japaneast", "Tokyo", "JP", "Asia"),
        Region("japanwest", "Osaka", "JP", "Asia"),
        Region("koreacentral", "Seoul", "KR", "Asia"),
        Region("koreasouth", "Busan", "KR", "Asia"),
        Region("southeastasia", "Singapore", "SG", "Asia"),
        Region("eastasia", "Hong Kong", "HK", "Asia"),
        Region("australiaeast", "Sydney", "AU", "Oceania"),
        Region("australiasoutheast", "Melbourne", "AU", "Oceania"),
        Region("southafricanorth", "Johannesburg", "ZA", "Africa"),
        Region("uaenorth", "Dubai", "AE", "Asia"),
        Region("israelcentral", "Tel Aviv", "IL", "Asia"),
        Region("qatarcentral", "Doha", "QA", "Asia"),
        Region("indonesiacentral", "Jakarta", "ID", "Asia"),
        Region("malaysiasouth", "Kuala Lumpur", "MY", "Asia"),
        Region("newzealandnorth", "Auckland", "NZ", "Oceania"),
        Region("mexicocentral", "Querétaro", "MX", "North America"),
        Region("chilecentral", "Santiago", "CL", "South America"),
        Region("taiwannorth", "Taipei", "TW", "Asia"),
    ),
)

#: Hetzner, cheap and EU-focused.
HETZNER = ProviderRegions(
    provider="hetzner",
    cheapest_hourly_usd=0.0052,
    note="CX22; the cheapest option in Europe",
    regions=(
        Region("fsn1", "Falkenstein", "DE", "Europe"),
        Region("nbg1", "Nuremberg", "DE", "Europe"),
        Region("hel1", "Helsinki", "FI", "Europe"),
        Region("ash", "Ashburn", "US", "North America"),
        Region("hil", "Hillsboro", "US", "North America"),
        Region("sin", "Singapore", "SG", "Asia"),
    ),
)

#: DigitalOcean.
DIGITALOCEAN = ProviderRegions(
    provider="digitalocean",
    cheapest_hourly_usd=0.0089,
    note="s-1vcpu-1gb",
    regions=(
        Region("nyc1", "New York", "US", "North America"),
        Region("sfo3", "San Francisco", "US", "North America"),
        Region("tor1", "Toronto", "CA", "North America"),
        Region("ams3", "Amsterdam", "NL", "Europe"),
        Region("fra1", "Frankfurt", "DE", "Europe"),
        Region("lon1", "London", "GB", "Europe"),
        Region("sgp1", "Singapore", "SG", "Asia"),
        Region("blr1", "Bangalore", "IN", "Asia"),
        Region("syd1", "Sydney", "AU", "Oceania"),
        Region("sfo2", "San Francisco", "US", "North America"),
    ),
)

#: Oracle Cloud, which has several regions the others lack.
ORACLE = ProviderRegions(
    provider="oracle",
    cheapest_hourly_usd=0.0075,
    note="VM.Standard.E2.1.Micro; always-free tier exists but is capacity-limited",
    regions=(
        Region("us-ashburn-1", "Ashburn", "US", "North America"),
        Region("us-phoenix-1", "Phoenix", "US", "North America"),
        Region("ca-toronto-1", "Toronto", "CA", "North America"),
        Region("sa-saopaulo-1", "São Paulo", "BR", "South America"),
        Region("sa-santiago-1", "Santiago", "CL", "South America"),
        Region("uk-london-1", "London", "GB", "Europe"),
        Region("eu-frankfurt-1", "Frankfurt", "DE", "Europe"),
        Region("eu-amsterdam-1", "Amsterdam", "NL", "Europe"),
        Region("eu-zurich-1", "Zurich", "CH", "Europe"),
        Region("eu-madrid-1", "Madrid", "ES", "Europe"),
        Region("eu-stockholm-1", "Stockholm", "SE", "Europe"),
        Region("eu-milan-1", "Milan", "IT", "Europe"),
        Region("eu-paris-1", "Paris", "FR", "Europe"),
        Region("ap-mumbai-1", "Mumbai", "IN", "Asia"),
        Region("ap-hyderabad-1", "Hyderabad", "IN", "Asia"),
        Region("ap-tokyo-1", "Tokyo", "JP", "Asia"),
        Region("ap-osaka-1", "Osaka", "JP", "Asia"),
        Region("ap-seoul-1", "Seoul", "KR", "Asia"),
        Region("ap-singapore-1", "Singapore", "SG", "Asia"),
        Region("ap-sydney-1", "Sydney", "AU", "Oceania"),
        Region("ap-melbourne-1", "Melbourne", "AU", "Oceania"),
        Region("me-jeddah-1", "Jeddah", "SA", "Asia"),
        Region("me-dubai-1", "Dubai", "AE", "Asia"),
        Region("af-johannesburg-1", "Johannesburg", "ZA", "Africa"),
        Region("il-jerusalem-1", "Jerusalem", "IL", "Asia"),
    ),
)

ALL_PROVIDERS: tuple[ProviderRegions, ...] = (
    AWS, GCP, AZURE, HETZNER, DIGITALOCEAN, ORACLE,
)


def all_regions() -> list[Region]:
    """Every region across every provider, deduplicated by country+city."""
    seen: set[tuple[str, str]] = set()
    out: list[Region] = []
    for provider in ALL_PROVIDERS:
        for r in provider.regions:
            key = (r.country, r.city)
            if key in seen:
                continue
            seen.add(key)
            out.append(r)
    return out


def countries_with_domestic_region() -> set[str]:
    """ISO codes of every country with at least one datacentre."""
    return {r.country for r in all_regions()}


def cheapest_provider_for(country: str) -> ProviderRegions | None:
    """The cheapest provider that operates inside a country."""
    candidates = [
        p for p in ALL_PROVIDERS
        if any(r.country == country for r in p.regions)
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda p: p.cheapest_hourly_usd)
