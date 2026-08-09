"""Comprehensive Indian Government Domain Seed Matrices and Directory Sources."""

from __future__ import annotations

from typing import List, Dict, Any
from schemas.domain import GovernmentLevel

# 1. All 36 Indian States and Union Territories with Apex Domains
STATES_AND_UTS = {
    # 28 States
    "Andhra Pradesh": {"code": "AP", "domain": "ap.gov.in", "level": GovernmentLevel.STATE_UT},
    "Arunachal Pradesh": {"code": "AR", "domain": "arunachalpradesh.gov.in", "level": GovernmentLevel.STATE_UT},
    "Assam": {"code": "AS", "domain": "assam.gov.in", "level": GovernmentLevel.STATE_UT},
    "Bihar": {"code": "BR", "domain": "bihar.gov.in", "level": GovernmentLevel.STATE_UT},
    "Chhattisgarh": {"code": "CG", "domain": "cgstate.gov.in", "level": GovernmentLevel.STATE_UT},
    "Goa": {"code": "GA", "domain": "goa.gov.in", "level": GovernmentLevel.STATE_UT},
    "Gujarat": {"code": "GJ", "domain": "gujaratindia.gov.in", "level": GovernmentLevel.STATE_UT},
    "Haryana": {"code": "HR", "domain": "haryana.gov.in", "level": GovernmentLevel.STATE_UT},
    "Himachal Pradesh": {"code": "HP", "domain": "himachal.nic.in", "level": GovernmentLevel.STATE_UT},
    "Jharkhand": {"code": "JH", "domain": "jharkhand.gov.in", "level": GovernmentLevel.STATE_UT},
    "Karnataka": {"code": "KA", "domain": "karnataka.gov.in", "level": GovernmentLevel.STATE_UT},
    "Kerala": {"code": "KL", "domain": "kerala.gov.in", "level": GovernmentLevel.STATE_UT},
    "Madhya Pradesh": {"code": "MP", "domain": "mp.gov.in", "level": GovernmentLevel.STATE_UT},
    "Maharashtra": {"code": "MH", "domain": "maharashtra.gov.in", "level": GovernmentLevel.STATE_UT},
    "Manipur": {"code": "MN", "domain": "manipur.gov.in", "level": GovernmentLevel.STATE_UT},
    "Meghalaya": {"code": "ML", "domain": "meghalaya.gov.in", "level": GovernmentLevel.STATE_UT},
    "Mizoram": {"code": "MZ", "domain": "mizoram.gov.in", "level": GovernmentLevel.STATE_UT},
    "Nagaland": {"code": "NL", "domain": "nagaland.gov.in", "level": GovernmentLevel.STATE_UT},
    "Odisha": {"code": "OD", "domain": "odisha.gov.in", "level": GovernmentLevel.STATE_UT},
    "Punjab": {"code": "PB", "domain": "punjab.gov.in", "level": GovernmentLevel.STATE_UT},
    "Rajasthan": {"code": "RJ", "domain": "rajasthan.gov.in", "level": GovernmentLevel.STATE_UT},
    "Sikkim": {"code": "SK", "domain": "sikkim.gov.in", "level": GovernmentLevel.STATE_UT},
    "Tamil Nadu": {"code": "TN", "domain": "tn.gov.in", "level": GovernmentLevel.STATE_UT},
    "Telangana": {"code": "TG", "domain": "telangana.gov.in", "level": GovernmentLevel.STATE_UT},
    "Tripura": {"code": "TR", "domain": "tripura.gov.in", "level": GovernmentLevel.STATE_UT},
    "Uttar Pradesh": {"code": "UP", "domain": "up.gov.in", "level": GovernmentLevel.STATE_UT},
    "Uttarakhand": {"code": "UK", "domain": "uk.gov.in", "level": GovernmentLevel.STATE_UT},
    "West Bengal": {"code": "WB", "domain": "wb.gov.in", "level": GovernmentLevel.STATE_UT},
    # 8 Union Territories
    "Andaman and Nicobar Islands": {"code": "AN", "domain": "andaman.gov.in", "level": GovernmentLevel.STATE_UT},
    "Chandigarh": {"code": "CH", "domain": "chandigarh.gov.in", "level": GovernmentLevel.STATE_UT},
    "Dadra and Nagar Haveli and Daman and Diu": {"code": "DH", "domain": "daman.nic.in", "level": GovernmentLevel.STATE_UT},
    "Delhi": {"code": "DL", "domain": "delhi.gov.in", "level": GovernmentLevel.STATE_UT},
    "Jammu and Kashmir": {"code": "JK", "domain": "jk.gov.in", "level": GovernmentLevel.STATE_UT},
    "Ladakh": {"code": "LA", "domain": "ladakh.nic.in", "level": GovernmentLevel.STATE_UT},
    "Lakshadweep": {"code": "LD", "domain": "lakshadweep.gov.in", "level": GovernmentLevel.STATE_UT},
    "Puducherry": {"code": "PY", "domain": "py.gov.in", "level": GovernmentLevel.STATE_UT},
}

