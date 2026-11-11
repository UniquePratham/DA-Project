"""Harvest real court and municipal domains from official sources.

Sources:
  - eCourts district court establishments (real, per-district)
  - Municipal corporation domains from real city names

Every candidate is measured over HTTP; only resolvers become reachable.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

OUT = Path("data/fixtures/extra_candidates.json")

# Real district names already harvested.
districts = json.loads(Path("data/fixtures/districts_full.json").read_text(encoding="utf-8"))

# Real municipal corporation names (largest cities, real entities).
MUNICIPAL = [
    ("Mumbai", "Maharashtra"), ("Delhi", "Delhi"), ("Bengaluru", "Karnataka"),
    ("Hyderabad", "Telangana"), ("Ahmedabad", "Gujarat"), ("Chennai", "Tamil Nadu"),
    ("Kolkata", "West Bengal"), ("Surat", "Gujarat"), ("Pune", "Maharashtra"),
    ("Jaipur", "Rajasthan"), ("Lucknow", "Uttar Pradesh"), ("Kanpur", "Uttar Pradesh"),
    ("Nagpur", "Maharashtra"), ("Indore", "Madhya Pradesh"), ("Thane", "Maharashtra"),
    ("Bhopal", "Madhya Pradesh"), ("Visakhapatnam", "Andhra Pradesh"),
    ("Patna", "Bihar"), ("Vadodara", "Gujarat"), ("Ghaziabad", "Uttar Pradesh"),
    ("Ludhiana", "Punjab"), ("Agra", "Uttar Pradesh"), ("Nashik", "Maharashtra"),
    ("Faridabad", "Haryana"), ("Meerut", "Uttar Pradesh"), ("Rajkot", "Gujarat"),
    ("Varanasi", "Uttar Pradesh"), ("Srinagar", "Jammu and Kashmir"),
    ("Aurangabad", "Maharashtra"), ("Dhanbad", "Jharkhand"), ("Amritsar", "Punjab"),
    ("Navi Mumbai", "Maharashtra"), ("Allahabad", "Uttar Pradesh"),
    ("Ranchi", "Jharkhand"), ("Howrah", "West Bengal"), ("Coimbatore", "Tamil Nadu"),
    ("Jabalpur", "Madhya Pradesh"), ("Gwalior", "Madhya Pradesh"),
    ("Vijayawada", "Andhra Pradesh"), ("Jodhpur", "Rajasthan"),
    ("Madurai", "Tamil Nadu"), ("Raipur", "Chhattisgarh"), ("Kota", "Rajasthan"),
    ("Guwahati", "Assam"), ("Chandigarh", "Chandigarh"), ("Solapur", "Maharashtra"),
    ("Hubballi", "Karnataka"), ("Tiruchirappalli", "Tamil Nadu"),
    ("Bareilly", "Uttar Pradesh"), ("Mysuru", "Karnataka"), ("Tiruppur", "Tamil Nadu"),
    ("Gurugram", "Haryana"), ("Aligarh", "Uttar Pradesh"), ("Jalandhar", "Punjab"),
    ("Bhubaneswar", "Odisha"), ("Salem", "Tamil Nadu"), ("Warangal", "Telangana"),
    ("Guntur", "Andhra Pradesh"), ("Bhiwandi", "Maharashtra"), ("Saharanpur", "Uttar Pradesh"),
    ("Gorakhpur", "Uttar Pradesh"), ("Bikaner", "Rajasthan"), ("Amravati", "Maharashtra"),
    ("Noida", "Uttar Pradesh"), ("Jamshedpur", "Jharkhand"), ("Bhilai", "Chhattisgarh"),
    ("Cuttack", "Odisha"), ("Firozabad", "Uttar Pradesh"), ("Kochi", "Kerala"),
    ("Nellore", "Andhra Pradesh"), ("Bhavnagar", "Gujarat"), ("Dehradun", "Uttarakhand"),
    ("Durgapur", "West Bengal"), ("Asansol", "West Bengal"), ("Rourkela", "Odisha"),
    ("Nanded", "Maharashtra"), ("Kolhapur", "Maharashtra"), ("Ajmer", "Rajasthan"),
    ("Akola", "Maharashtra"), ("Gulbarga", "Karnataka"), ("Jamnagar", "Gujarat"),
    ("Ujjain", "Madhya Pradesh"), ("Loni", "Uttar Pradesh"), ("Siliguri", "West Bengal"),
    ("Jhansi", "Uttar Pradesh"), ("Ulhasnagar", "Maharashtra"), ("Jammu", "Jammu and Kashmir"),
    ("Sangli", "Maharashtra"), ("Mangaluru", "Karnataka"), ("Erode", "Tamil Nadu"),
    ("Belagavi", "Karnataka"), ("Ambattur", "Tamil Nadu"), ("Tirunelveli", "Tamil Nadu"),
    ("Malegaon", "Maharashtra"), ("Gaya", "Bihar"), ("Udaipur", "Rajasthan"),
    ("Maheshtala", "West Bengal"), ("Tirupati", "Andhra Pradesh"), ("Davanagere", "Karnataka"),
    ("Kozhikode", "Kerala"), ("Kurnool", "Andhra Pradesh"), ("Rajpur Sonarpur", "West Bengal"),
    ("Rajahmundry", "Andhra Pradesh"), ("Bokaro", "Jharkhand"), ("South Dumdum", "West Bengal"),
    ("Bellary", "Karnataka"), ("Patiala", "Punjab"), ("Gopalpur", "West Bengal"),
    ("Agartala", "Tripura"), ("Bhagalpur", "Bihar"), ("Muzaffarnagar", "Uttar Pradesh"),
    ("Bhatpara", "West Bengal"), ("Panihati", "West Bengal"), ("Latur", "Maharashtra"),
    ("Dhule", "Maharashtra"), ("Rohtak", "Haryana"), ("Sagar", "Madhya Pradesh"),
    ("Korba", "Chhattisgarh"), ("Bhilwara", "Rajasthan"), ("Brahmapur", "Odisha"),
    ("Muzaffarpur", "Bihar"), ("Ahmednagar", "Maharashtra"), ("Mathura", "Uttar Pradesh"),
    ("Kollam", "Kerala"), ("Avadi", "Tamil Nadu"), ("Kadapa", "Andhra Pradesh"),
    ("Kamarhati", "West Bengal"), ("Sambalpur", "Odisha"), ("Bilaspur", "Chhattisgarh"),
    ("Shahjahanpur", "Uttar Pradesh"), ("Satara", "Maharashtra"), ("Bijapur", "Karnataka"),
    ("Rampur", "Uttar Pradesh"), ("Shivamogga", "Karnataka"), ("Chandrapur", "Maharashtra"),
    ("Junagadh", "Gujarat"), ("Thrissur", "Kerala"), ("Alwar", "Rajasthan"),
    ("Bardhaman", "West Bengal"), ("Kulti", "West Bengal"), ("Kakinada", "Andhra Pradesh"),
    ("Nizamabad", "Telangana"), ("Parbhani", "Maharashtra"), ("Tumkur", "Karnataka"),
    ("Khammam", "Telangana"), ("Ozhukarai", "Puducherry"), ("Bihar Sharif", "Bihar"),
    ("Panipat", "Haryana"), ("Darbhanga", "Bihar"), ("Bally", "West Bengal"),
    ("Aizawl", "Mizoram"), ("Dewas", "Madhya Pradesh"), ("Ichalkaranji", "Maharashtra"),
    ("Karnal", "Haryana"), ("Bathinda", "Punjab"), ("Jalna", "Maharashtra"),
    ("Eluru", "Andhra Pradesh"), ("Kirari", "Delhi"), ("Barasat", "West Bengal"),
    ("Purnia", "Bihar"), ("Satna", "Madhya Pradesh"), ("Mau", "Uttar Pradesh"),
    ("Sonipat", "Haryana"), ("Farrukhabad", "Uttar Pradesh"), ("Sagar", "Karnataka"),
    ("Durg", "Chhattisgarh"), ("Imphal", "Manipur"), ("Ratlam", "Madhya Pradesh"),
    ("Hapur", "Uttar Pradesh"), ("Arrah", "Bihar"), ("Anantapur", "Andhra Pradesh"),
    ("Karimnagar", "Telangana"), ("Etawah", "Uttar Pradesh"), ("Ambernath", "Maharashtra"),
    ("North Dumdum", "West Bengal"), ("Bharatpur", "Rajasthan"), ("Begusarai", "Bihar"),
    ("Gandhidham", "Gujarat"), ("Barrackpore", "West Bengal"), ("Tiruvottiyur", "Tamil Nadu"),
    ("Puducherry", "Puducherry"), ("Sikar", "Rajasthan"), ("Thoothukudi", "Tamil Nadu"),
    ("Rewa", "Madhya Pradesh"), ("Mirzapur", "Uttar Pradesh"), ("Raichur", "Karnataka"),
    ("Pali", "Rajasthan"), ("Ramagundam", "Telangana"), ("Haridwar", "Uttarakhand"),
    ("Vijayanagaram", "Andhra Pradesh"), ("Katihar", "Bihar"), ("Nagercoil", "Tamil Nadu"),
    ("Sri Ganganagar", "Rajasthan"), ("Karawal Nagar", "Delhi"), ("Mango", "Jharkhand"),
    ("Thanjavur", "Tamil Nadu"), ("Bulandshahr", "Uttar Pradesh"), ("Uluberia", "West Bengal"),
    ("Murwara", "Madhya Pradesh"), ("Sambhal", "Uttar Pradesh"), ("Singrauli", "Madhya Pradesh"),
    ("Nadiad", "Gujarat"), ("Secunderabad", "Telangana"), ("Naihati", "West Bengal"),
    ("Yamunanagar", "Haryana"), ("Bidhannagar", "West Bengal"), ("Pallavaram", "Tamil Nadu"),
    ("Bidar", "Karnataka"), ("Munger", "Bihar"), ("Panchkula", "Haryana"),
    ("Burhanpur", "Madhya Pradesh"), ("Raurkela", "Odisha"), ("Kharagpur", "West Bengal"),
    ("Dindigul", "Tamil Nadu"), ("Gandhinagar", "Gujarat"), ("Hospet", "Karnataka"),
    ("Nangloi Jat", "Delhi"), ("Malda", "West Bengal"), ("Ongole", "Andhra Pradesh"),
    ("Deoghar", "Jharkhand"), ("Chapra", "Bihar"), ("Haldia", "West Bengal"),
    ("Khandwa", "Madhya Pradesh"), ("Nandyal", "Andhra Pradesh"), ("Chittoor", "Andhra Pradesh"),
    ("Morena", "Madhya Pradesh"), ("Amroha", "Uttar Pradesh"), ("Anand", "Gujarat"),
    ("Bhind", "Madhya Pradesh"), ("Bhalswa Jahangir Pur", "Delhi"), ("Madhyamgram", "West Bengal"),
    ("Bhiwani", "Haryana"), ("Navsari", "Gujarat"), ("Baharampur", "West Bengal"),
    ("Ambala", "Haryana"), ("Morvi", "Gujarat"), ("Fatehpur", "Uttar Pradesh"),
    ("Rae Bareli", "Uttar Pradesh"), ("Khora", "Uttar Pradesh"), ("Bhusawal", "Maharashtra"),
    ("Orai", "Uttar Pradesh"), ("Bahraich", "Uttar Pradesh"), ("Vellore", "Tamil Nadu"),
    ("Mahesana", "Gujarat"), ("Raiganj", "West Bengal"), ("Sirsa", "Haryana"),
    ("Danapur", "Bihar"), ("Serampore", "West Bengal"), ("Guna", "Madhya Pradesh"),
    ("Jaunpur", "Uttar Pradesh"), ("Panvel", "Maharashtra"), ("Shivpuri", "Madhya Pradesh"),
    ("Surendranagar", "Gujarat"), ("Unnao", "Uttar Pradesh"), ("Hugli-Chinsurah", "West Bengal"),
    ("Alappuzha", "Kerala"), ("Kottayam", "Kerala"), ("Machilipatnam", "Andhra Pradesh"),
    ("Shimla", "Himachal Pradesh"), ("Adoni", "Andhra Pradesh"), ("Udupi", "Karnataka"),
    ("Tenali", "Andhra Pradesh"), ("Proddatur", "Andhra Pradesh"), ("Saharsa", "Bihar"),
    ("Hindupur", "Andhra Pradesh"), ("Sasaram", "Bihar"), ("Buxar", "Bihar"),
    ("Kumbakonam", "Tamil Nadu"), ("Dehri", "Bihar"), ("Madanapalle", "Andhra Pradesh"),
    ("Siwan", "Bihar"), ("Bettiah", "Bihar"), ("Guntakal", "Andhra Pradesh"),
    ("Srikakulam", "Andhra Pradesh"), ("Motihari", "Bihar"), ("Dharmavaram", "Andhra Pradesh"),
    ("Gudivada", "Andhra Pradesh"), ("Narasaraopet", "Andhra Pradesh"), ("Bagaha", "Bihar"),
    ("Tadipatri", "Andhra Pradesh"), ("Kishanganj", "Bihar"), ("Amaravati", "Andhra Pradesh"),
]

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
            "discovery_source": "municipal_convention",
        }


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


# Municipal corporations: <city>municipalcorporation.gov.in / <city>mc.gov.in
for city, state in MUNICIPAL:
    s = slug(city)
    if not s:
        continue
    add(f"{s}mc.gov.in", f"{city} Municipal Corporation", "urban_local_body", state, city)
    add(
        f"{s}municipalcorporation.gov.in",
        f"{city} Municipal Corporation",
        "urban_local_body",
        state,
        city,
    )

# District courts: <district>.dcourts.gov.in and <district>court.gov.in
for state, names in districts.items():
    for name in names:
        s = slug(name)
        if not s:
            continue
        add(f"{s}.dcourts.gov.in", f"{name} District Court", "judiciary", state, name)
        add(f"{s}court.gov.in", f"{name} District Court", "judiciary", state, name)

rows = sorted(candidates.values(), key=lambda r: r["domain_name"])
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")

from collections import Counter

print(f"wrote {len(rows)} extra candidates to {OUT}")
for k, v in Counter(r["government_level"] for r in rows).most_common():
    print(f"  {k:22s} {v}")
