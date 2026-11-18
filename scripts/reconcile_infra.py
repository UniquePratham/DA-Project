"""Reconcile the infrastructure ledger against the live provider.

Run this after any crash, or on a schedule. It is the restart-safety path the
spec requires: it finds jobs whose instance vanished, and instances whose job
was lost, and resolves both.

Usage:
    VULTR_API_KEY=... python scripts/reconcile_infra.py            # act
    VULTR_API_KEY=... python scripts/reconcile_infra.py --dry-run  # report only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from services.infrastructure.budget import BudgetGuard
from services.infrastructure.catalog import cost_model_from_catalog, load_catalog
from services.infrastructure.lifecycle import InfrastructureManager
from services.infrastructure.vultr import VultrProvider

STATE = REPO / "data" / "infra" / "state.json"
LEDGER = REPO / "data" / "infra" / "ledger.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    catalog = load_catalog()
    budget = BudgetGuard(per_job_usd=0.05, monthly_usd=1.00, ledger_path=LEDGER)
    mgr = InfrastructureManager(
        provider=VultrProvider(dry_run=args.dry_run),
        budget=budget,
        cost_model=cost_model_from_catalog(catalog),
        state_path=STATE,
        dry_run=args.dry_run,
    )

    report = mgr.reconcile(dry_run=args.dry_run)

    print(f"mode      : {'dry-run' if args.dry_run else 'live'}")
    print(f"healthy   : {len(report['healthy'])}")
    print(f"vanished  : {len(report['vanished'])} {report['vanished']}")
    print(f"orphans   : {len(report['orphans'])} {report['orphans']}")
    print(f"errors    : {len(report['errors'])} {report['errors']}")

    (REPO / "data" / "infra" / "reconcile.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
