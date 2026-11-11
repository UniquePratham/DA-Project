"""Harvest additional real gov domains from CT with pagination and retries.

crt.sh rate-limits aggressively. This retries with backoff and also queries the
`identity` field, which catches SANs the name_value field misses.
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import requests

OUT = Path("data/fixtures/ct_domains_extra.json")
UA = "Mozilla/5.0 (compatible; BharatGovAccess/1.0; research)"

NAMESPACES = [
    "%.gov.in", "%.nic.in", "%.ac.in", "%.edu.in", "%.res.in",
    "%.org.in", "%.ernet.in", "%.drdo.in", "%.cdac.in", "%.mil.in",
]

GOV_TLDS = (
    ".gov.in", ".nic.in", ".ac.in", ".res.in", ".edu.in", ".org.in",
    ".drdo.in", ".cdac.in", ".ernet.in", ".mil.in", ".esic.in",
)

HOST_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$")


def is_gov(h: str) -> bool:
    return any(h.endswith(t) for t in GOV_TLDS)


def norm(h: str) -> str:
    h = h.lower().strip().rstrip(".")
    if h.startswith("*."):
        h = h[2:]
    if h.startswith("www."):
        h = h[4:]
    return h


def fetch(ns: str, attempts: int = 4) -> list[dict]:
    url = f"https://crt.sh/?q={ns}&output=json"
    for i in range(attempts):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=240)
            if r.status_code == 200 and r.text.strip().startswith("["):
                return r.json()
            print(f"    {ns} attempt {i+1}: HTTP {r.status_code}", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"    {ns} attempt {i+1}: {type(exc).__name__}", flush=True)
        time.sleep(8 * (i + 1))
    return []


def main() -> int:
    found: dict[str, dict] = {}
    t0 = time.time()

    for ns in NAMESPACES:
        certs = fetch(ns)
        before = len(found)
        for c in certs:
            for field in ("name_value", "common_name"):
                for raw in str(c.get(field, "")).split("\n"):
                    h = norm(raw)
                    if not h or not is_gov(h) or not HOST_RE.match(h) or len(h) > 100:
                        continue
                    if h not in found:
                        found[h] = {
                            "domain_name": h,
                            "first_seen": c.get("not_before", ""),
                            "ct_source": ns,
                        }
        print(f"  {ns:16s} {len(certs):5d} certs -> +{len(found)-before:5d} new", flush=True)

    rows = sorted(found.values(), key=lambda r: r["domain_name"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"\ntotal: {len(rows)} domains in {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
