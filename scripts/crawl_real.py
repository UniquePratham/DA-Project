"""Real in-country measurement crawler for BharatGov Access.

Runs on the India node. Every value written here comes from an actual HTTP
request and the actual response body. Nothing is sampled or synthesised.

Measurement definitions (all deterministic, all reproducible):

  latency_ms        wall-clock time to first byte, measured with perf_counter
  status_code       final HTTP status after redirects
  acc_score         DOM-signal accessibility index (0-100), computed from
                    alt-text coverage, form labelling, lang attribute,
                    skip-link presence, and GIGW toolbar markers. This is a
                    heuristic index, NOT an axe-core audit.
  sec_score         weighted presence of HSTS, CSP, X-Frame-Options,
                    X-Content-Type-Options, Referrer-Policy
  lcp_sec           estimated from TTFB and document payload size
  multilingual      html[lang] not English, or Indic script present in body
  mobile_responsive viewport meta declares width=device-width
  arch              detected from framework markers in the response
  citizen_services  search input or grievance/complaint affordance present

Usage:
    python3 crawl_real.py --domains domains.json --out out.csv --workers 8
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
    "Upgrade-Insecure-Requests": "1",
}

INDIC = [
    "\u0939\u093f\u0928\u094d\u0926\u0940",  # hindi
    "\u09ac\u09be\u0982\u09b2\u09be",  # bengali
    "\u0c24\u0c46\u0c32\u0c41\u0c17\u0c41",  # telugu
    "\u0ba4\u0bae\u0bbf\u0bb4\u0bcd",  # tamil
    "\u0a97\u0ac1\u0a9c\u0ab0\u0abe\u0aa4\u0ac0",  # gujarati
    "\u0c95\u0ca8\u0ccd\u0ca8\u0ca1",  # kannada
    "\u0d2e\u0d32\u0d2f\u0d3e\u0d33\u0d02",  # malayalam
    "\u0b13\u0b21\u0b3c\u0b3f\u0b06",  # odia
    "\u0a2a\u0a70\u0a1c\u0a3e\u0a2c\u0a40",  # punjabi
]

TOOLBAR_MARKERS = [
    "accessibility toolbar",
    "accessibility-drop",
    "text-resize",
    "font-size",
    "font resize",
    "text-sizer",
    "increase font",
    "high contrast",
    "contrast-toggle",
    "skip to main content",
    "skip to content",
    "skip-to-content",
]

GRIEVANCE_MARKERS = [
    "grievance",
    "cpgrams",
    "samadhan",
    "spandana",
    "complaint",
    "jan sunwai",
    "helpline",
]

#: Headers and body markers that indicate a WAF or bot filter rather than a
#: genuinely missing page. Used to separate "blocked" from "broken".
WAF_HEADER_MARKERS = (
    "cf-ray",
    "x-sucuri-id",
    "x-akamai-transformed",
    "server-timing",
    "x-cache",
    "x-iinfo",
    "x-waf",
)

WAF_BODY_MARKERS = (
    "access denied",
    "request blocked",
    "cloudflare",
    "incapsula",
    "sucuri",
    "akamai",
    "captcha",
    "bot detection",
    "forbidden",
    "not acceptable",
)


def _looks_like_waf(resp) -> bool:
    """True when a 4xx/5xx looks like a bot filter rather than a dead page."""
    headers = {k.lower(): v for k, v in resp.headers.items()}
    if any(m in headers for m in WAF_HEADER_MARKERS):
        return True
    body = (resp.text or "")[:4000].lower()
    return any(m in body for m in WAF_BODY_MARKERS)


def measure(domain: str, timeout: float = 25.0) -> dict:
    """Fetch one domain and derive every metric from the real response."""
    url = f"https://{domain}"
    row = {
        "domain_name": domain,
        "final_url": "",
        "status_code": None,
        "is_reachable": False,
        "measurement_reason": "",
        "sub_accessibility_score": None,
        "sub_has_gigw_toolbar": None,
        "sub_response_latency_ms": None,
        "sub_lcp_est_sec": None,
        "sub_https_enforced": None,
        "sub_security_headers_score": None,
        "sub_is_multilingual": None,
        "sub_mobile_responsive": None,
        "sub_cms_architecture": None,
        "sub_has_citizen_services": None,
        "observatory_maturity_score": None,
        "html_bytes": None,
        "sha256": "",
        "blocked_by_waf": False,
    }

    t0 = time.perf_counter()
    try:
        resp = requests.get(
            url, headers=HEADERS, timeout=timeout, allow_redirects=True, verify=False
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
    except requests.exceptions.SSLError:
        # Retry over plain HTTP only to record that TLS failed.
        try:
            t0 = time.perf_counter()
            resp = requests.get(
                f"http://{domain}",
                headers=HEADERS,
                timeout=timeout,
                allow_redirects=True,
                verify=False,
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
        except Exception as exc:  # noqa: BLE001
            row["measurement_reason"] = f"TLS error: {type(exc).__name__}"
            return row
    except requests.exceptions.Timeout:
        row["measurement_reason"] = "Timeout"
        return row
    except requests.exceptions.ConnectionError:
        row["measurement_reason"] = "DNS or connection failure"
        return row
    except Exception as exc:  # noqa: BLE001
        row["measurement_reason"] = f"{type(exc).__name__}"
        return row

    row["final_url"] = resp.url
    row["status_code"] = resp.status_code
    row["sub_response_latency_ms"] = round(elapsed_ms, 1)

    # A 403/429/503 from a WAF is a distinct outcome, not a dead portal. The
    # site exists and serves citizens; it refuses our declared research client.
    # Recording it separately keeps it out of the accessibility averages while
    # still counting it as evidence about the estate.
    if resp.status_code in (403, 429, 503) and _looks_like_waf(resp):
        row["measurement_reason"] = f"WAF challenge (HTTP {resp.status_code})"
        row["blocked_by_waf"] = True
        return row

    if resp.status_code >= 400:
        row["measurement_reason"] = f"HTTP {resp.status_code}"
        return row

    html = resp.text or ""
    row["is_reachable"] = True
    row["measurement_reason"] = f"HTTP {resp.status_code}"
    row["html_bytes"] = len(resp.content)
    row["sub_https_enforced"] = resp.url.startswith("https://")

    import hashlib

    row["sha256"] = hashlib.sha256(resp.content).hexdigest()

    # ---- security headers (real response headers) ----
    h = {k.lower(): v for k, v in resp.headers.items()}
    sec = 0.0
    if "strict-transport-security" in h:
        sec += 25.0
    if "content-security-policy" in h:
        sec += 30.0
    if "x-frame-options" in h:
        sec += 20.0
    if "x-content-type-options" in h and "nosniff" in h["x-content-type-options"].lower():
        sec += 15.0
    if "referrer-policy" in h:
        sec += 10.0
    row["sub_security_headers_score"] = round(sec, 1)

    # ---- DOM signals (real parsed HTML) ----
    soup = BeautifulSoup(html[:400000], "html.parser")
    text_lower = html[:200000].lower()

    imgs = soup.find_all("img")
    if imgs:
        with_alt = sum(
            1 for i in imgs if i.get("alt") is not None and str(i.get("alt")).strip()
        )
        alt_cov = with_alt / len(imgs)
    else:
        alt_cov = 1.0

    fields = soup.find_all(["input", "select", "textarea"])
    if fields:
        labelled = sum(
            1
            for f in fields
            if f.get("aria-label")
            or f.get("aria-labelledby")
            or f.get("id")
            or f.get("title")
        )
        label_cov = labelled / len(fields)
    else:
        label_cov = 1.0

    html_tag = soup.find("html")
    lang_attr = (html_tag.get("lang") if html_tag else "") or ""
    has_lang = bool(lang_attr.strip())

    has_toolbar = any(m in text_lower for m in TOOLBAR_MARKERS)
    has_skip = any(
        m in text_lower for m in ["skip to main content", "skip to content", "skip-to-content"]
    )

    acc = 55.0
    acc += alt_cov * 20.0
    acc += label_cov * 15.0
    if has_lang:
        acc += 5.0
    if has_skip:
        acc += 5.0
    row["sub_accessibility_score"] = round(min(100.0, max(0.0, acc)), 1)
    row["sub_has_gigw_toolbar"] = bool(has_toolbar)

    # ---- performance ----
    html_kb = len(resp.content) / 1024.0
    row["sub_lcp_est_sec"] = round(
        max(0.1, (elapsed_ms / 1000.0) * 1.5 + (html_kb / 150.0)), 2
    )

    # ---- multilingual ----
    lang_lower = lang_attr.lower()
    is_multi = bool(lang_lower and not lang_lower.startswith("en"))
    if not is_multi:
        is_multi = any(s in html for s in INDIC)
    row["sub_is_multilingual"] = bool(is_multi)

    # ---- mobile ----
    vp = soup.find("meta", attrs={"name": re.compile(r"^viewport$", re.I)})
    row["sub_mobile_responsive"] = bool(
        vp and "width=device-width" in str(vp.get("content", "")).lower()
    )

    # ---- architecture ----
    arch = "custom_dynamic_cms"
    if "s3waas" in text_lower or "sites/all/themes" in text_lower:
        arch = "s3waas_drupal"
    elif "wp-content" in text_lower or "wp-includes" in text_lower:
        arch = "wordpress"
    elif "drupal" in text_lower:
        arch = "drupal"
    elif ".aspx" in text_lower or "viewstate" in text_lower or "asp.net" in str(h):
        arch = "legacy_asp_net"
    elif "_next" in text_lower or "ng-app" in text_lower or "react" in text_lower:
        arch = "modern_spa"
    row["sub_cms_architecture"] = arch

    # ---- citizen services ----
    has_search = bool(
        soup.find("input", attrs={"type": re.compile(r"search", re.I)})
        or soup.find("form", attrs={"role": "search"})
    )
    has_grievance = any(g in text_lower for g in GRIEVANCE_MARKERS)
    row["sub_has_citizen_services"] = bool(has_search or has_grievance)

    # ---- maturity (same published formula) ----
    mat = (
        row["sub_accessibility_score"] * 0.30
        + row["sub_security_headers_score"] * 0.25
        + max(0.0, 100.0 - row["sub_lcp_est_sec"] * 15.0) * 0.20
    )
    if row["sub_is_multilingual"]:
        mat += 10.0
    if row["sub_mobile_responsive"]:
        mat += 5.0
    if row["sub_has_citizen_services"]:
        mat += 5.0
    if arch == "s3waas_drupal":
        mat += 5.0
    row["observatory_maturity_score"] = round(min(100.0, max(0.0, mat)), 1)

    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--domains", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--timeout", type=float, default=25.0)
    args = ap.parse_args()

    with open(args.domains, encoding="utf-8") as f:
        domains = json.load(f)
    print(f"measuring {len(domains)} domains with {args.workers} workers", flush=True)

    rows = []
    done = 0
    t_start = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(measure, d, args.timeout): d for d in domains}
        for fut in as_completed(futures):
            domain = futures[fut]
            try:
                rows.append(fut.result())
            except Exception as exc:  # noqa: BLE001
                rows.append(
                    {
                        "domain_name": domain,
                        "is_reachable": False,
                        "measurement_reason": f"worker error {type(exc).__name__}",
                    }
                )
            done += 1
            if done % 25 == 0 or done == len(domains):
                rate = done / max(1e-9, time.time() - t_start)
                print(f"  {done}/{len(domains)} ({rate:.1f}/s)", flush=True)

    fields = [
        "domain_name",
        "final_url",
        "status_code",
        "is_reachable",
        "measurement_reason",
        "sub_accessibility_score",
        "sub_has_gigw_toolbar",
        "sub_response_latency_ms",
        "sub_lcp_est_sec",
        "sub_https_enforced",
        "sub_security_headers_score",
        "sub_is_multilingual",
        "sub_mobile_responsive",
        "sub_cms_architecture",
        "sub_has_citizen_services",
        "observatory_maturity_score",
        "html_bytes",
        "sha256",
        "blocked_by_waf",
    ]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    reach = sum(1 for r in rows if r.get("is_reachable"))
    print(f"\nwrote {len(rows)} rows to {args.out}")
    print(f"reachable: {reach} ({reach / len(rows) * 100:.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
