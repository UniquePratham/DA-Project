"""Run real axe-core WCAG audits on a sample of reachable portals.

This replaces the DOM-signal heuristic with an actual axe-core run in a real
browser. axe-core is injected from the local npm package, so the audit is
reproducible and does not depend on a CDN.

Output: data/real/axe_sample.csv with real violation counts per portal.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import sys
import time
from pathlib import Path

from playwright.async_api import async_playwright

AXE_PATH = Path("node_modules/axe-core/axe.min.js")


async def audit(page, url: str, axe_source: str, timeout_ms: int = 30000) -> dict:
    row = {
        "domain_name": "",
        "axe_url": url,
        "axe_status": "",
        "violations_total": None,
        "violations_critical": None,
        "violations_serious": None,
        "violations_moderate": None,
        "violations_minor": None,
        "axe_score": None,
        "rules_passed": None,
    }
    try:
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        row["axe_status"] = f"HTTP {resp.status if resp else 'none'}"
        await page.wait_for_timeout(1200)
        await page.add_script_tag(content=axe_source)
        result = await page.evaluate(
            """async () => {
                const r = await axe.run(document, {
                    runOnly: { type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa'] }
                });
                const counts = {critical:0, serious:0, moderate:0, minor:0};
                for (const v of r.violations) counts[v.impact] = (counts[v.impact]||0) + 1;
                return {
                    total: r.violations.length,
                    counts,
                    passes: r.passes.length,
                    incomplete: r.incomplete.length
                };
            }"""
        )
        c = result["counts"]
        row["violations_total"] = result["total"]
        row["violations_critical"] = c.get("critical", 0)
        row["violations_serious"] = c.get("serious", 0)
        row["violations_moderate"] = c.get("moderate", 0)
        row["violations_minor"] = c.get("minor", 0)
        row["rules_passed"] = result["passes"]
        # axe has no native score; this is a documented severity-weighted index.
        penalty = (
            c.get("critical", 0) * 12.0
            + c.get("serious", 0) * 6.0
            + c.get("moderate", 0) * 3.0
            + c.get("minor", 0) * 1.0
        )
        row["axe_score"] = round(max(0.0, min(100.0, 100.0 - penalty)), 1)
    except Exception as exc:  # noqa: BLE001
        row["axe_status"] = f"error: {type(exc).__name__}"
    return row


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="dataset CSV")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--concurrency", type=int, default=4)
    args = ap.parse_args()

    if not AXE_PATH.exists():
        print(f"missing {AXE_PATH}; run: npm install axe-core")
        return 1
    axe_source = AXE_PATH.read_text(encoding="utf-8")

    import pandas as pd

    df = pd.read_csv(args.csv)
    live = df[df.is_reachable].head(args.limit)
    print(f"auditing {len(live)} reachable portals with axe-core", flush=True)

    rows: list[dict] = []
    t0 = time.time()
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        sem = asyncio.Semaphore(args.concurrency)

        async def one(domain: str) -> None:
            async with sem:
                ctx = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
                    ),
                    ignore_https_errors=True,
                )
                page = await ctx.new_page()
                try:
                    r = await audit(page, f"https://{domain}", axe_source)
                    r["domain_name"] = domain
                    rows.append(r)
                finally:
                    await ctx.close()

        await asyncio.gather(*(one(d) for d in live["domain_name"]))
        await browser.close()

    fields = [
        "domain_name", "axe_url", "axe_status", "violations_total",
        "violations_critical", "violations_serious", "violations_moderate",
        "violations_minor", "axe_score", "rules_passed",
    ]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    ok = [r for r in rows if r["violations_total"] is not None]
    print(f"\naudited: {len(ok)}/{len(rows)} in {time.time()-t0:.0f}s")
    if ok:
        import statistics

        print(f"mean violations: {statistics.mean(r['violations_total'] for r in ok):.1f}")
        print(f"median violations: {statistics.median(r['violations_total'] for r in ok):.0f}")
        print(f"mean axe score: {statistics.mean(r['axe_score'] for r in ok):.1f}")
        print(f"portals with zero violations: {sum(1 for r in ok if r['violations_total']==0)}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
