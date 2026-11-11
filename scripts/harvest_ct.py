"""Harvest real Indian government domains from Certificate Transparency logs.

Certificate Transparency (crt.sh) is a public, append-only record of every TLS
certificate ever issued. A domain appearing here provably exists and served
HTTPS at some point. This is a real, auditable discovery source - not a guess.

Queries the gov.in, nic.in, ac.in, res.in and edu.in namespaces, extracts every
unique hostname, and writes them with their certificate evidence.
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import requests

OUT = Path("data/fixtures/ct_domains.json")
UA = "Mozilla/5.0 (compatible; BharatGovAccess/1.0; research)"

NAMESPACES = ["%.gov.in", "%.nic.in", "%.ac.in", "%.res.in", "%.edu.in"]

GOV_TLDS = (
    ".gov.in", ".nic.in", ".ac.in", ".res.in", ".edu.in",
    ".drdo.in", ".cdac.in", ".ernet.in", ".mil.in", ".esic.in",
)

HOST_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$")


def is_gov(host: str) -> bool:
    return any(host.endswith(t) for t in GOV_TLDS)


def norm(host: str) -> str:
    host = host.lower().strip().rstrip(".")
    if host.startswith("*."):
        host = host[2:]
    if host.startswith("www."):
        host = host[4:]
    return host


def main() -> int:
    found: dict[str, dict] = {}
    t0 = time.time()

    for ns in NAMESPACES:
        url = f"https://crt.sh/?q={ns}&output=json"
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=180)
            if r.status_code != 200:
                print(f"  {ns}: HTTP {r.status_code}", flush=True)
                continue
            certs = r.json()
        except Exception as exc:  # noqa: BLE001
            print(f"  {ns}: {type(exc).__name__}", flush=True)
            continue

        before = len(found)
        for c in certs:
            for raw in str(c.get("name_value", "")).split("\n"):
                host = norm(raw)
                if not host or not is_gov(host) or not HOST_RE.match(host):
                    continue
                if len(host) > 100:
                    continue
                if host not in found:
                    found[host] = {
                        "domain_name": host,
                        "first_seen": c.get("not_before", ""),
                        "issuer": c.get("issuer_name", "")[:120],
                        "ct_source": ns,
                    }
        print(f"  {ns}: {len(certs)} certs -> +{len(found) - before} new domains", flush=True)

    rows = sorted(found.values(), key=lambda r: r["domain_name"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"\ntotal unique real gov domains from CT: {len(rows)}")
    print(f"elapsed: {time.time() - t0:.1f}s")
    print("sample:", [r["domain_name"] for r in rows[:8]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