# 2. Central Government Ministries and Apex Institutions
CENTRAL_MINISTRIES_AND_APEX = [
    {"name": "President of India", "domain": "presidentofindia.nic.in", "tags": ["apex", "constitutional"]},
    {"name": "Prime Minister's Office", "domain": "pmindia.gov.in", "tags": ["apex", "executive"]},
    {"name": "National Portal of India", "domain": "india.gov.in", "tags": ["national_portal", "portal"]},
    {"name": "Ministry of Home Affairs", "domain": "mha.gov.in", "tags": ["ministry", "security"]},
    {"name": "Ministry of Finance", "domain": "finmin.nic.in", "tags": ["ministry", "finance"]},
    {"name": "Ministry of External Affairs", "domain": "mea.gov.in", "tags": ["ministry", "foreign"]},
    {"name": "Ministry of Defence", "domain": "mod.gov.in", "tags": ["ministry", "defence"]},
    {"name": "Ministry of Electronics and Information Technology", "domain": "meity.gov.in", "tags": ["ministry", "it"]},
    {"name": "Ministry of Health and Family Welfare", "domain": "mohfw.gov.in", "tags": ["ministry", "health"]},
    {"name": "Ministry of Education", "domain": "education.gov.in", "tags": ["ministry", "education"]},
    {"name": "Ministry of Agriculture and Farmers Welfare", "domain": "agricoop.nic.in", "tags": ["ministry", "agriculture"]},
    {"name": "Ministry of Road Transport and Highways", "domain": "morth.nic.in", "tags": ["ministry", "transport"]},
    {"name": "Ministry of Railways", "domain": "indianrailways.gov.in", "tags": ["ministry", "railways"]},
    {"name": "Ministry of Law and Justice", "domain": "lawmin.gov.in", "tags": ["ministry", "judiciary"]},
    {"name": "Ministry of Commerce and Industry", "domain": "commerce.gov.in", "tags": ["ministry", "commerce"]},
    {"name": "Ministry of Power", "domain": "powermin.gov.in", "tags": ["ministry", "power"]},
    {"name": "Ministry of Rural Development", "domain": "rural.nic.in", "tags": ["ministry", "rural"]},
    {"name": "Ministry of Housing and Urban Affairs", "domain": "mohua.gov.in", "tags": ["ministry", "urban"]},
    {"name": "Ministry of Environment, Forest and Climate Change", "domain": "moef.gov.in", "tags": ["ministry", "environment"]},
    {"name": "Ministry of Women and Child Development", "domain": "wcd.nic.in", "tags": ["ministry", "social"]},
    {"name": "Election Commission of India", "domain": "eci.gov.in", "tags": ["apex", "election"]},
    {"name": "Supreme Court of India", "domain": "sci.gov.in", "tags": ["apex", "judiciary"]},
    {"name": "Comptroller and Auditor General of India", "domain": "cag.gov.in", "tags": ["apex", "audit"]},
    {"name": "Union Public Service Commission", "domain": "upsc.gov.in", "tags": ["apex", "recruitment"]},
    {"name": "Unique Identification Authority of India", "domain": "uidai.gov.in", "tags": ["agency", "identity"]},
    {"name": "Income Tax Department", "domain": "incometax.gov.in", "tags": ["agency", "taxation"]},
    {"name": "Goods and Services Tax Network", "domain": "gst.gov.in", "tags": ["agency", "taxation"]},
    {"name": "National Informatics Centre", "domain": "nic.in", "tags": ["agency", "infrastructure"]},
    {"name": "Digital India", "domain": "digitalindia.gov.in", "tags": ["portal", "it"]},
    {"name": "MyGov India", "domain": "mygov.in", "tags": ["portal", "citizen_engagement"]},
    {"name": "Parivahan Sewa", "domain": "parivahan.gov.in", "tags": ["portal", "transport"]},
    {"name": "CoWIN Portal", "domain": "cowin.gov.in", "tags": ["portal", "health", "spa"]},
]

