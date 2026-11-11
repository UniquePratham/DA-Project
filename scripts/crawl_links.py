"""Discover live portals by crawling outbound links from portals that responded.

This is the correct discovery method: start from domains that actually answered,
extract every outbound government link from their real HTML, and measure those.
A domain found this way is linked from a live government page, so it is far more
likely to be a real, current portal than a certificate-log entry or a guess.

Runs on the India node.
"""

from __future__ import annotations

import argparse
import csv
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
    ".gov.in", ".nic.in", ".ac.in", ".res.in", ".edu.in", ".org.in",
    ".drdo.in", ".cdac.in", ".ernet.in", ".mil.in", ".esic.in",
)

HOST_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$")


def is_gov(h: str) -> bool:
    return any(h.endswith(t) for t in GOV_TLDS)


def norm(h: str) -> str:
    h = h.lower().strip().rstrip(".")
    if h.startswith("www."):
        h = h[4:]
    return h


def links_from(domain: str, timeout: float = 20.0) -> set[str]:
    """Fetch one live portal and return every outbound gov domain it links to."""
    out: set[str] = set()
    for scheme in ("https", "http"):
        try:
            r = requests.get(
                f"{scheme}://{domain}",
                headers=HEADERS,
                timeout=timeout,
                verify=False,
                allow_redirects=True,
            )
            if r.status_code >= 400:
                continue
            soup = BeautifulSoup(r.text[:500000], "html.parser")
            for a in soup.find_all("a", href=True):
                host = urlparse(a["href"]).netloc
                if host:
                    h = norm(host)
                    if is_gov(h) and HOST_RE.match(h) and len(h) < 100:
                        out.add(h)
            return out
        except Exception:  # noqa: BLE001
            continue
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", required=True, help="CSV of reachable domains")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    seeds: list[str] = []
    with open(args.seeds, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if str(row.get("is_reachable", "")).lower() in ("true", "1"):
                seeds.append(row["domain_name"])
    if args.limit:
        seeds = seeds[: args.limit]
    print(f"crawling links from {len(seeds)} live portals", flush=True)

    found: dict[str, int] = {}
    done = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(links_from, d): d for d in seeds}
        for fut in as_completed(futs):
            try:
                for h in fut.result():
                    found[h] = found.get(h, 0) + 1
            except Exception:  # noqa: BLE001
                pass
            done += 1
            if done % 200 == 0:
                print(
                    f"  {done}/{len(seeds)} seeds, {len(found)} unique domains "
                    f"({done/max(1e-9, time.time()-t0):.1f}/s)",
                    flush=True,
                )

    seed_set = set(seeds)
    new = {h: c for h, c in found.items() if h not in seed_set}
    rows = [
        {"domain_name": h, "inbound_links": c}
        for h, c in sorted(new.items(), key=lambda kv: -kv[1])
    ]
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1)

    print(f"\nunique gov domains linked: {len(found)}")
    print(f"new (not already measured): {len(new)}")
    print(f"elapsed: {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
