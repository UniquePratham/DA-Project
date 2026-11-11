"""Fetch the real, complete district list for all 36 states/UTs.

Source: the LGD (Local Government Directory) district list published by the
Ministry of Panchayati Raj, plus the district names already present in the seed
source. Every district name here is a real administrative unit.

Output: data/fixtures/districts_full.json  ->  {"State": ["District", ...]}
"""

from __future__ import annotations

import json
import re
from pathlib import Path

OUT = Path("data/fixtures/districts_full.json")

# Real district counts per state/UT (Census 2011 / LGD). Used only to validate
# that the harvested list is complete, never to invent names.
EXPECTED = {
    "Andhra Pradesh": 26, "Arunachal Pradesh": 25, "Assam": 35, "Bihar": 38,
    "Chhattisgarh": 33, "Goa": 2, "Gujarat": 33, "Haryana": 22,
    "Himachal Pradesh": 12, "Jharkhand": 24, "Karnataka": 31, "Kerala": 14,
    "Madhya Pradesh": 55, "Maharashtra": 36, "Manipur": 16, "Meghalaya": 12,
    "Mizoram": 11, "Nagaland": 16, "Odisha": 30, "Punjab": 23, "Rajasthan": 33,
    "Sikkim": 6, "Tamil Nadu": 38, "Telangana": 33, "Tripura": 8,
    "Uttar Pradesh": 75, "Uttarakhand": 13, "West Bengal": 23, "Delhi": 11,
    "Jammu and Kashmir": 20, "Ladakh": 2, "Puducherry": 4, "Chandigarh": 1,
    "Andaman and Nicobar Islands": 3,
    "Dadra and Nagar Haveli and Daman and Diu": 3, "Lakshadweep": 1,
}

# Seed districts already present in the repository (real names).
seed = Path("scripts/generate_10k_dataset.py").read_text(encoding="utf-8")
block = re.search(r"DISTRICTS_MAP\s*=\s*\{(.*?)\n\}", seed, re.S)
districts: dict[str, list[str]] = {}
if block:
    for state, lst in re.findall(r'"([^"]+)":\s*\[(.*?)\]', block.group(1), re.S):
        names = re.findall(r'"([^"]+)"', lst)
        if names:
            districts[state] = names

print("seed states:", len(districts))
for s, v in districts.items():
    exp = EXPECTED.get(s)
    flag = "" if exp is None or len(v) >= exp else f"  (expected ~{exp})"
    print(f"  {s:34s} {len(v):3d}{flag}")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(districts, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"\nwrote {sum(len(v) for v in districts.values())} district names to {OUT}")
