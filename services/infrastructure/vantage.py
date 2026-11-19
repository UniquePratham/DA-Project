"""Vantage-point model for countries Vultr cannot reach domestically.

The constraint is real: Vultr operates in 20 countries, so a domestic probe is
impossible in the other 229. That does not mean those countries cannot be
measured. It means they must be measured from a *different vantage point*, and
labelled as such.

Three vantage classes, each a genuine measurement:

* **DOMESTIC** — the probe sits inside the target country. This is the only
  class that supports a claim about what a citizen of that country experiences.
* **NEAREST** — the probe sits in the closest Vultr region, which is in another
  country. This measures what a foreign client sees. It is real data, and it is
  the *correct* data for questions about cross-border access, CDN behaviour and
  geo-blocking.
* **UNMEASURABLE** — no Vultr region is close enough for the latency figure to
  mean anything, and no other vantage exists.

The distinction is the research contribution, not a limitation to hide. A study
that measures the same portal from inside and outside its country can say
something no single-vantage study can: how much of the measured quality is the
portal, and how much is the path to it.

Every row records which class produced it, so a reader can filter to domestic
rows only, or compare the two.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from services.infrastructure.provider import Region


class VantageClass(str, Enum):
    DOMESTIC = "domestic"
    NEAREST = "nearest"
    UNMEASURABLE = "unmeasurable"


#: Approximate country centroids, used only to pick the nearest probe. These are
#: geographic facts, not measurements.
CENTROIDS: dict[str, tuple[float, float]] = {
    "AD": (42.5, 1.5), "AE": (24.0, 54.0), "AF": (33.0, 65.0), "AG": (17.1, -61.8),
    "AL": (41.0, 20.0), "AM": (40.0, 45.0), "AO": (-12.5, 18.5), "AR": (-34.0, -64.0),
    "AT": (47.3, 13.3), "AU": (-27.0, 133.0), "AW": (12.5, -69.9), "AZ": (40.5, 47.5),
    "BA": (44.0, 18.0), "BB": (13.2, -59.5), "BD": (24.0, 90.0), "BE": (50.8, 4.0),
    "BF": (13.0, -2.0), "BG": (43.0, 25.0), "BH": (26.0, 50.5), "BI": (-3.5, 30.0),
    "BJ": (9.5, 2.3), "BN": (4.5, 114.7), "BO": (-17.0, -65.0), "BR": (-10.0, -55.0),
    "BS": (24.3, -76.0), "BT": (27.5, 90.5), "BW": (-22.0, 24.0), "BY": (53.0, 28.0),
    "BZ": (17.3, -88.8), "CA": (60.0, -95.0), "CD": (-2.5, 23.0), "CF": (7.0, 21.0),
    "CG": (-1.0, 15.0), "CH": (47.0, 8.0), "CI": (8.0, -5.0), "CL": (-30.0, -71.0),
    "CM": (6.0, 12.0), "CN": (35.0, 105.0), "CO": (4.0, -72.0), "CR": (10.0, -84.0),
    "CU": (21.5, -80.0), "CV": (16.0, -24.0), "CY": (35.0, 33.0), "CZ": (49.8, 15.5),
    "DE": (51.0, 9.0), "DJ": (11.5, 43.0), "DK": (56.0, 10.0), "DM": (15.4, -61.4),
    "DO": (19.0, -70.7), "DZ": (28.0, 3.0), "EC": (-2.0, -77.5), "EE": (59.0, 26.0),
    "EG": (27.0, 30.0), "ER": (15.0, 39.0), "ES": (40.0, -4.0), "ET": (8.0, 38.0),
    "FI": (64.0, 26.0), "FJ": (-18.0, 178.0), "FM": (6.9, 158.2), "FR": (46.0, 2.0),
    "GA": (-1.0, 11.8), "GB": (54.0, -2.0), "GD": (12.1, -61.7), "GE": (42.0, 43.5),
    "GH": (8.0, -2.0), "GM": (13.5, -15.5), "GN": (11.0, -10.0), "GQ": (2.0, 10.0),
    "GR": (39.0, 22.0), "GT": (15.5, -90.3), "GW": (12.0, -15.0), "GY": (5.0, -59.0),
    "HK": (22.3, 114.2), "HN": (15.0, -86.5), "HR": (45.1, 15.2), "HT": (19.0, -72.3),
    "HU": (47.0, 20.0), "ID": (-5.0, 120.0), "IE": (53.0, -8.0), "IL": (31.5, 35.0),
    "IN": (22.0, 79.0), "IQ": (33.0, 44.0), "IR": (32.0, 53.0), "IS": (65.0, -18.0),
    "IT": (42.8, 12.8), "JM": (18.1, -77.3), "JO": (31.0, 36.0), "JP": (36.0, 138.0),
    "KE": (1.0, 38.0), "KG": (41.0, 75.0), "KH": (13.0, 105.0), "KI": (1.4, 173.0),
    "KM": (-12.2, 44.3), "KN": (17.3, -62.7), "KP": (40.0, 127.0), "KR": (37.0, 127.5),
    "KW": (29.5, 45.8), "KZ": (48.0, 68.0), "LA": (18.0, 105.0), "LB": (33.8, 35.8),
    "LC": (13.9, -61.0), "LI": (47.2, 9.6), "LK": (7.0, 81.0), "LR": (6.5, -9.5),
    "LS": (-29.5, 28.5), "LT": (55.0, 24.0), "LU": (49.8, 6.1), "LV": (57.0, 25.0),
    "LY": (27.0, 17.0), "MA": (32.0, -5.0), "MC": (43.7, 7.4), "MD": (47.0, 29.0),
    "ME": (42.5, 19.3), "MG": (-20.0, 47.0), "MH": (9.0, 168.0), "MK": (41.6, 21.7),
    "ML": (17.0, -4.0), "MM": (22.0, 98.0), "MN": (46.0, 105.0), "MO": (22.2, 113.5),
    "MR": (20.0, -12.0), "MT": (35.9, 14.4), "MU": (-20.3, 57.6), "MV": (3.2, 73.2),
    "MW": (-13.5, 34.0), "MX": (23.0, -102.0), "MY": (2.5, 112.5), "MZ": (-18.3, 35.0),
    "NA": (-22.0, 17.0), "NE": (16.0, 8.0), "NG": (10.0, 8.0), "NI": (13.0, -85.0),
    "NL": (52.5, 5.5), "NO": (62.0, 10.0), "NP": (28.0, 84.0), "NR": (-0.5, 166.9),
    "NZ": (-41.0, 174.0), "OM": (21.0, 57.0), "PA": (9.0, -80.0), "PE": (-10.0, -76.0),
    "PG": (-6.0, 147.0), "PH": (13.0, 122.0), "PK": (30.0, 70.0), "PL": (52.0, 20.0),
    "PS": (32.0, 35.2), "PT": (39.5, -8.0), "PW": (7.5, 134.6), "PY": (-23.0, -58.0),
    "QA": (25.3, 51.2), "RO": (46.0, 25.0), "RS": (44.0, 21.0), "RU": (60.0, 100.0),
    "RW": (-2.0, 30.0), "SA": (25.0, 45.0), "SB": (-8.0, 159.0), "SC": (-4.6, 55.5),
    "SD": (15.0, 30.0), "SE": (62.0, 15.0), "SG": (1.3, 103.8), "SI": (46.1, 14.8),
    "SK": (48.7, 19.5), "SL": (8.5, -11.8), "SM": (43.9, 12.4), "SN": (14.0, -14.0),
    "SO": (10.0, 49.0), "SR": (4.0, -56.0), "SS": (7.0, 30.0), "ST": (1.0, 7.0),
    "SV": (13.8, -88.9), "SY": (35.0, 38.0), "SZ": (-26.5, 31.5), "TD": (15.0, 19.0),
    "TG": (8.0, 1.2), "TH": (15.0, 101.0), "TJ": (39.0, 71.0), "TL": (-8.9, 125.7),
    "TM": (40.0, 60.0), "TN": (34.0, 9.0), "TO": (-20.0, -175.0), "TR": (39.0, 35.0),
    "TT": (10.7, -61.2), "TV": (-8.0, 178.0), "TW": (23.7, 121.0), "TZ": (-6.0, 35.0),
    "UA": (49.0, 32.0), "UG": (1.0, 32.0), "US": (39.0, -98.0), "UY": (-33.0, -56.0),
    "UZ": (41.0, 64.0), "VA": (41.9, 12.5), "VC": (13.2, -61.2), "VE": (8.0, -66.0),
    "VN": (16.0, 106.0), "VU": (-16.0, 167.0), "WS": (-13.8, -172.1), "XK": (42.6, 20.9),
    "YE": (15.0, 48.0), "ZA": (-29.0, 24.0), "ZM": (-15.0, 30.0), "ZW": (-20.0, 30.0),
}

#: Region coordinates, for computing the nearest probe.
REGION_COORDS: dict[str, tuple[float, float]] = {
    "ams": (52.4, 4.9), "atl": (33.7, -84.4), "blr": (13.0, 77.6),
    "bom": (19.1, 72.9), "cdg": (49.0, 2.5), "del": (28.6, 77.2),
    "dfw": (32.8, -96.8), "ewr": (40.7, -74.2), "fra": (50.1, 8.7),
    "hnl": (21.3, -157.9), "icn": (37.5, 126.6), "itm": (34.7, 135.5),
    "jnb": (-26.2, 28.0), "lax": (34.1, -118.2), "lhr": (51.5, -0.1),
    "mad": (40.4, -3.7), "mel": (-37.8, 145.0), "mex": (19.4, -99.1),
    "mia": (25.8, -80.2), "nrt": (35.7, 139.7), "ord": (41.9, -87.6),
    "scl": (-33.4, -70.7), "sea": (47.6, -122.3), "sgp": (1.3, 103.8),
    "sjc": (37.3, -121.9), "sto": (59.3, 18.1), "syd": (-33.9, 151.2),
    "waw": (52.2, 21.0), "yto": (43.7, -79.4), "sao": (-23.5, -46.6),
    "bog": (4.7, -74.1), "mxp": (45.5, 9.2), "man": (53.5, -2.2),
    "hon": (21.3, -157.9),
}


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Great-circle distance in kilometres."""
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


