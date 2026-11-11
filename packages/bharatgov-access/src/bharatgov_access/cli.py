"""Command-line interface for the BharatGov Access dataset.

    bharatgov info
    bharatgov tiers
    bharatgov arch
    bharatgov states --top 10
    bharatgov export --format csv --out census.csv
    bharatgov query --tier district --state Kerala --min-maturity 85
"""

from __future__ import annotations

import argparse
import sys

import pandas as pd

from . import (
    __version__,
    architecture_summary,
    describe_release,
    load,
    state_ranking,
    tier_summary,
)


def _print_table(df: pd.DataFrame) -> None:
    with pd.option_context(
        "display.max_columns", None,
        "display.width", 200,
        "display.max_rows", 200,
    ):
        print(df.to_string())


def cmd_info(_: argparse.Namespace) -> int:
    info = describe_release()
    width = max(len(k) for k in info)
    print(f"BharatGov Access v{info['version']}")
    print("-" * (width + 24))
    for key, value in info.items():
        if key in {"version", "source"}:
            continue
        print(f"{key.replace('_', ' ').capitalize():<{width}}  {value}")
    print(f"{'source':<{width}}  {info['source']}")
    return 0


def cmd_tiers(_: argparse.Namespace) -> int:
    _print_table(tier_summary())
    return 0


def cmd_arch(_: argparse.Namespace) -> int:
    _print_table(architecture_summary())
    return 0


def cmd_states(args: argparse.Namespace) -> int:
    _print_table(state_ranking(top=args.top))
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
        tiers=[args.tier] if args.tier else None,
        states=[args.state] if args.state else None,
    )

    if args.min_maturity is not None:
        df = df[df["observatory_maturity_score"] >= args.min_maturity]

    if args.search:
        needle = args.search.lower()
        mask = (
            df["domain_name"].str.lower().str.contains(needle, na=False)
            | df["entity_name"].str.lower().str.contains(needle, na=False)
            | df["district"].str.lower().str.contains(needle, na=False)
        )
        df = df[mask]

    columns = [
        "domain_name",
        "government_level",
        "state_or_ut",
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
        prog="bharatgov",
        description="Query the BharatGov Access census of 12,092 Indian government domains.",
    )
    parser.add_argument("--version", action="version", version=f"bharatgov-access {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("info", help="release summary").set_defaults(func=cmd_info)
    sub.add_parser("tiers", help="per-tier census table").set_defaults(func=cmd_tiers)
    sub.add_parser("arch", help="per-platform comparison").set_defaults(func=cmd_arch)

    states = sub.add_parser("states", help="state and UT ranking")
    states.add_argument("--top", type=int, default=None, help="show only the first N")
    states.set_defaults(func=cmd_states)

    export = sub.add_parser("export", help="write the census to a file")
    export.add_argument("--format", choices=["csv", "json", "parquet"], default="csv")
    export.add_argument("--out", required=True)
    export.add_argument("--reachable-only", action="store_true")
    export.set_defaults(func=cmd_export)

    query = sub.add_parser("query", help="filter domains")
    query.add_argument("--tier", choices=[
        "central", "state_ut", "district", "academic_research",
        "judiciary", "public_sector", "urban_local_body",
    ])
    query.add_argument("--state")
    query.add_argument("--search")
    query.add_argument("--min-maturity", type=float)
    query.add_argument("--limit", type=int, default=25)
    query.add_argument("--reachable-only", action="store_true")
    query.set_defaults(func=cmd_query)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
