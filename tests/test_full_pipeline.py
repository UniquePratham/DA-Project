"""Integration tests for the Master Observatory Pipeline."""

import asyncio
from pathlib import Path
import pytest
import pandas as pd

from scripts.run_pipeline import execute_observatory_pipeline


def test_full_observatory_pipeline(tmp_path):
    async def run():
        res = await execute_observatory_pipeline(dry_run=True, limit_websites=5, dataset_version="0.1.0-test")
        assert res["total_seeds"] > 100
        assert res["inspected_websites"] >= 1
        assert res["validated_observations"] >= 1

        # Check exported parquet
        parquet_file = Path(res["files"]["parquet"])
        assert parquet_file.exists()
        df = pd.read_parquet(parquet_file)
        assert len(df) >= 1
        assert "overall_accessibility_score" in df.columns
        assert "homepage_url" in df.columns
        assert "website_category" in df.columns

        # Check coverage audit
        cov_file = Path(res["files"]["coverage"])
        assert cov_file.exists()

    asyncio.run(run())
