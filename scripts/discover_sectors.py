"""Sector-targeted domain discovery.

The TLD-only approach under-samples health, judiciary and finance, because
those ministries often live on a subdomain or a separate namespace rather than
the main government TLD. This script queries Certificate Transparency for
sector-specific patterns inside each country's government namespace, so the
registry covers the sectors the research claims to measure.

Patterns are queried as ``%.<sector>.<tld>`` and ``%.<sector>%`` where the
namespace allows it. Every result is still validated against the country's
restricted namespace and the public-portal filter, so a sector query cannot
smuggle in a commercial site.

Usage:
    python scripts/discover_sectors.py --sectors health,judiciary
    python scripts/discover_sectors.py --countries DE,IT,ES --sectors health
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from collections import Counter
from pathlib import Path

import requests

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
UA = "Mozilla/5.0 (compatible; BharatGovAccess/1.0; research)"

#: Sector -> the subdomain labels that indicate it, in the language each
#: government actually uses. English-only labels miss most of the world:
#: Italy's health ministry is ``salute.gov.it``, not ``health.gov.it``.
SECTOR_LABELS: dict[str, list[str]] = {
    "health": [
        # English
        "health", "healthcare", "hospital", "hospitals", "medical", "medicine",
        "clinic", "clinics", "publichealth", "cdc", "nhs",
        # Romance
        "salute", "sanita", "sanidad", "salud", "sante", "santé", "saude",
        "saúde", "sanitaire", "solidarites-sante",
        # Germanic
        "gesundheit", "gesundheitsamt", "gesundheitsministerium", "gezondheid",
        "volksgezondheid", "sundhed", "hälsa", "helse", "terveys",
        # Slavic
        "zdrowie", "zdrav", "zdravi", "zdravotnictvo", "zdravstvo", "zdravje",
        "zdravookhraneniye", "zdorovya",
        # Other
        "egeszseg", "egészség", "soglas", "veselība", "sveikata", "tervis",
        "sănătate", "zdrave", "υγεια", "υγεία", "sağlik", "sağlık",
    ],
    "education": [
        "edu", "education", "univ", "university", "universities", "school",
        "schools", "college", "colleges", "academy", "institute", "research",
        "student", "students", "campus", "library", "libraries",
        "education", "educacion", "educación", "educacao", "educação",
        "bildung", "onderwijs", "utbildning", "undervisning", "koulutus",
        "osvita", "obrazovanie", "edukacja", "vzdelavanie", "izobrazevanje",
        "haridus", "svietimas", "izglitiba", "invatamant", "obrazovanje",
        "egitim", "εκπαιδευση", "παιδεια",
    ],
    "judiciary": [
        "court", "courts", "justice", "judiciary", "judicial", "tribunal",
        "tribunals", "supreme", "supremecourt", "highcourt", "districtcourt",
        "judiciario", "judiciaire", "justiz", "gerichte", "rechtspraak",
        "domstol", "sady", "sud", "tribunale", "corte", "cortes",
        "justicia", "justiça", "justitie", "giustizia", "gericht",
        "soud", "sąd", "sudstvo", "sodstvo", "tiesa", "tiesa", "kohus",
        "mahkeme", "δικαστηριο", "bíróság",
    ],
    "finance": [
        "finance", "financial", "tax", "taxes", "taxation", "revenue",
        "treasury", "budget", "fiscal", "customs", "excise", "gst", "vat",
        "finanz", "finanzen", "impots", "impôts", "fisco", "hacienda",
        "financas", "finanças", "skatt", "podatki", "dan", "belastingdienst",
        "finans", "finanse", "finante", "finante", "ministerio-de-hacienda",
        "maliye", "vergi", "φορολογια",
    ],
    "police": [
        "police", "policia", "policía", "polizei", "policie", "politi",
        "policija", "policja", "sheriff", "constabulary", "gendarmerie",
        "carabinieri", "politie", "poliisi", "poliitsei", "policia",
        "policja", "politsei", "policie", "rendorseg", "αστυνομια",
    ],
    "defence": [
        "defence", "defense", "army", "navy", "airforce", "military",
        "mod", "mil", "defensa", "defesa", "verteidigung", "obrona",
        "forsvaret", "vojsko", "defensie", "forsvar", "puolustus",
        "oborona", "obrana", "obramba", "kaitse", "krašto apsauga",
        "aizsardziba", "aparare", "savunma", "αμυνα",
    ],
    "transport": [
        "transport", "transportation", "rail", "railway", "railways", "road",
        "roads", "highway", "highways", "traffic", "metro", "transit",
        "aviation", "airport", "airports", "port", "ports", "shipping",
        "verkehr", "transporte", "trasporti", "transportes", "vervoer",
        "trafik", "liikenne", "transporti", "transports", "ulaşım",
        "μεταφορες",
    ],
    "environment": [
        "environment", "environmental", "climate", "forest", "forests",
        "wildlife", "pollution", "ecology", "umwelt", "medioambiente",
        "ambiente", "environnement", "miljo", "miljø", "milieu", "ymparisto",
        "klima", "srodowisko", "zivotni", "okolje", "keskkond", "aplinka",
        "vides", "mediu", "cevre", "περιβαλλον",
    ],
    "agriculture": [
        "agriculture", "agricultural", "agri", "farming", "farmers", "crop",
        "crops", "livestock", "fisheries", "landwirtschaft", "agricultura",
        "landbrug", "landbouw", "jordbruk", "maatalous", "rolnictwo",
        "zemedelstvi", "kmetijstvo", "pollumajandus", "zemes ukis",
        "lauksaimnieciba", "agricultura", "tarim", "γεωργια",
    ],
    "social": [
        "social", "welfare", "pension", "pensions", "benefits", "disability",
        "family", "families", "children", "youth", "elderly", "socialsecurity",
        "sozial", "seguridadsocial", "previdencia", "sociale", "socialezekerheid",
        "socialforsikring", "sosiaal", "sotsiaal", "socjalna", "socialni",
        "socialna", "sotsiaal", "sociālā", "sociala", "sosyal", "κοινωνικη",
    ],
}


def fetch_ct(query: str, attempts: int = 3) -> list[dict]:
    url = f"https://crt.sh/?q={query}&output=json"
    for i in range(attempts):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=240)
            if r.status_code == 200 and r.text.strip().startswith("["):
                return r.json()
            if r.status_code == 404:
                return []
        except Exception:  # noqa: BLE001
            pass
        time.sleep(5 * (i + 1))
    return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sectors", default="health,judiciary,finance")
    ap.add_argument("--countries", default="")
    ap.add_argument("--max-labels", type=int, default=6)
    args = ap.parse_args()

    sectors = [s.strip() for s in args.sectors.split(",") if s.strip()]
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    existing = {r["domain_name"] for r in registry}

    by_country = Counter(r["country"] for r in registry)
    if args.countries:
        targets = [c.strip().upper() for c in args.countries.split(",") if c.strip()]
    else:
        targets = sorted(by_country)

    print(f"sectors: {sectors}")
    print(f"countries: {len(targets)}")
    print(f"existing: {len(existing)} domains\n")

    added = 0
    for country in targets:
        tlds = discover.GOV_TLDS.get(country, [])
        if not tlds:
            continue
        before = len(existing)
        for sector in sectors:
            labels = SECTOR_LABELS.get(sector, [])[: args.max_labels]
            for tld in tlds:
                for label in labels:
                    query = f"%25.{label}.{tld}"
                    certs = fetch_ct(query)
                    if not certs:
                        continue
                    for c in certs:
                        for field in ("name_value", "common_name"):
                            for raw in str(c.get(field, "")).split("\n"):
                                h = discover.norm(raw)
                                if not h or not discover.HOST_RE.match(h) or len(h) > 100:
                                    continue
                                if not discover.matches_tld(h, tld):
                                    continue
                                ok, _reason = clean.is_clean(h, country)
                                if not ok:
                                    continue
                                if h in existing:
                                    continue
                                registry.append(
                                    {
                                        "domain_name": h,
                                        "country": country,
                                        "tld": tld,
                                        "sector": sector,
                                        "first_seen": c.get("not_before", ""),
                                        "source": "certificate_transparency_sector",
                                    }
                                )
                                existing.add(h)
        delta = len(existing) - before
        added += delta
        print(f"  {country}: +{delta} (total {len(existing)})", flush=True)

        REGISTRY.write_text(
            json.dumps(sorted(registry, key=lambda r: r["domain_name"]), indent=1, ensure_ascii=False),
            encoding="utf-8",
        )

    print(f"\nadded {added} sector-targeted domains")
    print(f"registry now: {len(registry)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