# 3. Sample Matrix of High-Profile District Administration Portals (S3WaaS Pattern: <district>.nic.in / <district>.dc.gov.in)
DISTRICT_SEEDS_BY_STATE = {
    "Uttar Pradesh": ["varanasi", "lucknow", "agra", "kanpurnagar", "prayagraj", "gautambuddhanagar", "ghaziabad", "gorakhpur", "meerut", "ayodhya", "bareilly", "aligarh", "jhansi", "moradabad", "mathura"],
    "Maharashtra": ["mumbai", "mumbaicity", "pune", "nagpur", "thane", "nashik", "aurangabad", "solapur", "kolhapur", "amravati", "nanded", "jalgaon", "akola", "satara"],
    "Karnataka": ["bengaluruurban", "bengalururural", "mysuru", "belagavi", "dharwad", "mangaluru", "kalaburagi", "ballari", "shivamogga", "tumakuru", "udupi", "hassan"],
    "Tamil Nadu": ["chennai", "coimbatore", "madurai", "tiruchirappalli", "salem", "tirunelveli", "tiruppur", "vellore", "erode", "thanjavur", "dindigul", "kancheepuram"],
    "West Bengal": ["kolkata", "north24parganas", "south24parganas", "howrah", "hooghly", "darjeeling", "paschimmedinipur", "purba-bardhaman", "murshidabad", "malda"],
    "Gujarat": ["ahmedabad", "surat", "vadodara", "rajkot", "bhavnagar", "jamnagar", "gandhinagar", "junagadh", "anand", "navsari", "kutch", "morbi"],
    "Rajasthan": ["jaipur", "jodhpur", "kota", "bikaner", "ajmer", "udaipur", "bhilwara", "alwar", "sikar", "bharatpur", "pali", "chittorgarh"],
    "Madhya Pradesh": ["bhopal", "indore", "gwalior", "jabalpur", "ujjain", "sagar", "rewa", "satna", "ratlam", "chhindwara"],
    "Bihar": ["patna", "gaya", "bhagalpur", "muzaffarpur", "purnia", "darbhanga", "biharsharif", "arrah", "begusarai", "katihar"],
    "Kerala": ["thiruvananthapuram", "ernakulam", "kozhikode", "thrissur", "kollam", "palakkad", "alappuzha", "kannur", "kottayam", "malappuram", "wayanad", "idukki", "kasaragod"],
    "Assam": ["kamrup", "kamrupmetro", "dibrugarh", "silchar", "jorhat", "nagaon", "cachar", "tinsukia", "sonitpur", "barpeta"],
    "Punjab": ["ludhiana", "amritsar", "jalandhar", "patiala", "bathinda", "mohali", "hoshiarpur", "gurdaspur", "pathankot"],
    "Haryana": ["gurugram", "faridabad", "panipat", "ambala", "karnal", "hisar", "rohtak", "sonipat", "panchkula"],
    "Odisha": ["khordha", "cuttack", "ganjam", "puri", "balasore", "sambalpur", "bhadrak", "sundargarh", "mayurbhanj"],
    "Telangana": ["hyderabad", "rangareddy", "medchal", "warangal", "khammam", "karimnagar", "nizamabad", "nalgonda"],
    "Andhra Pradesh": ["visakhapatnam", "vijayawada", "guntur", "nellore", "kurnool", "tirupati", "kadapa", "kakinada", "anantapur"],
}


class DomainSeedGenerator:
    """Generates structured seed records across all Indian governance levels."""

    @classmethod
    def generate_all_seeds(cls) -> List[Dict[str, Any]]:
        seeds: List[Dict[str, Any]] = []

        # 1. Central Ministries and Apex Bodies
        for entry in CENTRAL_MINISTRIES_AND_APEX:
            domain = entry["domain"]
            seeds.append({
                "domain_name": domain,
                "base_url": f"https://{domain}",
                "government_level": GovernmentLevel.CENTRAL.value,
                "entity_name": entry["name"],
                "tags": entry.get("tags", ["central"]),
            })

        # 2. State and UT Apex Portals
        for state_name, info in STATES_AND_UTS.items():
            domain = info["domain"]
            seeds.append({
                "domain_name": domain,
                "base_url": f"https://{domain}",
                "government_level": GovernmentLevel.STATE_UT.value,
                "state_or_ut": state_name,
                "entity_name": f"Government of {state_name} Portal",
                "tags": ["state_portal", info["code"].lower()],
            })

        # 3. District Administration Portals (S3WaaS)
        for state_name, districts in DISTRICT_SEEDS_BY_STATE.items():
            for dist in districts:
                # District S3WaaS canonical naming: <district>.nic.in
                domain = f"{dist.lower().replace('-', '')}.nic.in"
                seeds.append({
                    "domain_name": domain,
                    "base_url": f"https://{domain}",
                    "government_level": GovernmentLevel.DISTRICT.value,
                    "state_or_ut": state_name,
                    "district": dist.title(),
                    "entity_name": f"District Administration {dist.title()}",
                    "tags": ["district", "s3waas", state_name.lower().replace(" ", "_")],
                })

        return seeds
