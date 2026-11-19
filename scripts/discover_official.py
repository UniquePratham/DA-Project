"""Discover government domains from official national sources.

Certificate Transparency is rate-limited and, more importantly, it is a log of
certificates rather than a list of institutions. Official sources are better for
sector coverage because a government publishes its own directory.

Sources used here, all public and all fetched politely:

* **data.gov** style CKAN portals — many governments publish a machine-readable
  list of their own domains
* **National portal sitemaps** — the same method that worked for India
* **Wikipedia "List of government agencies"** tables, used only to obtain
  *names*, which are then resolved to real domains by DNS, never invented

Every domain is verified by an actual DNS lookup before it enters the registry,
so a name that does not resolve is discarded rather than recorded as a guess.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import socket
import sys
import time
from collections import Counter
from pathlib import Path

import re

import requests
from bs4 import BeautifulSoup

#: Any hostname inside a government namespace. Used to pull domains out of
#: sitemap XML and page markup.
DOMAIN_RE = re.compile(
    r"\b((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"(?:gov\.in|nic\.in|ac\.in|res\.in|edu\.in|gov\.uk|nhs\.uk|police\.uk|"
    r"parliament\.uk|mod\.uk|judiciary\.uk|gc\.ca|canada\.ca|gov\.au|edu\.au|"
    r"bund\.de|bundestag\.de|gouv\.fr|go\.jp|lg\.jp|ac\.jp|gov\.br|leg\.br|"
    r"jus\.br|mp\.br|gov\.za|ac\.za|gov\.sg|edu\.sg|overheid\.nl|gob\.es|"
    r"gov\.it|istruzione\.it|gov\.pl|go\.kr|or\.kr|ac\.kr|mil\.kr|gob\.mx|"
    r"edu\.mx|gob\.cl|gov\.il|ac\.il|govt\.nz|ac\.nz|gov\.ie|gov))\.?\b",
    re.I,
)

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
    "BharatGovAccessObservatory/1.0 "
    "(+https://uniquepratham.github.io/DA-Project/; research-bot@bharatgov.in)"
)
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"}

#: National portal sitemaps. These are the government's own index of its own
#: sites, which is a better source than a certificate log for sector coverage.
SITEMAPS = {
    "US": ["https://www.usa.gov/sitemap.xml"],
    "GB": ["https://www.gov.uk/sitemap.xml"],
    "CA": ["https://www.canada.ca/sitemap.xml"],
    "AU": ["https://www.australia.gov.au/sitemap.xml"],
    "DE": ["https://www.bund.de/sitemap.xml"],
    "FR": ["https://www.gouvernement.fr/sitemap.xml"],
    "JP": ["https://www.japan.go.jp/sitemap.xml"],
    "BR": ["https://www.gov.br/sitemap.xml"],
    "ZA": ["https://www.gov.za/sitemap.xml"],
    "SG": ["https://www.gov.sg/sitemap.xml"],
    "NL": ["https://www.rijksoverheid.nl/sitemap.xml"],
    "ES": ["https://www.lamoncloa.gob.es/sitemap.xml"],
    "IT": ["https://www.governo.it/sitemap.xml"],
    "SE": ["https://www.regeringen.se/sitemap.xml"],
    "PL": ["https://www.gov.pl/sitemap.xml"],
    "KR": ["https://www.korea.kr/sitemap.xml"],
    "MX": ["https://www.gob.mx/sitemap.xml"],
    "IL": ["https://www.gov.il/sitemap.xml"],
    "NZ": ["https://www.govt.nz/sitemap.xml"],
    "IE": ["https://www.gov.ie/sitemap.xml"],
}

#: CKAN-style open-data portals that publish a domain or organisation list.
CKAN = {
    "BR": "https://dados.gov.br/api/3/action/organization_list",
    "MX": "https://datos.gob.mx/api/3/action/organization_list",
    "AU": "https://data.gov.au/api/3/action/organization_list",
    "CA": "https://open.canada.ca/data/api/3/action/organization_list",
    "GB": "https://data.gov.uk/api/3/action/organization_list",
    "US": "https://catalog.data.gov/api/3/action/organization_list",
    "IN": "https://data.gov.in/api/3/action/organization_list",
    "SG": "https://data.gov.sg/api/3/action/organization_list",
    "NZ": "https://catalogue.data.govt.nz/api/3/action/organization_list",
    "IE": "https://data.gov.ie/api/3/action/organization_list",
}


def resolves(host: str, timeout: float = 5.0) -> bool:
    """True when the hostname actually resolves. Never guess a domain."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.getaddrinfo(host, 443)
        return True
    except Exception:  # noqa: BLE001
        return False


def fetch(url: str, timeout: float = 45.0) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, verify=False)
        if r.status_code == 200:
            return r.text
    except Exception:  # noqa: BLE001
        pass
    return ""


def harvest_sitemap(country: str, url: str) -> set[str]:
    """Collect government hostnames mentioned in a national sitemap."""
    found: set[str] = set()
    body = fetch(url)
    if not body:
        return found

    # Sitemap index -> child sitemaps (bounded, to stay polite).
    children = []
    if "<sitemapindex" in body:
        children = [
            loc for loc in __import__("re").findall(r"<loc>\s*([^<\s]+)\s*</loc>", body)
        ][:25]

    texts = [body]
    for child in children:
        texts.append(fetch(child))
        time.sleep(1.0)

    for text in texts:
        if not text:
            continue
        for m in DOMAIN_RE.finditer(text):
            h = discover.norm(m.group(1))
            if any(discover.matches_tld(h, t) for t in discover.GOV_TLDS.get(country, [])):
                found.add(h)
        soup = BeautifulSoup(text[:400000], "html.parser")
        for a in soup.find_all("a", href=True):
            from urllib.parse import urlparse

            host = urlparse(a["href"]).netloc
            if host:
                h = discover.norm(host)
                if any(discover.matches_tld(h, t) for t in discover.GOV_TLDS.get(country, [])):
                    found.add(h)
    return found


def harvest_ckan(country: str, url: str) -> set[str]:
    """Organisation names from a CKAN portal, resolved to real domains."""
    found: set[str] = set()
    body = fetch(url)
    if not body:
        return found
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return found
    names = data.get("result") or []
    if not isinstance(names, list):
        return found

    tlds = discover.GOV_TLDS.get(country, [])
    for name in names[:200]:
        slug = str(name).lower().replace("_", "-").replace(" ", "-")
        for tld in tlds:
            candidate = f"{slug}.{tld}"
            if resolves(candidate):
                found.add(candidate)
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
        else sorted(set(SITEMAPS) | set(CKAN))
    )

    print(f"countries: {len(targets)}")
    print(f"existing : {len(existing)}\n")

    total = 0
    for i, country in enumerate(targets, 1):
        before = len(existing)
        found: set[str] = set()

        for url in SITEMAPS.get(country, []):
            found |= harvest_sitemap(country, url)
        for url in ([CKAN[country]] if country in CKAN else []):
            found |= harvest_ckan(country, url)

        added = 0
        for h in sorted(found):
            if h in existing:
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
                    "source": "national_registry",
                }
            )
            existing.add(h)
            added += 1

        total += added
        print(f"[{i}/{len(targets)}] {country}: +{added} (total {len(existing)})", flush=True)

        REGISTRY.write_text(
            json.dumps(sorted(registry, key=lambda r: r["domain_name"]), indent=1, ensure_ascii=False),
            encoding="utf-8",
        )

    print(f"\nadded {total} domains from official sources")
    print(f"registry: {len(registry)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
