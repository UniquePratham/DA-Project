"""Discover sector-specific government domains from official ministry indexes.

crt.sh has become unusable: a single query now takes ~38 seconds and often
returns nothing, so a 45-query country takes half an hour. This script takes
the fast path instead.

Every government publishes a page listing its own ministries. Those pages are
small, fast, and authoritative, and they link directly to health, education,
justice and finance ministries. Harvesting them gives sector coverage in
seconds rather than hours, and the source is better: a ministry index is a
statement by the government about its own structure, not an inference from a
certificate log.

Every domain is verified by DNS before it is recorded.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import socket
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

spec = importlib.util.spec_from_file_location(
    "discover", REPO / "scripts" / "discover_global_domains.py"
)
discover = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discover)

spec2 = importlib.util.spec_from_file_location(
    "clean", REPO / "scripts" / "clean_global_domains.py"
)
clean = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(clean)

REGISTRY = REPO / "data" / "fixtures" / "global_domains.json"
UA = (
    "CivicWebObservatory/1.0 "
    "(+https://uniquepratham.github.io/DA-Project/; research-bot@civicweb.in)"
)
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"}

#: Ministry index pages per country. Each is a page the government publishes
#: listing its own ministries, which is the authoritative source for sector
#: coverage.
MINISTRY_INDEXES: dict[str, list[str]] = {
    "IN": [
        "https://www.india.gov.in/directory/ministries-departments",
        "https://www.india.gov.in/my-government/ministries-departments",
    ],
    "US": [
        "https://www.usa.gov/federal-agencies",
        "https://www.usa.gov/agency-index",
    ],
    "GB": [
        "https://www.gov.uk/government/organisations",
    ],
    "CA": [
        "https://www.canada.ca/en/government/dept.html",
    ],
    "AU": [
        "https://www.directory.gov.au/commonwealth-entities-and-companies",
        "https://www.australia.gov.au/departments-and-agencies",
    ],
    "DE": [
        "https://www.bund.de/DE/Behoerden/behoerden_node.html",
    ],
    "FR": [
        "https://www.gouvernement.fr/composition-du-gouvernement",
    ],
    "JP": [
        "https://www.japan.go.jp/links/",
    ],
    "BR": [
        "https://www.gov.br/pt-br/orgaos-do-governo",
    ],
    "ZA": [
        "https://www.gov.za/about-government/government-system",
    ],
    "SG": [
        "https://www.gov.sg/government-websites",
    ],
    "NL": [
        "https://www.rijksoverheid.nl/regering/ministeries",
    ],
    "ES": [
        "https://www.lamoncloa.gob.es/gobierno/Paginas/index.aspx",
    ],
    "IT": [
        "https://www.governo.it/it/ministeri",
    ],
    "PL": [
        "https://www.gov.pl/web/gov/ministerstwa",
    ],
    "KR": [
        "https://www.korea.kr/archive/expDocList.do",
    ],
    "MX": [
        "https://www.gob.mx/agencias",
    ],
    "CL": [
        "https://www.gob.cl/ministerios/",
    ],
    "IL": [
        "https://www.gov.il/he/departments",
    ],
}

#: Sector markers used to label a discovered domain. Matched against the link
#: text first (which is in the page's own language) and the hostname second.
SECTOR_TEXT_MARKERS: list[tuple[str, tuple[str, ...]]] = [
    ("health", (
        "health", "hospital", "medical", "medicine", "nhs", "sanidad",
        "salud", "sante", "santé", "salute", "gesundheit", "zdrowie",
        "zdrav", "saude", "saúde", "sanita", "gezondheid", "sundhed",
        "hälsa", "helse", "terveys", "egészség", "υγεια", "sağlik",
        "स्वास्थ्य", "आरोग्य", "স্বাস্থ্য", "சுகாதார", "ఆరోగ్య", "ಆರೋಗ್ಯ",
    )),
    ("education", (
        "education", "school", "university", "college", "educacion",
        "educación", "educacao", "educação", "bildung", "onderwijs",
        "utbildning", "koulutus", "edukacja", "vzdelavanie", "haridus",
        "izglitiba", "invatamant", "egitim", "शिक्षा", "শিক্ষা", "கல்வி",
        "విద్య", "ಶಿಕ್ಷಣ", "eğitim", "εκπαιδευση",
    )),
    ("judiciary", (
        "justice", "court", "judicial", "judiciary", "justicia", "justiça",
        "justiz", "giustizia", "justitie", "rechtspraak", "domstol",
        "tribunal", "corte", "sąd", "soud", "न्याय", "বিচার", "நீதி",
        "న్యాయ", "ನ್ಯಾಯ", "adalet", "δικαιοσυνη",
    )),
    ("finance", (
        "finance", "financial", "treasury", "tax", "revenue", "budget",
        "finanz", "finanzen", "hacienda", "fisco", "impots", "impôts",
        "financas", "finanças", "skatt", "podatki", "belastingdienst",
        "finanse", "maliye", "vergi", "वित्त", "অর্থ", "நிதி", "ఆర్థిక",
        "ಹಣಕಾಸು", "maliye",
    )),
    ("police", (
        "police", "policia", "policía", "polizei", "policie", "politi",
        "policija", "policja", "politie", "poliisi", "politsei",
        "gendarmerie", "carabinieri", "पुलिस", "পুলিশ", "காவல்",
    )),
    ("defence", (
        "defence", "defense", "defensa", "defesa", "verteidigung",
        "obrona", "forsvaret", "defensie", "forsvar", "puolustus",
        "army", "navy", "air force", "military", "रक्षा", "প্রতিরক্ষা",
        "பாதுகாப்பு", "రక్షణ", "ರಕ್ಷಣೆ",
    )),
    ("transport", (
        "transport", "transporte", "trasporti", "transportes", "verkehr",
        "vervoer", "trafik", "liikenne", "railway", "rail", "road",
        "highway", "aviation", "shipping", "परिवहन", "পরিবহন",
        "போக்குவரத்து", "రవాణా", "ಸಾರಿಗೆ",
    )),
    ("environment", (
        "environment", "medio ambiente", "ambiente", "environnement",
        "umwelt", "milieu", "miljo", "miljø", "climate", "forest",
        "wildlife", "पर्यावरण", "পরিবেশ", "சுற்றுச்சூழல்", "పర్యావరణ",
        "ಪರಿಸರ",
    )),
    ("agriculture", (
        "agriculture", "agricultura", "landwirtschaft", "landbrug",
        "landbouw", "jordbruk", "maatalous", "rolnictwo", "farming",
        "farmers", "कृषि", "কৃষি", "வேளாண்மை", "వ్యవసాయ", "ಕೃಷಿ",
    )),
    ("social", (
        "social", "welfare", "pension", "benefit", "disability", "family",
        "children", "women", "youth", "elderly", "sozial", "previdencia",
        "समाज", "কল্যাণ", "நலன்", "సంక్షేమ", "ಕಲ್ಯಾಣ",
    )),
]


def resolves(host: str, timeout: float = 4.0) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        socket.getaddrinfo(host, 443)
        return True
    except Exception:  # noqa: BLE001
        return False


def fetch(url: str, timeout: float = 40.0) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, verify=False)
        if r.status_code == 200:
            return r.text
    except Exception:  # noqa: BLE001
        pass
    return ""


def sector_for(text: str, host: str) -> str:
    """Label a link by its text first, then its hostname."""
    t = text.lower()
    for sector, markers in SECTOR_TEXT_MARKERS:
        if any(m in t for m in markers):
            return sector
    h = host.lower()
    for sector, markers in SECTOR_TEXT_MARKERS:
        if any(m in h for m in markers):
            return sector
    return "general"


def harvest(country: str, url: str) -> dict[str, str]:
    """Map hostname -> sector for every government link on a ministry index."""
    found: dict[str, str] = {}
    body = fetch(url)
    if not body:
        return found

    tlds = discover.GOV_TLDS.get(country, [])
    soup = BeautifulSoup(body[:800000], "html.parser")
    for a in soup.find_all("a", href=True):
        host = urlparse(a["href"]).netloc
        if not host:
            continue
        h = discover.norm(host)
        if not any(discover.matches_tld(h, t) for t in tlds):
            continue
        text = a.get_text(" ", strip=True)[:120]
        found.setdefault(h, sector_for(text, h))
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--countries", default="")
    args = ap.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    existing = {r["domain_name"] for r in registry}

    targets = (
        [c.strip().upper() for c in args.countries.split(",") if c.strip()]
        if args.countries
        else sorted(MINISTRY_INDEXES)
    )

    print(f"countries: {len(targets)}")
    print(f"existing : {len(existing)}\n")

    total = 0
    for i, country in enumerate(targets, 1):
        before = len(existing)
        found: dict[str, str] = {}
        for url in MINISTRY_INDEXES.get(country, []):
            found.update(harvest(country, url))
            time.sleep(1.0)

        added = 0
        for h, sector in sorted(found.items()):
            if h in existing:
                # Backfill the sector on an existing row if it has none.
                for r in registry:
                    if r["domain_name"] == h and not r.get("sector"):
                        r["sector"] = sector
                        break
                continue
            ok, _ = clean.is_clean(h, country)
            if not ok:
                continue
            if not resolves(h):
                continue
            registry.append(
                {
                    "domain_name": h,
                    "country": country,
                    "tld": next(
                        (t for t in discover.GOV_TLDS.get(country, []) if discover.matches_tld(h, t)),
                        "",
                    ),
                    "sector": sector,
                    "source": "ministry_index",
                }
            )
            existing.add(h)
            added += 1

        total += added
        print(
            f"[{i}/{len(targets)}] {country}: found {len(found)}, +{added} "
            f"(total {len(existing)})",
            flush=True,
        )
        REGISTRY.write_text(
            json.dumps(sorted(registry, key=lambda r: r["domain_name"]), indent=1, ensure_ascii=False),
            encoding="utf-8",
        )

    print(f"\nadded {total} domains from ministry indexes")
    print(f"registry: {len(registry)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
