"""Command-line interface for the CivicWeb Observatory dataset.

    civicweb info
    civicweb countries --top 10
    civicweb sectors
    civicweb vantage
    civicweb arch
    civicweb export --format csv --out measurements.csv
    civicweb query --country NL --min-maturity 80
"""

from __future__ import annotations

import argparse
import sys

import pandas as pd

from . import (
    __version__,
    architecture_summary,
    country_summary,
    describe_release,
    load,
    sector_summary,
    vantage_comparison,
)


def _print_table(df: pd.DataFrame) -> None:
    with pd.option_context(
        "display.max_columns", None,
        "display.width", 200,
        "display.max_rows", 300,
    ):
        print(df.to_string())


def cmd_info(_: argparse.Namespace) -> int:
    info = describe_release()
    width = max(len(k) for k in info)
    print(f"CivicWeb Observatory v{info['version']}")
    print("-" * (width + 24))
    for key, value in info.items():
        if key in {"version", "source"}:
            continue
        print(f"{key.replace('_', ' ').capitalize():<{width}}  {value}")
    print(f"{'source':<{width}}  {info['source']}")
    return 0


def cmd_countries(args: argparse.Namespace) -> int:
    _print_table(country_summary().head(args.top))
    return 0


def cmd_sectors(_: argparse.Namespace) -> int:
    _print_table(sector_summary())
    return 0


def cmd_vantage(_: argparse.Namespace) -> int:
    _print_table(vantage_comparison())
    return 0


def cmd_arch(_: argparse.Namespace) -> int:
    _print_table(architecture_summary())
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    df = load(reachable=True if args.reachable_only else None)
    out = args.out

    if args.format == "csv":
        df.to_csv(out, index=False)
    elif args.format == "json":
        df.to_json(out, orient="records", indent=2)
    elif args.format == "parquet":
        df.to_parquet(out, index=False)
    else:  # pragma: no cover - argparse restricts the choices
        raise SystemExit(f"unknown format {args.format}")

    print(f"Wrote {len(df):,} rows to {out}")
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    df = load(
        reachable=True if args.reachable_only else None,
        countries=[args.country] if args.country else None,
        domestic_only=args.domestic_only,
    )

    if args.min_maturity is not None:
        df = df[df["observatory_maturity_score"] >= args.min_maturity]

    if args.search:
        needle = args.search.lower()
        df = df[df["domain_name"].str.lower().str.contains(needle, na=False)]

    columns = [
        "domain_name",
        "probe_country",
        "domestic_probe",
        "sub_accessibility_score",
        "sub_security_headers_score",
        "sub_response_latency_ms",
        "observatory_maturity_score",
    ]

    result = df[columns].sort_values("observatory_maturity_score", ascending=False)
    _print_table(result.head(args.limit))
    print(f"\n{len(result):,} matching domains")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="civicweb",
        description=(
            "Query the CivicWeb Observatory measurement of 2,143 government "
            "domains across 82 countries."
        ),
    )
    parser.add_argument("--version", action="version", version=f"civicweb-observatory {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("info", help="release summary").set_defaults(func=cmd_info)
    sub.add_parser("sectors", help="per-sector table").set_defaults(func=cmd_sectors)
    sub.add_parser("vantage", help="domestic vs nearest comparison").set_defaults(func=cmd_vantage)
    sub.add_parser("arch", help="per-platform comparison").set_defaults(func=cmd_arch)

    countries = sub.add_parser("countries", help="country ranking")
    countries.add_argument("--top", type=int, default=20, help="show only the first N")
    countries.set_defaults(func=cmd_countries)

    export = sub.add_parser("export", help="write the dataset to a file")
    export.add_argument("--format", choices=["csv", "json", "parquet"], default="csv")
    export.add_argument("--out", required=True)
    export.add_argument("--reachable-only", action="store_true")
    export.set_defaults(func=cmd_export)

    query = sub.add_parser("query", help="filter domains")
    query.add_argument("--country", help="ISO-3166 alpha-2, e.g. NL")
    query.add_argument("--search", help="substring of the hostname")
    query.add_argument("--min-maturity", type=float)
    query.add_argument("--limit", type=int, default=25)
    query.add_argument("--reachable-only", action="store_true")
    query.add_argument(
        "--domestic-only",
        action="store_true",
        help="keep only rows measured from inside the target country",
    )
    query.set_defaults(func=cmd_query)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
