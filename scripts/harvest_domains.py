"""Harvest real Indian government domains from live public directories.

Sources (all real, all fetched live from the India node):
  1. india.gov.in sitemap  - the National Portal's own index
  2. india.gov.in/directory - the National Portal's website directory
  3. Link crawl from those pages, restricted to government TLDs

Every domain emitted here was observed in a real HTTP response. Nothing is
generated. Output is deduplicated and validated against the government TLD
allow-list.
"""

from __future__ import annotations

import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": UA, "Accept-Language": "en-IN,en;q=0.9"}

GOV_TLDS = (
    ".gov.in",
    ".nic.in",
    ".ac.in",
    ".res.in",
    ".edu.in",
    ".drdo.in",
    ".cdac.in",
    ".ernet.in",
    ".mil.in",
    ".esic.in",
)

DOMAIN_RE = re.compile(
    r"\b((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"(?:gov\.in|nic\.in|ac\.in|res\.in|edu\.in|drdo\.in|cdac\.in|ernet\.in|mil\.in|esic\.in))\b",
    re.I,
)


def is_gov(host: str) -> bool:
    host = host.lower().split(":")[0]
    return any(host.endswith(t) for t in GOV_TLDS)


def norm(host: str) -> str:
    host = host.lower().strip().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    return host


def fetch(url: str, timeout: float = 25.0) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, verify=False)
        if r.status_code == 200:
            return r.text
    except Exception:  # noqa: BLE001
        pass
    return ""


def harvest_sitemap() -> set[str]:
    """Walk india.gov.in sitemap index and collect every gov domain mentioned."""
    found: set[str] = set()
    seeds = [
        "https://www.india.gov.in/sitemap.xml",
        "https://www.india.gov.in/sitemap_index.xml",
    ]
    queue: list[str] = []
    for s in seeds:
        body = fetch(s)
        if not body:
            continue
        # Sitemap index -> child sitemaps
        queue.extend(re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body))
        found.update(m.group(1) for m in DOMAIN_RE.finditer(body))

    print(f"  sitemap children: {len(queue)}", flush=True)
    for child in queue[:60]:
        body = fetch(child)
        if not body:
            continue
        found.update(m.group(1) for m in DOMAIN_RE.finditer(body))
        for loc in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body):
            host = urlparse(loc).netloc
            if host and is_gov(host):
                found.add(host)
    return found


def harvest_directory() -> set[str]:
    """Crawl india.gov.in/directory pagination and collect outbound gov links."""
    found: set[str] = set()
    pages = ["https://www.india.gov.in/directory"]
    pages += [f"https://www.india.gov.in/directory?page={i}" for i in range(0, 40)]

    def one(url: str) -> set[str]:
        out: set[str] = set()
        body = fetch(url)
        if not body:
            return out
        soup = BeautifulSoup(body, "html.parser")
        for a in soup.find_all("a", href=True):
            host = urlparse(a["href"]).netloc
            if host and is_gov(host):
                out.add(host)
        out.update(m.group(1) for m in DOMAIN_RE.finditer(body))
        return out

    with ThreadPoolExecutor(max_workers=6) as pool:
        for fut in as_completed([pool.submit(one, p) for p in pages]):
            found |= fut.result()
    return found


def main() -> int:
    t0 = time.time()
    print("harvesting india.gov.in sitemap...", flush=True)
    a = harvest_sitemap()
    print(f"  -> {len(a)} domains", flush=True)

    print("harvesting india.gov.in directory...", flush=True)
    b = harvest_directory()
    print(f"  -> {len(b)} domains", flush=True)

    all_domains = {norm(d) for d in (a | b) if is_gov(norm(d))}
    all_domains = {d for d in all_domains if "." in d and len(d) < 100}

    out = sorted(all_domains)
    with open("harvested_domains.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)

    print(f"\ntotal unique real gov domains: {len(out)}")
    print(f"elapsed: {time.time() - t0:.1f}s")
    print("sample:", out[:10])
    return 0


if __name__ == "__main__":
    sys.exit(main())
