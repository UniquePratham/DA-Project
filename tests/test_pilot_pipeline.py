"""End-to-end integration test for the Phase 2 Pilot Pipeline."""

import asyncio
import pytest

from scripts.run_pilot import run_pilot_pipeline


def test_pilot_pipeline_dry_run():
    async def run():
        results = await run_pilot_pipeline(dry_run=True, max_sites=5)
        summary = results["summary"]
        assert summary["total"] == 5
        assert summary["passed"] == 5
        assert summary["failed"] == 0
        assert len(results["observations"]) == 5

        # Verify every observation has valid Level 1, Level 2, and Level 3 data
        for obs in results["observations"]:
            assert obs["crawl_id"].startswith("crawl-pilot-")
            assert len(obs["raw_evidence_ids"]) >= 1
            assert obs["is_validated"] is True
            assert obs["reliability"]["is_reachable"] is True
            assert obs["structure"]["dom_node_count"] > 0
            assert obs["classifications"]["website_category"] != ""

    asyncio.run(run())
