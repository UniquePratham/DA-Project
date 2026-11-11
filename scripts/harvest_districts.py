"""Harvest the complete real district list for all 36 states/UTs.

Source: Wikipedia's "List of districts in India" tables, which mirror the
official LGD district list. Every district name is a real administrative unit.
Nothing is invented; this only fills in the 18 states missing from the seed.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://en.wikipedia.org/wiki/List_of_districts_in_India"
OUT = Path("data/fixtures/districts_full.json")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36"

resp = requests.get(URL, headers={"User-Agent": UA}, timeout=40)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# The page has one table per state/UT, each preceded by a heading.
districts: dict[str, list[str]] = {}

for table in soup.find_all("table", class_="wikitable"):
    # Find the nearest preceding heading for the state name.
    heading = None
    for prev in table.find_all_previous(["h2", "h3", "h4"]):
        text = prev.get_text(" ", strip=True)
        text = re.sub(r"\[.*?\]", "", text).strip()
        if text and not text.lower().startswith(("list of", "see also", "notes", "references")):
            heading = text
            break
    if not heading:
        continue

    names: list[str] = []
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all(["td", "th"])
        if len(cells) < 2:
            continue
        # District name is normally the second column.
        raw = cells[1].get_text(" ", strip=True)
        raw = re.sub(r"\[.*?\]", "", raw).strip()
        raw = re.sub(r"\s*\(.*?\)\s*$", "", raw).strip()
        if raw and 2 < len(raw) < 60 and not raw.isdigit():
            names.append(raw)

    if names:
        districts.setdefault(heading, [])
        for n in names:
            if n not in districts[heading]:
                districts[heading].append(n)

# Merge with the seed districts already in the repo.
seed = Path("scripts/generate_10k_dataset.py").read_text(encoding="utf-8")
block = re.search(r"DISTRICTS_MAP\s*=\s*\{(.*?)\n\}", seed, re.S)
if block:
    for state, lst in re.findall(r'"([^"]+)":\s*\[(.*?)\]', block.group(1), re.S):
        names = re.findall(r'"([^"]+)"', lst)
        if not names:
            continue
        districts.setdefault(state, [])
        for n in names:
            if n not in districts[state]:
                districts[state].append(n)

# Drop obvious non-state headings.
BAD = {"india", "state", "union territory", "notes", "references", "see also"}
districts = {
    k: v
    for k, v in districts.items()
    if k.lower() not in BAD and len(v) >= 1 and len(k) < 60
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(districts, indent=1, ensure_ascii=False), encoding="utf-8")

total = sum(len(v) for v in districts.values())
print(f"states/UTs: {len(districts)}")
print(f"total districts: {total}\n")
for k in sorted(districts):
    print(f"  {k:40s} {len(districts[k]):3d}")
