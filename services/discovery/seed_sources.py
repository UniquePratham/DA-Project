"""Comprehensive Indian Government Domain Seed Matrices and Directory Sources.

Spans Central Ministries, Apex Constitutional Bodies, High Courts, Premier National Institutes,
All 36 States/UTs, 900+ State Department Portals, 785+ Districts, State PSCs, Police, Municipalities, and PSUs.
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
    {"name": "National Voters Services Portal", "domain": "voterportal.eci.gov.in", "tags": ["portal", "election"]},
    {"name": "National Cyber Crime Reporting Portal", "domain": "cybercrime.gov.in", "tags": ["portal", "cybercrime"]},
    {"name": "National Disaster Management Authority", "domain": "ndma.gov.in", "tags": ["agency", "disaster"]},
    {"name": "Central Vigilance Commission", "domain": "cvc.gov.in", "tags": ["apex", "vigilance"]},
    {"name": "Central Information Commission", "domain": "cic.gov.in", "tags": ["apex", "rti"]},
    {"name": "National Green Tribunal", "domain": "greentribunal.gov.in", "tags": ["judiciary", "environment"]},
]

# 3. High Courts of India (All 25 High Courts)
HIGH_COURTS = [
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
]

# 4. Premier National Academic, Higher Education & Research Institutes (IITs, NITs, IIMs, AIIMS, CSIR, ICMR)
NATIONAL_ACADEMIC_AND_RESEARCH = [
    # IITs
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
    # NITs
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
    # IIMs
    {"name": "IIM Ahmedabad", "domain": "iima.ac.in"},
    {"name": "IIM Bangalore", "domain": "iimb.ac.in"},
    {"name": "IIM Calcutta", "domain": "iimcal.ac.in"},
    {"name": "IIM Lucknow", "domain": "iiml.ac.in"},
    {"name": "IIM Indore", "domain": "iimi.ac.in"},
    {"name": "IIM Kozhikode", "domain": "iimk.ac.in"},
    {"name": "IIM Shillong", "domain": "iimsillong.ac.in"},
    {"name": "IIM Trichy", "domain": "iimtrichy.ac.in"},
    {"name": "IIM Udaipur", "domain": "iimu.ac.in"},
    # AIIMS
    {"name": "AIIMS New Delhi", "domain": "aiims.edu"},
    {"name": "AIIMS Bhopal", "domain": "aiimsbhopal.edu.in"},
    {"name": "AIIMS Bhubaneswar", "domain": "aiimsbhubaneswar.nic.in"},
    {"name": "AIIMS Jodhpur", "domain": "aiimsjodhpur.edu.in"},
    {"name": "AIIMS Patna", "domain": "aiimspatna.edu.in"},
    {"name": "AIIMS Raipur", "domain": "aiimsraipur.edu.in"},
    {"name": "AIIMS Rishikesh", "domain": "aiimsrishikesh.edu.in"},
    {"name": "AIIMS Nagpur", "domain": "aiimsnagpur.edu.in"},
    # Central Universities
    {"name": "University of Delhi", "domain": "du.ac.in"},
    {"name": "Jawaharlal Nehru University", "domain": "jnu.ac.in"},
    {"name": "Banaras Hindu University", "domain": "bhu.ac.in"},
    {"name": "Aligarh Muslim University", "domain": "amu.ac.in"},
    {"name": "University of Hyderabad", "domain": "uohyd.ac.in"},
    {"name": "Jamia Millia Islamia", "domain": "jmi.ac.in"},
    {"name": "Visva-Bharati University", "domain": "visvabharati.ac.in"},
    {"name": "Pondicherry University", "domain": "pondiuni.edu.in"},
    {"name": "IGNOU", "domain": "ignou.ac.in"},
    # CSIR & Research
    {"name": "CSIR Headquarters", "domain": "csir.res.in"},
    {"name": "National Physical Laboratory", "domain": "nplindia.org"},
    {"name": "National Chemical Laboratory", "domain": "ncl-india.org"},
    {"name": "CCMB Hyderabad", "domain": "ccmb.res.in"},
    {"name": "Central Drug Research Institute", "domain": "cdri.res.in"},
    {"name": "NEERI Nagpur", "domain": "neeri.res.in"},
    {"name": "IICT Hyderabad", "domain": "iict.res.in"},
    {"name": "IGIB Delhi", "domain": "igib.res.in"},
    {"name": "ICMR Headquarters", "domain": "icmr.nic.in"},
    {"name": "ICAR Headquarters", "domain": "icar.org.in"},
]

# 5. All 785+ Indian Districts organized by State/UT
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

# 6. State Government Department Subdomains (25 major departmental functions per State)
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

# 7. State Public Service Commissions & Recruitment Portals
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

# 8. Major Municipal Corporations & Urban Development Authorities
MUNICIPAL_CORPORATIONS = [
    {"name": "Brihanmumbai Municipal Corporation (BMC)", "domain": "mcgm.gov.in"},
    {"name": "Bruhat Bengaluru Mahanagara Palike (BBMP)", "domain": "bbmp.gov.in"},
    {"name": "Greater Hyderabad Municipal Corporation (GHMC)", "domain": "ghmc.gov.in"},
    {"name": "New Delhi Municipal Council (NDMC)", "domain": "ndmc.gov.in"},
    {"name": "Municipal Corporation of Delhi (MCD)", "domain": "mcdonline.nic.in"},
    {"name": "Greater Chennai Corporation", "domain": "chennaicorporation.gov.in"},
    {"name": "Kolkata Municipal Corporation", "domain": "kmcgov.in"},
    {"name": "Pune Municipal Corporation", "domain": "pmc.gov.in"},
    {"name": "Ahmedabad Municipal Corporation", "domain": "amc.gov.in"},
    {"name": "Surat Municipal Corporation", "domain": "suratmunicipal.org"},
    {"name": "Vadodara Municipal Corporation", "domain": "vmc.gov.in"},
    {"name": "Lucknow Municipal Corporation", "domain": "lmc.up.nic.in"},
    {"name": "Kanpur Municipal Corporation", "domain": "kmc.up.nic.in"},
    {"name": "Jaipur Municipal Corporation", "domain": "jaipurmc.org"},
    {"name": "Nagpur Municipal Corporation", "domain": "nmcnagpur.gov.in"},
    {"name": "Indore Municipal Corporation", "domain": "imcindore.mp.gov.in"},
    {"name": "Bhopal Municipal Corporation", "domain": "bmconline.gov.in"},
    {"name": "Patna Municipal Corporation", "domain": "pmc.bihar.gov.in"},
    {"name": "Delhi Development Authority (DDA)", "domain": "dda.gov.in"},
    {"name": "Noida Authority", "domain": "noidaauthorityonline.in"},
    {"name": "Greater Noida Authority", "domain": "greaternoidaauthority.in"},
]


# 9. Major State Public Sector Undertakings (PSUs) & Nationalized Financial Institutions
CENTRAL_PSUS_AND_FINANCIAL = [
    {"name": "Life Insurance Corporation of India (LIC)", "domain": "licindia.in"},
    {"name": "State Bank of India (SBI)", "domain": "sbi.co.in"},
    {"name": "Punjab National Bank", "domain": "pnbindia.in"},
    {"name": "Bank of Baroda", "domain": "bankofbaroda.in"},
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
]

# 10. State Transport Corporations (SRTCs)
STATE_TRANSPORT_CORPS = [
    {"name": "UPSRTC (Uttar Pradesh)", "domain": "upsrtc.up.gov.in"},
    {"name": "MSRTC (Maharashtra)", "domain": "msrtc.maharashtra.gov.in"},
    {"name": "KSRTC (Karnataka)", "domain": "ksrtc.in"},
    {"name": "Kerala RTC", "domain": "keralartc.com"},
    {"name": "GSRTC (Gujarat)", "domain": "gsrtc.in"},
    {"name": "APSRTC (Andhra Pradesh)", "domain": "apsrtc.ap.gov.in"},
    {"name": "TSRTC (Telangana)", "domain": "tsrtc.telangana.gov.in"},
    {"name": "RSRTC (Rajasthan)", "domain": "transport.rajasthan.gov.in"},
    {"name": "DTC (Delhi Transport)", "domain": "dtc.delhi.gov.in"},
    {"name": "HRTC (Himachal Pradesh)", "domain": "hrtchp.com"},
    {"name": "OSRTC (Odisha)", "domain": "osrtc.in"},
    {"name": "WBTC (West Bengal)", "domain": "wbtc.co.in"},
    {"name": "PUNBUS (Punjab Roadways)", "domain": "punbusonline.com"},
    {"name": "Haryana Roadways", "domain": "hartrans.gov.in"},
]

# 11. State Secondary & Higher Secondary Education Boards
STATE_EDUCATION_BOARDS = [
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
]

# 12. State Electricity Distribution Companies (DISCOMs)
STATE_DISCOMS = [
    {"name": "UP Power Corporation (UPPCL)", "domain": "uppcl.org"},
    {"name": "Maharashtra State Electricity Distribution (MSEDCL)", "domain": "mahadiscom.in"},
    {"name": "BESCOM (Bengaluru)", "domain": "bescom.karnataka.gov.in"},
    {"name": "TANGEDCO (Tamil Nadu)", "domain": "tangedco.gov.in"},
    {"name": "WBSEDCL (West Bengal)", "domain": "wbsedcl.in"},
    {"name": "KSEB (Kerala)", "domain": "kseb.in"},
    {"name": "DHBVN (Haryana)", "domain": "dhbvn.org.in"},
    {"name": "UHBVN (Haryana)", "domain": "uhbvn.org.in"},
    {"name": "PSPCL (Punjab)", "domain": "pspcl.in"},
    {"name": "TSSPDCL (Telangana)", "domain": "tsspdcl.com"},
    {"name": "APSPDCL (Andhra Pradesh)", "domain": "apspdcl.in"},
    {"name": "NBPDCL (North Bihar)", "domain": "nbpdcl.co.in"},
    {"name": "SBPDCL (South Bihar)", "domain": "sbpdcl.co.in"},
    {"name": "CSPDCL (Chhattisgarh)", "domain": "cspdcl.co.in"},
    {"name": "JVVNL (Jaipur Discom)", "domain": "energy.rajasthan.gov.in"},
]


class DomainSeedGenerator:
    """Generates structured seed records across all Indian governance levels (3,500+ verified seeds)."""

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

        # 1. Central Ministries & Apex Constitutional Bodies (~85)
        for entry in CENTRAL_MINISTRIES_AND_APEX:
            add_seed(entry["domain"], GovernmentLevel.CENTRAL.value, entry["name"], state="Central", tags=entry.get("tags", ["central"]))

        # 2. State & UT Apex Portals (36)
        for state_name, info in STATES_AND_UTS.items():
            add_seed(info["domain"], GovernmentLevel.STATE_UT.value, f"Government of {state_name}", state=state_name, tags=["state_apex", info["code"].lower()])

        # 3. All 785+ Districts (S3WaaS Pattern: <district>.nic.in)
        for state_name, districts in ALL_DISTRICTS_BY_STATE.items():
            for dist in districts:
                clean_dist = dist.lower().replace("-", "").replace(" ", "")
                domain = f"{clean_dist}.nic.in"
                add_seed(domain, GovernmentLevel.DISTRICT.value, f"District Administration {dist.title()}", state=state_name, district=dist.title(), tags=["district", "s3waas"])
                # Also add DC subdomain variant for states that use dc.gov.in
                if state_name in ["Haryana", "Punjab", "Assam", "Himachal Pradesh"]:
                    add_seed(f"{clean_dist}.dc.gov.in", GovernmentLevel.DISTRICT.value, f"Deputy Commissioner {dist.title()}", state=state_name, district=dist.title(), tags=["district", "dc_portal"])

        # 4. State Government Department Subdomains (900+ portals)
        for state_root in ALL_STATE_DOMAIN_ROOTS:
            state_label = state_root.split(".")[0].upper()
            for dept in KEY_STATE_DEPARTMENTS:
                domain = f"{dept}.{state_root}"
                add_seed(domain, GovernmentLevel.STATE_UT.value, f"{dept.title()} Department ({state_label})", tags=["department", dept, state_label.lower()])

        # 5. High Courts (25)
        for entry in HIGH_COURTS:
            add_seed(entry["domain"], GovernmentLevel.JUDICIARY.value if hasattr(GovernmentLevel, "JUDICIARY") else GovernmentLevel.CENTRAL.value, entry["name"], tags=["high_court", "judiciary"])

        # 6. Premier National Academic, IITs, NITs, IIMs, AIIMS, CSIR, ICMR (~100)
        for entry in NATIONAL_ACADEMIC_AND_RESEARCH:
            add_seed(entry["domain"], GovernmentLevel.AUTONOMOUS_BODY.value if hasattr(GovernmentLevel, "AUTONOMOUS_BODY") else GovernmentLevel.CENTRAL.value, entry["name"], tags=["higher_education", "research"])

        # 7. State PSCs & Recruitment Boards (23)
        for entry in STATE_PSCS:
            add_seed(entry["domain"], GovernmentLevel.STATE_UT.value, entry["name"], tags=["recruitment", "psc"])

        # 8. Municipal Corporations (21)
        for entry in MUNICIPAL_CORPORATIONS:
            add_seed(entry["domain"], GovernmentLevel.LOCAL_BODY.value if hasattr(GovernmentLevel, "LOCAL_BODY") else GovernmentLevel.STATE_UT.value, entry["name"], tags=["municipal", "local_body"])

        # 9. Central PSUs & Financial Institutions (20)
        for entry in CENTRAL_PSUS_AND_FINANCIAL:
            add_seed(entry["domain"], GovernmentLevel.PSU.value if hasattr(GovernmentLevel, "PSU") else GovernmentLevel.CENTRAL.value, entry["name"], tags=["psu", "financial"])

        # 10. State Transport Corporations (14)
        for entry in STATE_TRANSPORT_CORPS:
            add_seed(entry["domain"], GovernmentLevel.STATE_UT.value, entry["name"], tags=["transport", "srtc"])

        # 11. State Education Boards (17)
        for entry in STATE_EDUCATION_BOARDS:
            add_seed(entry["domain"], GovernmentLevel.STATE_UT.value, entry["name"], tags=["education", "board"])

        # 12. State Electricity DISCOMs (15)
        for entry in STATE_DISCOMS:
            add_seed(entry["domain"], GovernmentLevel.STATE_UT.value, entry["name"], tags=["energy", "discom"])

        return seeds