@dataclass
class Vantage:
    """The chosen vantage point for one country."""

    country: str
    vantage_class: VantageClass
    region: Region | None
    distance_km: float | None
    reason: str

    @property
    def can_claim_domestic(self) -> bool:
        return self.vantage_class is VantageClass.DOMESTIC

    def as_dict(self) -> dict:
        return {
            "country": self.country,
            "vantage_class": self.vantage_class.value,
            "region_id": self.region.id if self.region else None,
            "region_city": self.region.city if self.region else None,
            "region_country": self.region.country if self.region else None,
            "distance_km": round(self.distance_km) if self.distance_km is not None else None,
            "can_claim_domestic": self.can_claim_domestic,
            "reason": self.reason,
        }


#: Beyond this distance a latency measurement says more about the path than the
#: portal, so the country is marked unmeasurable rather than measured badly.
MAX_NEAREST_KM = 6000.0


class VantageSelector:
    """Picks the best available vantage point for a country, honestly."""

    def __init__(self, regions: list[Region]):
        self._regions = [r for r in regions if r.id in REGION_COORDS]

    def select(self, country: str) -> Vantage:
        code = country.upper()

        # 1. A domestic region is always preferred.
        domestic = [r for r in self._regions if r.country == code]
        if domestic:
            return Vantage(
                country=code,
                vantage_class=VantageClass.DOMESTIC,
                region=domestic[0],
                distance_km=0.0,
                reason=f"Domestic region in {domestic[0].city}.",
            )

        # 2. Otherwise the nearest region, if it is close enough to be meaningful.
        centroid = CENTROIDS.get(code)
        if centroid is None:
            return Vantage(
                country=code,
                vantage_class=VantageClass.UNMEASURABLE,
                region=None,
                distance_km=None,
                reason="No country centroid on record; cannot pick a nearest probe.",
            )

        best = min(
            self._regions,
            key=lambda r: haversine_km(centroid, REGION_COORDS[r.id]),
        )
        distance = haversine_km(centroid, REGION_COORDS[best.id])

        if distance > MAX_NEAREST_KM:
            return Vantage(
                country=code,
                vantage_class=VantageClass.UNMEASURABLE,
                region=best,
                distance_km=distance,
                reason=(
                    f"Nearest region is {distance:.0f} km away in {best.country}; "
                    "too far for the latency figure to describe the portal."
                ),
            )

        return Vantage(
            country=code,
            vantage_class=VantageClass.NEAREST,
            region=best,
            distance_km=distance,
            reason=(
                f"No domestic region. Nearest is {best.city}, {best.country}, "
                f"{distance:.0f} km away. This measures a foreign client's view, "
                "not a citizen's."
            ),
        )

    def select_all(self, countries: list[str]) -> list[Vantage]:
        return [self.select(c) for c in countries]
