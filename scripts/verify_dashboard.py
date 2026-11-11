"""End-to-end verification of the BharatGov Access dashboard.

Covers four independent concerns:

1. Layout    — no horizontal overflow at 320/375/414/768/1024/1280/1600 px, in every view.
2. Data      — every rendered figure matches an independent pandas computation.
3. Behaviour — tabs, theme, palette, ledger filters/sort/paging, map selection, CSV export.
4. A11y      — landmarks, tab semantics, focus visibility, contrast, labels, keyboard paths.

Usage:
    python scripts/verify_dashboard.py                 # all suites
    python scripts/verify_dashboard.py --suite data    # one suite
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from pathlib import Path

import pandas as pd
from playwright.async_api import async_playwright

CSV = Path("resources/bharatgov_access_clean.csv")
PAGE = Path("dashboard/index.html").resolve().as_uri()
OUT = Path("scratch/verify")

WIDTHS = [320, 375, 414, 768, 1024, 1280, 1600]
VIEWS = ["overview", "atlas", "ledger", "standard", "method"]

TIERS = [
    "central",
    "state_ut",
    "district",
    "academic_research",
    "judiciary",
    "public_sector",
    "urban_local_body",
]

# ``local_body`` and ``urban_local_body`` are the same tier in the release.
LEVEL_MAP = {
    "central": ["central"],
    "state_ut": ["state_ut"],
    "district": ["district"],
    "academic_research": ["academic_research"],
    "judiciary": ["judiciary"],
    "public_sector": ["public_sector"],
    "urban_local_body": ["urban_local_body", "local_body"],
}

TIER_LABELS = {
    "Central ministries": "central",
    "State departments": "state_ut",
    "District administrations": "district",
    "Higher education": "academic_research",
    "Judiciary": "judiciary",
    "Public sector & banks": "public_sector",
    "Urban local bodies": "urban_local_body",
}

ARCH_LABELS = {
    "S3WaaS (Drupal)": "s3waas_drupal",
    "Custom dynamic CMS": "custom_dynamic_cms",
    "Modern SPA": "modern_spa",
    "Legacy ASP.NET": "legacy_asp_net",
    "WordPress": "wordpress",
}

failures: list[str] = []
checks = 0


def fail(message: str) -> None:
    failures.append(message)


def num(text: str) -> float | None:
    cleaned = str(text).replace(",", "").replace("%", "").strip()
    if cleaned in {"", "—", "-", "N/A"}:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    return float(match.group()) if match else None


def check(label: str, actual, want, tol: float = 0.06) -> None:
    global checks
    checks += 1
    if actual is None or want is None:
        fail(f"{label}: missing (actual={actual!r} want={want!r})")
        return
    if abs(float(actual) - float(want)) > tol:
        fail(f"{label}: rendered {actual} != expected {want:.4f}")


def expected() -> dict:
    df = pd.read_csv(CSV)
    live = df[df["is_reachable"]]

    out: dict = {
        "total": len(df),
        "reachable": len(live),
        "unreachable": len(df) - len(live),
        "acc": live["sub_accessibility_score"].mean(),
        "sec": live["sub_security_headers_score"].mean(),
        "maturity": live["observatory_maturity_score"].mean(),
        "medianLat": live["sub_response_latency_ms"].median(),
        "medianLcp": live["sub_lcp_est_sec"].median(),
        "gigw": live["sub_has_gigw_toolbar"].mean() * 100,
        "multi": live["sub_is_multilingual"].mean() * 100,
        "mobile": live["sub_mobile_responsive"].mean() * 100,
        "services": live["sub_has_citizen_services"].mean() * 100,
        "https": live["sub_https_enforced"].mean() * 100,
        "perfectSec": int((live["sub_security_headers_score"] == 100).sum()),
        "slowTtfb": int((live["sub_response_latency_ms"] > 2000).sum()),
        "districtShare": (df["government_level"] == "district").mean() * 100,
    }

    out["lcpBuckets"] = [
        int((live["sub_lcp_est_sec"] <= 2.5).sum()),
        int(((live["sub_lcp_est_sec"] > 2.5) & (live["sub_lcp_est_sec"] <= 4)).sum()),
        int((live["sub_lcp_est_sec"] > 4).sum()),
    ]
    out["latBuckets"] = [
        int((live["sub_response_latency_ms"] <= 500).sum()),
        int(((live["sub_response_latency_ms"] > 500) & (live["sub_response_latency_ms"] <= 1000)).sum()),
        int(((live["sub_response_latency_ms"] > 1000) & (live["sub_response_latency_ms"] <= 2000)).sum()),
        int((live["sub_response_latency_ms"] > 2000).sum()),
    ]
    out["secBuckets"] = [
        int((live["sub_security_headers_score"] < 25).sum()),
        int(((live["sub_security_headers_score"] >= 25) & (live["sub_security_headers_score"] < 50)).sum()),
        int(((live["sub_security_headers_score"] >= 50) & (live["sub_security_headers_score"] < 75)).sum()),
        int(((live["sub_security_headers_score"] >= 75) & (live["sub_security_headers_score"] < 100)).sum()),
        int((live["sub_security_headers_score"] == 100).sum()),
    ]
    out["arch"] = live["sub_cms_architecture"].value_counts().to_dict()

    tiers = {}
    for key in TIERS:
        all_rows = df[df["government_level"].isin(LEVEL_MAP[key])]
        up = all_rows[all_rows["is_reachable"]]
        tiers[key] = {
            "total": len(all_rows),
            "live": len(up),
            "acc": up["sub_accessibility_score"].mean(),
            "sec": up["sub_security_headers_score"].mean(),
            "gigw": up["sub_has_gigw_toolbar"].mean() * 100,
            "multi": up["sub_is_multilingual"].mean() * 100,
            "mobile": up["sub_mobile_responsive"].mean() * 100,
            "maturity": up["observatory_maturity_score"].mean(),
        }
    out["tiers"] = tiers

    states = {}
    for name, group in live.groupby("state_or_ut"):
        states[name] = {
            "total": int((df["state_or_ut"] == name).sum()),
            "live": len(group),
            "maturity": group["observatory_maturity_score"].mean(),
            "acc": group["sub_accessibility_score"].mean(),
            "sec": group["sub_security_headers_score"].mean(),
            "lat": group["sub_response_latency_ms"].median(),
        }
    out["states"] = states
    out["df"] = df
    return out


# --------------------------------------------------------------------- suites


async def suite_layout(browser) -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    for width in WIDTHS:
        page = await browser.new_page(viewport={"width": width, "height": 900})
        errors: list[str] = []
        page.on(
            "console",
            lambda m: errors.append(f"console.{m.type}: {m.text}")
            if m.type in ("error", "warning")
            else None,
        )
        page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))

        await page.goto(PAGE)
        await page.wait_for_selector("body[data-ready='true']", timeout=20000)

        for view in VIEWS:
            await page.evaluate("v => document.querySelector(`[data-view='${v}']`).click()", view)
            await page.wait_for_timeout(200)

            metrics = await page.evaluate(
                """() => {
                    const de = document.documentElement;
                    const inScroller = (el) => {
                        for (let p = el.parentElement; p; p = p.parentElement) {
                            const ox = getComputedStyle(p).overflowX;
                            if (ox === 'auto' || ox === 'scroll') return true;
                        }
                        return false;
                    };
                    const wide = [];
                    document.querySelectorAll('body *').forEach(el => {
                        const r = el.getBoundingClientRect();
                        if (r.width > window.innerWidth + 1 && r.height > 0) {
                            if (getComputedStyle(el).position === 'fixed') return;
                            if (inScroller(el)) return;
                            wide.push({
                                tag: el.tagName.toLowerCase(),
                                cls: (el.className || '').toString().slice(0, 50),
                                w: Math.round(r.width),
                            });
                        }
                    });
                    return {
                        scrollW: de.scrollWidth,
                        clientW: de.clientWidth,
                        wide: wide.slice(0, 5),
                    };
                }"""
            )

            if metrics["scrollW"] > metrics["clientW"] + 1:
                fail(f"layout {width}px /{view}: overflow {metrics['scrollW']} > {metrics['clientW']}")
            if metrics["wide"]:
                fail(f"layout {width}px /{view}: wide {metrics['wide']}")

            await page.screenshot(
                path=str(OUT / f"{width}-{view}.png"), full_page=(view != "ledger")
            )

        if errors:
            fail(f"layout {width}px: console {errors[:3]}")

        await page.close()


async def suite_data(browser, exp: dict) -> None:
    page = await browser.new_page(viewport={"width": 1440, "height": 1000})
    await page.goto(PAGE)
    await page.wait_for_selector("body[data-ready='true']", timeout=20000)

    binds = await page.evaluate(
        """() => {
            const out = {};
            document.querySelectorAll('[data-bind]').forEach(el => {
                const k = el.getAttribute('data-bind');
                if (!(k in out)) out[k] = el.textContent.trim();
            });
            return out;
        }"""
    )
    check("band total", num(binds.get("total", "")), exp["total"], 0)
    check("band reachable", num(binds.get("reachable", "")), exp["reachable"], 0)
    check("band unreachable", num(binds.get("unreachable", "")), exp["unreachable"], 0)
    check("band acc", num(binds.get("acc", "")), exp["acc"])
    check("band sec", num(binds.get("sec", "")), exp["sec"])
    check("band maturity", num(binds.get("maturity", "")), exp["maturity"])
    check("band medianLat", num(binds.get("medianLat", "")), exp["medianLat"], 1.0)
    check("band medianLcp", num(binds.get("medianLcp", "")), exp["medianLcp"], 0.01)
    check("band districtShare", num(binds.get("districtShare", "")), exp["districtShare"])

    matrix = await page.evaluate(
        """() => Array.from(document.querySelectorAll('#tier-matrix-body tr')).map(tr =>
            Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim()))"""
    )
    for row in matrix[:-1]:
        key = TIER_LABELS.get(row[0])
        if not key:
            fail(f"tier matrix: unknown label {row[0]!r}")
            continue
        want = exp["tiers"][key]
        check(f"tier[{key}] total", num(row[1]), want["total"], 0)
        check(f"tier[{key}] live", num(row[2]), want["live"], 0)
        check(f"tier[{key}] acc", num(row[3]), want["acc"])
        check(f"tier[{key}] sec", num(row[4]), want["sec"])
        check(f"tier[{key}] gigw", num(row[5]), want["gigw"])
        check(f"tier[{key}] multi", num(row[6]), want["multi"])
        check(f"tier[{key}] mobile", num(row[7]), want["mobile"])

    national = matrix[-1]
    check("tier national total", num(national[1]), exp["total"], 0)
    check("tier national live", num(national[2]), exp["reachable"], 0)
    check("tier national acc", num(national[3]), exp["acc"])
    check("tier national sec", num(national[4]), exp["sec"])

    async def bucket_counts(chart_id: str) -> list[int]:
        return await page.evaluate(
            """id => Array.from(document.querySelectorAll('#' + id + ' rect.bar title'))
                    .map(t => {
                        const m = t.textContent.match(/([\\d,]+)\\s*portals/);
                        return m ? Number(m[1].replace(/,/g, '')) : null;
                    })""",
            chart_id,
        )

    for chart, key in [
        ("chart-lcp", "lcpBuckets"),
        ("chart-latency", "latBuckets"),
        ("chart-sec", "secBuckets"),
    ]:
        got = await bucket_counts(chart)
        for i, want in enumerate(exp[key]):
            check(f"{key}[{i}]", got[i] if i < len(got) else None, want, 0)

    arch = await page.evaluate(
        """() => Array.from(document.querySelectorAll('#chart-arch rect.bar title')).map(t => t.textContent)"""
    )
    for text in arch:
        label, _, rest = text.partition(":")
        key = ARCH_LABELS.get(label.strip())
        if not key:
            fail(f"arch chart: unknown label {label!r}")
            continue
        check(f"arch[{key}]", num(rest), exp["arch"].get(key, 0), 0)

    ranks = await page.evaluate(
        """() => Array.from(document.querySelectorAll('#state-rank-body tr')).map(tr =>
            Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim()))"""
    )
    if not ranks:
        fail("state ranking table is empty")
    for row in ranks:
        name = row[1]
        want = exp["states"].get(name)
        if not want:
            fail(f"state rank: {name!r} not in source CSV")
            continue
        check(f"state[{name}] total", num(row[2]), want["total"], 0)
        check(f"state[{name}] maturity", num(row[3]), want["maturity"])
        check(f"state[{name}] acc", num(row[4]), want["acc"])
        check(f"state[{name}] sec", num(row[5]), want["sec"])
        check(f"state[{name}] lat", num(row[6]), want["lat"], 1.0)

    ledger = await page.evaluate(
        """() => Array.from(document.querySelectorAll('#ledger-body tr')).map(tr => {
            const td = tr.querySelectorAll('td');
            return {
                domain: td[0].querySelector('.ledger__domain').textContent.trim(),
                acc: td[3].textContent.trim(),
                sec: td[4].textContent.trim(),
                ttfb: td[5].textContent.trim(),
                lcp: td[6].textContent.trim(),
            };
        })"""
    )
    live_df = exp["df"][exp["df"]["is_reachable"]].sort_values(
        ["observatory_maturity_score", "domain_name"], ascending=[False, True]
    )
    for i, row in enumerate(ledger):
        src = live_df.iloc[i]
        if row["domain"] != src["domain_name"]:
            fail(f"ledger row {i}: {row['domain']!r} != {src['domain_name']!r}")
            continue
        check(f"ledger[{i}] acc", num(row["acc"]), src["sub_accessibility_score"])
        check(f"ledger[{i}] sec", num(row["sec"]), src["sub_security_headers_score"])
        check(f"ledger[{i}] ttfb", num(row["ttfb"]), src["sub_response_latency_ms"], 1.0)
        check(f"ledger[{i}] lcp", num(row["lcp"]), src["sub_lcp_est_sec"], 0.01)

    findings = await page.evaluate(
        """() => Array.from(document.querySelectorAll('#findings li')).map(li =>
            li.querySelector('p').textContent.replace(/\\s+/g, ' ').trim())"""
    )
    joined = " ".join(findings)
    for label, want in [
        ("perfectSec", exp["perfectSec"]),
        ("slowTtfb", exp["slowTtfb"]),
        ("medianLat", exp["medianLat"]),
    ]:
        candidates = {
            f"{int(want):,}",
            str(int(want)),
            f"{int(round(want)):,}",
            str(int(round(want))),
        }
        if not any(c in joined for c in candidates):
            fail(f"findings prose does not quote {label}={int(want):,}")

    await page.close()


async def suite_behaviour(browser, exp: dict) -> None:
    page = await browser.new_page(viewport={"width": 1440, "height": 1000})
    await page.goto(PAGE)
    await page.wait_for_selector("body[data-ready='true']", timeout=20000)

    # --- tabs
    for view in VIEWS:
        await page.click(f"[data-view='{view}']")
        await page.wait_for_timeout(120)
        visible = await page.evaluate(
            """() => Array.from(document.querySelectorAll('.view'))
                    .filter(el => !el.hidden).map(el => el.id)"""
        )
        if visible != [f"view-{view}"]:
            fail(f"tabs: selecting {view} showed {visible}")
        if await page.get_attribute(f"[data-view='{view}']", "aria-selected") != "true":
            fail(f"tabs: {view} not aria-selected")

    # --- theme switch (explicit light / dark control)
    await page.click("[data-theme-set='dark']")
    await page.wait_for_timeout(200)
    if await page.get_attribute("html", "data-theme") != "dark":
        fail("theme: dark button did not apply dark")
    if await page.get_attribute("[data-theme-set='dark']", "aria-pressed") != "true":
        fail("theme: dark button not aria-pressed")
    if await page.get_attribute("[data-theme-set='light']", "aria-pressed") != "false":
        fail("theme: light button still pressed")

    await page.click("[data-theme-set='light']")
    await page.wait_for_timeout(200)
    if await page.get_attribute("html", "data-theme") != "light":
        fail("theme: light button did not apply light")

    # --- keyboard shortcut still toggles
    await page.keyboard.press("t")
    await page.wait_for_timeout(200)
    if await page.get_attribute("html", "data-theme") != "dark":
        fail("theme: 't' shortcut did not toggle")
    await page.keyboard.press("t")
    await page.wait_for_timeout(200)

    # --- palette
    await page.keyboard.press("/")
    await page.wait_for_timeout(150)
    if await page.is_hidden("#palette"):
        fail("palette: '/' did not open")
    await page.fill("#palette-input", "meity")
    await page.wait_for_timeout(250)
    results = await page.evaluate(
        """() => Array.from(document.querySelectorAll('.palette__item')).map(li => li.textContent)"""
    )
    if not results:
        fail("palette: no results for 'meity'")
    elif not any("meity" in r.lower() for r in results):
        fail(f"palette: results lack meity: {results[:2]}")
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(300)
    if not await page.is_hidden("#palette"):
        fail("palette: Enter did not close")
    if "meity" not in (await page.input_value("#ledger-search")).lower():
        fail("palette: ledger search not populated")

    # --- ledger tier filter
    await page.select_option("#ledger-tier", "central")
    await page.wait_for_timeout(250)
    tiers = await page.evaluate(
        """() => Array.from(document.querySelectorAll('#ledger-body tr td:nth-child(2) .tag'))
                .map(t => t.textContent.trim())"""
    )
    if not tiers or any(t != "Central" for t in tiers):
        fail(f"ledger: tier filter leaked {set(tiers)}")

    # --- ledger status filter (clear the palette's search term first)
    await page.fill("#ledger-search", "")
    await page.select_option("#ledger-tier", "all")
    await page.select_option("#ledger-status", "unreachable")
    await page.wait_for_timeout(300)
    statuses = await page.evaluate(
        """() => Array.from(document.querySelectorAll('#ledger-body tr td:last-child .status'))
                .map(t => t.textContent.trim())"""
    )
    if not statuses or any("Offline" not in s for s in statuses):
        fail(f"ledger: unreachable filter leaked {set(statuses)}")

    # --- sorting monotonic
    await page.select_option("#ledger-status", "reachable")
    await page.select_option("#ledger-sort", "latency")
    await page.wait_for_timeout(250)
    latencies = await page.evaluate(
        """() => Array.from(document.querySelectorAll('#ledger-body tr td:nth-child(6)'))
                .map(td => Number(td.textContent.replace(/,/g, '')))"""
    )
    if latencies != sorted(latencies):
        fail("ledger: latency sort not ascending")

    # --- paging (clear the palette's search term first)
    await page.fill("#ledger-search", "")
    await page.select_option("#ledger-sort", "maturity")
    await page.wait_for_timeout(300)
    first = await page.evaluate(
        """() => document.querySelector('#ledger-body .ledger__domain').textContent.trim()"""
    )
    await page.click("#ledger-next")
    await page.wait_for_timeout(300)
    second = await page.evaluate(
        """() => document.querySelector('#ledger-body .ledger__domain').textContent.trim()"""
    )
    if first == second:
        fail("ledger: next page did not change rows")
    if "Page 2" not in (await page.text_content("#ledger-pos")):
        fail("ledger: pager position wrong")

    # --- map selection drives the dossier
    await page.click("[data-view='atlas']")
    await page.wait_for_timeout(300)
    await page.click("#state-rank-body tr:nth-child(3)")
    await page.wait_for_timeout(250)
    dossier = (await page.text_content("#dossier-name")).strip()
    row_name = (await page.text_content("#state-rank-body tr:nth-child(3) td:nth-child(2)")).strip()
    if dossier != row_name:
        fail(f"atlas: dossier {dossier!r} != clicked {row_name!r}")

    # --- CSV export
    await page.click("[data-view='ledger']")
    await page.wait_for_timeout(200)
    await page.select_option("#ledger-status", "all")
    await page.select_option("#ledger-tier", "all")
    await page.fill("#ledger-search", "")
    await page.wait_for_timeout(300)
    async with page.expect_download() as info:
        await page.click("#ledger-export")
    download = await info.value
    path = OUT / "export.csv"
    await download.save_as(str(path))
    exported = pd.read_csv(path)
    if len(exported) != exp["total"]:
        fail(f"export: {len(exported)} rows != {exp['total']}")
    if list(exported.columns)[:3] != ["domain", "entity", "level"]:
        fail(f"export: unexpected columns {list(exported.columns)[:3]}")

    await page.close()


async def suite_a11y(browser) -> None:
    page = await browser.new_page(viewport={"width": 1280, "height": 900})
    await page.goto(PAGE)
    await page.wait_for_selector("body[data-ready='true']", timeout=20000)

    structure = await page.evaluate(
        """() => ({
            header: !!document.querySelector('header'),
            nav: !!document.querySelector('nav'),
            main: !!document.querySelector('main'),
            footer: !!document.querySelector('footer'),
            skip: !!document.querySelector('.skip-link'),
            lang: document.documentElement.lang,
            title: document.title,
        })"""
    )
    for key in ("header", "nav", "main", "footer", "skip"):
        if not structure[key]:
            fail(f"a11y: missing {key}")
    if structure["lang"] != "en":
        fail(f"a11y: html lang={structure['lang']!r}")
    if not structure["title"]:
        fail("a11y: empty title")

    tabs = await page.evaluate(
        """() => Array.from(document.querySelectorAll('[role=tab]')).map(t => ({
            id: t.id,
            controls: t.getAttribute('aria-controls'),
            selected: t.getAttribute('aria-selected'),
        }))"""
    )
    if len(tabs) != len(VIEWS):
        fail(f"a11y: {len(tabs)} tabs, expected {len(VIEWS)}")
    for tab in tabs:
        if not tab["controls"] or not await page.query_selector(f"#{tab['controls']}"):
            fail(f"a11y: tab {tab['id']} aria-controls broken")
    if len([t for t in tabs if t["selected"] == "true"]) != 1:
        fail("a11y: tab selection is not exactly one")

    unnamed = await page.evaluate(
        """() => {
            const out = [];
            document.querySelectorAll('button, a[href], input, select').forEach(el => {
                if (el.closest('[hidden]')) return;
                const name = (el.getAttribute('aria-label') || el.textContent || '').trim()
                    || (el.labels && el.labels.length ? el.labels[0].textContent.trim() : '')
                    || el.getAttribute('title') || '';
                if (!name) out.push(el.outerHTML.slice(0, 90));
            });
            return out;
        }"""
    )
    if unnamed:
        fail(f"a11y: {len(unnamed)} unnamed controls: {unnamed[:3]}")

    svg_issues = await page.evaluate(
        """() => {
            const out = [];
            document.querySelectorAll('svg').forEach(svg => {
                if (!svg.getAttribute('aria-label') && !svg.getAttribute('aria-hidden')) {
                    out.push(svg.outerHTML.slice(0, 70));
                }
            });
            return out;
        }"""
    )
    if svg_issues:
        fail(f"a11y: {len(svg_issues)} unlabelled svg: {svg_issues[:2]}")

    await page.focus("[data-view='overview']")
    await page.keyboard.press("ArrowRight")
    await page.wait_for_timeout(200)
    focused = await page.evaluate("() => document.activeElement.id")
    if focused != "tab-atlas":
        fail(f"a11y: ArrowRight focused {focused!r}, expected tab-atlas")

    ring = await page.evaluate(
        """() => {
            const el = document.querySelector('#palette-open');
            el.focus();
            const cs = getComputedStyle(el);
            return { width: cs.outlineWidth, style: cs.outlineStyle };
        }"""
    )
    if ring["style"] == "none" or ring["width"] in ("0px", ""):
        fail(f"a11y: no focus ring on icon button ({ring})")

    # Chrome reports these tokens as oklch(), which canvas does not normalise, so
    # convert OKLCH -> OKLab -> linear sRGB -> sRGB explicitly before computing
    # relative luminance.
    contrast_js = """() => {
        const toRgb = (value) => {
            const oklch = value.match(/oklch\\(\\s*([\\d.]+)\\s+([\\d.]+)\\s+([\\d.]+)/);
            if (oklch) {
                const L = Number(oklch[1]);
                const C = Number(oklch[2]);
                const H = (Number(oklch[3]) * Math.PI) / 180;
                const a = C * Math.cos(H);
                const b = C * Math.sin(H);

                const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
                const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
                const s_ = L - 0.0894841775 * a - 1.2914855480 * b;
                const l = l_ ** 3, m = m_ ** 3, s = s_ ** 3;

                const lin = [
                    +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
                    -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
                    -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
                ];
                return lin.map(v => {
                    const c = Math.max(0, Math.min(1, v));
                    const enc = c <= 0.0031308 ? 12.92 * c : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
                    return Math.round(enc * 255);
                });
            }
            return value.match(/[\\d.]+/g).slice(0, 3).map(Number);
        };
        const lum = (rgb) => {
            const [r, g, b] = rgb.map(v => {
                const s = v / 255;
                return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
            });
            return 0.2126 * r + 0.7152 * g + 0.0722 * b;
        };
        const ratio = (a, b) => {
            const [l1, l2] = [lum(a), lum(b)].sort((x, y) => y - x);
            return (l1 + 0.05) / (l2 + 0.05);
        };
        const body = getComputedStyle(document.body);
        const paper = toRgb(body.backgroundColor);
        return {
            body: ratio(toRgb(body.color), paper),
            muted: ratio(toRgb(getComputedStyle(document.querySelector('.band__note')).color), paper),
            label: ratio(toRgb(getComputedStyle(document.querySelector('.band__label')).color), paper),
            ink: toRgb(body.color),
            paper: paper,
        };
    }"""

    light = await page.evaluate(contrast_js)
    if light["body"] < 7:
        fail(f"a11y: light body contrast {light['body']:.2f} < 7")
    if light["muted"] < 4.5:
        fail(f"a11y: light muted contrast {light['muted']:.2f} < 4.5")
    if light["label"] < 4.5:
        fail(f"a11y: light label contrast {light['label']:.2f} < 4.5")

    await page.click("[data-theme-set='dark']")
    await page.wait_for_timeout(250)
    dark = await page.evaluate(contrast_js)
    if dark["body"] < 7:
        fail(f"a11y: dark body contrast {dark['body']:.2f} < 7")
    if dark["muted"] < 4.5:
        fail(f"a11y: dark muted contrast {dark['muted']:.2f} < 4.5")
    if dark["label"] < 4.5:
        fail(f"a11y: dark label contrast {dark['label']:.2f} < 4.5")

    await page.close()


# ----------------------------------------------------------------------- main


async def main(suites: list[str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    exp = expected()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()

        if "layout" in suites:
            await suite_layout(browser)
        if "data" in suites:
            await suite_data(browser, exp)
        if "behaviour" in suites:
            await suite_behaviour(browser, exp)
        if "a11y" in suites:
            await suite_a11y(browser)

        await browser.close()

    print(f"Ran {checks} numeric assertions. Suites: {', '.join(suites)}")
    if failures:
        print(f"\n{len(failures)} FAILURE(S)")
        for f in failures[:50]:
            print(" -", f)
        return 1

    print("All suites passed.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--suite", default="all", choices=["all", "layout", "data", "behaviour", "a11y"]
    )
    args = parser.parse_args()
    chosen = ["layout", "data", "behaviour", "a11y"] if args.suite == "all" else [args.suite]
    sys.exit(asyncio.run(main(chosen)))
