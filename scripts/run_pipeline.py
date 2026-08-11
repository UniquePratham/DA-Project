"""High-Throughput Parallel Master Orchestrator Pipeline for BharatGov Access Observatory.

Operates at the WEBSITE level (1 row per unique government website/domain),
extracting multi-page features (homepage, about, contact, citizen services, circulars)
across thousands of verified central, state, district, and academic portals.
"""

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
from services.safety.governor import SafetyGovernor
from services.agent.controller import AgenticController
from services.analytics.exporter import DatasetExporter


async def execute_observatory_pipeline(
    dry_run: bool = False,
    limit_websites: int = 3000,
    max_pages_per_domain: int = 4,
    concurrency: int = 16,
    dataset_version: str = "2.0.0",
    checkpoint_every: int = 25,
) -> Dict[str, Any]:
    print("=" * 80)
    print(" 🏛️  BharatGov Access - Large-Scale Website Observatory Pipeline")
    print(f" Mode: {'DRY RUN (Simulated)' if dry_run else 'LIVE PRODUCTION (Polite Concurrent Crawl)'}")
    print(f" Target Unique Websites: {limit_websites:,} | Concurrency Workers: {concurrency}")
    print(f" Multi-Page Depth: Up to {max_pages_per_domain + 1} pages/site | Dataset Version: {dataset_version}")
    print("=" * 80)

    settings.ensure_dirs()
    crawl_id = f"crawl-master-{time.strftime('%Y%m%d-%H%M%S')}"

    # 1. Harvest & Seed Domain Registry
    print("\n[*] Initializing Government Domain Discovery Harvester...")
    registry_mgr = DomainRegistryManager()
    total_seeds = registry_mgr.load_seeds(verify_dns=False)
    registry_mgr.save_to_file()
    print(f"    Loaded {total_seeds:,} initial verified seed domains across Central & 36 States/Districts.")

    # 2. Dynamic Domain Queue
    queue: asyncio.Queue[GovernmentEntityRecord] = asyncio.Queue()
    seen_domains: Set[str] = set()

    for d in registry_mgr.list_domains():
        seen_domains.add(d.domain_name)
        queue.put_nowait(d)

    observations: List[ObservationRecord] = []
    processed_records: List[GovernmentEntityRecord] = []
    lock = asyncio.Lock()

    # 3. Initialize Shared Safety Governor, Agent Controller & Exporter
    governor = SafetyGovernor()
    agent = AgenticController(governor=governor)
    exporter = DatasetExporter()

    print(f"\n[*] Starting Parallel Worker Pool ({concurrency} workers, Queue: {queue.qsize():,})...\n")

    async def worker_task(worker_id: int):
        nonlocal observations, processed_records

        while True:
            async with lock:
                if len(processed_records) >= limit_websites or (queue.empty() and len(processed_records) > 0):
                    break

            try:
                domain = await asyncio.wait_for(queue.get(), timeout=2.0)
            except (asyncio.TimeoutError, asyncio.QueueEmpty):
                break

            async with lock:
                processed_records.append(domain)
                current_site_idx = len(processed_records)

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
                    <a href="/services">Citizen Services</a>
                    <a href="/contact">Contact Directory</a>
                    <a href="/orders">Gazette Circulars</a>
                </body>
                </html>
                """

            try:
                domain_obs_list, new_domains = await agent.execute_multi_page_domain_session(
                    domain,
                    crawl_id,
                    max_subpages=max_pages_per_domain,
                    simulated_html=simulated_html,
                )

                async with lock:
                    for obs in domain_obs_list:
                        observations.append(obs)

                    # Dynamic Queue Expansion
                    for nd in new_domains:
                        if nd not in seen_domains:
                            seen_domains.add(nd)
                            new_rec = GovernmentEntityRecord(
                                domain_name=nd,
                                base_url=f"https://{nd}",
                                canonical_url=f"https://{nd}/",
                                government_level=GovernmentLevel.UNKNOWN,
                                entity_name=nd,
                                status=DomainStatus.VERIFIED,
                                tags=["dynamically_discovered"],
                            )
                            registry_mgr.add_domain(new_rec)
                            queue.put_nowait(new_rec)

                    # Progress logging
                    lat_str = f"{domain_obs_list[0].reliability.response_latency_ms:.0f}ms" if domain_obs_list and domain_obs_list[0].reliability and domain_obs_list[0].reliability.response_latency_ms is not None else "N/A"
                    score_str = f"{domain_obs_list[0].accessibility.accessibility_score:.0f}" if domain_obs_list and domain_obs_list[0].accessibility and domain_obs_list[0].accessibility.accessibility_score is not None else "N/A"
                    print(f"[{current_site_idx:,}/{limit_websites:,} Websites | W{worker_id}] {domain.domain_name} ({len(domain_obs_list)} pgs) -> [OK] {lat_str} | Score: {score_str} | Queue: {queue.qsize():,}", flush=True)

                    # Incremental Checkpoint Save
                    if current_site_idx > 0 and current_site_idx % checkpoint_every == 0:
                        exporter.export_release(dataset_version, observations, processed_records)
                        registry_mgr.save_to_file()
                        print(f"    --> [CHECKPOINT SAVED] {current_site_idx:,} unique websites ({len(observations):,} page audits) exported to data/releases/\n", flush=True)

            except Exception as e:
                print(f"[W{worker_id}] {domain.domain_name} -> [ERROR: {str(e)[:40]}]", flush=True)
            finally:
                queue.task_done()

    # Launch worker pool
    workers = [asyncio.create_task(worker_task(w_id)) for w_id in range(1, concurrency + 1)]
    await asyncio.gather(*workers)

    # Final Export (1 row per website)
    print("\n[*] Exporting Final DataHub KGP Website-Level Dataset Release...")
    release_files = exporter.export_release(dataset_version, observations, processed_records)
    registry_mgr.save_to_file()

    print("=" * 80)
    print(" 🚀 Pipeline Execution Complete!")
    print(f"  - Total Unique Websites in Dataset: {len(processed_records):,}")
    print(f"  - Total Multi-Page Observations:    {len(observations):,}")
    print(f"  - Parquet Release (1 row/site):     {release_files['parquet']}")
    print(f"  - CSV Release (1 row/site):         {release_files['csv']}")
    print(f"  - JSONL Stream:                     {release_files['jsonl']}")
    print(f"  - Coverage Audit:                   {release_files['coverage']}")
    print(f"  - DataHub Manifest:                 {release_files['manifest']}")
    print("=" * 80)

    return {
        "crawl_id": crawl_id,
        "dataset_version": dataset_version,
        "total_seeds": total_seeds,
        "total_discovered": len(seen_domains),
        "inspected_websites": len(processed_records),
        "validated_observations": len(observations),
        "files": {k: str(v) for k, v in release_files.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Large-Scale BharatGov Access Website Observatory Pipeline")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Run with simulated offline fixtures")
    parser.add_argument("--live", action="store_true", default=True, help="Run live polite network collection")
    parser.add_argument("--limit", "--limit-websites", dest="limit", type=int, default=3000, help="Target unique websites limit (default: 3000)")
    parser.add_argument("--pages-per-domain", type=int, default=4, help="Max subpages per domain (default: 4)")
    parser.add_argument("--workers", type=int, default=16, help="Concurrent worker tasks (default: 16)")
    parser.add_argument("--version", type=str, default="2.0.0", help="Dataset release version (default: 2.0.0)")
    parser.add_argument("--checkpoint", type=int, default=25, help="Save release checkpoint every N websites (default: 25)")
    args = parser.parse_args()

    dry_run = args.dry_run
    res = asyncio.run(execute_observatory_pipeline(
        dry_run=dry_run,
        limit_websites=args.limit,
        max_pages_per_domain=args.pages_per_domain,
        concurrency=args.workers,
        dataset_version=args.version,
        checkpoint_every=args.checkpoint,
    ))
    return 0 if res["validated_observations"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
