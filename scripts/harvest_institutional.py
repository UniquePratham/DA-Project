"""Harvest real institutional domains from official directories.

Sources:
  - UGC university directory (all recognised Indian universities)
  - eCourts estate (all court establishments)
  - india.gov.in sitemap (already harvested)

Every domain is extracted from a live HTTP response. Nothing is invented.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

OUT = Path("data/fixtures/institutional_domains.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36"

GOV_TLDS = (
    ".gov.in", ".nic.in", ".ac.in", ".res.in", ".edu.in", ".org.in",
    ".drdo.in", ".cdac.in", ".ernet.in", ".mil.in", ".esic.in",
)

DOMAIN_RE = re.compile(
    r"\b((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"(?:gov\.in|nic\.in|ac\.in|res\.in|edu\.in|org\.in|ernet\.in|drdo\.in|cdac\.in))\b",
    re.I,
)

PAGES = [
    "https://www.ugc.gov.in/university",
    "https://www.ugc.gov.in/university?page=1",
    "https://www.ugc.gov.in/university?page=2",
    "https://www.ugc.gov.in/university?page=3",
    "https://www.ugc.gov.in/university?page=4",
    "https://www.ugc.gov.in/university?page=5",
    "https://www.ugc.gov.in/colleges",
    "https://ecourts.gov.in/ecourts_home/",
    "https://www.india.gov.in/directory",
]


def norm(h: str) -> str:
    h = h.lower().strip().rstrip(".")
    if h.startswith("www."):
        h = h[4:]
    return h


def main() -> int:
    found: dict[str, str] = {}

    for url in PAGES:
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=45, verify=False)
            if r.status_code != 200:
                print(f"  {url}: HTTP {r.status_code}", flush=True)
                continue
        except Exception as exc:  # noqa: BLE001
            print(f"  {url}: {type(exc).__name__}", flush=True)
            continue

        before = len(found)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            m = DOMAIN_RE.search(a["href"])
            if m:
                found.setdefault(norm(m.group(1)), url)
        for m in DOMAIN_RE.finditer(r.text):
            found.setdefault(norm(m.group(1)), url)
        print(f"  {url[:60]:60s} +{len(found)-before}", flush=True)

    rows = [
        {"domain_name": d, "source_page": s}
        for d, s in sorted(found.items())
        if any(d.endswith(t) for t in GOV_TLDS) and len(d) < 100
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\ntotal institutional domains: {len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
