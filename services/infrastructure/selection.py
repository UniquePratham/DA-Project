"""Choose the best measurement region for a country.

The research claim depends on measuring from inside the target country, so the
first rule is absolute: only a region physically in that country is eligible.
A nearby region is never substituted, because a foreign probe cannot support a
domestic claim.

Within the eligible set we prefer, in order:

1. **Fewest known blocks.** A region whose egress has already produced WAF
   challenges for this country's domains is deprioritised. This is learned from
   real measurement outcomes, not guessed.
2. **Lowest observed latency** to that country's domains, from real probes.
3. **Most central geography**, as a tie-break, using the region's own
   coordinates where the provider exposes them.

When there is no history the choice falls back to the provider's ordering, and
the decision is recorded as ``no_history`` so the dashboard can say so rather
than implying a measured preference.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .provider import Region


@dataclass
class RegionScore:
    """Why a region was chosen, so the choice can be audited."""

    region: Region
    eligible: bool
    blocks: int = 0
    median_latency_ms: float | None = None
    samples: int = 0
    reason: str = ""

    def as_dict(self) -> dict:
        return {
            "region_id": self.region.id,
            "city": self.region.city,
            "country": self.region.country,
            "eligible": self.eligible,
            "blocks": self.blocks,
            "median_latency_ms": self.median_latency_ms,
            "samples": self.samples,
            "reason": self.reason,
        }


@dataclass
class RegionHistory:
    """Observed outcomes per (region, country) pair.

    Populated from real measurement runs. An empty history is honest: it means
    we have not measured yet, not that the region is good.
    """

    #: (region_id, target_country) -> number of WAF blocks observed
    blocks: dict[tuple[str, str], int] = field(default_factory=dict)
    #: (region_id, target_country) -> list of observed latencies in ms
    latencies: dict[tuple[str, str], list[float]] = field(default_factory=dict)

    def record(self, region_id: str, country: str, latency_ms: float, blocked: bool) -> None:
        key = (region_id, country.upper())
        if blocked:
            self.blocks[key] = self.blocks.get(key, 0) + 1
        else:
            self.latencies.setdefault(key, []).append(latency_ms)

    def block_count(self, region_id: str, country: str) -> int:
        return self.blocks.get((region_id, country.upper()), 0)

    def median_latency(self, region_id: str, country: str) -> float | None:
        vals = self.latencies.get((region_id, country.upper()))
        if not vals:
            return None
        s = sorted(vals)
        n = len(s)
        mid = n // 2
        return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0

    def sample_count(self, region_id: str, country: str) -> int:
        return len(self.latencies.get((region_id, country.upper()), []))


class RegionSelector:
    """Picks the measurement region for a country, or refuses."""

    def __init__(self, regions: list[Region], history: RegionHistory | None = None):
        self._regions = regions
        self.history = history or RegionHistory()

    def eligible(self, country_code: str) -> list[Region]:
        """Regions physically inside the country. Never a neighbour."""
        code = country_code.upper()
        return [r for r in self._regions if r.country == code]

    def score(self, country_code: str) -> list[RegionScore]:
        """Every domestic region, ranked, with the reason recorded."""
        code = country_code.upper()
        out: list[RegionScore] = []
        for r in self.eligible(code):
            blocks = self.history.block_count(r.id, code)
            lat = self.history.median_latency(r.id, code)
            samples = self.history.sample_count(r.id, code)
            if samples == 0 and blocks == 0:
                reason = "no_history"
            elif blocks > 0:
                reason = f"{blocks} WAF block(s) observed"
            else:
                reason = f"median {lat:.0f} ms over {samples} sample(s)"
            out.append(
                RegionScore(
                    region=r,
                    eligible=True,
                    blocks=blocks,
                    median_latency_ms=lat,
                    samples=samples,
                    reason=reason,
                )
            )

        # Rank: fewest blocks, then lowest latency, then provider order.
        def key(s: RegionScore):
            lat = s.median_latency_ms if s.median_latency_ms is not None else float("inf")
            return (s.blocks, lat)

        out.sort(key=key)
        return out

    def select(self, country_code: str) -> RegionScore | None:
        """The best domestic region, or ``None`` when the country is unsupported."""
        ranked = self.score(country_code)
        return ranked[0] if ranked else None

    def select_or_raise(self, country_code: str) -> RegionScore:
        chosen = self.select(country_code)
        if chosen is None:
            raise LookupError(
                f"no cloud region inside {country_code.upper()}; domestic "
                "measurement is not possible and a neighbouring region will not "
                "be substituted"
            )
        return chosen
