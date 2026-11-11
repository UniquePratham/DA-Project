"""Render the research paper from Markdown to HTML and PDF.

The Markdown file is the single source of truth. This script converts it with
Python-Markdown (tables, fenced code, footnotes), wraps it in an IEEE-style
two-column print stylesheet, typesets the LaTeX math with KaTeX, and prints to
PDF with Playwright.

Usage:
    python scripts/render_paper.py            # HTML + PDF
    python scripts/render_paper.py --html     # HTML only
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

SOURCE = Path("research_paper/BharatGov_Access_Research_Paper.md")
HTML_OUT = Path("research_paper/BharatGov_Access_Research_Paper.html")
PDF_OUT = Path("research_paper/BharatGov_Access_Research_Paper.pdf")

STYLESHEET = """
@page {
  size: letter portrait;
  margin: 17mm 13mm 18mm 13mm;
}

*, *::before, *::after { box-sizing: border-box; }

html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }

body {
  font-family: "Times New Roman", Times, Georgia, serif;
  font-size: 9.6pt;
  line-height: 1.34;
  color: #111;
  margin: 0;
  background: #fff;
  text-align: justify;
  hyphens: auto;
}

/* ---------------------------------------------------------------- masthead */

.masthead {
  text-align: center;
  border-bottom: 1.5pt solid #111;
  padding-bottom: 9pt;
  margin-bottom: 12pt;
  column-span: all;
}

.masthead .venue {
  font-size: 8pt;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #555;
  margin-bottom: 7pt;
}

.masthead h1 {
  font-size: 17pt;
  line-height: 1.16;
  font-weight: bold;
  margin: 0 0 8pt;
  text-align: center;
  letter-spacing: -0.005em;
}

.masthead .authors {
  font-size: 10pt;
  margin-bottom: 3pt;
}

.masthead .affiliation {
  font-size: 8.6pt;
  font-style: italic;
  color: #333;
  line-height: 1.4;
}

/* ------------------------------------------------------------------ layout */

.body-columns {
  column-count: 2;
  column-gap: 7mm;
  column-fill: auto;
}

h2 {
  font-size: 10.4pt;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin: 12pt 0 5pt;
  padding-bottom: 2pt;
  border-bottom: 0.5pt solid #bbb;
  break-after: avoid;
  text-align: left;
}

h3 {
  font-size: 9.8pt;
  font-weight: bold;
  font-style: italic;
  margin: 9pt 0 3pt;
  break-after: avoid;
  text-align: left;
}

p { margin: 0 0 5pt; orphans: 2; widows: 2; }

ul, ol { margin: 0 0 6pt; padding-left: 14pt; }
li { margin-bottom: 2.5pt; }

strong { font-weight: bold; }
em { font-style: italic; }

code {
  font-family: "Consolas", "Courier New", monospace;
  font-size: 8.4pt;
  background: #f2f2f2;
  padding: 0 1.5pt;
  border-radius: 1.5pt;
}

pre {
  font-family: "Consolas", "Courier New", monospace;
  font-size: 6.4pt;
  line-height: 1.25;
  background: #f7f7f7;
  border: 0.5pt solid #ddd;
  border-left: 2pt solid #a63a1e;
  padding: 5pt 6pt;
  /* Centre the block itself; the ASCII art inside stays left-aligned so its
     columns line up. Without `fit-content` the block fills both columns and the
     narrower diagram appears stranded against the left edge. */
  margin: 6pt auto;
  width: fit-content;
  max-width: 100%;
  overflow: visible;
  white-space: pre;
  break-inside: avoid;
  text-align: left;
  box-sizing: border-box;
  /* Architecture diagrams are wider than a single column, so they span both. */
  column-span: all;
}

pre code { background: none; padding: 0; font-size: inherit; }

/* ------------------------------------------------------------------ tables */

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 7.4pt;
  line-height: 1.24;
  margin: 6pt 0 8pt;
  break-inside: avoid;
  text-align: left;
}

thead th {
  background: #1b1612;
  color: #fff;
  font-weight: bold;
  padding: 3pt 3pt;
  border: 0.4pt solid #1b1612;
  vertical-align: bottom;
}

tbody td {
  padding: 2.4pt 3pt;
  border: 0.4pt solid #ccc;
  vertical-align: top;
}

