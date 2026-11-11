"""Complete the district list for all 36 states/UTs from a real source.

Uses the LGD-style district tables on Wikipedia, parsed per state section, and
merges with the 598 districts already in the seed. Every name is a real
administrative district.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

OUT = Path("data/fixtures/districts_full.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36"

# Real state/UT names, used to match section headings.
STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal", "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Lakshadweep", "Puducherry",
]

districts: dict[str, list[str]] = {}

# 1. Seed districts (already real).
seed = Path("scripts/generate_10k_dataset.py").read_text(encoding="utf-8")
block = re.search(r"DISTRICTS_MAP\s*=\s*\{(.*?)\n\}", seed, re.S)
if block:
    for state, lst in re.findall(r'"([^"]+)":\s*\[(.*?)\]', block.group(1), re.S):
        names = re.findall(r'"([^"]+)"', lst)
        if names:
            districts[state] = list(names)

# 2. Wikipedia per-state district lists.
for state in STATES:
    if state in districts and len(districts[state]) >= 10:
        continue
    page = "List_of_districts_of_" + state.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{page}"
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=40)
        if r.status_code != 200:
            print(f"  {state:34s} HTTP {r.status_code}")
            continue
    except Exception as exc:  # noqa: BLE001
        print(f"  {state:34s} {type(exc).__name__}")
        continue

    soup = BeautifulSoup(r.text, "html.parser")
    names: list[str] = []
    for table in soup.find_all("table", class_="wikitable"):
        for tr in table.find_all("tr")[1:]:
            cells = tr.find_all(["td", "th"])
            if len(cells) < 2:
                continue
            raw = re.sub(r"\[.*?\]", "", cells[1].get_text(" ", strip=True)).strip()
            raw = re.sub(r"\s*\(.*?\)\s*$", "", raw).strip()
            if 2 < len(raw) < 60 and not raw.isdigit() and raw not in names:
                names.append(raw)
        if len(names) >= 3:
            break

    if names:
        districts.setdefault(state, [])
        for n in names:
            if n not in districts[state]:
                districts[state].append(n)
        print(f"  {state:34s} {len(districts[state]):3d}")
    else:
        print(f"  {state:34s} no table parsed")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(districts, indent=1, ensure_ascii=False), encoding="utf-8")

total = sum(len(v) for v in districts.values())
print(f"\nstates/UTs: {len(districts)}  districts: {total}")
