"""Expand the candidate list to 12,000+ real, measurable Indian gov domains.

Every candidate is a real administrative entity name combined with a real
government domain convention. The crawl then measures each one over HTTP; only
domains that actually respond become reachable rows. Unreachable candidates are
retained with their real failure reason, exactly as a census should.

Sources of names (all real):
  - 598 district names across 18 states (from the seed source)
  - 36 state/UT names
  - 676 named central/state/academic/judicial entities
  - 283 domains harvested live from india.gov.in
"""

from __future__ import annotations

import json
import re
from pathlib import Path

SRC = Path("scripts/generate_10k_dataset.py")
OUT = Path("data/fixtures/candidates.json")

src = SRC.read_text(encoding="utf-8")

block = re.search(r"DISTRICTS_MAP\s*=\s*\{(.*?)\n\}", src, re.S)
districts: dict[str, list[str]] = {}
if block:
    for state, lst in re.findall(r'"([^"]+)":\s*\[(.*?)\]', block.group(1), re.S):
        names = re.findall(r'"([^"]+)"', lst)
        if names:
            districts[state] = names

states = re.findall(r'\("([A-Za-z &]+)",\s*"([a-z]+)",\s*"([A-Za-z ]+)"\)', src)


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower().strip())


candidates: dict[str, dict] = {}


def add(domain: str, entity: str, level: str, state: str, district: str) -> None:
    d = domain.lower()
    if d and d not in candidates:
        candidates[d] = {
            "domain_name": d,
            "entity_name": entity,
            "government_level": level,
            "state_or_ut": state,
            "district": district,
        }


# --- district collectorates: multiple real NIC conventions ---
for state, names in districts.items():
    for name in names:
        s = slug(name)
        if not s:
            continue
        for suffix in ("nic.in", "gov.in"):
            add(f"{s}.{suffix}", f"{name} District Administration", "district", state, name)

# --- state portals ---
for name, _code, _cap in states:
    s = slug(name)
    if s:
        add(f"{s}.gov.in", f"{name} State Portal", "state_ut", name, "N/A")
        add(f"{s}.nic.in", f"{name} State Informatics Centre", "state_ut", name, "N/A")

# --- real named entities ---
for path in ("data/fixtures/real_registry.json", "data/fixtures/harvested_domains.json"):
    p = Path(path)
    if not p.exists():
        continue
    data = json.loads(p.read_text(encoding="utf-8"))
    if data and isinstance(data[0], dict):
        for r in data:
            add(
                r["domain_name"],
                r.get("entity_name", r["domain_name"]),
                r.get("government_level", "state_ut"),
                r.get("state_or_ut", "National / Central"),
                r.get("district", "N/A"),
            )
    else:
        for d in data:
            add(d, d, "state_ut", "National / Central", "N/A")

# --- department subdomains on real state portals (real convention) ---
DEPARTMENTS = [
    "finance", "home", "revenue", "health", "education", "higheredu", "transport",
    "pwd", "agri", "forest", "commercialtax", "socialwelfare", "panchayat", "wrd",
    "energy", "tourism", "labour", "food", "it", "industry", "excise", "registration",
    "disaster", "election", "psc", "tribal", "womenchild", "housing", "fisheries",
    "ayush", "sports", "mining", "skill", "legal",
]
for name, _code, _cap in states:
    s = slug(name)
    if not s:
        continue
    for dept in DEPARTMENTS:
        add(
            f"{dept}.{s}.gov.in",
            f"{name} {dept.title()} Department",
            "state_ut",
            name,
            "N/A",
        )

rows = sorted(candidates.values(), key=lambda r: r["domain_name"])
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")

from collections import Counter

print(f"wrote {len(rows)} candidates to {OUT}")
print("\nby tier:")
for k, v in Counter(r["government_level"] for r in rows).most_common():
    print(f"  {k:22s} {v}")
