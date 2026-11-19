"""Sector-targeted discovery with backoff and verification.

The first attempt at this returned zero for every country because crt.sh was
rate-limiting with 502s and the failures were swallowed. This version:

* retries with exponential backoff and reports failures loudly
* verifies each query actually returned certificates before trusting it
* records which query produced each domain, so coverage can be audited
* writes progress after every country so a crash does not lose work

Labels are multilingual because English-only labels miss most of the world:
Italy's health ministry is ``salute.gov.it``, France's is ``sante.gouv.fr``.
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
LOG = REPO / "data" / "fixtures" / "sector_discovery_log.json"

UA = (
    "CivicWebObservatory/1.0 "
    "(+https://uniquepratham.github.io/DA-Project/; research-bot@civicweb.in)"
)

#: Sector -> subdomain labels in the languages governments actually use.
SECTOR_LABELS: dict[str, list[str]] = {
    "health": [
        "salute", "sante", "santé", "sanidad", "salud", "saude", "saúde",
        "gesundheit", "health", "nhs", "zdrowie", "zdrav", "zdravi",
        "zdravotnictvo", "zdravstvo", "egeszseg", "egészség", "gezondheid",
        "volksgezondheid", "sundhed", "hälsa", "helse", "terveys",
        "soglas", "veseliba", "sveikata", "sanita", "moh", "doh", "mohfw",
        "hospital", "hospitals", "medic", "medical", "clinic", "clinics",
        "publichealth", "cdc", "nha",
    ],
    "judiciary": [
        "justice", "justicia", "justiça", "justiz", "giustizia", "justitie",
        "court", "courts", "judiciary", "judicial", "tribunal", "tribunals",
        "supreme", "supremecourt", "highcourt", "districtcourt", "corte",
        "cortes", "gerichte", "rechtspraak", "domstol", "sady", "sud",
        "soud", "sąd", "sudstvo", "sodstvo", "tiesa", "kohus", "mahkeme",
        "judiciario", "judiciaire", "bíróság",
    ],
    "finance": [
        "finance", "finanz", "finanzen", "finanzas", "financas", "finanças",
        "impots", "impôts", "fisco", "hacienda", "tax", "taxes", "taxation",
        "revenue", "treasury", "budget", "fiscal", "customs", "excise",
        "gst", "vat", "skatt", "podatki", "belastingdienst", "finans",
        "finanse", "finante", "maliye", "vergi",
    ],
    "education": [
        "education", "educacion", "educación", "educacao", "educação",
        "bildung", "onderwijs", "utbildning", "undervisning", "koulutus",
        "edukacja", "vzdelavanie", "izobrazevanje", "haridus", "svietimas",
        "izglitiba", "invatamant", "obrazovanje", "egitim", "edu",
        "university", "universities", "school", "schools", "college",
        "academy", "institute", "research", "student", "campus", "library",
    ],
    "police": [
        "police", "policia", "policía", "polizei", "policie", "politi",
        "policija", "policja", "politie", "poliisi", "politsei",
        "gendarmerie", "carabinieri", "constabulary", "sheriff",
        "rendorseg",
    ],
    "defence": [
        "defence", "defense", "defensa", "defesa", "verteidigung",
        "obrona", "forsvaret", "vojsko", "defensie", "forsvar",
        "puolustus", "oborona", "obrana", "obramba", "kaitse",
        "aparare", "savunma", "army", "navy", "airforce", "military",
    ],
    "transport": [
        "transport", "transporte", "trasporti", "transportes", "verkehr",
        "vervoer", "trafik", "liikenne", "transporti", "transports",
        "transportation", "rail", "railway", "railways", "road", "roads",
        "highway", "highways", "traffic", "metro", "transit", "aviation",
        "airport", "airports", "port", "ports", "shipping",
    ],
    "environment": [
        "environment", "environmental", "medioambiente", "ambiente",
        "environnement", "umwelt", "milieu", "miljo", "miljø", "ymparisto",
        "klima", "srodowisko", "zivotni", "okolje", "keskkond", "aplinka",
        "vides", "mediu", "cevre", "climate", "forest", "forests",
        "wildlife", "pollution", "ecology",
    ],
    "agriculture": [
        "agriculture", "agricultura", "landwirtschaft", "landbrug",
        "landbouw", "jordbruk", "maatalous", "rolnictwo", "zemedelstvi",
        "kmetijstvo", "pollumajandus", "lauksaimnieciba", "tarim",
        "agricultural", "agri", "farming", "farmers", "crop", "crops",
        "livestock", "fisheries",
    ],
    "social": [
        "social", "sozial", "sociale", "socialezekerheid", "socialforsikring",
        "sosiaal", "sotsiaal", "socjalna", "socialni", "socialna",
        "sociala", "sosyal", "welfare", "pension", "pensions", "benefits",
        "disability", "family", "families", "children", "youth", "elderly",
        "socialsecurity", "seguridadsocial", "previdencia",
    ],
}


def fetch_ct(query: str, attempts: int = 5) -> tuple[list[dict], str]:
    """Fetch a crt.sh query with backoff. Returns (certs, status).

    crt.sh rate-limits aggressively and returns 502 or an HTML error page
    rather than a 429, so a naive client sees "no results" when it is actually
    being throttled. The backoff here is deliberately long and the status is
    returned so the caller can distinguish "empty" from "throttled".
    """
    url = f"https://crt.sh/?q={query}&output=json"
    last = ""
    for i in range(attempts):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=180)
            if r.status_code == 200:
                text = r.text.strip()
                if text.startswith("["):
                    return r.json(), "ok"
                if text in ("", "[]"):
                    return [], "empty"
                last = f"non-json ({text[:40]})"
            elif r.status_code == 404:
                return [], "not-found"
            elif r.status_code in (502, 503, 504):
                last = f"HTTP {r.status_code} (throttled)"
            else:
                last = f"HTTP {r.status_code}"
        except Exception as exc:  # noqa: BLE001
            last = type(exc).__name__
        # Long, growing backoff: 20s, 40s, 80s, 160s.
        time.sleep(20 * (2**i))
    return [], f"failed: {last}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sectors", default="health,judiciary,finance")
    ap.add_argument("--countries", default="")
    ap.add_argument("--max-labels", type=int, default=10)
    ap.add_argument("--pause", type=float, default=2.0)
    args = ap.parse_args()

    sectors = [s.strip() for s in args.sectors.split(",") if s.strip()]
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    existing = {r["domain_name"] for r in registry}

    by_country = Counter(r["country"] for r in registry)
    if args.countries:
        targets = [c.strip().upper() for c in args.countries.split(",") if c.strip()]
    else:
        targets = sorted(by_country)

    print(f"sectors   : {sectors}")
    print(f"countries : {len(targets)}")
    print(f"existing  : {len(existing)} domains\n")

    log: list[dict] = []
    total_added = 0

    for ci, country in enumerate(targets, 1):
        tlds = discover.GOV_TLDS.get(country, [])
        if not tlds:
            continue
        before = len(existing)
        queries = 0
        hits = 0

        for sector in sectors:
            labels = SECTOR_LABELS.get(sector, [])[: args.max_labels]
            for tld in tlds:
                for label in labels:
                    query = f"%25.{label}.{tld}"
                    certs, status = fetch_ct(query)
                    queries += 1
                    if status.startswith("failed: HTTP 502") or "throttled" in status:
                        # crt.sh is throttling. Stop this country rather than
                        # burning backoff on every remaining label.
                        log.append(
                            {"country": country, "query": query, "status": status, "certs": 0}
                        )
                        print(f"  {country}: throttled, skipping remaining labels", flush=True)
                        break
                    if status != "ok":
                        log.append(
                            {"country": country, "query": query, "status": status, "certs": 0}
                        )
                        time.sleep(args.pause)
                        continue
                    hits += 1
                    added_here = 0
                    for c in certs:
                        for field in ("name_value", "common_name"):
                            for raw in str(c.get(field, "")).split("\n"):
                                h = discover.norm(raw)
                                if not h or not discover.HOST_RE.match(h) or len(h) > 100:
                                    continue
                                if not discover.matches_tld(h, tld):
                                    continue
                                ok, _ = clean.is_clean(h, country)
                                if not ok or h in existing:
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
                                added_here += 1
                    log.append(
                        {
                            "country": country,
                            "query": query,
                            "status": status,
                            "certs": len(certs),
                            "added": added_here,
                        }
                    )
                    time.sleep(args.pause)

        delta = len(existing) - before
        total_added += delta
        print(
            f"[{ci}/{len(targets)}] {country}: +{delta} "
            f"({queries} queries, {hits} returned certs, total {len(existing)})",
            flush=True,
        )

        REGISTRY.write_text(
            json.dumps(
                sorted(registry, key=lambda r: r["domain_name"]),
                indent=1,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        LOG.write_text(json.dumps(log, indent=1), encoding="utf-8")

    print(f"\nadded {total_added} sector-targeted domains")
    print(f"registry: {len(registry)}")
    failed = [e for e in log if e["status"] != "ok"]
    print(f"queries: {len(log)}, failed: {len(failed)}")
    if failed:
        print("sample failures:", failed[:5])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
