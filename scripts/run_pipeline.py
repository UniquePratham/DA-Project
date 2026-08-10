"""High-Throughput Parallel Master Orchestrator Pipeline for BharatGov Access Observatory.

Utilizes 16 concurrent async workers, multi-page deep auditing per domain,
and dynamic in-memory hyperlink expansion to collect 10,000+ to 50,000+ observations.
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
    limit_observations: int = 10000,
    max_pages_per_domain: int = 4,
    concurrency: int = 16,
    dataset_version: str = "1.0.0",
    checkpoint_every: int = 50,
) -> Dict[str, Any]:
    print("=" * 80)
    print(" 🏛️  BharatGov Access - Large-Scale Observatory Pipeline")
    print(f" Mode: {'DRY RUN (Simulated)' if dry_run else 'LIVE PRODUCTION (Polite Concurrent Crawl)'}")
    print(f" Concurrency Workers: {concurrency} | Max Pages/Domain: {max_pages_per_domain + 1}")
    print(f" Target Observations: {limit_observations:,} | Dataset Version: {dataset_version}")
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
            # Stop condition
            async with lock:
                if len(observations) >= limit_observations or (queue.empty() and len(processed_records) > 0):
                    break

            try:
                domain = await asyncio.wait_for(queue.get(), timeout=2.0)
            except (asyncio.TimeoutError, asyncio.QueueEmpty):
                break

            async with lock:
                processed_records.append(domain)
                current_domain_idx = len(processed_records)

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
                    print(f"[{len(observations):,}/{limit_observations:,} Obs | W{worker_id}] {domain.domain_name} ({len(domain_obs_list)} pgs) -> [OK] {lat_str} | Score: {score_str} | Queue: {queue.qsize():,}", flush=True)

                    # Incremental Checkpoint Save
                    if len(observations) > 0 and len(observations) % checkpoint_every < len(domain_obs_list):
                        exporter.export_release(dataset_version, observations, processed_records)
                        registry_mgr.save_to_file()
                        print(f"    --> [CHECKPOINT SAVED] {len(observations):,} observations & {len(processed_records):,} domains exported to data/releases/\n", flush=True)

            except Exception as e:
                print(f"[W{worker_id}] {domain.domain_name} -> [ERROR: {str(e)[:40]}]", flush=True)
            finally:
                queue.task_done()

    # Launch worker pool
    workers = [asyncio.create_task(worker_task(w_id)) for w_id in range(1, concurrency + 1)]
    await asyncio.gather(*workers)

    # Final Export
    print("\n[*] Exporting Final DataHub KGP Dataset Release...")
    release_files = exporter.export_release(dataset_version, observations, processed_records)
    registry_mgr.save_to_file()

    print("=" * 80)
    print(" 🚀 Pipeline Execution Complete!")
    print(f"  - Total Discovered Domains: {len(seen_domains):,}")
    print(f"  - Total Inspected Domains:  {len(processed_records):,}")
    print(f"  - Total Validated Obs:      {len(observations):,}")
    print(f"  - Parquet Release:          {release_files['parquet']}")
    print(f"  - CSV Release:              {release_files['csv']}")
    print(f"  - JSONL Stream:             {release_files['jsonl']}")
    print(f"  - Coverage Audit:           {release_files['coverage']}")
    print(f"  - DataHub Manifest:         {release_files['manifest']}")
    print("=" * 80)

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
    parser = argparse.ArgumentParser(description="Run Large-Scale BharatGov Access Observatory Pipeline")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Run with simulated offline fixtures")
    parser.add_argument("--live", action="store_true", default=True, help="Run live polite network collection")
    parser.add_argument("--limit", type=int, default=10000, help="Target observations limit (default: 10000)")
    parser.add_argument("--pages-per-domain", type=int, default=4, help="Max subpages per domain (default: 4)")
    parser.add_argument("--workers", type=int, default=16, help="Concurrent worker tasks (default: 16)")
    parser.add_argument("--version", type=str, default="1.0.0", help="Dataset release version (default: 1.0.0)")
    parser.add_argument("--checkpoint", type=int, default=50, help="Save release checkpoint every N observations (default: 50)")
    args = parser.parse_args()

    dry_run = args.dry_run
    res = asyncio.run(execute_observatory_pipeline(
        dry_run=dry_run,
        limit_observations=args.limit,
        max_pages_per_domain=args.pages_per_domain,
        concurrency=args.workers,
        dataset_version=args.version,
        checkpoint_every=args.checkpoint,
    ))
    return 0 if res["validated_observations"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
