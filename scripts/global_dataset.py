"""Read the released global measurement dataset without corrupting ISO codes.

``pandas.read_csv`` treats the literal string ``NA`` as missing by default.
Namibia's ISO-3166 alpha-2 code *is* ``NA``, so every Namibian row silently
vanished from every aggregate built on the default reader — 10 measured domains
and one whole country, with no error anywhere.

This module is the single reader for the released CSV. It disables the default
NA sentinel list and treats only the empty field as missing, which is what the
crawler actually writes for an unmeasured value.

It also re-exports the sector classifier from the released package, so the
dashboard, the deck and the package cannot disagree about which sector a domain
belongs to.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent

#: The append-only measurement log. Every job appends its rows, so a host
#: measured twice appears twice. Never aggregate this directly.
RAW_CSV = REPO / "data" / "real" / "global_measurements.csv"

#: The canonical release: one row per host, latest measurement wins, and no
#: content score on a body too small to audit. Built by
#: ``scripts/build_canonical_dataset.py``. This is what every aggregate reads.
GLOBAL_CSV = REPO / "data" / "real" / "global_measurements_canonical.csv"

_PACKAGE_SRC = REPO / "packages" / "civicweb-observatory" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

from civicweb_observatory import SECTORS, classify_sector  # noqa: E402

__all__ = [
    "GLOBAL_CSV",
    "RAW_CSV",
    "BOOLEAN_COLUMNS",
    "SECTORS",
    "classify_sector",
    "country_name",
    "read_global",
    "reachable",
    "domestic",
    "nearest",
]


def country_name(code: str) -> str:
    """ISO-3166 alpha-2 to a display name, falling back to the code."""
    import pycountry

    try:
        return pycountry.countries.get(alpha_2=code).name
    except AttributeError:
        return code


#: Columns the crawler writes as ``True``/``False``. Read as strings first so a
#: missing value stays missing instead of becoming ``False``.
BOOLEAN_COLUMNS = (
    "is_reachable",
    "blocked_by_waf",
    "domestic_probe",
    "sub_has_gigw_toolbar",
    "sub_https_enforced",
    "sub_is_multilingual",
    "sub_mobile_responsive",
    "sub_has_citizen_services",
    "robots_disallowed",
)


def read_global(path: Path | str | None = None) -> pd.DataFrame:
    """Load the global measurements with ISO codes preserved.

    Args:
        path: Optional override for the CSV location.

    Returns:
        The dataset with ``probe_country`` intact for every row, including
        Namibia. Boolean columns are nullable ``boolean`` so an unmeasured
        value is distinguishable from ``False``.
    """
    df = pd.read_csv(
        path or GLOBAL_CSV,
        keep_default_na=False,
        na_values=[""],
    )

    for column in BOOLEAN_COLUMNS:
        if column in df.columns:
            df[column] = df[column].astype("boolean")

    return df


def reachable(df: pd.DataFrame) -> pd.DataFrame:
    """Rows that answered, with the nullable boolean resolved."""
    return df[df["is_reachable"].fillna(False).astype(bool)]


def domestic(df: pd.DataFrame) -> pd.DataFrame:
    """Rows measured from a probe inside the target country."""
    return df[df["domestic_probe"].fillna(False).astype(bool)]


def nearest(df: pd.DataFrame) -> pd.DataFrame:
    """Rows measured from a probe in another country."""
    return df[~df["domestic_probe"].fillna(False).astype(bool)]
