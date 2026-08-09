"""Playwright Headless Browser Session Manager for BharatGov Access."""

from __future__ import annotations

import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from configs.settings import settings


class BrowserSessionManager:
    """Manages Chromium instances and page lifecycle with isolated contexts."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._lock = asyncio.Lock()

    async def get_browser(self) -> Browser:
        async with self._lock:
            if self._playwright is None:
                self._playwright = await async_playwright().start()
            if self._browser is None or not self._browser.is_connected():
                self._browser = await self._playwright.chromium.launch(
                    headless=self.headless,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                    ],
                )
            return self._browser

    async def render_page(
        self,
        url: str,
        viewport_width: int = 1280,
        viewport_height: int = 800,
        timeout_ms: int = 30000,
        wait_until: str = "domcontentloaded",
    ) -> Dict[str, Any]:
        """Render a URL inside an isolated Chromium context and extract rendered HTML & metrics."""
        browser = await self.get_browser()
        context: BrowserContext = await browser.new_context(
            viewport={"width": viewport_width, "height": viewport_height},
            user_agent=settings.user_agent,
            ignore_https_errors=True,
        )
        page: Page = await context.new_page()

        try:
            resp = await page.goto(url, timeout=timeout_ms, wait_until=wait_until)
            # Brief pause for JS hydration
            await page.wait_for_timeout(1000)

            html = await page.content()
            title = await page.title()
            status = resp.status if resp else 200

            # Extract basic browser metrics
            performance_timing = await page.evaluate("""() => {
                const nav = performance.getEntriesByType('navigation')[0];
                return nav ? {
                    domContentLoaded: nav.domContentLoadedEventEnd,
                    load: nav.loadEventEnd,
                    duration: nav.duration
                } : {};
            }""")

            return {
                "url": url,
                "final_url": page.url,
                "status_code": status,
                "title": title,
                "rendered_html": html,
                "performance_timing": performance_timing,
                "page": page,
                "context": context,
            }
        except Exception as e:
            await context.close()
            return {
                "url": url,
                "final_url": url,
                "status_code": 500,
                "title": "",
                "rendered_html": "",
                "performance_timing": {},
                "page": None,
                "context": None,
                "error": str(e),
            }

    async def close(self) -> None:
        async with self._lock:
            if self._browser:
                await self._browser.close()
                self._browser = None
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
