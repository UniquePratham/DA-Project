"""Bundle the released global dataset into the Python package.

The package previously shipped the India-only census. The project now measures
82 countries, so the bundled artefact is the global measurement table with its
vantage provenance intact.

Usage:
    python scripts/build_package_data.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import pandas as pd  # noqa: E402

from global_dataset import read_global  # noqa: E402

OUT = (
    REPO
    / "packages"
    / "civicweb-observatory"
    / "src"
    / "civicweb_observatory"
    / "data"
    / "civicweb_observatory_global.parquet"
)


def main() -> int:
    df = read_global()

    # Parquet keeps the nullable booleans as nullable, so an unmeasured value
    # stays distinguishable from False.
    for column in df.columns:
        if df[column].dtype == "object":
            df[column] = df[column].astype("string")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT, index=False)

    check = pd.read_parquet(OUT)
    assert len(check) == len(df), "row count changed on write"
    assert check["probe_country"].notna().all(), "a country code was lost"

    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")
    print(f"  rows: {len(check):,}")
    print(f"  countries: {check['probe_country'].nunique()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
