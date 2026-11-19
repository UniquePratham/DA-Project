"""Pytest configuration.

The package under ``packages/civicweb-observatory`` is not installed in the
test environment, so its ``src`` directory is added to ``sys.path`` here. This
is more reliable than the ``pythonpath`` ini option, which is ignored when
pytest is invoked with an explicit path outside ``testpaths``.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
PKG_SRC = REPO / "packages" / "civicweb-observatory" / "src"

for path in (REPO, PKG_SRC):
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))
