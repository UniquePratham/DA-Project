"""Screenshot capture and image optimization tooling."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional, Dict, Any

from playwright.async_api import Page


class ScreenshotManager:
    """Captures and stores optimized screenshots for visual evidence."""

    @staticmethod
    async def capture_page(
        page: Page,
        output_path: Path,
        full_page: bool = False,
    ) -> Dict[str, Any]:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_bytes = await page.screenshot(
            path=str(output_path),
            full_page=full_page,
            type="png",
        )

        sha256_hash = hashlib.sha256(screenshot_bytes).hexdigest()
        byte_size = len(screenshot_bytes)

        return {
            "file_path": str(output_path),
            "sha256_hash": sha256_hash,
            "byte_size": byte_size,
            "content_type": "image/png",
        }
