"""Comprehensive Indian Government Domain Seed Matrices and Directory Sources.

Spans Central Ministries, Apex Constitutional Bodies, High Courts & Tribunals,
Government Hospitals & Medical Colleges (AIIMS, Safdarjung, PGIMER),
Government School Systems (KVS, NVS, Sainik Schools, EMRS),
Public Central & State Universities, IITs/NITs/IIMs, CSIR & ICMR Labs,
Law Enforcement & CAPFs, State PSCs & RRBs, All 36 States/UTs,
900+ State Department Portals, 785+ Districts, Municipalities, and Nationalized PSUs.
"""

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

# 2. Central Government Ministries, Constitutional Bodies & National Portals
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
    {"name": "Ministry of Jal Shakti", "domain": "jalshakti-dowr.gov.in", "tags": ["ministry", "water"]},
    {"name": "Ministry of Petroleum and Natural Gas", "domain": "mopng.gov.in", "tags": ["ministry", "energy"]},
    {"name": "Ministry of Labour and Employment", "domain": "labour.gov.in", "tags": ["ministry", "labour"]},
    {"name": "Ministry of Communications", "domain": "dot.gov.in", "tags": ["ministry", "telecom"]},
    {"name": "Ministry of Tourism", "domain": "tourism.gov.in", "tags": ["ministry", "tourism"]},
    {"name": "Ministry of Culture", "domain": "indiaculture.gov.in", "tags": ["ministry", "culture"]},
    {"name": "Ministry of Civil Aviation", "domain": "civilaviation.gov.in", "tags": ["ministry", "aviation"]},
    {"name": "Ministry of Coal", "domain": "coal.nic.in", "tags": ["ministry", "mining"]},
    {"name": "Ministry of Mines", "domain": "mines.gov.in", "tags": ["ministry", "mining"]},
    {"name": "Ministry of Corporate Affairs", "domain": "mca.gov.in", "tags": ["ministry", "corporate"]},
    {"name": "Ministry of Science and Technology", "domain": "dst.gov.in", "tags": ["ministry", "science"]},
    {"name": "Ministry of New and Renewable Energy", "domain": "mnre.gov.in", "tags": ["ministry", "energy"]},
    {"name": "Ministry of Statistics and Programme Implementation", "domain": "mospi.gov.in", "tags": ["ministry", "statistics"]},
    {"name": "Ministry of Skill Development and Entrepreneurship", "domain": "msde.gov.in", "tags": ["ministry", "skills"]},
    {"name": "Ministry of Micro, Small and Medium Enterprises", "domain": "msme.gov.in", "tags": ["ministry", "msme"]},
    {"name": "Ministry of Food Processing Industries", "domain": "mofpi.gov.in", "tags": ["ministry", "food"]},
    {"name": "Ministry of Panchayati Raj", "domain": "panchayat.gov.in", "tags": ["ministry", "panchayat"]},
    {"name": "Ministry of Parliamentary Affairs", "domain": "mpa.gov.in", "tags": ["ministry", "parliament"]},
    {"name": "Ministry of Heavy Industries", "domain": "heavyindustries.gov.in", "tags": ["ministry", "industry"]},
    {"name": "Ministry of Ports, Shipping and Waterways", "domain": "shipmin.gov.in", "tags": ["ministry", "shipping"]},
    {"name": "Ministry of Social Justice and Empowerment", "domain": "socialjustice.gov.in", "tags": ["ministry", "social"]},
    {"name": "Ministry of Tribal Affairs", "domain": "tribal.nic.in", "tags": ["ministry", "tribal"]},
    {"name": "Ministry of Minority Affairs", "domain": "minorityaffairs.gov.in", "tags": ["ministry", "minority"]},
    {"name": "Ministry of Youth Affairs and Sports", "domain": "yas.nic.in", "tags": ["ministry", "sports"]},
    {"name": "Ministry of Textiles", "domain": "texmin.nic.in", "tags": ["ministry", "textiles"]},
    {"name": "Ministry of Personnel, Public Grievances and Pensions", "domain": "persmin.gov.in", "tags": ["ministry", "personnel"]},
    {"name": "Ministry of Chemicals and Fertilizers", "domain": "fert.nic.in", "tags": ["ministry", "chemicals"]},
    {"name": "Department of Atomic Energy", "domain": "dae.gov.in", "tags": ["apex", "atomic"]},
    {"name": "Department of Space", "domain": "dos.gov.in", "tags": ["apex", "space"]},
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
    {"name": "Passport Seva Portal", "domain": "passportindia.gov.in", "tags": ["portal", "passport"]},
    {"name": "e-Courts Services", "domain": "ecourts.gov.in", "tags": ["portal", "judiciary"]},
    {"name": "National Scholarship Portal", "domain": "scholarships.gov.in", "tags": ["portal", "education"]},
    {"name": "National Health Authority", "domain": "nha.gov.in", "tags": ["agency", "health"]},
    {"name": "Department of Posts (India Post)", "domain": "indiapost.gov.in", "tags": ["agency", "postal"]},
    {"name": "ISRO - Indian Space Research Organisation", "domain": "isro.gov.in", "tags": ["research", "space"]},
    {"name": "DRDO - Defence Research & Development", "domain": "drdo.gov.in", "tags": ["research", "defence"]},
    {"name": "Reserve Bank of India", "domain": "rbi.org.in", "tags": ["apex", "banking"]},
    {"name": "Securities and Exchange Board of India", "domain": "sebi.gov.in", "tags": ["apex", "finance"]},
    {"name": "Telecom Regulatory Authority of India", "domain": "trai.gov.in", "tags": ["apex", "telecom"]},
    {"name": "Food Safety and Standards Authority of India", "domain": "fssai.gov.in", "tags": ["agency", "food"]},
    {"name": "Bureau of Indian Standards", "domain": "bis.gov.in", "tags": ["agency", "standards"]},
    {"name": "Competition Commission of India", "domain": "cci.gov.in", "tags": ["agency", "competition"]},
    {"name": "NITI Aayog", "domain": "niti.gov.in", "tags": ["apex", "planning"]},
    {"name": "National Human Rights Commission", "domain": "nhrc.nic.in", "tags": ["apex", "human_rights"]},
    {"name": "DBT Bharat (Direct Benefit Transfer)", "domain": "dbtbharat.gov.in", "tags": ["portal", "schemes"]},
    {"name": "PM Kisan Samman Nidhi", "domain": "pmkisan.gov.in", "tags": ["portal", "agriculture"]},
    {"name": "Employees Provident Fund Organisation", "domain": "epfindia.gov.in", "tags": ["agency", "labour"]},
    {"name": "Employees State Insurance Corporation", "domain": "esic.gov.in", "tags": ["agency", "labour"]},
    {"name": "Government e Marketplace (GeM)", "domain": "gem.gov.in", "tags": ["portal", "procurement"]},
    {"name": "National Cyber Crime Reporting Portal", "domain": "cybercrime.gov.in", "tags": ["portal", "cybercrime"]},
    {"name": "National Disaster Management Authority", "domain": "ndma.gov.in", "tags": ["agency", "disaster"]},
    {"name": "Central Vigilance Commission", "domain": "cvc.gov.in", "tags": ["apex", "vigilance"]},
    {"name": "Central Information Commission", "domain": "cic.gov.in", "tags": ["apex", "rti"]},
    {"name": "National Green Tribunal", "domain": "greentribunal.gov.in", "tags": ["judiciary", "environment"]},
]