tbody tr:nth-child(even) { background: #f7f5f2; }

/* Wide tables (the tier and platform comparisons) span both columns. */
table.wide {
  column-span: all;
  font-size: 7.8pt;
}

/* ------------------------------------------------------------------- math */

.katex { font-size: 0.96em; }

/* Display equations must never be clipped. `overflow: hidden` silently
   truncates the tail of an over-wide formula in print, so it is `visible`
   here; long equations are broken across lines in the Markdown source
   instead of being forced to span columns. */
.katex-display {
  margin: 6pt 0;
  overflow: visible;
  text-align: center;
}

/* ------------------------------------------------------------------ rules */

hr {
  border: 0;
  border-top: 0.5pt solid #ccc;
  margin: 9pt 0;
}

blockquote {
  margin: 6pt 0;
  padding-left: 8pt;
  border-left: 2pt solid #ccc;
  color: #333;
  font-style: italic;
}

a { color: #111; text-decoration: none; }

/* --------------------------------------------------------------- utilities */

.abstract {
  font-size: 9pt;
  background: #faf8f5;
  border-top: 1pt solid #111;
  border-bottom: 1pt solid #111;
  padding: 7pt 0;
  margin-bottom: 10pt;
  column-span: all;
}

.abstract h2 {
  border: 0;
  margin: 0 0 4pt;
  font-size: 9pt;
  letter-spacing: 0.1em;
}

.abstract p { margin-bottom: 4pt; }

.keywords {
  font-size: 8.4pt;
  margin-top: 5pt;
  color: #333;
}

@media print {
  .body-columns { column-fill: auto; }
}
"""


def split_front_matter(text: str) -> tuple[str, str]:
    """Separate the title block from the body so the masthead can span columns."""
    lines = text.split("\n")
    title_index = next(i for i, line in enumerate(lines) if line.startswith("# "))

    title = lines[title_index][2:].strip()
    rest = lines[title_index + 1 :]

    authors: list[str] = []
    affiliation: list[str] = []
    body_start = 0

    for i, line in enumerate(rest):
        stripped = line.strip()
        if stripped.startswith("**") and stripped.endswith("**"):
            # "**Pratham Agarwal**, **Amit Kumar Bairagi**, and **Vishwajeet Nand Yaduraj**"
            names = re.findall(r"\*\*(.+?)\*\*", stripped)
            authors.extend(names)
        elif stripped.startswith("*") and stripped.endswith("*") and stripped:
            affiliation.append(stripped.strip("*").strip())
        elif stripped == "---":
            body_start = i + 1
            break
        elif stripped:
            body_start = i
            break

    body = "\n".join(rest[body_start:])

    masthead = (
        '<header class="masthead">'
        '<div class="venue">Department of Computer Science and Engineering &middot; IIT Kharagpur &middot; 2026</div>'
        f"<h1>{title}</h1>"
        f'<div class="authors">{", ".join(authors)}</div>'
        f'<div class="affiliation">{"<br>".join(affiliation)}</div>'
        "</header>"
    )

    return masthead, body


def promote_wide_tables(html: str) -> str:
    """Mark the two comparison tables so they span both columns."""
    for marker in ("Governance Tier", "S3WaaS Drupal", "State / UT"):
        html = re.sub(
            r"<table>(?=(?:(?!</table>).)*?" + re.escape(marker) + ")",
            '<table class="wide">',
            html,
            count=1,
            flags=re.S,
        )
    return html


def protect_math(text: str) -> tuple[str, dict[str, str]]:
    """Swap math blocks for placeholders before Markdown runs.

    Python-Markdown treats a backslash as an escape character, so the ``\\\\``
    row separator inside a LaTeX ``aligned`` environment collapses to a single
    backslash and the equation renders as one unbroken line. Stashing the math
    first and restoring it afterwards keeps the LaTeX byte-exact.
    """
    store: dict[str, str] = {}

    def stash(match: re.Match[str]) -> str:
        key = f"\x00MATH{len(store)}\x00"
        store[key] = match.group(0)
        return key

    # Display math first, then inline, so the display delimiters win.
    text = re.sub(r"\$\$.*?\$\$", stash, text, flags=re.S)
    text = re.sub(r"(?<!\$)\$(?!\$)[^$\n]+?\$", stash, text)
    return text, store


def restore_math(html: str, store: dict[str, str]) -> str:
    for key, value in store.items():
        html = html.replace(key, value)
    return html


def build_html() -> str:
    raw = SOURCE.read_text(encoding="utf-8")
    masthead, body = split_front_matter(raw)

    body, math_store = protect_math(body)

    rendered = markdown.markdown(
        body,
        extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
        output_format="html5",
    )
    rendered = restore_math(rendered, math_store)
    rendered = promote_wide_tables(rendered)

    # Pull the abstract into its own spanning block.
    rendered = re.sub(
        r"<h2>Abstract</h2>(.*?)(?=<h2>)",
        r'<section class="abstract"><h2>Abstract</h2>\1</section>',
        rendered,
        count=1,
        flags=re.S,
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>BharatGov Access — Research Paper</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<style>{STYLESHEET}</style>
</head>
<body>
{masthead}
<div class="body-columns">
{rendered}
</div>
<script>
  renderMathInElement(document.body, {{
    delimiters: [
      {{left: '$$', right: '$$', display: true}},
      {{left: '$', right: '$', display: false}}
    ],
    throwOnError: false
  }});
</script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", action="store_true", help="skip PDF generation")
    args = parser.parse_args()

    html = build_html()
    HTML_OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {HTML_OUT} ({len(html) / 1024:.0f} KB)")

    if args.html:
        return 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(HTML_OUT.resolve().as_uri())
        page.wait_for_timeout(2500)  # let KaTeX finish typesetting
        page.pdf(
            path=str(PDF_OUT),
            format="Letter",
            print_background=True,
            margin={"top": "17mm", "bottom": "18mm", "left": "13mm", "right": "13mm"},
        )
        browser.close()

    print(f"Wrote {PDF_OUT} ({PDF_OUT.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
