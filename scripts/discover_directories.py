"""Discover government domains from agency directories.

A national portal's sitemap lists its own pages, not the whole government. What
does enumerate agencies is a directory page, and most governments publish one.

This script harvests those directories, extracts every outbound government link,
and verifies each by DNS before recording it. A name that does not resolve is
discarded rather than guessed.

Sources are the official "A-Z of government" style indexes. Where a country has
no such index, it is skipped rather than approximated.
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

#: Official agency directories. Each entry is a page that links to many
#: government bodies, which is what a sitemap does not do.
DIRECTORIES: dict[str, list[str]] = {
    "US": [
        "https://www.usa.gov/agency-index",
        "https://www.usa.gov/federal-agencies/a",
        "https://www.usa.gov/state-government",
    ],
    "GB": [
        "https://www.gov.uk/government/organisations",
        "https://www.gov.uk/find-local-council",
    ],
    "CA": [
        "https://www.canada.ca/en/government/dept.html",
        "https://www.canada.ca/en/government/agencies.html",
    ],
    "AU": [
        "https://www.australia.gov.au/departments-and-agencies",
        "https://www.directory.gov.au/",
    ],
    "DE": [
        "https://www.bund.de/DE/Behoerden/behoerden_node.html",
        "https://www.bundesregierung.de/breg-de/bundesregierung/bundesministerien",
    ],
    "FR": [
        "https://www.gouvernement.fr/composition-du-gouvernement",
        "https://www.service-public.fr/",
    ],
    "JP": [
        "https://www.japan.go.jp/links/",
        "https://www.kantei.go.jp/jp/link/index.html",
    ],
    "BR": [
        "https://www.gov.br/pt-br/orgaos-do-governo",
        "https://www.gov.br/pt-br/canais_atendimento",
    ],
    "ZA": [
        "https://www.gov.za/about-government/government-system",
        "https://www.gov.za/directory",
    ],
    "SG": [
        "https://www.gov.sg/contact-us",
        "https://www.gov.sg/government-websites",
    ],
    "NL": [
        "https://www.rijksoverheid.nl/regering/ministeries",
        "https://www.overheid.nl/",
    ],
    "ES": [
        "https://www.lamoncloa.gob.es/gobierno/Paginas/index.aspx",
        "https://administracion.gob.es/",
    ],
    "IT": [
        "https://www.governo.it/it/i-governi-dal-1943-ad-oggi/i-governi-nelle-legislature/19278",
        "https://www.italia.it/",
    ],
    "SE": [
        "https://www.regeringen.se/sveriges-regering/",
        "https://www.myndighetsregistret.se/",
    ],
    "PL": [
        "https://www.gov.pl/web/gov/ministerstwa",
        "https://www.gov.pl/",
    ],
    "KR": [
        "https://www.korea.kr/archive/expDocList.do",
        "https://www.gov.kr/",
    ],
    "MX": [
        "https://www.gob.mx/agencias",
        "https://www.gob.mx/",
    ],
    "IL": [
        "https://www.gov.il/he/departments",
        "https://www.gov.il/en/departments",
    ],
    "NZ": [
        "https://www.govt.nz/organisations/",
        "https://www.publicservice.govt.nz/",
    ],
    "IE": [
        "https://www.gov.ie/en/organisation/",
        "https://www.gov.ie/en/",
    ],
    "IN": [
        "https://www.india.gov.in/directory",
        "https://www.india.gov.in/website-directory",
    ],
}


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


def harvest(country: str, url: str) -> set[str]:
    """Every government hostname linked from a directory page."""
    found: set[str] = set()
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
        if any(discover.matches_tld(h, t) for t in tlds):
            found.add(h)

    # Also catch hostnames written as text rather than links.
    for m in re.finditer(
        r"\b((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,})\b", body[:400000], re.I
    ):
        h = discover.norm(m.group(1))
        if any(discover.matches_tld(h, t) for t in tlds):
            found.add(h)
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
        else sorted(DIRECTORIES)
    )

    print(f"countries: {len(targets)}")
    print(f"existing : {len(existing)}\n")

    total = 0
    for i, country in enumerate(targets, 1):
        before = len(existing)
        found: set[str] = set()
        for url in DIRECTORIES.get(country, []):
            found |= harvest(country, url)
            time.sleep(1.5)

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
                    "source": "agency_directory",
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

    print(f"\nadded {total} domains from agency directories")
    print(f"registry: {len(registry)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
