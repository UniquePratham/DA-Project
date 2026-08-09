"""Master Orchestrator Pipeline for BharatGov Access Observatory."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is in Python path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from configs.settings import settings
from schemas.domain import GovernmentEntityRecord, DomainStatus
from schemas.observation import ObservationRecord
from services.discovery.registry import DomainRegistryManager
from services.safety.governor import SafetyGovernor
from services.agent.controller import AgenticController
from services.analytics.exporter import DatasetExporter


async def execute_observatory_pipeline(
    dry_run: bool = True,
    limit: int = 15,
    dataset_version: str = "0.1.0",
) -> Dict[str, Any]:
    print("=" * 70)
    print(" BharatGov Access - Master Observatory Pipeline")
    print(f" Mode: {'DRY RUN (Simulated)' if dry_run else 'LIVE PRODUCTION'}")
    print(f" Dataset Version: {dataset_version} | Target: DataHub KGP")
    print("=" * 70)

    settings.ensure_dirs()
    crawl_id = f"crawl-master-{time.strftime('%Y%m%d-%H%M%S')}"

    # 1. Harvest & Seed Domain Registry
    print("\n[*] Initializing Government Domain Discovery Harvester...")
    registry_mgr = DomainRegistryManager()
    total_seeds = registry_mgr.load_seeds(verify_dns=False)
    registry_mgr.save_to_file()
    print(f"    Loaded {total_seeds} government domains across 36 States/UTs and Central Ministries.")

    # 2. Select batch of domains
    target_domains = registry_mgr.list_domains()[:limit]
    print(f"[*] Dispatching inspection batch of {len(target_domains)} domains to Agent Controller...")

    # 3. Execute Agent Controller under Safety Governor
    governor = SafetyGovernor()
    agent = AgenticController(governor=governor)
    observations: List[ObservationRecord] = []

    for idx, domain in enumerate(target_domains, 1):
        print(f"    [{idx}/{len(target_domains)}] Inspecting: {domain.domain_name} ({domain.entity_name})...", end=" ")

        simulated_html = None
        if dry_run:
            simulated_html = f"""
            <html lang="hi">
            <head>
                <title>{domain.entity_name}</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body>
                <h1>{domain.entity_name}</h1>
                <p>भारत सरकार का आधिकारिक पोर्टल।</p>
                <a href="/about">About Us</a>
                <a href="/docs/gazette.pdf">Circulars</a>
            </body>
            </html>
            """

        obs = await agent.execute_domain_session(domain, crawl_id, simulated_html=simulated_html)
        if obs:
            observations.append(obs)
            print(f"[VALIDATED] (Lang: {obs.language.detected_primary_language}, Nodes: {obs.structure.dom_node_count})")
        else:
            print("[UNAVAILABLE/REJECTED]")

    # 4. Export DataHub KGP Releases & Coverage Audit
    print("\n[*] Exporting DataHub KGP Dataset Release...")
    exporter = DatasetExporter()
    release_files = exporter.export_release(dataset_version, observations, target_domains)

    print("=" * 70)
    print(" Pipeline Execution Complete!")
    print(f"  - Total Observations: {len(observations)}")
    print(f"  - Parquet Release:   {release_files['parquet']}")
    print(f"  - JSONL Stream:      {release_files['jsonl']}")
    print(f"  - Coverage Audit:    {release_files['coverage']}")
    print(f"  - DataHub Manifest:  {release_files['manifest']}")
    print("=" * 70)

    return {
        "crawl_id": crawl_id,
        "dataset_version": dataset_version,
        "total_seeds": total_seeds,
        "inspected": len(target_domains),
        "validated_observations": len(observations),
        "files": {k: str(v) for k, v in release_files.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BharatGov Access Master Pipeline")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Run with simulated offline fixtures")
    parser.add_argument("--live", action="store_true", help="Run live polite network collection")
    parser.add_argument("--limit", type=int, default=15, help="Number of domains to inspect")
    parser.add_argument("--version", type=str, default="0.1.0", help="Dataset version")
    args = parser.parse_args()

    dry_run = not args.live
    res = asyncio.run(execute_observatory_pipeline(dry_run=dry_run, limit=args.limit, dataset_version=args.version))
    return 0 if res["validated_observations"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
