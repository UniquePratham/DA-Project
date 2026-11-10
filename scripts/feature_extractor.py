"""
Cloud Bangalore Crawler & Feature Extractor for BharatGov Access.
Extracts 5 Main Features & 10 Sub-Features across 2,390 Government Portals.
"""

import asyncio
import re
import time
from typing import Dict, Any, List, Optional
import httpx
from bs4 import BeautifulSoup
import pandas as pd

CHROME_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
BROWSER_HEADERS = {
    "User-Agent": CHROME_UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
    "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
}

# Regional language indicators for Indian 8th Schedule languages
REGIONAL_INDICATORS = [
    "hindi", "हिन्दी", "বাংলা", "bengali", "मराठी", "marathi", "తెలుగు", "telugu",
    "தமிழ்", "tamil", "ગુજરાતી", "gujarati", "ಕನ್ನಡ", "kannada", "മലയാളം", "malayalam",
    "ଓଡ଼ିଆ", "odia", "ਪੰਜਾਬੀ", "punjabi", "অসমীয়া", "assamese", "اردو", "urdu",
    "lang=hi", "/hi/", "/hi", "lang=bn", "lang=ta", "lang=te", "language-select", "bilingual"
]

def extract_features_from_response(html: str, headers: Dict[str, str], latency_ms: float, final_url: str) -> Dict[str, Any]:
    text_lower = html[:120000].lower()
    soup = BeautifulSoup(html[:150000], "html.parser") if html else None

    # --- Pillar 1: Accessibility (Sub-features 1 & 2) ---
    alt_coverage = 1.0
    form_labeled = 1.0
    has_lang = False
    has_toolbar = False
    has_resize = False
    has_contrast = False
    has_skip = False

    if soup:
        imgs = soup.find_all("img")
        if imgs:
            with_alt = sum(1 for img in imgs if img.get("alt") is not None and str(img.get("alt")).strip() != "")
            alt_coverage = round(with_alt / len(imgs), 2)
        
        inputs = soup.find_all(["input", "select", "textarea"])
        if inputs:
            labeled = sum(1 for inp in inputs if inp.get("aria-label") or inp.get("id") or inp.get("placeholder"))
            form_labeled = round(labeled / len(inputs), 2)

        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            has_lang = True

        # GIGW Accessibility toolbar detection
        if any(k in text_lower for k in ["accessibility toolbar", "accessibility-drop", "text-resize", "font-size", "a+", "a-", "theme-changer"]):
            has_toolbar = True
        if any(k in text_lower for k in ["font resize", "font-resize", "text-sizer", "a+", "a-", "increase font"]):
            has_resize = True
        if any(k in text_lower for k in ["high contrast", "contrast-toggle", "dark-mode", "dark mode", "contrast"]):
            has_contrast = True
        if any(k in text_lower for k in ["skip to main content", "skip to content", "skip-to-content", "#main-content", "#content"]):
            has_skip = True

    # Composite accessibility index (0-100)
    acc_score = 65.0
    acc_score += (alt_coverage * 15.0)
    acc_score += (form_labeled * 10.0)
    if has_lang: acc_score += 4.0
    if has_skip: acc_score += 6.0
    acc_score = round(min(98.5, max(50.0, acc_score)), 1)
    has_gigw_toolbar = bool(has_toolbar or has_resize or has_contrast or has_skip)

    # --- Pillar 2: Performance (Sub-features 3 & 4) ---
    resp_latency = round(latency_ms, 1)
    # LCP estimation based on TTFB and HTML payload size
    html_kb = len(html.encode("utf-8", errors="ignore")) / 1024.0
    lcp_sec = round(max(0.6, (latency_ms / 1000.0) * 1.5 + (html_kb / 150.0)), 2)

    # --- Pillar 3: Security & Cryptography (Sub-features 5 & 6) ---
    is_https = final_url.startswith("https://")
    headers_lower = {k.lower(): v for k, v in headers.items()}
    has_hsts = "strict-transport-security" in headers_lower
    has_csp = "content-security-policy" in headers_lower
    has_xcto = "x-content-type-options" in headers_lower
    has_xfo = "x-frame-options" in headers_lower

    sec_score = 40.0 if is_https else 10.0
    if has_hsts: sec_score += 25.0
    if has_csp: sec_score += 15.0
    if has_xcto: sec_score += 10.0
    if has_xfo: sec_score += 10.0
    sec_score = round(min(100.0, sec_score), 1)

    # --- Pillar 4: Linguistic & Mobile Inclusivity (Sub-features 7 & 8) ---
    is_multi = False
    if has_lang and html_tag and str(html_tag.get("lang")).lower() not in ["en", "en-us"]:
        is_multi = True
    elif any(ind in text_lower for ind in REGIONAL_INDICATORS):
        is_multi = True

    is_mobile = False
    if soup:
        vp = soup.find("meta", attrs={"name": re.compile(r"^viewport$", re.I)})
        if vp and "width=device-width" in str(vp.get("content", "")).lower():
            is_mobile = True

    # --- Pillar 5: Architecture & Citizen Interactivity (Sub-features 9 & 10) ---
    arch = "custom_dynamic_cms"
    if "s3waas" in text_lower or "s3waas" in str(headers_lower) or "sites/all/themes" in text_lower or "drupal" in text_lower:
        arch = "s3waas_drupal"
    elif "wp-content" in text_lower or "wordpress" in text_lower:
        arch = "wordpress"
    elif ".aspx" in text_lower or "viewstate" in text_lower or "asp.net" in str(headers_lower):
        arch = "legacy_asp_net"
    elif "react" in text_lower or "ng-app" in text_lower or "angular" in text_lower or "_next" in text_lower:
        arch = "modern_spa"

    has_search = False
    has_grievance = False
    if soup:
        if soup.find("input", attrs={"type": re.compile(r"search", re.I)}) or "search" in text_lower:
            has_search = True
        if any(g in text_lower for g in ["grievance", "cpgrams", "samadhan", "spandana", "complaint", "jan sunwai", "cm helpline"]):
            has_grievance = True
    has_citizen_services = bool(has_search or has_grievance)

    # --- Overall Maturity Composite Score (0-100) ---
    maturity = (acc_score * 0.30) + (sec_score * 0.25) + (max(0.0, 100.0 - lcp_sec * 15.0) * 0.20)
    if is_multi: maturity += 10.0
    if is_mobile: maturity += 5.0
    if has_citizen_services: maturity += 5.0
    if arch == "s3waas_drupal": maturity += 5.0
    maturity_score = round(min(98.0, max(45.0, maturity)), 1)

    return {
        "sub_accessibility_score": acc_score,
        "sub_has_gigw_toolbar": has_gigw_toolbar,
        "sub_response_latency_ms": resp_latency,
        "sub_lcp_est_sec": lcp_sec,
        "sub_https_enforced": is_https,
        "sub_security_headers_score": sec_score,
        "sub_is_multilingual": is_multi,
        "sub_mobile_responsive": is_mobile,
        "sub_cms_architecture": arch,
        "sub_has_citizen_services": has_citizen_services,
        "observatory_maturity_score": maturity_score
    }

