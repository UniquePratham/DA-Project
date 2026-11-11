"""Capture presentation-grade screenshots of the dashboard.

Renders each view at a fixed 1600x1000 viewport with a 2x device scale factor so
the images stay crisp when placed in a slide deck or a PDF.

Usage:
    python scripts/capture_screenshots.py
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

PAGE = Path("dashboard/index.html").resolve().as_uri()
OUT = Path("resources/screenshots")

VIEWS = [
    ("overview", "01-overview"),
    ("atlas", "02-atlas"),
    ("ledger", "03-ledger"),
    ("standard", "04-standard"),
    ("method", "05-method"),
]


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()

        for theme in ("light", "dark"):
            page = await browser.new_page(
                viewport={"width": 1600, "height": 1000}, device_scale_factor=2
            )
            await page.goto(PAGE)
            await page.wait_for_selector("body[data-ready='true']", timeout=20000)
            await page.click(f"[data-theme-set='{theme}']")
            await page.wait_for_timeout(400)

            for view, name in VIEWS:
                await page.click(f"[data-view='{view}']")
                await page.wait_for_timeout(500)
                suffix = "" if theme == "light" else "-dark"
                target = OUT / f"{name}{suffix}.png"
                await page.screenshot(path=str(target), full_page=False)
                print(f"{target}  {target.stat().st_size / 1024:.0f} KB")

            await page.close()

        # A tall full-page capture of the overview, for the deck's hero slide.
        page = await browser.new_page(
            viewport={"width": 1600, "height": 1000}, device_scale_factor=2
        )
        await page.goto(PAGE)
        await page.wait_for_selector("body[data-ready='true']", timeout=20000)
        await page.wait_for_timeout(600)
        target = OUT / "00-overview-full.png"
        await page.screenshot(path=str(target), full_page=True)
        print(f"{target}  {target.stat().st_size / 1024:.0f} KB")

        # Mobile proof shot.
        mobile = await browser.new_page(
            viewport={"width": 390, "height": 844}, device_scale_factor=3
        )
        await mobile.goto(PAGE)
        await mobile.wait_for_selector("body[data-ready='true']", timeout=20000)
        await mobile.wait_for_timeout(500)
        target = OUT / "06-mobile.png"
        await mobile.screenshot(path=str(target), full_page=False)
        print(f"{target}  {target.stat().st_size / 1024:.0f} KB")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
