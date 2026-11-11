"""Download and self-host the dashboard's font stack as latin-subset woff2 files.

The dashboard must render identically from a ``file://`` URL with no network, so
the fonts are vendored into ``dashboard/static/fonts`` and declared with local
``@font-face`` rules in ``dashboard/static/app.css``.

Usage:
    python scripts/fetch_fonts.py
"""

from __future__ import annotations

import re
import urllib.request
from pathlib import Path

FONT_DIR = Path("dashboard/static/fonts")

# family -> list of (css2 axis spec, local file stem)
FAMILIES = {
    "Newsreader": [
        ("ital,opsz,wght@0,6..72,400", "newsreader-400"),
        ("ital,opsz,wght@0,6..72,600", "newsreader-600"),
        ("ital,opsz,wght@0,6..72,700", "newsreader-700"),
        ("ital,opsz,wght@1,6..72,400", "newsreader-400-italic"),
    ],
    "Public Sans": [
        ("wght@400", "publicsans-400"),
        ("wght@500", "publicsans-500"),
        ("wght@600", "publicsans-600"),
        ("wght@700", "publicsans-700"),
    ],
    "IBM Plex Mono": [
        ("wght@400", "plexmono-400"),
        ("wght@500", "plexmono-500"),
    ],
}

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

LATIN_BLOCK = re.compile(r"/\*\s*latin\s*\*/\s*@font-face\s*\{(.*?)\}", re.S)
URL_RE = re.compile(r"url\((https://[^)]+\.woff2)\)")


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def main() -> None:
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    written = 0

    for family, variants in FAMILIES.items():
        for axis, stem in variants:
            css_url = (
                "https://fonts.googleapis.com/css2?"
                f"family={family.replace(' ', '+')}:{axis}&display=swap"
            )
            css = fetch(css_url).decode("utf-8")
            block = LATIN_BLOCK.search(css)
            if not block:
                raise SystemExit(f"No latin subset found for {family} {axis}")
            match = URL_RE.search(block.group(1))
            if not match:
                raise SystemExit(f"No woff2 URL found for {family} {axis}")

            target = FONT_DIR / f"{stem}.woff2"
            target.write_bytes(fetch(match.group(1)))
            written += 1
            print(f"{target}  {target.stat().st_size / 1024:.1f} KB")

    print(f"\n{written} font files written to {FONT_DIR}")


if __name__ == "__main__":
    main()
