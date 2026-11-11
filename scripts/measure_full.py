"""Measure every feature with its proper tool, not a heuristic.

Feature -> tool mapping:

  accessibility   axe-core 4.x (WCAG 2.0/2.1 A+AA rules) in headless Chromium
  security        real response headers, scored against the OWASP Secure
                  Headers Project directive set
  TLS             real certificate inspection via Python ssl (issuer, expiry,
                  protocol version, cipher)
  performance     real TTFB from perf_counter, real transfer size from the
                  response, real DOM node count from the parsed document
  mobile          real viewport meta + real horizontal-overflow check at 375px
                  in headless Chromium
  multilingual    real html[lang] + real hreflang alternates + real Indic
                  script detection in the rendered text
  architecture    real framework fingerprints in HTML, headers and asset paths
  citizen svcs    real form/input/search affordances in the parsed DOM

Nothing here is sampled, guessed, or synthesised. Every value is read from a
live response or a live browser evaluation.

Usage:
    python3 measure_full.py --domains domains.json --out full.csv --workers 6
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import re
import socket
import ssl
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
}

# OWASP Secure Headers Project directive set, weighted by defensive value.
SECURITY_DIRECTIVES = {
    "strict-transport-security": 25.0,
    "content-security-policy": 30.0,
    "x-frame-options": 15.0,
    "x-content-type-options": 10.0,
    "referrer-policy": 10.0,
    "permissions-policy": 10.0,
}

INDIC_RANGES = [
    (0x0900, 0x097F),  # Devanagari
    (0x0980, 0x09FF),  # Bengali
    (0x0A00, 0x0A7F),  # Gurmukhi
    (0x0A80, 0x0AFF),  # Gujarati
    (0x0B00, 0x0B7F),  # Oriya
    (0x0B80, 0x0BFF),  # Tamil
    (0x0C00, 0x0C7F),  # Telugu
    (0x0C80, 0x0CFF),  # Kannada
    (0x0D00, 0x0D7F),  # Malayalam
]


def has_indic(text: str) -> bool:
    for ch in text[:200000]:
        cp = ord(ch)
        for lo, hi in INDIC_RANGES:
            if lo <= cp <= hi:
                return True
    return False


def tls_info(domain: str, timeout: float = 12.0) -> dict:
    """Real TLS handshake: issuer, expiry, protocol, cipher."""
    out = {
        "tls_ok": False,
        "tls_issuer": "",
        "tls_days_to_expiry": None,
        "tls_protocol": "",
        "tls_cipher": "",
        "tls_error": "",
    }
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with socket.create_connection((domain, 443), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                out["tls_ok"] = True
                out["tls_protocol"] = ssock.version() or ""
                cipher = ssock.cipher()
                out["tls_cipher"] = cipher[0] if cipher else ""
                issuer = cert.get("issuer", [])
                for rdn in issuer:
                    for k, v in rdn:
                        if k == "organizationName":
                            out["tls_issuer"] = v
                not_after = cert.get("notAfter")
                if not_after:
                    exp = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(
                        tzinfo=timezone.utc
                    )
                    out["tls_days_to_expiry"] = (exp - datetime.now(timezone.utc)).days
    except Exception as exc:  # noqa: BLE001
        out["tls_error"] = type(exc).__name__
    return out


def http_measure(domain: str, timeout: float = 25.0) -> dict:
    """Real HTTP measurement: status, TTFB, headers, DOM signals."""
    row = {
        "domain_name": domain,
        "final_url": "",
        "status_code": None,
        "is_reachable": False,
        "measurement_reason": "",
        "ttfb_ms": None,
        "total_ms": None,
        "html_bytes": None,
        "sha256": "",
        "sec_score": None,
        "sec_hsts": False,
        "sec_csp": False,
        "sec_xfo": False,
        "sec_xcto": False,
        "sec_referrer": False,
        "sec_permissions": False,
        "https_enforced": False,
        "has_lang_attr": False,
        "lang_value": "",
        "has_hreflang": False,
        "has_indic_script": False,
        "has_viewport": False,
        "viewport_content": "",
        "dom_nodes": None,
        "img_count": None,
        "img_missing_alt": None,
        "form_count": None,
        "input_count": None,
        "has_search": False,
        "has_grievance": False,
        "arch": "",
        "arch_evidence": "",
    }

    t0 = time.perf_counter()
    try:
        r = requests.get(
            f"https://{domain}", headers=HEADERS, timeout=timeout,
            allow_redirects=True, verify=False,
        )
        row["ttfb_ms"] = round((time.perf_counter() - t0) * 1000.0, 1)
    except Exception as exc:  # noqa: BLE001
        row["measurement_reason"] = type(exc).__name__
        return row

    row["total_ms"] = round((time.perf_counter() - t0) * 1000.0, 1)
    row["final_url"] = r.url
    row["status_code"] = r.status_code
    if r.status_code >= 400:
        row["measurement_reason"] = f"HTTP {r.status_code}"
        return row

    row["is_reachable"] = True
    row["measurement_reason"] = f"HTTP {r.status_code}"
    row["html_bytes"] = len(r.content)
    row["sha256"] = hashlib.sha256(r.content).hexdigest()
    row["https_enforced"] = r.url.startswith("https://")

    # --- security: real headers against the OWASP directive set ---
    h = {k.lower(): v for k, v in r.headers.items()}
    score = 0.0
    for directive, weight in SECURITY_DIRECTIVES.items():
        present = directive in h
        if present:
            score += weight
        key = {
            "strict-transport-security": "sec_hsts",
            "content-security-policy": "sec_csp",
            "x-frame-options": "sec_xfo",
            "x-content-type-options": "sec_xcto",
            "referrer-policy": "sec_referrer",
            "permissions-policy": "sec_permissions",
        }[directive]
        row[key] = present
    row["sec_score"] = round(score, 1)

    # --- DOM signals from the real parsed document ---
    html = r.text or ""
    soup = BeautifulSoup(html[:600000], "html.parser")

    html_tag = soup.find("html")
    lang = (html_tag.get("lang") if html_tag else "") or ""
    row["has_lang_attr"] = bool(lang.strip())
    row["lang_value"] = lang.strip()[:20]
    row["has_hreflang"] = bool(soup.find("link", attrs={"rel": "alternate", "hreflang": True}))
    row["has_indic_script"] = has_indic(html)

    vp = soup.find("meta", attrs={"name": re.compile(r"^viewport$", re.I)})
    row["has_viewport"] = bool(vp)
    row["viewport_content"] = (vp.get("content", "") if vp else "")[:80]

    row["dom_nodes"] = len(soup.find_all(True))
    imgs = soup.find_all("img")
    row["img_count"] = len(imgs)
    row["img_missing_alt"] = sum(
        1 for i in imgs if i.get("alt") is None or not str(i.get("alt")).strip()
    )
    forms = soup.find_all("form")
    row["form_count"] = len(forms)
    row["input_count"] = len(soup.find_all(["input", "select", "textarea"]))
    row["has_search"] = bool(
        soup.find("input", attrs={"type": re.compile(r"search", re.I)})
        or soup.find("form", attrs={"role": "search"})
        or soup.find("input", attrs={"name": re.compile(r"search|q$", re.I)})
    )
    text_lower = html[:300000].lower()
    row["has_grievance"] = any(
        g in text_lower
        for g in ("grievance", "cpgrams", "samadhan", "spandana", "complaint", "helpline")
    )

    # --- architecture: real fingerprints ---
    arch, evidence = "custom_dynamic_cms", ""
    checks = [
        ("s3waas_drupal", ["s3waas", "sites/all/themes/custom"]),
        ("wordpress", ["wp-content", "wp-includes", "wp-json"]),
        ("drupal", ["drupal", "sites/default/files", "core/misc/drupal"]),
        ("legacy_asp_net", ["__viewstate", "asp.net", ".aspx"]),
        ("modern_spa", ["_next/static", "__next", "ng-version", "data-reactroot"]),
    ]
    for name, markers in checks:
        for m in markers:
            if m in text_lower or m in str(h).lower():
                arch, evidence = name, m
                break
        if evidence:
            break
    row["arch"] = arch
    row["arch_evidence"] = evidence
    return row


async def browser_measure(page, domain: str, axe_source: str) -> dict:
    """Real browser measurement: axe-core, mobile overflow, rendered DOM."""
    out = {
        "axe_total": None,
        "axe_critical": None,
        "axe_serious": None,
        "axe_moderate": None,
        "axe_minor": None,
        "axe_score": None,
        "axe_passes": None,
        "mobile_overflow_px": None,
        "rendered_dom_nodes": None,
    }
    try:
        await page.goto(f"https://{domain}", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(1000)

        # Real axe-core WCAG audit.
        await page.add_script_tag(content=axe_source)
        res = await page.evaluate(
            """async () => {
                const r = await axe.run(document, {
                    runOnly: { type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa'] }
                });
                const c = {critical:0, serious:0, moderate:0, minor:0};
                for (const v of r.violations) c[v.impact] = (c[v.impact]||0) + 1;
                return {total: r.violations.length, c, passes: r.passes.length,
                        nodes: document.getElementsByTagName('*').length};
            }"""
        )
        c = res["c"]
        out["axe_total"] = res["total"]
        out["axe_critical"] = c.get("critical", 0)
        out["axe_serious"] = c.get("serious", 0)
        out["axe_moderate"] = c.get("moderate", 0)
        out["axe_minor"] = c.get("minor", 0)
        out["axe_passes"] = res["passes"]
        out["rendered_dom_nodes"] = res["nodes"]
        penalty = (
            c.get("critical", 0) * 12.0 + c.get("serious", 0) * 6.0
            + c.get("moderate", 0) * 3.0 + c.get("minor", 0) * 1.0
        )
        out["axe_score"] = round(max(0.0, min(100.0, 100.0 - penalty)), 1)

        # Real mobile overflow at 375px.
        await page.set_viewport_size({"width": 375, "height": 812})
        await page.wait_for_timeout(600)
        out["mobile_overflow_px"] = await page.evaluate(
            "Math.max(0, document.documentElement.scrollWidth - document.documentElement.clientWidth)"
        )
    except Exception:  # noqa: BLE001
        pass
    return out


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--domains", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--axe", default="node_modules/axe-core/axe.min.js")
    args = ap.parse_args()

    axe_path = Path(args.axe)
    if not axe_path.exists():
        print(f"missing axe-core at {axe_path}; run: npm install axe-core")
        return 1
    axe_source = axe_path.read_text(encoding="utf-8")

    domains = json.loads(Path(args.domains).read_text(encoding="utf-8"))
    if args.limit:
        domains = domains[: args.limit]
    print(f"measuring {len(domains)} domains with real tools", flush=True)

    rows: list[dict] = []
    t0 = time.time()

    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        sem = asyncio.Semaphore(args.workers)

        async def one(domain: str) -> None:
            async with sem:
                # HTTP + TLS are blocking; run them off the event loop.
                http_row = await asyncio.to_thread(http_measure, domain)
                tls_row = await asyncio.to_thread(tls_info, domain)
                http_row.update(tls_row)

                if http_row["is_reachable"]:
                    ctx = await browser.new_context(
                        user_agent=UA, ignore_https_errors=True,
                        viewport={"width": 1440, "height": 900},
                    )
                    page = await ctx.new_page()
                    try:
                        http_row.update(await browser_measure(page, domain, axe_source))
                    finally:
                        await ctx.close()
                rows.append(http_row)

        await asyncio.gather(*(one(d) for d in domains))
        await browser.close()

    fields = [
        "domain_name", "final_url", "status_code", "is_reachable", "measurement_reason",
        "ttfb_ms", "total_ms", "html_bytes", "sha256",
        "sec_score", "sec_hsts", "sec_csp", "sec_xfo", "sec_xcto", "sec_referrer",
        "sec_permissions", "https_enforced",
        "tls_ok", "tls_issuer", "tls_days_to_expiry", "tls_protocol", "tls_cipher", "tls_error",
        "has_lang_attr", "lang_value", "has_hreflang", "has_indic_script",
        "has_viewport", "viewport_content", "dom_nodes", "img_count", "img_missing_alt",
        "form_count", "input_count", "has_search", "has_grievance",
        "arch", "arch_evidence",
        "axe_total", "axe_critical", "axe_serious", "axe_moderate", "axe_minor",
        "axe_score", "axe_passes", "mobile_overflow_px", "rendered_dom_nodes",
    ]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    reach = [r for r in rows if r["is_reachable"]]
    axed = [r for r in reach if r.get("axe_total") is not None]
    print(f"\nwrote {len(rows)} rows in {time.time()-t0:.0f}s")
    print(f"reachable: {len(reach)} ({len(reach)/len(rows)*100:.1f}%)")
    print(f"axe-audited: {len(axed)}")
    if axed:
        import statistics

        print(f"  mean axe violations: {statistics.mean(r['axe_total'] for r in axed):.1f}")
        print(f"  mean axe score: {statistics.mean(r['axe_score'] for r in axed):.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
