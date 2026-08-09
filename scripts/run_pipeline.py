"""Master Orchestrator Pipeline for BharatGov Access Observatory."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Set

# Ensure project root is in Python path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from configs.settings import settings
from schemas.domain import GovernmentEntityRecord, GovernmentLevel, DomainStatus
from schemas.observation import ObservationRecord
from services.discovery.registry import DomainRegistryManager
from services.discovery.harvester import DomainHarvester
from services.safety.governor import SafetyGovernor
from services.agent.controller import AgenticController
from services.analytics.exporter import DatasetExporter


async def execute_observatory_pipeline(
    dry_run: bool = True,
    limit: int = 15,
    dataset_version: str = "0.1.0",
    checkpoint_every: int = 25,
) -> Dict[str, Any]:
    print("=" * 75)
    print(" BharatGov Access - Master Observatory Pipeline")
    print(f" Mode: {'DRY RUN (Simulated)' if dry_run else 'LIVE PRODUCTION (Polite Network Crawl)'}")
    print(f" Dataset Version: {dataset_version} | Target Limit: {limit} domains")
    print("=" * 75)

    settings.ensure_dirs()
    crawl_id = f"crawl-master-{time.strftime('%Y%m%d-%H%M%S')}"

    # 1. Harvest & Seed Domain Registry
    print("\n[*] Initializing Government Domain Discovery Harvester...")
    registry_mgr = DomainRegistryManager()
    total_seeds = registry_mgr.load_seeds(verify_dns=False)
    registry_mgr.save_to_file()
    print(f"    Loaded {total_seeds} initial seed domains across 36 States/UTs and Central Ministries.")

    # 2. Dynamic Domain Queue
    queue: List[GovernmentEntityRecord] = registry_mgr.list_domains()
    seen_domains: Set[str] = {r.domain_name for r in queue}
    observations: List[ObservationRecord] = []
    processed_records: List[GovernmentEntityRecord] = []

    # 3. Initialize Agent Controller & Exporter
    governor = SafetyGovernor()
    agent = AgenticController(governor=governor)
    exporter = DatasetExporter()

    print(f"\n[*] Starting Observatory Run (Queue size: {len(queue)}, Target: {limit})...\n")

    idx = 0
    while queue and idx < limit:
        domain = queue.pop(0)
        idx += 1
        processed_records.append(domain)

        print(f"[{idx}/{limit}] {domain.domain_name} ({domain.entity_name[:35]})...", end=" ", flush=True)

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
                <a href="https://digitalindia.gov.in">Digital India</a>
                <a href="/about">About Us</a>
                <a href="/docs/gazette.pdf">Circulars</a>
            </body>
            </html>
            """

        obs = await agent.execute_domain_session(domain, crawl_id, simulated_html=simulated_html)
        if obs:
            observations.append(obs)
            print(f"[OK] {obs.reliability.response_latency_ms:.0f}ms | Score: {obs.accessibility.accessibility_score:.0f} | Lang: {obs.language.detected_primary_language}")

            # Dynamic Discovery: Extract newly discovered gov links from page HTML to expand the queue
            if not dry_run:
                try:
                    # Read stored HTML evidence to find new domains
                    ev_file = settings.raw_data_dir / "html" / f"{obs.raw_evidence_ids[0]}.html"
                    if ev_file.exists():
                        page_html = ev_file.read_text(encoding="utf-8", errors="ignore")
                        new_links = DomainHarvester.extract_gov_links_from_html(page_html, domain.base_url)
                        for new_d in new_links:
                            if new_d not in seen_domains:
                                seen_domains.add(new_d)
                                new_rec = GovernmentEntityRecord(
                                    domain_name=new_d,
                                    base_url=f"https://{new_d}",
                                    canonical_url=f"https://{new_d}/",
                                    government_level=GovernmentLevel.UNKNOWN,
                                    entity_name=new_d,
                                    status=DomainStatus.VERIFIED,
                                    tags=["dynamically_discovered"],
                                )
                                registry_mgr.add_domain(new_rec)
                                queue.append(new_rec)
                except Exception:
                    pass
        else:
            print("[UNAVAILABLE/REJECTED]")

        # Incremental checkpoint export
        if idx % checkpoint_every == 0 and observations:
            exporter.export_release(dataset_version, observations, processed_records)
            registry_mgr.save_to_file()
            print(f"    --> [CHECKPOINT SAVED] {len(observations)} observations exported to data/releases/")

    # Final Export
    print("\n[*] Exporting Final DataHub KGP Dataset Release...")
    release_files = exporter.export_release(dataset_version, observations, processed_records)
    registry_mgr.save_to_file()

    print("=" * 75)
    print(" Pipeline Execution Complete!")
    print(f"  - Total Discovered Domains: {len(seen_domains)}")
    print(f"  - Total Processed Domains:  {len(processed_records)}")
    print(f"  - Validated Observations:   {len(observations)}")
    print(f"  - Parquet Release:          {release_files['parquet']}")
    print(f"  - CSV Release:              {release_files['csv']}")
    print(f"  - JSONL Stream:             {release_files['jsonl']}")
    print(f"  - Coverage Audit:           {release_files['coverage']}")
    print(f"  - DataHub Manifest:         {release_files['manifest']}")
    print("=" * 75)

    return {
        "crawl_id": crawl_id,
        "dataset_version": dataset_version,
        "total_seeds": total_seeds,
        "total_discovered": len(seen_domains),
        "inspected": len(processed_records),
        "validated_observations": len(observations),
        "files": {k: str(v) for k, v in release_files.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BharatGov Access Master Pipeline")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Run with simulated offline fixtures")
    parser.add_argument("--live", action="store_true", default=True, help="Run live polite network collection (default)")
    parser.add_argument("--limit", type=int, default=10000, help="Max domains to inspect (default: 10000)")
    parser.add_argument("--version", type=str, default="1.0.0", help="Dataset version (default: 1.0.0)")
    parser.add_argument("--checkpoint", type=int, default=25, help="Save dataset release every N domains (default: 25)")
    args = parser.parse_args()

    dry_run = args.dry_run
    res = asyncio.run(execute_observatory_pipeline(
        dry_run=dry_run,
        limit=args.limit,
        dataset_version=args.version,
        checkpoint_every=args.checkpoint,
    ))
    return 0 if res["validated_observations"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