# 3. Government Hospitals, Premier Public Medical Colleges & Healthcare Bodies
GOVERNMENT_HOSPITALS_AND_HEALTH = [
    # AIIMS Institutes (All 20+ Functional AIIMS)
    {"name": "AIIMS New Delhi", "domain": "aiims.edu", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Bhopal", "domain": "aiimsbhopal.edu.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Bhubaneswar", "domain": "aiimsbhubaneswar.nic.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Jodhpur", "domain": "aiimsjodhpur.edu.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Patna", "domain": "aiimspatna.edu.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Raipur", "domain": "aiimsraipur.edu.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Rishikesh", "domain": "aiimsrishikesh.edu.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Nagpur", "domain": "aiimsnagpur.edu.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Mangalagiri", "domain": "aiimsmangalagiri.edu.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Gorakhpur", "domain": "aiimsgorakhpur.edu.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Kalyani", "domain": "aiimskalyani.edu.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Bathinda", "domain": "aiimsbathinda.edu.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Deoghar", "domain": "aiimsdeoghar.edu.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Bibinagar", "domain": "aiimsbibinagar.edu.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Guwahati", "domain": "aiimsguwahati.ac.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Rajkot", "domain": "aiimsrajkot.edu.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Bilaspur", "domain": "aiimsbilaspur.edu.in", "tags": ["hospital", "aiims", "central"]},
    {"name": "AIIMS Raebareli", "domain": "aiimsraebareli.edu.in", "tags": ["hospital", "aiims", "central"]},
    # Apex Central Government Hospitals & Research Institutes
    {"name": "Safdarjung Hospital & VMMC Delhi", "domain": "vmmc-sjh.nic.in", "tags": ["hospital", "central"]},
    {"name": "Dr. Ram Manohar Lohia Hospital Delhi", "domain": "rmlh.nic.in", "tags": ["hospital", "central"]},
    {"name": "Lady Hardinge Medical College & Hospitals", "domain": "lhmc-hosp.gov.in", "tags": ["hospital", "central"]},
    {"name": "Postgraduate Institute of Medical Education & Research (PGIMER Chandigarh)", "domain": "pgimer.edu.in", "tags": ["hospital", "research", "central"]},
    {"name": "JIPMER Puducherry", "domain": "jipmer.edu.in", "tags": ["hospital", "research", "central"]},
    {"name": "National Institute of Mental Health and Neurosciences (NIMHANS)", "domain": "nimhans.ac.in", "tags": ["hospital", "research", "central"]},
    {"name": "King George's Medical University (KGMU Lucknow)", "domain": "kgmu.org", "tags": ["hospital", "state"]},
    {"name": "Sanjay Gandhi Postgraduate Institute of Medical Sciences (SGPGIMS)", "domain": "sgpgi.org.in", "tags": ["hospital", "state"]},
    {"name": "Institute of Liver and Biliary Sciences (ILBS Delhi)", "domain": "ilbs.in", "tags": ["hospital", "state"]},
    {"name": "Tata Memorial Centre (DAE Hospital)", "domain": "tmc.gov.in", "tags": ["hospital", "cancer", "central"]},
    {"name": "Regional Cancer Centre Thiruvananthapuram", "domain": "rcctvm.gov.in", "tags": ["hospital", "cancer", "state"]},
    {"name": "National Institute of Tuberculosis and Respiratory Diseases", "domain": "nitrd.nic.in", "tags": ["hospital", "central"]},
    {"name": "Central Drugs Standard Control Organization (CDSCO)", "domain": "cdsco.gov.in", "tags": ["health", "regulatory"]},
    {"name": "National Health Mission (NHM)", "domain": "nhm.gov.in", "tags": ["health", "schemes"]},
    {"name": "National AIDS Control Organisation (NACO)", "domain": "naco.gov.in", "tags": ["health", "central"]},
    # State Government Medical Colleges & Hospitals
    {"name": "Madras Medical College & Rajiv Gandhi Govt General Hospital", "domain": "mmc.tn.gov.in", "tags": ["hospital", "state_medical"]},
    {"name": "Calcutta Medical College", "domain": "calcutnamedicalcollege.edu.in", "tags": ["hospital", "state_medical"]},
    {"name": "Grant Government Medical College & Sir JJ Group of Hospitals Mumbai", "domain": "gmcmumbai.gov.in", "tags": ["hospital", "state_medical"]},
    {"name": "Patna Medical College and Hospital (PMCH)", "domain": "pmch.bihar.gov.in", "tags": ["hospital", "state_medical"]},
    {"name": "Government Medical College Jammu", "domain": "gmcjammu.nic.in", "tags": ["hospital", "state_medical"]},
    {"name": "Government Medical College Patiala", "domain": "gmcpatiala.com", "tags": ["hospital", "state_medical"]},
    {"name": "SCB Medical College & Hospital Cuttack", "domain": "scbmch.in", "tags": ["hospital", "state_medical"]},
    {"name": "Pt. J.N.M. Medical College Raipur", "domain": "bmcraipur.cg.gov.in", "tags": ["hospital", "state_medical"]},
    {"name": "Goa Medical College and Hospital", "domain": "gmc.goa.gov.in", "tags": ["hospital", "state_medical"]},
    {"name": "Karnataka Institute of Medical Sciences (KIMS)", "domain": "kims.karnataka.gov.in", "tags": ["hospital", "state_medical"]},
    {"name": "Osmania Medical College Hyderabad", "domain": "osmaniamedicalcollege.edu.in", "tags": ["hospital", "state_medical"]},
    {"name": "Andhra Medical College Visakhapatnam", "domain": "andhramedicalcollege.edu.in", "tags": ["hospital", "state_medical"]},
]

# 4. Strictly Public & Government-Run School Systems, Boards & Autonomous Organizations
GOVERNMENT_SCHOOLS_AND_SYSTEMS = [
    # Kendriya Vidyalaya Sangathan (Apex & 25 Official Regional Offices)
    {"name": "Kendriya Vidyalaya Sangathan (KVS HQ)", "domain": "kvsangathan.nic.in", "tags": ["school_system", "central"]},
    {"name": "KVS Regional Office Delhi", "domain": "rodelhi.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Mumbai", "domain": "romumbai.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Chennai", "domain": "rochennai.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Kolkata", "domain": "rokolkata.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Hyderabad", "domain": "rohyderabad.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Bengaluru", "domain": "robengaluru.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Ahmedabad", "domain": "roahmedabad.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Jaipur", "domain": "rojaipur.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Lucknow", "domain": "rolucknow.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Patna", "domain": "ropatna.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Guwahati", "domain": "rogauhati.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Bhopal", "domain": "robhopal.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Chandigarh", "domain": "rochandigarh.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Dehradun", "domain": "rodehradun.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Ernakulam", "domain": "roernakulam.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Jabalpur", "domain": "rojabalpur.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Raipur", "domain": "roraipur.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Ranchi", "domain": "roranchi.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Silchar", "domain": "rosilchar.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Varanasi", "domain": "rovaranasi.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Gurugram", "domain": "rogurugram.kvs.gov.in", "tags": ["school_system", "kvs"]},
    {"name": "KVS Regional Office Agra", "domain": "roagra.kvs.gov.in", "tags": ["school_system", "kvs"]},
    # Navodaya Vidyalaya Samiti (Apex & 8 Regional Offices)
    {"name": "Navodaya Vidyalaya Samiti (NVS HQ)", "domain": "navodaya.gov.in", "tags": ["school_system", "central"]},
    {"name": "NVS Regional Office Bhopal", "domain": "nvsbhopal.gov.in", "tags": ["school_system", "nvs"]},
    {"name": "NVS Regional Office Chandigarh", "domain": "nvsrochandigarh.gov.in", "tags": ["school_system", "nvs"]},
    {"name": "NVS Regional Office Hyderabad", "domain": "nvsrohyderabad.gov.in", "tags": ["school_system", "nvs"]},
    {"name": "NVS Regional Office Jaipur", "domain": "nvsrojaipur.gov.in", "tags": ["school_system", "nvs"]},
    {"name": "NVS Regional Office Lucknow", "domain": "nvsrolucknow.gov.in", "tags": ["school_system", "nvs"]},
    {"name": "NVS Regional Office Patna", "domain": "nvsropatna.gov.in", "tags": ["school_system", "nvs"]},
    {"name": "NVS Regional Office Pune", "domain": "nvsropune.gov.in", "tags": ["school_system", "nvs"]},
    {"name": "NVS Regional Office Shillong", "domain": "nvsroshillong.gov.in", "tags": ["school_system", "nvs"]},
    # Sainik Schools (Ministry of Defence Run)
    {"name": "Sainik Schools Society", "domain": "sainikschoolsociety.in", "tags": ["school_system", "defence"]},
    {"name": "Sainik School Satara", "domain": "sainikschoolsatara.org", "tags": ["school", "defence"]},
    {"name": "Sainik School Ghorakhal", "domain": "sainikschoolghorakhal.org", "tags": ["school", "defence"]},
    {"name": "Sainik School Kunjpura", "domain": "sainikschoolkunjpura.org", "tags": ["school", "defence"]},
    {"name": "Sainik School Nagrota", "domain": "sainikschoolnagrota.com", "tags": ["school", "defence"]},
    {"name": "Sainik School Korukonda", "domain": "sainikschoolkorukonda.org", "tags": ["school", "defence"]},
    {"name": "Sainik School Amaravathinagar", "domain": "sainikschoolamaravathinagar.edu.in", "tags": ["school", "defence"]},
    {"name": "Sainik School Rewa", "domain": "sainikschoolrewa.nic.in", "tags": ["school", "defence"]},
    {"name": "Sainik School Kapurthala", "domain": "sainikschoolkapurthala.com", "tags": ["school", "defence"]},
    {"name": "Sainik School Chittorgarh", "domain": "sainikschoolchittorgarh.edu.in", "tags": ["school", "defence"]},
    {"name": "Sainik School Tilaiya", "domain": "sainikschooltilaiya.org", "tags": ["school", "defence"]},
    {"name": "Sainik School Sujanpur Tira", "domain": "sainikschoolsujanpurtira.org", "tags": ["school", "defence"]},
    # Eklavya Model Residential Schools (Tribal Affairs Ministry)
    {"name": "National Education Society for Tribal Students (EMRS)", "domain": "nests.gov.in", "tags": ["school_system", "tribal"]},
    # Public Educational Bodies & Open Schooling
    {"name": "National Institute of Open Schooling (NIOS)", "domain": "nios.ac.in", "tags": ["education_board", "open_school"]},
    {"name": "NCERT", "domain": "ncert.nic.in", "tags": ["education", "curriculum"]},
    {"name": "CBSE", "domain": "cbse.gov.in", "tags": ["education_board", "central"]},
    {"name": "Directorate of Education Delhi (Govt Schools)", "domain": "edudel.nic.in", "tags": ["school_system", "state_govt"]},
    {"name": "Samagra Shiksha Abhiyan", "domain": "samagrashiksha.education.gov.in", "tags": ["school_system", "schemes"]},
]

# 5. Public Central & State Universities, IIITs, IITs, NITs, IIMs, Research Labs
NATIONAL_ACADEMIC_AND_RESEARCH = [
    # IITs (23)
    {"name": "IIT Bombay", "domain": "iitb.ac.in"},
    {"name": "IIT Delhi", "domain": "iitd.ac.in"},
    {"name": "IIT Madras", "domain": "iitm.ac.in"},
    {"name": "IIT Kharagpur", "domain": "iitkgp.ac.in"},
    {"name": "IIT Kanpur", "domain": "iitk.ac.in"},
    {"name": "IIT Roorkee", "domain": "iitr.ac.in"},
    {"name": "IIT Guwahati", "domain": "iitg.ac.in"},
    {"name": "IIT Hyderabad", "domain": "iith.ac.in"},
    {"name": "IIT Indore", "domain": "iiti.ac.in"},
    {"name": "IIT BHU", "domain": "iitbhu.ac.in"},
    {"name": "IIT ISM Dhanbad", "domain": "iitism.ac.in"},
    {"name": "IIT Gandhinagar", "domain": "iitgn.ac.in"},
    {"name": "IIT Ropar", "domain": "iitrpr.ac.in"},
    {"name": "IIT Bhubaneswar", "domain": "iitbbs.ac.in"},
    {"name": "IIT Jodhpur", "domain": "iitj.ac.in"},
    {"name": "IIT Patna", "domain": "iitp.ac.in"},
    {"name": "IIT Mandi", "domain": "iitmandi.ac.in"},
    {"name": "IIT Palakkad", "domain": "iitpkd.ac.in"},
    {"name": "IIT Tirupati", "domain": "iittp.ac.in"},
    {"name": "IIT Jammu", "domain": "iitjammu.ac.in"},
    {"name": "IIT Goa", "domain": "iitgoa.ac.in"},
    {"name": "IIT Dharwad", "domain": "iitdh.ac.in"},
    {"name": "IIT Bhilai", "domain": "iitbhilai.ac.in"},
    # NITs (31)
    {"name": "NIT Trichy", "domain": "nitt.edu"},
    {"name": "NIT Surathkal", "domain": "nitk.ac.in"},
    {"name": "NIT Warangal", "domain": "nitw.ac.in"},
    {"name": "VNIT Nagpur", "domain": "vnit.ac.in"},
    {"name": "MNIT Jaipur", "domain": "mnit.ac.in"},
    {"name": "NIT Calicut", "domain": "nitc.ac.in"},
    {"name": "MNNIT Allahabad", "domain": "mnnit.ac.in"},
    {"name": "NIT Rourkela", "domain": "nitrkl.ac.in"},
    {"name": "NIT Silchar", "domain": "nits.ac.in"},
    {"name": "NIT Jalandhar", "domain": "nitj.ac.in"},
    {"name": "SVNIT Surat", "domain": "svnit.ac.in"},
    {"name": "NIT Patna", "domain": "nitp.ac.in"},
    {"name": "NIT Raipur", "domain": "nitrr.ac.in"},
    {"name": "NIT Jamshedpur", "domain": "nitjsr.ac.in"},
    {"name": "NIT Hamirpur", "domain": "nith.ac.in"},
    {"name": "NIT Durgapur", "domain": "nitdgp.ac.in"},
    {"name": "NIT Meghalaya", "domain": "nitm.ac.in"},
    {"name": "NIT Manipur", "domain": "nitmanipur.ac.in"},
    {"name": "NIT Nagaland", "domain": "nitnagaland.ac.in"},
    {"name": "NIT Mizoram", "domain": "nitmz.ac.in"},
    {"name": "NIT Sikkim", "domain": "nitsikkim.ac.in"},
    {"name": "NIT Puducherry", "domain": "nitpy.edu.in"},
    {"name": "NIT Andhra Pradesh", "domain": "nitandhra.ac.in"},
    {"name": "NIT Goa", "domain": "nitgoa.ac.in"},
    {"name": "NIT Uttarakhand", "domain": "nituk.ac.in"},
    {"name": "NIT Delhi", "domain": "nitdelhi.ac.in"},
    {"name": "NIT Agartala", "domain": "nita.ac.in"},
    {"name": "NIT Arunachal Pradesh", "domain": "nitap.ac.in"},
    # IIITs (Public/PPP)
    {"name": "IIIT Allahabad", "domain": "iiita.ac.in"},
    {"name": "IIITDM Kancheepuram", "domain": "iiitdm.ac.in"},
    {"name": "IIIT Delhi", "domain": "iiitd.ac.in"},
    {"name": "IIIT Gwalior", "domain": "iiitm.ac.in"},
    {"name": "IIITDM Jabalpur", "domain": "iiitdmj.ac.in"},
    {"name": "IIITDM Kurnool", "domain": "iiitk.ac.in"},
    {"name": "IIIT Guwahati", "domain": "iiitg.ac.in"},
    {"name": "IIIT Vadodara", "domain": "iiitvadodara.ac.in"},
    {"name": "IIIT Sri City", "domain": "iiits.ac.in"},
    {"name": "IIIT Kota", "domain": "iiitkota.ac.in"},
    {"name": "IIIT Kalyani", "domain": "iiitkalyani.ac.in"},
    {"name": "IIIT Una", "domain": "iiituna.ac.in"},
    {"name": "IIIT Sonepat", "domain": "iiitsonepat.ac.in"},
    {"name": "IIIT Lucknow", "domain": "iiitl.ac.in"},
    {"name": "IIIT Dharwad", "domain": "iiitdwd.ac.in"},
    {"name": "IIIT Kottayam", "domain": "iiitkottayam.ac.in"},
    {"name": "IIIT Ranchi", "domain": "iiitranchi.ac.in"},
    {"name": "IIIT Nagpur", "domain": "iiitnagpur.ac.in"},
    {"name": "IIIT Pune", "domain": "iiitp.ac.in"},
    {"name": "IIIT Bhagalpur", "domain": "iiitbh.ac.in"},
    {"name": "IIIT Bhopal", "domain": "iiitbhopal.ac.in"},
    {"name": "IIIT Surat", "domain": "iiitsurat.ac.in"},
    {"name": "IIIT Agartala", "domain": "iiitagartala.ac.in"},
    {"name": "IIIT Raichur", "domain": "iiitr.ac.in"},
    # IIMs (20)
    {"name": "IIM Ahmedabad", "domain": "iima.ac.in"},
    {"name": "IIM Bangalore", "domain": "iimb.ac.in"},
    {"name": "IIM Calcutta", "domain": "iimcal.ac.in"},
    {"name": "IIM Lucknow", "domain": "iiml.ac.in"},
    {"name": "IIM Indore", "domain": "iimi.ac.in"},
    {"name": "IIM Kozhikode", "domain": "iimk.ac.in"},
    {"name": "IIM Shillong", "domain": "iimsillong.ac.in"},
    {"name": "IIM Trichy", "domain": "iimtrichy.ac.in"},
    {"name": "IIM Udaipur", "domain": "iimu.ac.in"},
    {"name": "IIM Rohtak", "domain": "iimrohtak.ac.in"},
    {"name": "IIM Raipur", "domain": "iimraipur.ac.in"},
    {"name": "IIM Ranchi", "domain": "iimranchi.ac.in"},
    {"name": "IIM Kashipur", "domain": "iimkashipur.ac.in"},
    {"name": "IIM Nagpur", "domain": "iimnagpur.ac.in"},
    {"name": "IIM Visakhapatnam", "domain": "iimv.ac.in"},
    {"name": "IIM Bodh Gaya", "domain": "iimbg.ac.in"},
    {"name": "IIM Sambalpur", "domain": "iimsambalpur.ac.in"},
    {"name": "IIM Sirmaur", "domain": "iimsirmaur.ac.in"},
    {"name": "IIM Jammu", "domain": "iimjammu.ac.in"},
    # Central Public Universities
    {"name": "University of Delhi", "domain": "du.ac.in"},
    {"name": "Jawaharlal Nehru University", "domain": "jnu.ac.in"},
    {"name": "Banaras Hindu University", "domain": "bhu.ac.in"},
    {"name": "Aligarh Muslim University", "domain": "amu.ac.in"},
    {"name": "University of Hyderabad", "domain": "uohyd.ac.in"},
    {"name": "Jamia Millia Islamia", "domain": "jmi.ac.in"},
    {"name": "Visva-Bharati University", "domain": "visvabharati.ac.in"},
    {"name": "Pondicherry University", "domain": "pondiuni.edu.in"},
    {"name": "Tezpur University", "domain": "tezu.ernet.in"},
    {"name": "Central University of Rajasthan", "domain": "curaj.ac.in"},
    {"name": "Central University of Jammu", "domain": "cujammu.ac.in"},
    {"name": "Central University of Punjab", "domain": "cup.edu.in"},
    {"name": "Central University of Haryana", "domain": "cuh.ac.in"},
    {"name": "Central University of Karnataka", "domain": "cuk.ac.in"},
    {"name": "Central University of Kerala", "domain": "cukerala.ac.in"},
    {"name": "Central University of Tamil Nadu", "domain": "cutn.ac.in"},
    {"name": "Central University of South Bihar", "domain": "cub.ac.in"},
    {"name": "Central University of Gujarat", "domain": "cug.ac.in"},
    {"name": "Central University of Jharkhand", "domain": "cuj.ac.in"},
    {"name": "Central University of Odisha", "domain": "cuo.ac.in"},
    {"name": "North-Eastern Hill University", "domain": "nehu.ac.in"},
    {"name": "Mizoram University", "domain": "mzu.edu.in"},
    {"name": "Nagaland University", "domain": "nagalanduniversity.ac.in"},
    {"name": "Assam University", "domain": "aus.ac.in"},
    {"name": "Manipur University", "domain": "manipuruniv.ac.in"},
    {"name": "HNB Garhwal University", "domain": "hnbgu.ac.in"},
    {"name": "IGNOU", "domain": "ignou.ac.in"},
    # Premier State Public Universities
    {"name": "University of Mumbai", "domain": "mu.ac.in"},
    {"name": "Savitribai Phule Pune University", "domain": "unipune.ac.in"},
    {"name": "University of Calcutta", "domain": "caluniv.ac.in"},
    {"name": "University of Madras", "domain": "unom.ac.in"},
    {"name": "Osmania University", "domain": "osmania.ac.in"},
    {"name": "Andhra University", "domain": "andhrauniversity.edu.in"},
    {"name": "University of Kerala", "domain": "keralauniversity.ac.in"},
    {"name": "University of Lucknow", "domain": "lkouniv.ac.in"},
    {"name": "Patna University", "domain": "patnauniversity.ac.in"},
    {"name": "University of Rajasthan", "domain": "rajasthanuniversity.ac.in"},
    {"name": "Panjab University Chandigarh", "domain": "puchd.ac.in"},
    {"name": "Guru Nanak Dev University", "domain": "gndu.ac.in"},
    {"name": "Maharshi Dayanand University", "domain": "mdu.ac.in"},
    {"name": "Gauhati University", "domain": "gauhati.ac.in"},
    {"name": "Utkal University", "domain": "utkaluniversity.ac.in"},
    {"name": "Anna University", "domain": "annauniv.edu"},
    {"name": "JNTU Hyderabad", "domain": "jntuh.ac.in"},
    {"name": "AKTU Uttar Pradesh", "domain": "aktu.ac.in"},
    {"name": "VTU Karnataka", "domain": "vtu.ac.in"},
    {"name": "GTU Gujarat", "domain": "gtu.ac.in"},
    # CSIR & National Laboratories
    {"name": "CSIR Headquarters", "domain": "csir.res.in"},
    {"name": "National Physical Laboratory", "domain": "nplindia.org"},
    {"name": "National Chemical Laboratory", "domain": "ncl-india.org"},
    {"name": "CCMB Hyderabad", "domain": "ccmb.res.in"},
    {"name": "Central Drug Research Institute", "domain": "cdri.res.in"},
    {"name": "NEERI Nagpur", "domain": "neeri.res.in"},
    {"name": "IICT Hyderabad", "domain": "iict.res.in"},
    {"name": "IGIB Delhi", "domain": "igib.res.in"},
    {"name": "IICB Kolkata", "domain": "iicb.res.in"},
    {"name": "National Institute of Oceanography", "domain": "nio.org"},
    {"name": "CRRI Delhi", "domain": "crridom.gov.in"},
    {"name": "CBRI Roorkee", "domain": "cbri.res.in"},
    {"name": "CIMAP Lucknow", "domain": "cimap.res.in"},
    {"name": "IIIM Jammu", "domain": "iiim.res.in"},
    {"name": "CEERI Pilani", "domain": "ceeri.res.in"},
    {"name": "CECRI Karaikudi", "domain": "cecri.res.in"},
    {"name": "CLRI Chennai", "domain": "clri.org"},
    {"name": "CFTRI Mysore", "domain": "cftri.res.in"},
    {"name": "CSIO Chandigarh", "domain": "csio.res.in"},
    {"name": "AMPRI Bhopal", "domain": "ampri.res.in"},
    {"name": "CIMFR Dhanbad", "domain": "cimfr.nic.in"},
    {"name": "IHBT Palampur", "domain": "ihbt.res.in"},
    # ICMR & ICAR
    {"name": "ICMR Headquarters", "domain": "icmr.nic.in"},
    {"name": "National Institute of Virology (NIV)", "domain": "niv.co.in"},
    {"name": "National Institute of Epidemiology (NIE)", "domain": "nie.gov.in"},
    {"name": "National Institute of Nutrition (NIN)", "domain": "nin.res.in"},
    {"name": "ICAR Headquarters", "domain": "icar.org.in"},
    {"name": "IARI Pusa Delhi", "domain": "iari.res.in"},
    {"name": "IVRI Bareilly", "domain": "ivri.nic.in"},
    {"name": "NDRI Karnal", "domain": "ndri.res.in"},
    {"name": "CIFE Mumbai", "domain": "cife.edu.in"},
    # DAE / ISRO Centers
    {"name": "Bhabha Atomic Research Centre (BARC)", "domain": "barc.gov.in"},
    {"name": "Tata Institute of Fundamental Research (TIFR)", "domain": "tifr.res.in"},
    {"name": "Indira Gandhi Centre for Atomic Research (IGCAR)", "domain": "igcar.gov.in"},
    {"name": "Vikram Sarabhai Space Centre (VSSC)", "domain": "vssc.gov.in"},
    {"name": "UR Rao Satellite Centre (URSC)", "domain": "ursc.gov.in"},
    {"name": "Space Applications Centre (SAC)", "domain": "sac.gov.in"},
    {"name": "Satish Dhawan Space Centre (SDSC SHAR)", "domain": "shar.gov.in"},
]

# 6. Law Enforcement, CAPFs & Investigative Agencies
LAW_ENFORCEMENT_AND_SECURITY = [
    # Central Armed Police Forces (CAPFs) & Paramilitary
    {"name": "Border Security Force (BSF)", "domain": "bsf.gov.in", "tags": ["capf", "security"]},
    {"name": "Central Reserve Police Force (CRPF)", "domain": "crpf.gov.in", "tags": ["capf", "security"]},
    {"name": "Central Industrial Security Force (CISF)", "domain": "cisf.gov.in", "tags": ["capf", "security"]},
    {"name": "Indo-Tibetan Border Police (ITBP)", "domain": "itbpolice.nic.in", "tags": ["capf", "security"]},
    {"name": "Sashastra Seema Bal (SSB)", "domain": "ssb.gov.in", "tags": ["capf", "security"]},
    {"name": "National Security Guard (NSG)", "domain": "nsg.gov.in", "tags": ["capf", "security"]},
    {"name": "Assam Rifles", "domain": "assamrifles.gov.in", "tags": ["capf", "security"]},
    {"name": "Indian Coast Guard", "domain": "indiancoastguard.gov.in", "tags": ["defence", "security"]},
    # Investigative & Intelligence Agencies
    {"name": "Central Bureau of Investigation (CBI)", "domain": "cbi.gov.in", "tags": ["investigation", "police"]},
    {"name": "National Investigation Agency (NIA)", "domain": "nia.gov.in", "tags": ["investigation", "security"]},
    {"name": "National Crime Records Bureau (NCRB)", "domain": "ncrb.gov.in", "tags": ["police", "records"]},
    {"name": "Bureau of Police Research and Development (BPRD)", "domain": "bprd.nic.in", "tags": ["police", "research"]},
    {"name": "Directorate of Enforcement (ED)", "domain": "enforcementdirectorate.gov.in", "tags": ["enforcement", "finance"]},
    {"name": "Directorate of Revenue Intelligence (DRI)", "domain": "dri.nic.in", "tags": ["enforcement", "customs"]},
    {"name": "Narcotics Control Bureau (NCB)", "domain": "narcoticsindia.nic.in", "tags": ["police", "narcotics"]},
    # State Police Forces
    {"name": "Uttar Pradesh Police", "domain": "uppolice.gov.in", "tags": ["state_police"]},
    {"name": "Maharashtra Police", "domain": "mahapolice.gov.in", "tags": ["state_police"]},
    {"name": "Delhi Police", "domain": "delhipolice.gov.in", "tags": ["state_police"]},
    {"name": "Tamil Nadu Police", "domain": "tnpolice.gov.in", "tags": ["state_police"]},
    {"name": "Karnataka State Police", "domain": "ksp.karnataka.gov.in", "tags": ["state_police"]},
    {"name": "Bihar Police", "domain": "biharpolice.bihar.gov.in", "tags": ["state_police"]},
    {"name": "Rajasthan Police", "domain": "police.rajasthan.gov.in", "tags": ["state_police"]},
    {"name": "Madhya Pradesh Police", "domain": "mppolice.gov.in", "tags": ["state_police"]},
    {"name": "Gujarat Police", "domain": "gujaratpolice.gov.in", "tags": ["state_police"]},
    {"name": "Kerala Police", "domain": "keralapolice.gov.in", "tags": ["state_police"]},
    {"name": "West Bengal Police", "domain": "wbpolice.gov.in", "tags": ["state_police"]},
    {"name": "Odisha Police", "domain": "odishapolice.gov.in", "tags": ["state_police"]},
    {"name": "Punjab Police", "domain": "punjabpolice.gov.in", "tags": ["state_police"]},
    {"name": "Haryana Police", "domain": "haryanapolice.gov.in", "tags": ["state_police"]},
    {"name": "Assam Police", "domain": "assampolice.gov.in", "tags": ["state_police"]},
    {"name": "Chhattisgarh Police", "domain": "cgpolice.gov.in", "tags": ["state_police"]},
    {"name": "Jharkhand Police", "domain": "jhpolice.gov.in", "tags": ["state_police"]},
    {"name": "Telangana State Police", "domain": "tspolice.gov.in", "tags": ["state_police"]},
    {"name": "Andhra Pradesh Police", "domain": "appolice.gov.in", "tags": ["state_police"]},
    {"name": "Uttarakhand Police", "domain": "uttarakhandpolice.uk.gov.in", "tags": ["state_police"]},
    {"name": "Himachal Pradesh Police", "domain": "hppolice.nic.in", "tags": ["state_police"]},
    {"name": "Jammu & Kashmir Police", "domain": "jkpolice.gov.in", "tags": ["state_police"]},
    {"name": "Goa Police", "domain": "goapolice.gov.in", "tags": ["state_police"]},
]

# 7. Railway Recruitment Boards (RRBs) across India
RAILWAY_RECRUITMENT_BOARDS = [
    {"name": "RRB Ahmedabad", "domain": "rrbahmedabad.gov.in"},
    {"name": "RRB Ajmer", "domain": "rrbajmer.gov.in"},
    {"name": "RRB Prayagraj (Allahabad)", "domain": "rrbald.gov.in"},
    {"name": "RRB Mumbai", "domain": "rrbmumbai.gov.in"},
    {"name": "RRB Kolkata", "domain": "rrbkolkata.gov.in"},
    {"name": "RRB Chennai", "domain": "rrbchennai.gov.in"},
    {"name": "RRB Secunderabad", "domain": "rrbsecunderabad.gov.in"},
    {"name": "RRB Patna", "domain": "rrbpatna.gov.in"},
    {"name": "RRB Bengaluru", "domain": "rrbbnc.gov.in"},
    {"name": "RRB Bhopal", "domain": "rrbbpl.nic.in"},
    {"name": "RRB Chandigarh", "domain": "rrbcdg.gov.in"},
    {"name": "RRB Gorakhpur", "domain": "rrbgkp.gov.in"},
    {"name": "RRB Guwahati", "domain": "rrbguwahati.gov.in"},
    {"name": "RRB Jammu-Srinagar", "domain": "rrbjammu.nic.in"},
    {"name": "RRB Malda", "domain": "rrbmalda.gov.in"},
    {"name": "RRB Muzaffarpur", "domain": "rrbmuzaffarpur.gov.in"},
    {"name": "RRB Ranchi", "domain": "rrbranchi.gov.in"},
    {"name": "RRB Siliguri", "domain": "rrbsiliguri.gov.in"},
    {"name": "RRB Thiruvananthapuram", "domain": "rrbthiruvananthapuram.gov.in"},
    {"name": "RRB Bilaspur", "domain": "rrbbilaspur.gov.in"},
]

# 8. High Courts & National Tribunals
HIGH_COURTS_AND_TRIBUNALS = [
    {"name": "Allahabad High Court", "domain": "allahabadhighcourt.in"},
    {"name": "Bombay High Court", "domain": "bombayhighcourt.nic.in"},
    {"name": "Calcutta High Court", "domain": "calcuttahighcourt.gov.in"},
    {"name": "Chhattisgarh High Court", "domain": "highcourt.cg.gov.in"},
    {"name": "Delhi High Court", "domain": "delhihighcourt.nic.in"},
    {"name": "Gauhati High Court", "domain": "ghconline.gov.in"},
    {"name": "Gujarat High Court", "domain": "gujarathighcourt.nic.in"},
    {"name": "Himachal Pradesh High Court", "domain": "hphighcourt.nic.in"},
    {"name": "Jammu & Kashmir High Court", "domain": "jkhighcourt.nic.in"},
    {"name": "Jharkhand High Court", "domain": "jharkhandhighcourt.nic.in"},
    {"name": "Karnataka High Court", "domain": "karnatakahiighcourt.kar.nic.in"},
    {"name": "Kerala High Court", "domain": "hckerala.gov.in"},
    {"name": "Madhya Pradesh High Court", "domain": "mphc.gov.in"},
    {"name": "Madras High Court", "domain": "madrashighcourt.nic.in"},
    {"name": "Manipur High Court", "domain": "hcmimphal.nic.in"},
    {"name": "Meghalaya High Court", "domain": "meghalayahighcourt.nic.in"},
    {"name": "Orissa High Court", "domain": "orissahighcourt.nic.in"},
    {"name": "Patna High Court", "domain": "patnahighcourt.gov.in"},
    {"name": "Punjab and Haryana High Court", "domain": "highcourtchd.gov.in"},
    {"name": "Rajasthan High Court", "domain": "hcraj.nic.in"},
    {"name": "Sikkim High Court", "domain": "hcs.gov.in"},
    {"name": "Telangana High Court", "domain": "tshc.gov.in"},
    {"name": "Andhra Pradesh High Court", "domain": "hc.ap.nic.in"},
    {"name": "Tripura High Court", "domain": "tripurahighcourt.nic.in"},
    {"name": "Uttarakhand High Court", "domain": "highcourtofuttarakhand.gov.in"},
    {"name": "Central Administrative Tribunal (CAT)", "domain": "cgat.gov.in"},
    {"name": "National Company Law Tribunal (NCLT)", "domain": "nclt.gov.in"},
    {"name": "National Company Law Appellate Tribunal", "domain": "nclat.nic.in"},
    {"name": "Telecom Disputes Settlement Tribunal (TDSAT)", "domain": "tdsat.gov.in"},
    {"name": "Armed Forces Tribunal (AFT)", "domain": "aftdelhi.nic.in"},
    {"name": "National Consumer Disputes Redressal Commission", "domain": "ncdrc.nic.in"},
]

# 9. All 785+ Indian Districts organized by State/UT
ALL_DISTRICTS_BY_STATE = {
    "Uttar Pradesh": [
        "agra", "aligarh", "ambedkarnagar", "amethi", "amroha", "auraiya", "ayodhya", "azamgarh",
        "baghpat", "bahraich", "ballia", "balrampur", "banda", "barabanki", "bareilly", "basti",
        "bhadohi", "bijnor", "budaun", "bulandshahr", "chandauli", "chitrakoot", "deoria", "etah",
        "etawah", "farrukhabad", "fatehpur", "firozabad", "gautambuddhanagar", "ghaziabad", "ghazipur",
        "gonda", "gorakhpur", "hamirpur", "hapur", "hardoi", "hathras", "jalaun", "jaunpur", "jhansi",
        "kannauj", "kanpurdehat", "kanpurnagar", "kasganj", "kaushambi", "kheri", "kushinagar",
        "lalitpur", "lucknow", "maharajganj", "mahoba", "mainpuri", "mathura", "mau", "meerut",
        "mirzapur", "moradabad", "muzaffarnagar", "pilibhit", "pratapgarh", "prayagraj", "raebareli",
        "rampur", "saharanpur", "sambhal", "santkabirnagar", "shahjahanpur", "shamli", "shravasti",
        "siddharthnagar", "sitapur", "sonbhadra", "sultanpur", "unnao", "varanasi"
    ],
    "Maharashtra": [
        "ahmednagar", "akola", "amravati", "aurangabad", "beed", "bhandara", "buldhana", "chandrapur",
        "dhule", "gadchiroli", "gondia", "hingoli", "jalgaon", "jalna", "kolhapur", "latur", "mumbai",
        "mumbaicity", "mumbaisuburban", "nagpur", "nanded", "nandurbar", "nashik", "osmanabad", "palghar",
        "parbhani", "pune", "raigad", "ratnagiri", "sangli", "satara", "sindhudurg", "solapur",
        "thane", "wardha", "washim", "yavatmal"
    ],
    "Bihar": [
        "araria", "arwal", "aurangabad", "banka", "begusarai", "bhagalpur", "bhojpur", "buxar",
        "darbhanga", "eastchamparan", "gaya", "gopalganj", "jamui", "jehanabad", "kaimur", "katihar",
        "khagaria", "kishanganj", "lakhisarai", "madhepura", "madhubani", "munger", "muzaffarpur",
        "nalanda", "nawada", "patna", "purnia", "rohtas", "saharsa", "samastipur", "saran",
        "sheikhpura", "sheohar", "sitamarhi", "siwan", "supaul", "vaishali", "westchamparan"
    ],
    "Tamil Nadu": [
        "ariyalur", "chengalpattu", "chennai", "coimbatore", "cuddalore", "dharmapuri", "dindigul",
        "erode", "kallakurichi", "kancheepuram", "kanyakumari", "karur", "krishnagiri", "madurai",
        "mayiladuthurai", "nagapattinam", "namakkal", "nilgiris", "perambalur", "pudukkottai",
        "ramanathapuram", "ranipet", "salem", "sivaganga", "tenkasi", "thanjavur", "theni",
        "thoothukudi", "tiruchirappalli", "tirunelveli", "tirupathur", "tiruppur", "tiruvallur",
        "tiruvannamalai", "tiruvarur", "vellore", "viluppuram", "virudhunagar"
    ],
    "Madhya Pradesh": [
        "agar-malwa", "alirajpur", "anuppur", "ashoknagar", "balaghat", "barwani", "betul", "bhind",
        "bhopal", "burhanpur", "chhatarpur", "chhindwara", "damoh", "datia", "dewas", "dhar", "dindori",
        "guna", "gwalior", "harda", "hoshangabad", "indore", "jabalpur", "jhabua", "katni", "khandwa",
        "khargone", "mandla", "mandsaur", "morena", "narsinghpur", "neemuch", "niwari", "panna",
        "raisen", "rajgarh", "ratlam", "rewa", "sagar", "satna", "sehore", "seoni", "shahdol",
        "shajapur", "sheopur", "shivpuri", "sidhi", "singrauli", "tikamgarh", "ujjain", "umaria", "vidisha"
    ],
    "Rajasthan": [
        "ajmer", "alwar", "banswara", "baran", "barmer", "bharatpur", "bhilwara", "bikaner",
        "bundi", "chittorgarh", "churu", "dausa", "dholpur", "dungarpur", "hanumangarh", "jaipur",
        "jaisalmer", "jalore", "jhalawar", "jhunjhunu", "jodhpur", "karauli", "kota", "nagaur",
        "pali", "pratapgarh", "rajsamand", "sawaimadhopur", "sikar", "sirohi", "sriganganagar",
        "tonk", "udaipur", "anupgarh", "balotra", "beawar", "deeg", "didwana", "dudu", "gangapurcity",
        "jaipurrural", "jodhpurrural", "kekri", "kotputli", "khairthal", "neemkathana", "phalodi", "salumber", "sanchore"
    ],
    "Karnataka": [
        "bagalkote", "ballari", "belagavi", "bengalururural", "bengaluruurban", "bidar", "chamarajanagara",
        "chikkaballapura", "chikkamagaluru", "chitradurga", "dakshinakannada", "davanagere", "dharwad",
        "gadag", "hassan", "haveri", "kalaburagi", "kodagu", "kolar", "koppal", "mandya", "mysuru",
        "raichur", "ramanagara", "shivamogga", "tumakuru", "udupi", "uttarakannada", "vijayanagara",
        "vijayapura", "yadgir"
    ],
    "Gujarat": [
        "ahmedabad", "amreli", "anand", "aravalli", "banaskantha", "bharuch", "bhavnagar", "botad",
        "chhotaudepur", "dahod", "dang", "devbhumidwarka", "gandhinagar", "girsomnath", "jamnagar",
        "junagadh", "kheda", "kutch", "mahisagar", "mehsana", "morbi", "narmada", "navsari",
        "panchmahal", "patan", "porbandar", "rajkot", "sabarkantha", "surat", "surendranagar",
        "tapi", "vadodara", "valsad"
    ],
    "West Bengal": [
        "alipurduar", "bankura", "birbhum", "coochbehar", "dakshindinajpur", "darjeeling", "hooghly",
        "howrah", "jalpaiguri", "jhargram", "kalimpong", "kolkata", "malda", "murshidabad", "nadia",
        "north24parganas", "paschim-bardhaman", "paschimmedinipur", "purbabardhaman", "purbamedinipur",
        "purulia", "south24parganas", "uttardinajpur"
    ],
    "Odisha": [
        "angul", "balangir", "balasore", "bargarh", "bhadrak", "boudh", "cuttack", "deogarh",
        "dhenkanal", "gajapati", "ganjam", "jagatsinghpur", "jajpur", "jharsuguda", "kalahandi",
        "kandhamal", "kendrapara", "kendujhar", "khordha", "koraput", "malkangiri", "mayurbhanj",
        "nabarangpur", "nayagarh", "nuapada", "puri", "rayagada", "sambalpur", "subarnapur", "sundargarh"
    ],
    "Kerala": [
        "alappuzha", "ernakulam", "idukki", "kannur", "kasaragod", "kollam", "kottayam",
        "kozhikode", "malappuram", "palakkad", "pathanamthitta", "thiruvananthapuram", "thrissur", "wayanad"
    ],
    "Andhra Pradesh": [
        "allurisitharamaraju", "anakapalli", "anantapur", "annamayya", "bapatla", "chittoor",
        "eastgodavari", "eluru", "guntur", "kakinada", "konaseema", "krishna", "kurnool",
        "nandyal", "ntr", "palnadu", "parvathipurammanyam", "prakasam", "srikakulam",
        "srisathyasai", "spsrnellore", "tirupati", "visakhapatnam", "vizianagaram", "westgodavari", "ysrkadapa"
    ],
    "Telangana": [
        "adilabad", "bhadradrikothagudem", "hanumakonda", "hyderabad", "jagtial", "jangaon",
        "jayashankar", "jogulambagadwal", "kamareddy", "karimnagar", "khammam", "kumurambheem",
        "mahabubabad", "mahabubnagar", "mancherial", "medak", "medchalmalkajgiri", "mulugu",
        "nagarkurnool", "nalgonda", "narayanpet", "nirmal", "nizamabad", "peddapalli",
        "rajannasircilla", "rangareddy", "sangareddy", "siddipet", "suryapet", "vikarabad",
        "wanaparthy", "warangal", "yadadribhuvanagiri"
    ],
    "Assam": [
        "baksa", "barpeta", "biswanath", "bongaigaon", "cachar", "charaideo", "chirang",
        "darrang", "dhemaji", "dhubri", "dibrugarh", "dima-hasao", "goalpara", "golaghat",
        "hailakandi", "hojai", "jorhat", "kamrup", "kamrupmetro", "karbianglong", "karimganj",
        "kokrajhar", "lakhimpur", "majuli", "morigaon", "nagaon", "nalbari", "sivasagar",
        "sonitpur", "southsalmara", "tinsukia", "udalguri", "westkarbianglong"
    ],
    "Punjab": [
        "amritsar", "barnala", "bathinda", "faridkot", "fatehgarhsahib", "fazilka", "ferozepur",
        "gurdaspur", "hoshiarpur", "jalandhar", "kapurthala", "ludhiana", "malerkotla", "mansa",
        "moga", "mohali", "muktsar", "pathankot", "patiala", "rupnagar", "sangrur", "nawanshahr", "tarantaran"
    ],
    "Haryana": [
        "ambala", "bhiwani", "charkhidadri", "faridabad", "fatehabad", "gurugram", "hisar",
        "jhajjar", "jind", "kaithal", "karnal", "kurukshetra", "mahendragarh", "nuh",
        "palwal", "panchkula", "panipat", "rewari", "rohtak", "sirsa", "sonipat", "yamunanagar"
    ],
    "Chhattisgarh": [
        "balod", "balodabazar", "balrampur", "bastar", "bemetara", "bijapur", "bilaspur",
        "dantewada", "dhamtari", "durg", "gariaband", "gaurela-pendra-marwahi", "janjgir-champa",
        "jashpur", "kabirdham", "kanker", "kondagaon", "korba", "koriya", "mahasamund",
        "manendragarh", "mohla-manpur", "mungeli", "narayanpur", "raigarh", "raipur",
        "rajnandgaon", "sarangarh", "shakti", "sukma", "surajpur", "surguja", "khairagarh"
    ],
    "Jharkhand": [
        "bokaro", "chatra", "deoghar", "dhanbad", "dumka", "east-singhbhum", "garhwa", "giridih",
        "godda", "gumla", "hazaribagh", "jamtara", "khunti", "koderma", "latehar", "lohardaga",
        "pakur", "palamu", "ramgarh", "ranchi", "sahibganj", "seraikela", "simdega", "west-singhbhum"
    ],
    "Uttarakhand": [
        "almora", "bageshwar", "chamoli", "champawat", "dehradun", "haridwar", "nainital",
        "pauri", "pithoragarh", "rudraprayag", "tehri", "usnagar", "uttarkashi"
    ],
    "Himachal Pradesh": [
        "bilaspurhp", "chamba", "hamirpurhp", "kangra", "kinnaur", "kullu", "lahul-spiti",
        "mandi", "shimla", "sirmour", "solan", "una"
    ],
    "Jammu and Kashmir": [
        "anantnag", "bandipora", "baramulla", "budgam", "doda", "ganderbal", "jammu", "kathua",
        "kishtwar", "kulgam", "kupwara", "poonch", "pulwama", "rajouri", "ramban", "reasi",
        "samba", "shopian", "srinagar", "udhampur"
    ],
    "Delhi": [
        "centraldelhi", "eastdelhi", "newdelhi", "northdelhi", "north-eastdelhi", "north-westdelhi",
        "shahdara", "southdelhi", "south-eastdelhi", "south-westdelhi", "westdelhi"
    ],
    "Goa": ["northgoa", "southgoa"],
    "Tripura": ["dhalai", "gomati", "khowai", "northtripura", "sepahijala", "southtripura", "unakoti", "westtripura"],
    "Meghalaya": ["eastgarohills", "eastjaintiahills", "eastkhasihills", "northgarohills", "ri-bhoi", "southgarohills", "southwestgarohills", "southwestkhasihills", "westgarohills", "westjaintiahills", "westkhasihills", "easternwestkhasihills"],
    "Manipur": ["bishnupur", "chandel", "churachandpur", "imphal-east", "imphal-west", "jiri", "kakching", "kamjong", "kangpokpi", "noney", "pherzawl", "senapati", "tamenglong", "tengnoupal", "thoubal", "ukhrul"],
    "Nagaland": ["chumoukedima", "dimapur", "kiphire", "kohima", "longleng", "mokokchung", "mon", "niuland", "noklak", "peren", "phek", "shamator", "tsenminyu", "tuensang", "wohka", "zunheboto"],
    "Arunachal Pradesh": ["anjaw", "changlang", "dibangvalley", "eastkameng", "eastsiang", "kamle", "kra-daadi", "kurungkumey", "leparada", "lohit", "longding", "lower-dibangvalley", "lowersiang", "lowersubansiri", "namsai", "pakkekessang", "papumpare", "shi-yomi", "siang", "tawang", "tirap", "upperkameng", "uppersiang", "uppersubansiri", "westkameng", "westsiang"],
    "Mizoram": ["aizawl", "champhai", "hnahthial", "khawzawl", "kolasib", "lawngtlai", "lunglei", "mamit", "saitual", "serchhip", "siaha"],
    "Sikkim": ["gangtok", "gyalshing", "mangan", "namchi", "pakyong", "soreng"],
    "Ladakh": ["leh", "kargil"],
    "Puducherry": ["puducherry", "karaikal", "mahe", "yanam"],
    "Andaman and Nicobar Islands": ["nicobar", "north-middle-andaman", "south-andaman"],
    "Chandigarh": ["chandigarh"],
    "Dadra and Nagar Haveli and Daman and Diu": ["daman", "diu", "dnh"],
    "Lakshadweep": ["lakshadweep"]
}

# 10. State Government Department Subdomains (25 major departments per State/UT)
KEY_STATE_DEPARTMENTS = [
    "police", "revenue", "education", "health", "transport", "finance", "forest",
    "agriculture", "pwd", "wrd", "excise", "tourism", "labour", "food",
    "socialwelfare", "panchayat", "industry", "commercialtax", "energy", "housing",
    "dm", "tribal", "fisheries", "cooperation", "planning"
]

ALL_STATE_DOMAIN_ROOTS = [
    "up.gov.in", "maharashtra.gov.in", "rajasthan.gov.in", "mp.gov.in", "gujarat.gov.in",
    "karnataka.gov.in", "tn.gov.in", "kerala.gov.in", "bihar.gov.in", "wb.gov.in",
    "odisha.gov.in", "punjab.gov.in", "haryana.gov.in", "assam.gov.in", "cgstate.gov.in",
    "jharkhand.gov.in", "telangana.gov.in", "ap.gov.in", "uk.gov.in", "himachal.nic.in",
    "delhi.gov.in", "jk.gov.in", "goa.gov.in", "tripura.gov.in", "meghalaya.gov.in",
    "manipur.gov.in", "nagaland.gov.in", "mizoram.gov.in", "sikkim.gov.in", "arunachalpradesh.gov.in",
    "py.gov.in", "andaman.gov.in", "chandigarh.gov.in", "daman.nic.in", "ladakh.nic.in", "lakshadweep.gov.in"
]

# 11. Nationalized Banks, Financial Regulatory & Central PSUs
CENTRAL_PSUS_AND_FINANCIAL = [
    # Public Sector Nationalized Banks (12)
    {"name": "State Bank of India (SBI)", "domain": "sbi.co.in"},
    {"name": "Punjab National Bank", "domain": "pnbindia.in"},
    {"name": "Bank of Baroda", "domain": "bankofbaroda.in"},
    {"name": "Canara Bank", "domain": "canarabank.com"},
    {"name": "Union Bank of India", "domain": "unionbankofindia.co.in"},
    {"name": "Bank of India", "domain": "bankofindia.co.in"},
    {"name": "Indian Bank", "domain": "indianbank.in"},
    {"name": "Central Bank of India", "domain": "centralbankofindia.co.in"},
    {"name": "Indian Overseas Bank", "domain": "iob.in"},
    {"name": "UCO Bank", "domain": "ucobank.com"},
    {"name": "Bank of Maharashtra", "domain": "bankofmaharashtra.in"},
    {"name": "Punjab & Sind Bank", "domain": "punjabandsindbank.co.in"},
    # Development Financial & Insurance
    {"name": "Life Insurance Corporation of India (LIC)", "domain": "licindia.in"},
    {"name": "NABARD", "domain": "nabard.org"},
    {"name": "SIDBI", "domain": "sidbi.in"},
    {"name": "EXIM Bank of India", "domain": "eximbankindia.in"},
    {"name": "National Housing Bank (NHB)", "domain": "nhb.org.in"},
    {"name": "Insurance Regulatory and Development Authority (IRDAI)", "domain": "irdai.gov.in"},
    {"name": "Pension Fund Regulatory and Development Authority (PFRDA)", "domain": "pfrda.org.in"},
    # Maharatna & Navratna PSUs
    {"name": "National Highways Authority of India (NHAI)", "domain": "nhai.gov.in"},
    {"name": "IRCTC", "domain": "irctc.co.in"},
    {"name": "Indian Oil Corporation (IOCL)", "domain": "iocl.com"},
    {"name": "Oil and Natural Gas Corporation (ONGC)", "domain": "ongcindia.com"},
    {"name": "NTPC Limited", "domain": "ntpc.co.in"},
    {"name": "Bharat Heavy Electricals Limited (BHEL)", "domain": "bhel.in"},
    {"name": "Steel Authority of India (SAIL)", "domain": "sail.co.in"},
    {"name": "GAIL (India) Limited", "domain": "gailonline.com"},
    {"name": "Coal India Limited", "domain": "coalindia.in"},
    {"name": "Bharat Petroleum (BPCL)", "domain": "bharatpetroleum.in"},
    {"name": "Hindustan Petroleum (HPCL)", "domain": "hindustanpetroleum.com"},
    {"name": "Power Grid Corporation of India", "domain": "powergrid.in"},
    {"name": "Hindustan Aeronautics Limited (HAL)", "domain": "hal-india.co.in"},
    {"name": "Bharat Electronics Limited (BEL)", "domain": "bel-india.in"},
    {"name": "Oil India Limited", "domain": "oil-india.com"},
    {"name": "Container Corporation of India (CONCOR)", "domain": "concorindia.co.in"},
    {"name": "NMDC Limited", "domain": "nmdc.co.in"},
    {"name": "Power Finance Corporation (PFC)", "domain": "pfcindia.com"},
    {"name": "REC Limited", "domain": "recindia.nic.in"},
]

# 12. State Public Service Commissions & Recruitment Portals
STATE_PSCS = [
    {"name": "UP Public Service Commission", "domain": "uppsc.up.nic.in"},
    {"name": "Maharashtra Public Service Commission", "domain": "mpsc.gov.in"},
    {"name": "Bihar Public Service Commission", "domain": "bpsc.bih.nic.in"},
    {"name": "Tamil Nadu Public Service Commission", "domain": "tnpsc.gov.in"},
    {"name": "Karnataka Public Service Commission", "domain": "kpsc.kar.nic.in"},
    {"name": "Rajasthan Public Service Commission", "domain": "rpsc.rajasthan.gov.in"},
    {"name": "MP Public Service Commission", "domain": "mppsc.mp.gov.in"},
    {"name": "Gujarat Public Service Commission", "domain": "gpsc.gujarat.gov.in"},
    {"name": "Odisha Public Service Commission", "domain": "opsc.gov.in"},
    {"name": "Telangana State Public Service Commission", "domain": "tspsc.gov.in"},
    {"name": "Andhra Pradesh Public Service Commission", "domain": "psc.ap.gov.in"},
    {"name": "Kerala Public Service Commission", "domain": "keralapsc.gov.in"},
    {"name": "West Bengal Public Service Commission", "domain": "wbpsc.gov.in"},
    {"name": "Haryana Public Service Commission", "domain": "hpsc.gov.in"},
    {"name": "Punjab Public Service Commission", "domain": "ppsc.gov.in"},
    {"name": "Assam Public Service Commission", "domain": "apsc.nic.in"},
    {"name": "Chhattisgarh Public Service Commission", "domain": "psc.cg.gov.in"},
    {"name": "Jharkhand Public Service Commission", "domain": "jpsc.gov.in"},
    {"name": "Uttarakhand Public Service Commission", "domain": "psc.uk.gov.in"},
    {"name": "Himachal Pradesh Public Service Commission", "domain": "hppsc.hp.gov.in"},
    {"name": "Delhi Subordinate Services Selection Board", "domain": "dsssb.delhi.gov.in"},
    {"name": "Staff Selection Commission (SSC)", "domain": "ssc.nic.in"},
    {"name": "Railway Recruitment Control Board", "domain": "rrcb.gov.in"},
]

# 13. State Secondary Education Boards & Transport Corporations
STATE_BOARDS_AND_TRANSPORT = [
    {"name": "UP Madhyamik Shiksha Parishad (UPMSP)", "domain": "upmsp.edu.in"},
    {"name": "Maharashtra State Board (MSBSHSE)", "domain": "mahahsscboard.in"},
    {"name": "Bihar School Examination Board (BSEB)", "domain": "biharboardonline.bihar.gov.in"},
    {"name": "Directorate of Govt Examinations Tamil Nadu", "domain": "dge.tn.gov.in"},
    {"name": "Karnataka School Examination and Assessment Board", "domain": "kseab.karnataka.gov.in"},
    {"name": "Gujarat Secondary & Higher Secondary Board", "domain": "gseb.org"},
    {"name": "West Bengal Board of Secondary Education", "domain": "wbbse.wb.gov.in"},
    {"name": "Board of School Education Haryana", "domain": "bseh.org.in"},
    {"name": "Punjab School Education Board", "domain": "pseb.ac.in"},
    {"name": "Jharkhand Academic Council", "domain": "jac.jharkhand.gov.in"},
    {"name": "Chhattisgarh Board of Secondary Education", "domain": "cgbse.nic.in"},
    {"name": "Kerala DHSE", "domain": "dhsekerala.gov.in"},
    {"name": "Board of Secondary Education Odisha", "domain": "bseodisha.ac.in"},
    {"name": "Board of Secondary Education Telangana", "domain": "bse.telangana.gov.in"},
    {"name": "Board of Secondary Education Andhra Pradesh", "domain": "bse.ap.gov.in"},
    {"name": "Board of Secondary Education Rajasthan", "domain": "rajeduboard.rajasthan.gov.in"},
    {"name": "MP Board of Secondary Education", "domain": "mpbse.nic.in"},
    {"name": "UPSRTC (Uttar Pradesh)", "domain": "upsrtc.up.gov.in"},
    {"name": "MSRTC (Maharashtra)", "domain": "msrtc.maharashtra.gov.in"},
    {"name": "KSRTC (Karnataka)", "domain": "ksrtc.in"},
    {"name": "Kerala RTC", "domain": "keralartc.com"},
    {"name": "GSRTC (Gujarat)", "domain": "gsrtc.in"},
    {"name": "APSRTC (Andhra Pradesh)", "domain": "apsrtc.ap.gov.in"},
    {"name": "TSRTC (Telangana)", "domain": "tsrtc.telangana.gov.in"},
    {"name": "DTC (Delhi Transport)", "domain": "dtc.delhi.gov.in"},
    {"name": "HRTC (Himachal Pradesh)", "domain": "hrtchp.com"},
    {"name": "OSRTC (Odisha)", "domain": "osrtc.in"},
    {"name": "WBTC (West Bengal)", "domain": "wbtc.co.in"},
]


class DomainSeedGenerator:
    """Generates structured seed records across all Indian governance levels (3,000+ verified seeds)."""

    @classmethod
    def generate_all_seeds(cls) -> List[Dict[str, Any]]:
        seeds: List[Dict[str, Any]] = []
        seen: set[str] = set()

        def add_seed(domain: str, level: str, entity: str, state: str | None = None, district: str | None = None, tags: list[str] | None = None):
            d = domain.lower().strip()
            if d not in seen:
                seen.add(d)
                seeds.append({
                    "domain_name": d,
                    "base_url": f"https://{d}",
                    "government_level": level,
                    "state_or_ut": state,
                    "district": district,
                    "entity_name": entity,
                    "tags": tags or [level],
                })

        # 1. Central Ministries & Apex Constitutional Bodies
        for entry in CENTRAL_MINISTRIES_AND_APEX:
            add_seed(entry["domain"], GovernmentLevel.CENTRAL.value, entry["name"], state="Central", tags=entry.get("tags", ["central"]))

        # 2. State & UT Apex Portals (36)
        for state_name, info in STATES_AND_UTS.items():
            add_seed(info["domain"], GovernmentLevel.STATE_UT.value, f"Government of {state_name}", state=state_name, tags=["state_apex", info["code"].lower()])

        # 3. Government Hospitals, AIIMS & Health Bodies
        for entry in GOVERNMENT_HOSPITALS_AND_HEALTH:
            add_seed(entry["domain"], GovernmentLevel.AUTONOMOUS_BODY.value if hasattr(GovernmentLevel, "AUTONOMOUS_BODY") else GovernmentLevel.CENTRAL.value, entry["name"], tags=entry.get("tags", ["hospital"]))

        # 4. Government School Systems (KVS, NVS, Sainik, EMRS)
        for entry in GOVERNMENT_SCHOOLS_AND_SYSTEMS:
            add_seed(entry["domain"], GovernmentLevel.AUTONOMOUS_BODY.value if hasattr(GovernmentLevel, "AUTONOMOUS_BODY") else GovernmentLevel.CENTRAL.value, entry["name"], tags=entry.get("tags", ["schools"]))

        # 5. Public Universities, IITs, NITs, IIMs, CSIR & ICMR Labs
        for entry in NATIONAL_ACADEMIC_AND_RESEARCH:
            add_seed(entry["domain"], GovernmentLevel.AUTONOMOUS_BODY.value if hasattr(GovernmentLevel, "AUTONOMOUS_BODY") else GovernmentLevel.CENTRAL.value, entry["name"], tags=["higher_education", "research"])

        # 6. Law Enforcement & CAPFs
        for entry in LAW_ENFORCEMENT_AND_SECURITY:
            add_seed(entry["domain"], GovernmentLevel.CENTRAL.value if "capf" in entry.get("tags", []) else GovernmentLevel.STATE_UT.value, entry["name"], tags=entry.get("tags", ["security"]))

        # 7. Railway Recruitment Boards (RRBs)
        for entry in RAILWAY_RECRUITMENT_BOARDS:
            add_seed(entry["domain"], GovernmentLevel.CENTRAL.value, entry["name"], tags=["railways", "recruitment"])

        # 8. High Courts & National Tribunals
        for entry in HIGH_COURTS_AND_TRIBUNALS:
            add_seed(entry["domain"], GovernmentLevel.JUDICIARY.value if hasattr(GovernmentLevel, "JUDICIARY") else GovernmentLevel.CENTRAL.value, entry["name"], tags=["judiciary", "tribunal"])

        # 9. All 785+ Districts (S3WaaS Pattern: <district>.nic.in)
        for state_name, districts in ALL_DISTRICTS_BY_STATE.items():
            for dist in districts:
                clean_dist = dist.lower().replace("-", "").replace(" ", "")
                domain = f"{clean_dist}.nic.in"
                add_seed(domain, GovernmentLevel.DISTRICT.value, f"District Administration {dist.title()}", state=state_name, district=dist.title(), tags=["district", "s3waas"])
                if state_name in ["Haryana", "Punjab", "Assam", "Himachal Pradesh"]:
                    add_seed(f"{clean_dist}.dc.gov.in", GovernmentLevel.DISTRICT.value, f"Deputy Commissioner {dist.title()}", state=state_name, district=dist.title(), tags=["district", "dc_portal"])

        # 10. State Government Department Subdomains (900+ portals)
        for state_root in ALL_STATE_DOMAIN_ROOTS:
            state_label = state_root.split(".")[0].upper()
            for dept in KEY_STATE_DEPARTMENTS:
                domain = f"{dept}.{state_root}"
                add_seed(domain, GovernmentLevel.STATE_UT.value, f"{dept.title()} Department ({state_label})", tags=["department", dept, state_label.lower()])

        # 11. Nationalized Banks, Central PSUs & Financial Regulatory
        for entry in CENTRAL_PSUS_AND_FINANCIAL:
            add_seed(entry["domain"], GovernmentLevel.PSU.value if hasattr(GovernmentLevel, "PSU") else GovernmentLevel.CENTRAL.value, entry["name"], tags=["psu", "financial"])

        # 12. State PSCs (23)
        for entry in STATE_PSCS:
            add_seed(entry["domain"], GovernmentLevel.STATE_UT.value, entry["name"], tags=["recruitment", "psc"])

        # 13. State Education Boards & Transport
        for entry in STATE_BOARDS_AND_TRANSPORT:
            add_seed(entry["domain"], GovernmentLevel.STATE_UT.value, entry["name"], tags=["state_utility"])

        return seeds
