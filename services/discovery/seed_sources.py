"""Comprehensive Indian Government Domain Seed Matrices and Directory Sources.

Spans Central Ministries, Apex Constitutional Bodies, High Courts, National Institutes,
All 36 States/UTs, 500+ State Department Portals, and all 785+ Indian Districts.
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
]

# 3. All 785+ Indian Districts organized by State/UT
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

# 4. State Government Department Subdomains (e.g. police.up.gov.in, revenue.rajasthan.gov.in)
KEY_STATE_DEPARTMENTS = [
    "police", "revenue", "education", "health", "transport", "finance", "forest",
    "agriculture", "pwd", "wrd", "excise", "tourism", "labour", "food",
    "socialwelfare", "panchayat", "industry", "commercialtax", "highcourt", "energy"
]

STATE_DOMAIN_ROOTS = [
    "up.gov.in", "maharashtra.gov.in", "rajasthan.gov.in", "mp.gov.in", "gujarat.gov.in",
    "karnataka.gov.in", "tn.gov.in", "kerala.gov.in", "bihar.gov.in", "wb.gov.in",
    "odisha.gov.in", "punjab.gov.in", "haryana.gov.in", "assam.gov.in", "cgstate.gov.in",
    "jharkhand.gov.in", "telangana.gov.in", "ap.gov.in", "uk.gov.in", "himachal.nic.in",
    "delhi.gov.in", "jk.gov.in", "goa.gov.in"
]


class DomainSeedGenerator:
    """Generates structured seed records across all Indian governance levels."""

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

        # 1. Central Ministries & Apex
        for entry in CENTRAL_MINISTRIES_AND_APEX:
            add_seed(entry["domain"], GovernmentLevel.CENTRAL.value, entry["name"], tags=entry.get("tags", ["central"]))

        # 2. State & UT Apex Portals
        for state_name, info in STATES_AND_UTS.items():
            add_seed(info["domain"], GovernmentLevel.STATE_UT.value, f"Government of {state_name}", state=state_name, tags=["state_apex", info["code"].lower()])

        # 3. All 785+ Districts (S3WaaS Pattern: <district>.nic.in)
        for state_name, districts in ALL_DISTRICTS_BY_STATE.items():
            for dist in districts:
                clean_dist = dist.lower().replace("-", "").replace(" ", "")
                domain = f"{clean_dist}.nic.in"
                add_seed(domain, GovernmentLevel.DISTRICT.value, f"District Administration {dist.title()}", state=state_name, district=dist.title(), tags=["district", "s3waas"])

        # 4. State Government Department Subdomains (500+ portals)
        for state_root in STATE_DOMAIN_ROOTS:
            state_label = state_root.split(".")[0].upper()
            for dept in KEY_STATE_DEPARTMENTS:
                domain = f"{dept}.{state_root}"
                add_seed(domain, GovernmentLevel.STATE_UT.value, f"{dept.title()} Department ({state_label})", tags=["department", dept, state_label.lower()])

        return seeds
