"""Rebuild the dashboard as a global-first site.

The previous structure had a "Future" tab holding the global data, which was
wrong: the project *is* global, so global data belongs in the main views and
India is one country among 81 rather than the subject.

New structure, six views:

1. **Overview** — global headline figures, findings, country ranking
2. **World** — the map, coverage by vantage class, country dossiers
3. **Countries** — sortable table of every measured country
4. **Registry** — the searchable domain ledger
5. **Standard** — the measurement framework
6. **Developers** — API, schema, reproduction, package

India-specific content moves into the country dossier, where it belongs.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "dashboard" / "index.html"


def main() -> int:
    html = INDEX.read_text(encoding="utf-8")

    # 1. Rename the tabs and their views.
    renames = [
        ("atlas", "world"),
        ("ledger", "registry"),
        ("method", "developers"),
    ]
    for old, new in renames:
        html = html.replace(f'id="tab-{old}"', f'id="tab-{new}"')
        html = html.replace(f'aria-controls="view-{old}"', f'aria-controls="view-{new}"')
        html = html.replace(f'data-view="{old}"', f'data-view="{new}"')
        html = html.replace(f'id="view-{old}"', f'id="view-{new}"')
        html = html.replace(f'aria-labelledby="tab-{old}"', f'aria-labelledby="tab-{new}"')

    # 2. Drop the Future view entirely; its content moves into World and Countries.
    start = html.find('<!-- ========================================================== 06 FUTURE -->')
    if start > 0:
        end = html.find("</section>", html.find('id="view-future"'))
        # find the closing of the future section (it is the last view)
        end = html.find("  </div>\n</main>", start)
        html = html[:start] + html[end:]

    INDEX.write_text(html, encoding="utf-8")
    print("renamed views and removed the Future tab")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
