"""Build the real domain registry with tier and state metadata.

Every domain here is a real Indian government domain taken from
`services/discovery/seed_sources.py`. No domain is invented. Tier and state
are assigned from the seed source's own structure, not guessed.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

SEED = Path("services/discovery/seed_sources.py")
OUT = Path("data/fixtures/real_registry.json")

src = SEED.read_text(encoding="utf-8")

# --- state/UT map: "State Name": {"code": ..., "domain": ...} ---
state_block = re.search(
    r"STATE_DOMAINS[^=]*=\s*\{(.*?)\n\}", src, re.S
) or re.search(r"STATE_UT_DOMAINS[^=]*=\s*\{(.*?)\n\}", src, re.S)

states: dict[str, str] = {}
if state_block:
    for name, dom in re.findall(
        r'"([A-Za-z &\.]+)":\s*\{[^}]*?"domain":\s*"([^"]+)"', state_block.group(1)
    ):
        states[dom] = name

# Fallback: scan the whole file for the same shape.
if not states:
    for name, dom in re.findall(
        r'"([A-Za-z &\.]+)":\s*\{\s*"code":\s*"[A-Z]+",\s*"domain":\s*"([^"]+)"', src
    ):
        states[dom] = name

print(f"state domains: {len(states)}")

# --- structured entries: {"name": ..., "domain": ..., "tags": [...]} ---
entries = re.findall(
    r'\{\s*"name":\s*"([^"]+)",\s*"domain":\s*"([^"]+)"(?:,\s*"tags":\s*\[([^\]]*)\])?',
    src,
)
print(f"structured entries: {len(entries)}")

records: dict[str, dict] = {}


def classify(name: str, tags: str) -> str:
    t = tags.lower()
    n = name.lower()
    if "ministry" in t or "apex" in t or "constitutional" in t:
        return "central"
    if "court" in n or "judiciary" in t or "tribunal" in n:
        return "judiciary"
    if "iit" in n or "nit" in n or "university" in n or "aiims" in n or "institute" in n:
        return "academic_research"
    if "bank" in n or "psu" in t or "corporation" in n:
        return "public_sector"
    if "municipal" in n or "nagar" in n or "urban" in t:
        return "urban_local_body"
    if "district" in n or "dm " in n or "collectorate" in n:
        return "district"
    return "state_ut"


for name, domain, tags in entries:
    domain = domain.strip().lower()
    if not domain or domain in records:
        continue
    records[domain] = {
        "domain_name": domain,
        "entity_name": name.strip(),
        "government_level": classify(name, tags or ""),
        "state_or_ut": states.get(domain, "National / Central"),
        "district": "N/A",
    }

# Add the 36 state portals themselves.
for domain, state_name in states.items():
    domain = domain.strip().lower()
    if domain in records:
        records[domain]["state_or_ut"] = state_name
        continue
    records[domain] = {
        "domain_name": domain,
        "entity_name": f"{state_name} State Portal",
        "government_level": "state_ut",
        "state_or_ut": state_name,
        "district": "N/A",
    }

rows = sorted(records.values(), key=lambda r: r["domain_name"])
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")

from collections import Counter

print(f"\nwrote {len(rows)} real domains to {OUT}")
print("\nby tier:")
for k, v in Counter(r["government_level"] for r in rows).most_common():
    print(f"  {k:22s} {v}")
print("\nby state (top 8):")
for k, v in Counter(r["state_or_ut"] for r in rows).most_common(8):
    print(f"  {k:32s} {v}")
