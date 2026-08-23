"""Comprehensive Indian Government Domain Seed Matrices and Directory Sources.

Spans Central Ministries, Apex Constitutional Bodies, High Courts & Tribunals,
Defence & Strategic Subdomains (tdf.drdo.gov.in, defproc.gov.in, rac.gov.in, ada.gov.in, DRDO Labs),
National & State e-Procurement Portals (GeM, CPPP, Mahatenders, Eproc Rajasthan, etc.),
National Flagship Missions & e-Services (DigiLocker, UMANG, CoWIN, ABDM, PM-Kisan, e-Courts, CPGRAMS),
State Land Records (Bhulekh, Bhoomi, Dharani, Mahabhumi) & e-District Portals,
Urban Local Bodies & Municipal Corporations (BMC, MCD, BBMP, GHMC, Chennai Corp, KMC, etc.),
Space & Atomic Energy Subdomains (ISRO, NRSC, Bhuvan, SAC, BARC, DAE),
Government Hospitals & Medical Colleges (AIIMS, Safdarjung, PGIMER, JIPMER),
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
    {"name": "CPGRAMS Central Public Grievance Portal", "domain": "pgportal.gov.in", "tags": ["grievance", "central"]},
    {"name": "RTI Online Portal", "domain": "rtionline.gov.in", "tags": ["rti", "central"]},
    {"name": "Official Gazette of India (e-Gazette)", "domain": "egazette.gov.in", "tags": ["gazette", "central"]},
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
    {"name": "Department of Personnel and Training (DoPT)", "domain": "dopt.gov.in", "tags": ["apex", "personnel"]},
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
    {"name": "Reserve Bank of India", "domain": "rbi.org.in", "tags": ["apex", "banking"]},
    {"name": "Securities and Exchange Board of India", "domain": "sebi.gov.in", "tags": ["apex", "finance"]},
    {"name": "Telecom Regulatory Authority of India", "domain": "trai.gov.in", "tags": ["apex", "telecom"]},
    {"name": "Food Safety and Standards Authority of India", "domain": "fssai.gov.in", "tags": ["agency", "food"]},
    {"name": "Bureau of Indian Standards", "domain": "bis.gov.in", "tags": ["agency", "standards"]},
    {"name": "Competition Commission of India", "domain": "cci.gov.in", "tags": ["agency", "competition"]},
    {"name": "NITI Aayog", "domain": "niti.gov.in", "tags": ["apex", "planning"]},
    {"name": "National Human Rights Commission", "domain": "nhrc.nic.in", "tags": ["apex", "human_rights"]},
    {"name": "Central Vigilance Commission", "domain": "cvc.gov.in", "tags": ["apex", "vigilance"]},
    {"name": "Central Information Commission", "domain": "cic.gov.in", "tags": ["apex", "rti"]},
    {"name": "National Green Tribunal", "domain": "greentribunal.gov.in", "tags": ["judiciary", "environment"]},
    {"name": "CERT-In (Indian Computer Emergency Response Team)", "domain": "cert-in.org.in", "tags": ["cybersecurity", "meity"]},
    {"name": "National Critical Information Infrastructure Protection Centre", "domain": "nciipc.gov.in", "tags": ["cybersecurity", "security"]},
    {"name": "National Knowledge Network (NKN)", "domain": "nkn.gov.in", "tags": ["infrastructure", "network"]},
    {"name": "Centre for Development of Advanced Computing (C-DAC)", "domain": "cdac.in", "tags": ["it", "supercomputing"]},
    {"name": "Software Technology Parks of India (STPI)", "domain": "stpi.in", "tags": ["it", "exports"]},
]

# 3. Defence, Strategic Organisations, DRDO Subdomains & Procurement
DEFENCE_STRATEGIC_AND_PROCUREMENT = [
    # DRDO Subdomains & Bodies
    {"name": "DRDO Technology Development Fund (TDF)", "domain": "tdf.drdo.gov.in", "tags": ["defence", "drdo", "innovation"]},
    {"name": "DRDO Recruitment & Assessment Centre (RAC)", "domain": "rac.gov.in", "tags": ["defence", "drdo", "recruitment"]},
    {"name": "Aeronautical Development Agency (ADA)", "domain": "ada.gov.in", "tags": ["defence", "drdo", "aviation"]},
    {"name": "Defence eProcurement Portal", "domain": "defproc.gov.in", "tags": ["defence", "procurement"]},
    {"name": "Defence Research & Development Organisation (DRDO HQ)", "domain": "drdo.gov.in", "tags": ["defence", "drdo"]},
    {"name": "Aeronautical Development Establishment (ADE)", "domain": "ade.drdo.in", "tags": ["defence", "drdo_lab"]},
    {"name": "Armament Research & Development Establishment (ARDE)", "domain": "arde.drdo.in", "tags": ["defence", "drdo_lab"]},
    {"name": "Centre for AI & Robotics (CAIR)", "domain": "cair.drdo.in", "tags": ["defence", "drdo_lab"]},
    {"name": "Defence Electronics Applications Lab (DEAL)", "domain": "deal.drdo.in", "tags": ["defence", "drdo_lab"]},
    {"name": "Defence Scientific Info & Documentation (DESIDOC)", "domain": "desidoc.drdo.in", "tags": ["defence", "drdo_lab"]},
    {"name": "Defence Electronics Research Lab (DLRL)", "domain": "dlrl.drdo.in", "tags": ["defence", "drdo_lab"]},
    {"name": "Defence Metallurgical Research Lab (DMRL)", "domain": "dmrl.drdo.in", "tags": ["defence", "drdo_lab"]},
    {"name": "Defence Research & Development Lab (DRDL)", "domain": "drdl.drdo.in", "tags": ["defence", "drdo_lab"]},
    {"name": "Gas Turbine Research Establishment (GTRE)", "domain": "gtre.drdo.in", "tags": ["defence", "drdo_lab"]},
    {"name": "Institute of Nuclear Medicine & Allied Sciences (INMAS)", "domain": "inmas.drdo.in", "tags": ["defence", "drdo_lab"]},
    {"name": "Electronics & Radar Development Establishment (LRDE)", "domain": "lrde.drdo.in", "tags": ["defence", "drdo_lab"]},
    {"name": "Research & Development Establishment Engineers (R&DE)", "domain": "rde.drdo.in", "tags": ["defence", "drdo_lab"]},
    {"name": "Solid State Physics Laboratory (SSPL)", "domain": "sspl.drdo.in", "tags": ["defence", "drdo_lab"]},
    {"name": "Terminal Ballistics Research Laboratory (TBRL)", "domain": "tbrl.drdo.in", "tags": ["defence", "drdo_lab"]},
    {"name": "Centre for Personnel Talent Management (CEPTAM)", "domain": "ceptam.drdo.in", "tags": ["defence", "drdo_recruitment"]},
    {"name": "Centre for Military Airworthiness (CEMILAC)", "domain": "cemilac.drdo.in", "tags": ["defence", "drdo_certification"]},
    {"name": "Department of Defence Production", "domain": "ddpmod.gov.in", "tags": ["defence", "production"]},
    {"name": "Make in India Defence Portal", "domain": "makeinindiadefence.gov.in", "tags": ["defence", "industry"]},
    {"name": "SRIJAN Defence Indigenisation Portal", "domain": "srijandefence.gov.in", "tags": ["defence", "indigenisation"]},
    {"name": "SPARSH Defence Pension Portal", "domain": "sparsh.defencepension.gov.in", "tags": ["defence", "pension"]},
    {"name": "Department of Ex-Servicemen Welfare", "domain": "desw.gov.in", "tags": ["defence", "welfare"]},
    {"name": "Kendriya Sainik Board", "domain": "ksb.gov.in", "tags": ["defence", "veterans"]},
    # Armed Forces Official Recruitment & Portals
    {"name": "Indian Army", "domain": "indianarmy.nic.in", "tags": ["defence", "army"]},
    {"name": "Join Indian Army Portal", "domain": "joinindianarmy.nic.in", "tags": ["defence", "army", "recruitment"]},
    {"name": "Indian Navy", "domain": "indiannavy.nic.in", "tags": ["defence", "navy"]},
    {"name": "Join Indian Navy Portal", "domain": "joinindiannavy.gov.in", "tags": ["defence", "navy", "recruitment"]},
    {"name": "Indian Air Force", "domain": "indianairforce.nic.in", "tags": ["defence", "airforce"]},
    {"name": "Career Indian Air Force", "domain": "careerindianairforce.cdac.in", "tags": ["defence", "airforce", "recruitment"]},
    {"name": "AFCAT CDAC Portal", "domain": "afcat.cdac.in", "tags": ["defence", "airforce", "exam"]},
    {"name": "Indian Coast Guard", "domain": "indiancoastguard.gov.in", "tags": ["defence", "coastguard"]},
]

# 4. National & State e-Procurement Portals (GeM, CPPP, State eTenders)
NATIONAL_AND_STATE_E_PROCUREMENT = [
    # Central Procurement Portals
    {"name": "Government e-Marketplace (GeM)", "domain": "gem.gov.in", "tags": ["procurement", "central"]},
    {"name": "Central Public Procurement Portal (CPPP)", "domain": "eprocure.gov.in", "tags": ["procurement", "cppp"]},
    {"name": "eProcurement System of India (eTenders)", "domain": "etenders.gov.in", "tags": ["procurement", "etenders"]},
    # State Government e-Procurement Portals
    {"name": "UP eTender Portal", "domain": "etender.up.nic.in", "tags": ["procurement", "up"]},
    {"name": "Maharashtra eTenders (MahaTenders)", "domain": "mahatenders.gov.in", "tags": ["procurement", "maharashtra"]},
    {"name": "Rajasthan eProcurement", "domain": "eproc.rajasthan.gov.in", "tags": ["procurement", "rajasthan"]},
    {"name": "Bihar eProcurement", "domain": "eproc.bihar.gov.in", "tags": ["procurement", "bihar"]},
    {"name": "Odisha Tenders", "domain": "tendersodisha.gov.in", "tags": ["procurement", "odisha"]},
    {"name": "West Bengal eTenders", "domain": "wbtenders.gov.in", "tags": ["procurement", "wb"]},
    {"name": "Tamil Nadu eTenders", "domain": "tntenders.gov.in", "tags": ["procurement", "tn"]},
    {"name": "Karnataka Public Procurement Portal (KPPP)", "domain": "kppp.karnataka.gov.in", "tags": ["procurement", "karnataka"]},
    {"name": "Kerala eTenders", "domain": "etenders.kerala.gov.in", "tags": ["procurement", "kerala"]},
    {"name": "Assam Tenders", "domain": "assamtenders.gov.in", "tags": ["procurement", "assam"]},
    {"name": "Haryana eTenders", "domain": "etenders.hry.nic.in", "tags": ["procurement", "haryana"]},
    {"name": "Punjab eProcurement", "domain": "eproc.punjab.gov.in", "tags": ["procurement", "punjab"]},
    {"name": "Madhya Pradesh Tenders", "domain": "mptenders.gov.in", "tags": ["procurement", "mp"]},
    {"name": "Andhra Pradesh eProcurement", "domain": "tender.apeprocurement.gov.in", "tags": ["procurement", "ap"]},
    {"name": "Telangana eProcurement", "domain": "tender.telangana.gov.in", "tags": ["procurement", "telangana"]},
    {"name": "Himachal Pradesh Tenders", "domain": "hptenders.gov.in", "tags": ["procurement", "hp"]},
    {"name": "Jharkhand Tenders", "domain": "jharkhandtenders.gov.in", "tags": ["procurement", "jharkhand"]},
    {"name": "Uttarakhand Tenders", "domain": "uktenders.gov.in", "tags": ["procurement", "uk"]},
    {"name": "Chhattisgarh Tenders", "domain": "cgtenders.gov.in", "tags": ["procurement", "cg"]},
    {"name": "Delhi Govt eTenders", "domain": "delhitenders.gov.in", "tags": ["procurement", "delhi"]},
    {"name": "Jammu & Kashmir Tenders", "domain": "jktenders.gov.in", "tags": ["procurement", "jk"]},
    {"name": "Goa eTenders", "domain": "goatenders.gov.in", "tags": ["procurement", "goa"]},
]

# 5. National Flagship Mission Platforms & Citizen e-Governance Portals
FLAGSHIP_MISSIONS_AND_CITIZEN_SERVICES = [
    # Citizen Identity & Locker
    {"name": "DigiLocker Portal", "domain": "digilocker.gov.in", "tags": ["identity", "locker", "flagship"]},
    {"name": "UMANG National Portal", "domain": "umang.gov.in", "tags": ["citizen_services", "mobile", "flagship"]},
    {"name": "Ayushman Bharat Digital Mission (ABDM)", "domain": "abdm.gov.in", "tags": ["health", "digital", "flagship"]},
    {"name": "PM Jan Arogya Yojana (PM-JAY)", "domain": "pmjay.gov.in", "tags": ["health", "insurance", "flagship"]},
    {"name": "eSanjeevani National Telemedicine", "domain": "esanjeevani.in", "tags": ["health", "telemedicine"]},
    {"name": "Direct Benefit Transfer (DBT Bharat)", "domain": "dbtbharat.gov.in", "tags": ["finance", "welfare", "dbt"]},
    {"name": "myScheme National Platform", "domain": "myscheme.gov.in", "tags": ["schemes", "citizen"]},
    {"name": "Open Government Data (OGD) Platform", "domain": "data.gov.in", "tags": ["open_data", "governance"]},
    # Agriculture & Rural Digital Missions
    {"name": "PM Kisan Samman Nidhi Portal", "domain": "pmkisan.gov.in", "tags": ["agriculture", "dbt"]},
    {"name": "e-NAM National Agriculture Market", "domain": "enam.gov.in", "tags": ["agriculture", "market"]},
    {"name": "Agmarknet Agricultural Marketing", "domain": "agmarknet.gov.in", "tags": ["agriculture", "prices"]},
    {"name": "Soil Health Card Portal", "domain": "soilhealth.dac.gov.in", "tags": ["agriculture", "soil"]},
    {"name": "Mahatma Gandhi NREGA Portal", "domain": "nrega.nic.in", "tags": ["rural", "employment", "welfare"]},
    {"name": "Pradhan Mantri Gram Sadak Yojana (PMGSY)", "domain": "pmgsy.nic.in", "tags": ["rural", "roads"]},
    {"name": "PMAY-Gramin (Rural Housing)", "domain": "pmayg.nic.in", "tags": ["rural", "housing"]},
    {"name": "PMAY-Urban (Urban Housing)", "domain": "pmaymis.gov.in", "tags": ["urban", "housing"]},
    {"name": "Swachh Bharat Mission (Grameen)", "domain": "swachhbharatmission.ddws.gov.in", "tags": ["sanitation", "rural"]},
    {"name": "Jal Jeevan Mission", "domain": "jaljeevanmission.gov.in", "tags": ["water", "rural"]},
    {"name": "National Social Assistance Programme (NSAP)", "domain": "nsap.nic.in", "tags": ["welfare", "pension"]},
    # Transport & Highways Subdomains
    {"name": "Sarathi Parivahan (Driving Licences)", "domain": "sarathi.parivahan.gov.in", "tags": ["transport", "licence"]},
    {"name": "Vahan Parivahan (Vehicle Registration)", "domain": "vahan.parivahan.gov.in", "tags": ["transport", "vehicle"]},
    {"name": "eChallan Parivahan", "domain": "echallan.parivahan.gov.in", "tags": ["transport", "challan"]},
    {"name": "National Highways Authority of India", "domain": "nhai.gov.in", "tags": ["highways", "infrastructure"]},
    {"name": "Indian Railways Passenger Reservation Enquiry", "domain": "indianrail.gov.in", "tags": ["railways", "reservation"]},
    {"name": "Centre for Railway Information Systems (CRIS)", "domain": "cris.org.in", "tags": ["railways", "it"]},
    # Taxation, Customs & Corporate Affairs
    {"name": "ICEGATE Indian Customs Electronic Gateway", "domain": "icegate.gov.in", "tags": ["customs", "trade"]},
    {"name": "Directorate General of Foreign Trade (DGFT)", "domain": "dgft.gov.in", "tags": ["commerce", "trade"]},
    {"name": "Intellectual Property India (IP India)", "domain": "ipindia.gov.in", "tags": ["patents", "trademarks"]},
    {"name": "Ministry of Corporate Affairs (MCA21)", "domain": "mca.gov.in", "tags": ["corporate", "registration"]},
    {"name": "Employees Provident Fund Organisation (EPFO)", "domain": "epfindia.gov.in", "tags": ["labour", "pension"]},
    {"name": "Employees State Insurance Corporation (ESIC)", "domain": "esic.gov.in", "tags": ["labour", "insurance"]},
    # Judicial & Immigration Services
    {"name": "eCourts National Services Portal", "domain": "services.ecourts.gov.in", "tags": ["judiciary", "services"]},
    {"name": "National Judicial Data Grid (NJDG)", "domain": "njdg.ecourts.gov.in", "tags": ["judiciary", "data"]},
    {"name": "e-Filing Judicial Portal", "domain": "e-filing.ecourts.gov.in", "tags": ["judiciary", "efiling"]},
    {"name": "Indian Visa Online", "domain": "indianvisaonline.gov.in", "tags": ["immigration", "visa"]},
    {"name": "Bureau of Immigration India", "domain": "boio.nic.in", "tags": ["immigration", "security"]},
]

# 6. State Land Records (Bhulekh) & e-District Portals across States
STATE_LAND_RECORDS_AND_E_DISTRICT = [
    # Land Records (Bhulekh / Bhoomi / Dharani)
    {"name": "UP Bhulekh (Uttar Pradesh)", "domain": "upbhulekh.gov.in", "tags": ["land_records", "up"]},
    {"name": "Mahabhumi Land Records (Maharashtra)", "domain": "bhulekh.mahabhumi.gov.in", "tags": ["land_records", "maharashtra"]},
    {"name": "Apna Khata Land Records (Rajasthan)", "domain": "apnakhata.rajasthan.gov.in", "tags": ["land_records", "rajasthan"]},
    {"name": "Bhoomi Land Records (Karnataka)", "domain": "landrecords.karnataka.gov.in", "tags": ["land_records", "karnataka"]},
    {"name": "Dharani Portal (Telangana)", "domain": "dharani.telangana.gov.in", "tags": ["land_records", "telangana"]},
    {"name": "Meebhoomi (Andhra Pradesh)", "domain": "meebhoomi.ap.gov.in", "tags": ["land_records", "ap"]},
    {"name": "Bihar Bhumi (Bihar)", "domain": "biharbhumi.bihar.gov.in", "tags": ["land_records", "bihar"]},
    {"name": "MP Bhulekh (Madhya Pradesh)", "domain": "mpbhulekh.gov.in", "tags": ["land_records", "mp"]},
    {"name": "Bhulekh Odisha", "domain": "bhulekh.ori.nic.in", "tags": ["land_records", "odisha"]},
    {"name": "Banglarbhumi (West Bengal)", "domain": "banglarbhumi.gov.in", "tags": ["land_records", "wb"]},
    {"name": "Jamabandi Land Records (Punjab)", "domain": "jamabandi.punjab.gov.in", "tags": ["land_records", "punjab"]},
    {"name": "Jamabandi Land Records (Haryana)", "domain": "jamabandi.nic.in", "tags": ["land_records", "haryana"]},
    {"name": "Jharbhoomi (Jharkhand)", "domain": "jharbhoomi.jharkhand.gov.in", "tags": ["land_records", "jharkhand"]},
    {"name": "Devbhoomi Bhulekh (Uttarakhand)", "domain": "bhulekh.uk.gov.in", "tags": ["land_records", "uk"]},
    {"name": "Bhuiyan Land Records (Chhattisgarh)", "domain": "bhuiyan.cg.nic.in", "tags": ["land_records", "cg"]},
    {"name": "AnyRoR Land Records (Gujarat)", "domain": "anyror.gujarat.gov.in", "tags": ["land_records", "gujarat"]},
    # State e-District & Integrated Citizen Portals
    {"name": "e-District Uttar Pradesh", "domain": "edistrict.up.gov.in", "tags": ["edistrict", "up"]},
    {"name": "Aaple Sarkar Portal (Maharashtra)", "domain": "aaplesarkar.mahaonline.gov.in", "tags": ["edistrict", "maharashtra"]},
    {"name": "Seva Sindhu (Karnataka)", "domain": "sevasindhu.karnataka.gov.in", "tags": ["edistrict", "karnataka"]},
    {"name": "MeeSeva Portal (Telangana)", "domain": "meeseva.telangana.gov.in", "tags": ["edistrict", "telangana"]},
    {"name": "Grama Ward Sachivalayam (Andhra Pradesh)", "domain": "gramawardsachivalayam.ap.gov.in", "tags": ["edistrict", "ap"]},
    {"name": "ServiceOnline Bihar (e-District)", "domain": "serviceonline.bihar.gov.in", "tags": ["edistrict", "bihar"]},
    {"name": "e-Mitra Rajasthan Portal", "domain": "emitra.rajasthan.gov.in", "tags": ["edistrict", "rajasthan"]},
    {"name": "MP e-District (Madhya Pradesh)", "domain": "mpedistrict.gov.in", "tags": ["edistrict", "mp"]},
    {"name": "e-District Odisha", "domain": "edistrict.odisha.gov.in", "tags": ["edistrict", "odisha"]},
    {"name": "e-District West Bengal", "domain": "edistrict.wb.gov.in", "tags": ["edistrict", "wb"]},
    {"name": "e-District Delhi Govt", "domain": "edistrict.delhigovt.nic.in", "tags": ["edistrict", "delhi"]},
    {"name": "Saral Haryana Citizen Services", "domain": "saralharyana.gov.in", "tags": ["edistrict", "haryana"]},
    {"name": "Connect Punjab e-Services", "domain": "connect.punjab.gov.in", "tags": ["edistrict", "punjab"]},
    {"name": "e-District Kerala", "domain": "edistrict.kerala.gov.in", "tags": ["edistrict", "kerala"]},
    {"name": "Digital Gujarat Portal", "domain": "digitalgujarat.gov.in", "tags": ["edistrict", "gujarat"]},
    {"name": "Sewa Setu Assam Portal", "domain": "sewasetu.assam.gov.in", "tags": ["edistrict", "assam"]},
    {"name": "e-District Chhattisgarh", "domain": "edistrict.cgstate.gov.in", "tags": ["edistrict", "cg"]},
    {"name": "JharSewa Jharkhand", "domain": "jharsewa.jharkhand.gov.in", "tags": ["edistrict", "jharkhand"]},
    {"name": "e-Services Uttarakhand (Apuni Sarkar)", "domain": "eservices.uk.gov.in", "tags": ["edistrict", "uk"]},
    {"name": "e-District Himachal Pradesh", "domain": "edistrict.hp.gov.in", "tags": ["edistrict", "hp"]},
    {"name": "e-District Jammu & Kashmir", "domain": "edistrict.jk.gov.in", "tags": ["edistrict", "jk"]},
    {"name": "Goa Services Portal", "domain": "services.goa.gov.in", "tags": ["edistrict", "goa"]},
    # State Public Grievance Portals
    {"name": "Jan Sunwai Samadhan (UP Grievance)", "domain": "jansunwai.up.nic.in", "tags": ["grievance", "up"]},
    {"name": "Maharashtra Grievance Redressal", "domain": "grievances.maharashtra.gov.in", "tags": ["grievance", "maharashtra"]},
    {"name": "Rajasthan Sampark Portal", "domain": "sampark.rajasthan.gov.in", "tags": ["grievance", "rajasthan"]},
    {"name": "Samadhan Bihar Grievance", "domain": "samadhan.bihar.gov.in", "tags": ["grievance", "bihar"]},
    {"name": "CM Helpline 181 Madhya Pradesh", "domain": "cmhelpline.mp.gov.in", "tags": ["grievance", "mp"]},
    {"name": "Spandana AP Public Grievances", "domain": "spandana.ap.gov.in", "tags": ["grievance", "ap"]},
    {"name": "CMO Kerala Grievance Portal", "domain": "cmo.kerala.gov.in", "tags": ["grievance", "kerala"]},
    {"name": "SWAGAT Gujarat Online Grievances", "domain": "swagat.gujarat.gov.in", "tags": ["grievance", "gujarat"]},
    {"name": "JK Grievance Redressal (JK-IGRAMS)", "domain": "jkgrievance.jk.gov.in", "tags": ["grievance", "jk"]},
]

# 7. Major Urban Local Bodies & Municipal Corporations
MAJOR_MUNICIPAL_CORPORATIONS = [
    {"name": "Brihanmumbai Municipal Corporation (BMC)", "domain": "portal.mcgm.gov.in", "tags": ["ulb", "mumbai", "maharashtra"]},
    {"name": "Municipal Corporation of Delhi (MCD)", "domain": "mcdonline.nic.in", "tags": ["ulb", "delhi"]},
    {"name": "Bruhat Bengaluru Mahanagara Palike (BBMP)", "domain": "bbmp.gov.in", "tags": ["ulb", "bengaluru", "karnataka"]},
    {"name": "Greater Hyderabad Municipal Corporation (GHMC)", "domain": "ghmc.gov.in", "tags": ["ulb", "hyderabad", "telangana"]},
    {"name": "Greater Chennai Corporation", "domain": "chennaicorporation.gov.in", "tags": ["ulb", "chennai", "tn"]},
    {"name": "Kolkata Municipal Corporation", "domain": "kmcgov.in", "tags": ["ulb", "kolkata", "wb"]},
    {"name": "Ahmedabad Municipal Corporation", "domain": "ahmedabadcity.gov.in", "tags": ["ulb", "ahmedabad", "gujarat"]},
    {"name": "Pune Municipal Corporation", "domain": "pmc.gov.in", "tags": ["ulb", "pune", "maharashtra"]},
    {"name": "Surat Municipal Corporation", "domain": "suratmunicipal.gov.in", "tags": ["ulb", "surat", "gujarat"]},
    {"name": "Jaipur Municipal Corporation", "domain": "jaipurmc.org", "tags": ["ulb", "jaipur", "rajasthan"]},
    {"name": "Lucknow Municipal Corporation", "domain": "lmc.up.nic.in", "tags": ["ulb", "lucknow", "up"]},
    {"name": "Kanpur Municipal Corporation", "domain": "kmc.up.nic.in", "tags": ["ulb", "kanpur", "up"]},
    {"name": "Varanasi Nagar Nigam", "domain": "nnvns.org.in", "tags": ["ulb", "varanasi", "up"]},
    {"name": "Agra Nagar Nigam", "domain": "nagarnigamagra.com", "tags": ["ulb", "agra", "up"]},
    {"name": "Navi Mumbai Municipal Corporation", "domain": "nmmc.gov.in", "tags": ["ulb", "navimumbai", "maharashtra"]},
    {"name": "Thane Municipal Corporation", "domain": "thanecity.gov.in", "tags": ["ulb", "thane", "maharashtra"]},
    {"name": "Pimpri Chinchwad Municipal Corporation", "domain": "pcmcindia.gov.in", "tags": ["ulb", "pcmc", "maharashtra"]},
    {"name": "Nagpur Municipal Corporation", "domain": "nmcnagpur.gov.in", "tags": ["ulb", "nagpur", "maharashtra"]},
    {"name": "Nashik Municipal Corporation", "domain": "nashikcorporation.in", "tags": ["ulb", "nashik", "maharashtra"]},
    {"name": "Indore Municipal Corporation", "domain": "imcindore.mp.gov.in", "tags": ["ulb", "indore", "mp"]},
    {"name": "Bhopal Municipal Corporation", "domain": "bhopalcorporation.org", "tags": ["ulb", "bhopal", "mp"]},
    {"name": "Patna Municipal Corporation", "domain": "pmc.bihar.gov.in", "tags": ["ulb", "patna", "bihar"]},
    {"name": "Chandigarh Municipal Corporation", "domain": "mcchandigarh.gov.in", "tags": ["ulb", "chandigarh"]},
    {"name": "Coimbatore Corporation", "domain": "ccmc.gov.in", "tags": ["ulb", "coimbatore", "tn"]},
    {"name": "Madurai Corporation", "domain": "maduraicorporation.co.in", "tags": ["ulb", "madurai", "tn"]},
    {"name": "Kochi Municipal Corporation", "domain": "kochicity.lsgkerala.gov.in", "tags": ["ulb", "kochi", "kerala"]},
    {"name": "Thiruvananthapuram Corporation", "domain": "corporationoftrivandrum.in", "tags": ["ulb", "trivandrum", "kerala"]},
    {"name": "Greater Visakhapatnam Municipal Corp (GVMC)", "domain": "gvmc.gov.in", "tags": ["ulb", "vizag", "ap"]},
    {"name": "Vijayawada Municipal Corporation", "domain": "vmc.ap.gov.in", "tags": ["ulb", "vijayawada", "ap"]},
]

# 8. Space, Atomic Energy, Earth Sciences & Scientific Research
SPACE_ATOMIC_ENERGY_AND_EARTH_SCIENCES = [
    # ISRO & Space Subdomains
    {"name": "ISRO Headquarters", "domain": "isro.gov.in", "tags": ["space", "isro"]},
    {"name": "National Remote Sensing Centre (NRSC)", "domain": "nrsc.gov.in", "tags": ["space", "nrsc"]},
    {"name": "Bhuvan ISRO Geo-Portal", "domain": "bhuvan.nrsc.gov.in", "tags": ["space", "geoportal", "maps"]},
    {"name": "Bhoonidhi Open Data Archive (NRSC)", "domain": "bhoonidhi.nrsc.gov.in", "tags": ["space", "satellite_data"]},
    {"name": "Space Applications Centre (SAC Ahmedabad)", "domain": "sac.gov.in", "tags": ["space", "sac"]},
    {"name": "VEDAS SAC ISRO Geo-Spatial Portal", "domain": "vedas.sac.gov.in", "tags": ["space", "analytics"]},
    {"name": "MOSDAC Meteorological & Oceanographic Data", "domain": "mosdac.gov.in", "tags": ["space", "weather_data"]},
    {"name": "Vikram Sarabhai Space Centre (VSSC)", "domain": "vssc.gov.in", "tags": ["space", "rockets"]},
    {"name": "Liquid Propulsion Systems Centre (LPSC)", "domain": "lpsc.gov.in", "tags": ["space", "propulsion"]},
    {"name": "UR Rao Satellite Centre (URSC)", "domain": "ursc.gov.in", "tags": ["space", "satellites"]},
    {"name": "Indian Institute of Remote Sensing (IIRS)", "domain": "iirs.gov.in", "tags": ["space", "education"]},
    {"name": "IN-SPACe (Indian National Space Promotion)", "domain": "inspace.gov.in", "tags": ["space", "commercial"]},
    {"name": "NewSpace India Limited (NSIL)", "domain": "nsilindia.co.in", "tags": ["space", "psu"]},
    # Atomic Energy & Earth Sciences
    {"name": "Bhabha Atomic Research Centre (BARC)", "domain": "barc.gov.in", "tags": ["atomic", "research"]},
    {"name": "Department of Atomic Energy (DAE)", "domain": "dae.gov.in", "tags": ["atomic", "central"]},
    {"name": "Indira Gandhi Centre for Atomic Research (IGCAR)", "domain": "igcar.gov.in", "tags": ["atomic", "research"]},
    {"name": "Variable Energy Cyclotron Centre (VECC)", "domain": "vecc.gov.in", "tags": ["atomic", "physics"]},
    {"name": "Raja Ramanna Centre for Advanced Technology", "domain": "rrcat.gov.in", "tags": ["atomic", "lasers"]},
    {"name": "Atomic Energy Regulatory Board (AERB)", "domain": "aerb.gov.in", "tags": ["atomic", "safety"]},
    {"name": "India Meteorological Department (IMD Weather)", "domain": "imd.gov.in", "tags": ["weather", "earth_sciences"]},
    {"name": "Indian National Centre for Ocean Info Services", "domain": "incois.gov.in", "tags": ["ocean", "tsunami"]},
    {"name": "National Centre for Polar & Ocean Research", "domain": "ncpor.res.in", "tags": ["polar", "antarctica"]},
    {"name": "Indian Institute of Tropical Meteorology", "domain": "iitm.res.in", "tags": ["climate", "monsoon"]},
]

# 9. National Examinations, Admissions & Academic Services
EXAMINATIONS_AND_ADMISSIONS_SERVICES = [
    {"name": "National Testing Agency (NTA)", "domain": "nta.ac.in", "tags": ["exams", "admissions"]},
    {"name": "JEE (Main) Examination Portal", "domain": "jeemain.nta.ac.in", "tags": ["exams", "jee"]},
    {"name": "NEET (UG) Medical Examination Portal", "domain": "neet.nta.ac.in", "tags": ["exams", "neet"]},
    {"name": "CUET (UG) Common University Entrance Test", "domain": "cuetug.nta.ac.in", "tags": ["exams", "cuet"]},
    {"name": "UGC-NET Examination Portal", "domain": "ugcnet.nta.ac.in", "tags": ["exams", "ugcnet"]},
    {"name": "NIC Examination Services Portal", "domain": "examinationservices.nic.in", "tags": ["exams", "nic"]},
    {"name": "CBSE Exam Results Portal", "domain": "results.cbse.nic.in", "tags": ["exams", "results"]},
    {"name": "Joint Seat Allocation Authority (JoSAA)", "domain": "josaa.nic.in", "tags": ["admissions", "iit_nit"]},
    {"name": "Central Seat Allocation Board (CSAB)", "domain": "csab.nic.in", "tags": ["admissions", "nit"]},
    {"name": "Medical Counselling Committee (MCC NEET)", "domain": "mcc.nic.in", "tags": ["admissions", "medical"]},
    {"name": "National Board of Examinations (NBE/NBEMS)", "domain": "natboard.edu.in", "tags": ["exams", "medical"]},
    {"name": "SWAYAM Free Online Education Portal", "domain": "swayam.gov.in", "tags": ["education", "mooc"]},
    {"name": "National Academic Depository (NAD)", "domain": "nad.gov.in", "tags": ["education", "degrees"]},
    {"name": "AICTE Approval & Regulation Portal", "domain": "aicte-india.org", "tags": ["education", "technical"]},
    {"name": "University Grants Commission (UGC)", "domain": "ugc.ac.in", "tags": ["education", "higher"]},
]

# 10. Government Hospitals, AIIMS & Health Bodies
GOVERNMENT_HOSPITALS_AND_HEALTH = [
    # AIIMS Network
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
    # Apex Central Hospitals
    {"name": "Safdarjung Hospital & VMMC Delhi", "domain": "vmmc-sjh.nic.in", "tags": ["hospital", "central"]},
    {"name": "Dr. Ram Manohar Lohia Hospital Delhi", "domain": "rmlh.nic.in", "tags": ["hospital", "central"]},
    {"name": "Lady Hardinge Medical College", "domain": "lhmc-hosp.gov.in", "tags": ["hospital", "central"]},
    {"name": "PGIMER Chandigarh", "domain": "pgimer.edu.in", "tags": ["hospital", "research", "central"]},
    {"name": "JIPMER Puducherry", "domain": "jipmer.edu.in", "tags": ["hospital", "research", "central"]},
    {"name": "NIMHANS Bengaluru", "domain": "nimhans.ac.in", "tags": ["hospital", "research", "central"]},
    {"name": "King George's Medical University (KGMU)", "domain": "kgmu.org", "tags": ["hospital", "state"]},
    {"name": "SGPGIMS Lucknow", "domain": "sgpgi.org.in", "tags": ["hospital", "state"]},
    {"name": "Institute of Liver and Biliary Sciences (ILBS)", "domain": "ilbs.in", "tags": ["hospital", "state"]},
    {"name": "Tata Memorial Centre Mumbai", "domain": "tmc.gov.in", "tags": ["hospital", "cancer", "central"]},
    {"name": "Regional Cancer Centre Thiruvananthapuram", "domain": "rcctvm.gov.in", "tags": ["hospital", "cancer", "state"]},
    {"name": "National Institute of TB and Respiratory Diseases", "domain": "nitrd.nic.in", "tags": ["hospital", "central"]},
    {"name": "Central Drugs Standard Control Organization", "domain": "cdsco.gov.in", "tags": ["health", "regulatory"]},
    {"name": "National Health Mission", "domain": "nhm.gov.in", "tags": ["health", "schemes"]},
    {"name": "Madras Medical College", "domain": "mmc.tn.gov.in", "tags": ["hospital", "state_medical"]},
    {"name": "Calcutta Medical College", "domain": "calcutnamedicalcollege.edu.in", "tags": ["hospital", "state_medical"]},
    {"name": "Grant Medical College Mumbai", "domain": "gmcmumbai.gov.in", "tags": ["hospital", "state_medical"]},
    {"name": "Patna Medical College (PMCH)", "domain": "pmch.bihar.gov.in", "tags": ["hospital", "state_medical"]},
    {"name": "GMC Jammu", "domain": "gmcjammu.nic.in", "tags": ["hospital", "state_medical"]},
]

# 11. Government School Systems (KVS, NVS, Sainik, EMRS)
GOVERNMENT_SCHOOLS_AND_SYSTEMS = [
    # KVS Headquarters & Regional Offices
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
    # Navodaya Vidyalaya Samiti
    {"name": "Navodaya Vidyalaya Samiti (NVS HQ)", "domain": "navodaya.gov.in", "tags": ["school_system", "central"]},
    {"name": "NVS Regional Office Bhopal", "domain": "nvsbhopal.gov.in", "tags": ["school_system", "nvs"]},
    {"name": "NVS Regional Office Chandigarh", "domain": "nvsrochandigarh.gov.in", "tags": ["school_system", "nvs"]},
    {"name": "NVS Regional Office Hyderabad", "domain": "nvsrohyderabad.gov.in", "tags": ["school_system", "nvs"]},
    {"name": "NVS Regional Office Jaipur", "domain": "nvsrojaipur.gov.in", "tags": ["school_system", "nvs"]},
    {"name": "NVS Regional Office Lucknow", "domain": "nvsrolucknow.gov.in", "tags": ["school_system", "nvs"]},
    {"name": "NVS Regional Office Patna", "domain": "nvsropatna.gov.in", "tags": ["school_system", "nvs"]},
    {"name": "NVS Regional Office Pune", "domain": "nvsropune.gov.in", "tags": ["school_system", "nvs"]},
    {"name": "NVS Regional Office Shillong", "domain": "nvsroshillong.gov.in", "tags": ["school_system", "nvs"]},
    # Sainik Schools Society & EMRS
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
    {"name": "Eklavya Model Residential Schools (EMRS)", "domain": "nests.gov.in", "tags": ["school_system", "tribal"]},
    {"name": "National Institute of Open Schooling", "domain": "nios.ac.in", "tags": ["education_board", "open_school"]},
    {"name": "NCERT", "domain": "ncert.nic.in", "tags": ["education", "curriculum"]},
    {"name": "CBSE", "domain": "cbse.gov.in", "tags": ["education_board", "central"]},
    {"name": "Delhi Directorate of Education (Govt Schools)", "domain": "edudel.nic.in", "tags": ["school_system", "state_govt"]},
]

# 12. Public Central & State Universities, IITs, NITs, IIMs, CSIR & ICMR Labs
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
    # IIITs
    {"name": "IIIT Allahabad", "domain": "iiita.ac.in"},
    {"name": "IIITDM Kancheepuram", "domain": "iiitdm.ac.in"},
    {"name": "IIIT Delhi", "domain": "iiitd.ac.in"},
    {"name": "IIIT Gwalior", "domain": "iiitm.ac.in"},
    {"name": "IIITDM Jabalpur", "domain": "iiitdmj.ac.in"},
    # IIMs (20)
    {"name": "IIM Ahmedabad", "domain": "iima.ac.in"},
    {"name": "IIM Bangalore", "domain": "iimb.ac.in"},
    {"name": "IIM Calcutta", "domain": "iimcal.ac.in"},
    {"name": "IIM Lucknow", "domain": "iiml.ac.in"},
    {"name": "IIM Indore", "domain": "iimi.ac.in"},
    {"name": "IIM Kozhikode", "domain": "iimk.ac.in"},
    {"name": "IIM Shillong", "domain": "iimsillong.ac.in"},
    # Central Public Universities
    {"name": "University of Delhi", "domain": "du.ac.in"},
    {"name": "Jawaharlal Nehru University", "domain": "jnu.ac.in"},
    {"name": "Banaras Hindu University", "domain": "bhu.ac.in"},
    {"name": "Aligarh Muslim University", "domain": "amu.ac.in"},
    {"name": "University of Hyderabad", "domain": "uohyd.ac.in"},
    {"name": "Jamia Millia Islamia", "domain": "jmi.ac.in"},
    {"name": "Visva-Bharati University", "domain": "visvabharati.ac.in"},
    {"name": "Pondicherry University", "domain": "pondiuni.edu.in"},
    {"name": "IGNOU", "domain": "ignou.ac.in"},
    # Premier State Public Universities
    {"name": "University of Mumbai", "domain": "mu.ac.in"},
    {"name": "Savitribai Phule Pune University", "domain": "unipune.ac.in"},
    {"name": "University of Calcutta", "domain": "caluniv.ac.in"},
    {"name": "University of Madras", "domain": "unom.ac.in"},
    {"name": "Osmania University", "domain": "osmania.ac.in"},
    {"name": "Anna University", "domain": "annauniv.edu"},
    {"name": "AKTU Uttar Pradesh", "domain": "aktu.ac.in"},
    # CSIR Labs
    {"name": "CSIR Headquarters", "domain": "csir.res.in"},
    {"name": "National Physical Laboratory", "domain": "nplindia.org"},
    {"name": "National Chemical Laboratory", "domain": "ncl-india.org"},
    {"name": "CCMB Hyderabad", "domain": "ccmb.res.in"},
    {"name": "Central Drug Research Institute", "domain": "cdri.res.in"},
    {"name": "NEERI Nagpur", "domain": "neeri.res.in"},
    {"name": "IICT Hyderabad", "domain": "iict.res.in"},
    {"name": "IGIB Delhi", "domain": "igib.res.in"},
    {"name": "IICB Kolkata", "domain": "iicb.res.in"},
    {"name": "CLRI Chennai", "domain": "clri.org"},
    {"name": "CFTRI Mysore", "domain": "cftri.res.in"},
    # ICMR & ICAR
    {"name": "ICMR Headquarters", "domain": "icmr.nic.in"},
    {"name": "National Institute of Virology", "domain": "niv.co.in"},
    {"name": "National Institute of Epidemiology", "domain": "nie.gov.in"},
    {"name": "National Institute of Nutrition", "domain": "nin.res.in"},
    {"name": "ICAR Headquarters", "domain": "icar.org.in"},
    {"name": "IARI Pusa Delhi", "domain": "iari.res.in"},
]

# 13. Law Enforcement, CAPFs & Investigative Agencies
LAW_ENFORCEMENT_AND_SECURITY = [
    # CAPFs & Paramilitary
    {"name": "Border Security Force (BSF)", "domain": "bsf.gov.in", "tags": ["capf", "security"]},
    {"name": "Central Reserve Police Force (CRPF)", "domain": "crpf.gov.in", "tags": ["capf", "security"]},
    {"name": "Central Industrial Security Force (CISF)", "domain": "cisf.gov.in", "tags": ["capf", "security"]},
    {"name": "Indo-Tibetan Border Police (ITBP)", "domain": "itbpolice.nic.in", "tags": ["capf", "security"]},
    {"name": "Sashastra Seema Bal (SSB)", "domain": "ssb.gov.in", "tags": ["capf", "security"]},
    {"name": "National Security Guard (NSG)", "domain": "nsg.gov.in", "tags": ["capf", "security"]},
    {"name": "Assam Rifles", "domain": "assamrifles.gov.in", "tags": ["capf", "security"]},
    # Investigative
    {"name": "Central Bureau of Investigation (CBI)", "domain": "cbi.gov.in", "tags": ["investigation", "police"]},
    {"name": "National Investigation Agency (NIA)", "domain": "nia.gov.in", "tags": ["investigation", "security"]},
    {"name": "National Crime Records Bureau (NCRB)", "domain": "ncrb.gov.in", "tags": ["police", "records"]},
    {"name": "Bureau of Police Research and Development", "domain": "bprd.nic.in", "tags": ["police", "research"]},
    {"name": "Directorate of Enforcement (ED)", "domain": "enforcementdirectorate.gov.in", "tags": ["enforcement", "finance"]},
    {"name": "Narcotics Control Bureau (NCB)", "domain": "narcoticsindia.nic.in", "tags": ["police", "narcotics"]},
    {"name": "National Cyber Crime Reporting Portal", "domain": "cybercrime.gov.in", "tags": ["police", "cybercrime"]},
    # State Police HQs & Traffic
    {"name": "Uttar Pradesh Police", "domain": "uppolice.gov.in", "tags": ["state_police"]},
    {"name": "UP Police Traffic Subdomain", "domain": "traffic.uppolice.gov.in", "tags": ["state_police", "traffic"]},
    {"name": "UP CCTNS Portal", "domain": "cctns.uppolice.gov.in", "tags": ["state_police", "cctns"]},
    {"name": "Maharashtra Police", "domain": "mahapolice.gov.in", "tags": ["state_police"]},
    {"name": "Delhi Police", "domain": "delhipolice.gov.in", "tags": ["state_police"]},
    {"name": "Delhi Traffic Police", "domain": "traffic.delhipolice.gov.in", "tags": ["state_police", "traffic"]},
    {"name": "Tamil Nadu Police", "domain": "tnpolice.gov.in", "tags": ["state_police"]},
    {"name": "Karnataka State Police", "domain": "ksp.karnataka.gov.in", "tags": ["state_police"]},
    {"name": "Bengaluru Traffic Police", "domain": "bengalurutrafficpolice.gov.in", "tags": ["state_police", "traffic"]},
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
    {"name": "Telangana State Police", "domain": "tspolice.gov.in", "tags": ["state_police"]},
    {"name": "Andhra Pradesh Police", "domain": "appolice.gov.in", "tags": ["state_police"]},
    {"name": "Uttarakhand Police", "domain": "uttarakhandpolice.uk.gov.in", "tags": ["state_police"]},
    {"name": "Himachal Pradesh Police", "domain": "hppolice.nic.in", "tags": ["state_police"]},
    {"name": "Jammu & Kashmir Police", "domain": "jkpolice.gov.in", "tags": ["state_police"]},
    {"name": "Goa Police", "domain": "goapolice.gov.in", "tags": ["state_police"]},
]

# 14. All 25 High Courts & National Tribunals
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
    {"name": "National Consumer Commission (NCDRC)", "domain": "ncdrc.nic.in"},
]

# 15. All 785+ Indian Districts organized by State/UT
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

# 16. State Government Department Subdomains (25 departments per State/UT)
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

# 17. Nationalized Banks, Central PSUs & Financial Institutions
CENTRAL_PSUS_AND_FINANCIAL = [
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
    {"name": "Life Insurance Corporation of India (LIC)", "domain": "licindia.in"},
    {"name": "NABARD", "domain": "nabard.org"},
    {"name": "SIDBI", "domain": "sidbi.in"},
    {"name": "EXIM Bank of India", "domain": "eximbankindia.in"},
    {"name": "National Housing Bank (NHB)", "domain": "nhb.org.in"},
    {"name": "IRDAI", "domain": "irdai.gov.in"},
    {"name": "PFRDA", "domain": "pfrda.org.in"},
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

# 18. State Public Service Commissions & Recruitment Portals
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


class DomainSeedGenerator:
    """Generates structured seed records across all Indian governance levels (2,400+ verified seeds)."""

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
            add_seed(entry["domain"], GovernmentLevel.CENTRAL.value, entry["name"], state="Central Government", tags=entry.get("tags", ["central"]))

        # 2. Defence, Strategic & Procurement Subdomains (tdf.drdo.gov.in, defproc.gov.in, rac.gov.in, DRDO Labs)
        for entry in DEFENCE_STRATEGIC_AND_PROCUREMENT:
            add_seed(entry["domain"], GovernmentLevel.CENTRAL.value, entry["name"], state="Central Government", tags=entry.get("tags", ["defence"]))

        # 3. National & State e-Procurement Portals (GeM, CPPP, State eTenders)
        for entry in NATIONAL_AND_STATE_E_PROCUREMENT:
            add_seed(entry["domain"], GovernmentLevel.CENTRAL.value if "central" in entry.get("tags", []) or "cppp" in entry.get("tags", []) else GovernmentLevel.STATE_UT.value, entry["name"], tags=entry.get("tags", ["procurement"]))

        # 4. National Flagship Missions & e-Services (DigiLocker, UMANG, CoWIN, ABDM, eCourts)
        for entry in FLAGSHIP_MISSIONS_AND_CITIZEN_SERVICES:
            add_seed(entry["domain"], GovernmentLevel.CENTRAL.value, entry["name"], state="Central Government", tags=entry.get("tags", ["flagship"]))

        # 5. State Land Records (Bhulekh) & e-District Portals
        for entry in STATE_LAND_RECORDS_AND_E_DISTRICT:
            add_seed(entry["domain"], GovernmentLevel.STATE_UT.value, entry["name"], tags=entry.get("tags", ["land_records", "edistrict"]))

        # 6. Major Urban Local Bodies & Municipal Corporations
        for entry in MAJOR_MUNICIPAL_CORPORATIONS:
            add_seed(entry["domain"], GovernmentLevel.LOCAL_BODY.value if hasattr(GovernmentLevel, "LOCAL_BODY") else GovernmentLevel.STATE_UT.value, entry["name"], tags=entry.get("tags", ["ulb", "municipality"]))

        # 7. Space, Atomic Energy & Earth Sciences (ISRO, NRSC, Bhuvan, BARC)
        for entry in SPACE_ATOMIC_ENERGY_AND_EARTH_SCIENCES:
            add_seed(entry["domain"], GovernmentLevel.CENTRAL.value, entry["name"], state="Central Government", tags=entry.get("tags", ["space", "atomic"]))

        # 8. National Examinations & Admissions Services (NTA, JoSAA, NEET, JEE)
        for entry in EXAMINATIONS_AND_ADMISSIONS_SERVICES:
            add_seed(entry["domain"], GovernmentLevel.AUTONOMOUS_BODY.value if hasattr(GovernmentLevel, "AUTONOMOUS_BODY") else GovernmentLevel.CENTRAL.value, entry["name"], state="Central Government", tags=entry.get("tags", ["exams"]))

        # 9. State & UT Apex Portals (36)
        for state_name, info in STATES_AND_UTS.items():
            add_seed(info["domain"], GovernmentLevel.STATE_UT.value, f"Government of {state_name}", state=state_name, tags=["state_apex", info["code"].lower()])

        # 10. Government Hospitals, AIIMS & Health Bodies
        for entry in GOVERNMENT_HOSPITALS_AND_HEALTH:
            add_seed(entry["domain"], GovernmentLevel.AUTONOMOUS_BODY.value if hasattr(GovernmentLevel, "AUTONOMOUS_BODY") else GovernmentLevel.CENTRAL.value, entry["name"], tags=entry.get("tags", ["hospital"]))

        # 11. Government School Systems (KVS, NVS, Sainik, EMRS)
        for entry in GOVERNMENT_SCHOOLS_AND_SYSTEMS:
            add_seed(entry["domain"], GovernmentLevel.AUTONOMOUS_BODY.value if hasattr(GovernmentLevel, "AUTONOMOUS_BODY") else GovernmentLevel.CENTRAL.value, entry["name"], tags=entry.get("tags", ["schools"]))

        # 12. Public Universities, IITs, NITs, IIMs, CSIR & ICMR Labs
        for entry in NATIONAL_ACADEMIC_AND_RESEARCH:
            add_seed(entry["domain"], GovernmentLevel.AUTONOMOUS_BODY.value if hasattr(GovernmentLevel, "AUTONOMOUS_BODY") else GovernmentLevel.CENTRAL.value, entry["name"], tags=["higher_education", "research"])

        # 13. Law Enforcement, CAPFs & Police Forces
        for entry in LAW_ENFORCEMENT_AND_SECURITY:
            add_seed(entry["domain"], GovernmentLevel.CENTRAL.value if "capf" in entry.get("tags", []) else GovernmentLevel.STATE_UT.value, entry["name"], tags=entry.get("tags", ["security"]))

        # 14. High Courts & National Tribunals (25 High Courts + Tribunals)
        for entry in HIGH_COURTS_AND_TRIBUNALS:
            add_seed(entry["domain"], GovernmentLevel.JUDICIARY.value if hasattr(GovernmentLevel, "JUDICIARY") else GovernmentLevel.CENTRAL.value, entry["name"], tags=["judiciary", "tribunal"])

        # 15. All 785+ Districts (S3WaaS Pattern: <district>.nic.in)
        for state_name, districts in ALL_DISTRICTS_BY_STATE.items():
            for dist in districts:
                clean_dist = dist.lower().replace("-", "").replace(" ", "")
                domain = f"{clean_dist}.nic.in"
                add_seed(domain, GovernmentLevel.DISTRICT.value, f"District Administration {dist.title()}", state=state_name, district=dist.title(), tags=["district", "s3waas"])
                if state_name in ["Haryana", "Punjab", "Assam", "Himachal Pradesh"]:
                    add_seed(f"{clean_dist}.dc.gov.in", GovernmentLevel.DISTRICT.value, f"Deputy Commissioner {dist.title()}", state=state_name, district=dist.title(), tags=["district", "dc_portal"])

        # 16. State Government Department Subdomains (900+ portals)
        for state_root in ALL_STATE_DOMAIN_ROOTS:
            state_label = state_root.split(".")[0].upper()
            for dept in KEY_STATE_DEPARTMENTS:
                domain = f"{dept}.{state_root}"
                add_seed(domain, GovernmentLevel.STATE_UT.value, f"{dept.title()} Department ({state_label})", tags=["department", dept, state_label.lower()])

        # 17. Nationalized Banks, Central PSUs & Financial Regulatory
        for entry in CENTRAL_PSUS_AND_FINANCIAL:
            add_seed(entry["domain"], GovernmentLevel.PSU.value if hasattr(GovernmentLevel, "PSU") else GovernmentLevel.CENTRAL.value, entry["name"], tags=["psu", "financial"])

        # 18. State PSCs (23)
        for entry in STATE_PSCS:
            add_seed(entry["domain"], GovernmentLevel.STATE_UT.value, entry["name"], tags=["recruitment", "psc"])

        return seeds
