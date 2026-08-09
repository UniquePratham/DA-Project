"""Unit tests for Evidence Store Manager and Provenance Tracker."""

import os
from pathlib import Path
import pytest

from schemas.evidence import EvidenceType
from tools.evidence.storage import EvidenceStoreManager
from tools.evidence.provenance import ProvenanceTracker


def test_evidence_storage_and_hashing(tmp_path):
    manager = EvidenceStoreManager(base_dir=tmp_path)

    # Store HTML
    html_content = "<html><body><h1>Ministry of Finance</h1></body></html>"
    rec = manager.store_text(
        crawl_id="crawl-test-1",
        domain_id="dom-fin-1",
        source_url="https://finmin.nic.in",
        text=html_content,
        evidence_type=EvidenceType.HTML,
    )

    assert rec.byte_size == len(html_content.encode("utf-8"))
    assert Path(rec.file_path).exists()
    assert len(rec.sha256_hash) == 64

    # Store JSON
    json_data = {"score": 95, "status": "pass"}
    j_rec = manager.store_json(
        crawl_id="crawl-test-1",
        domain_id="dom-fin-1",
        source_url="https://finmin.nic.in",
        json_obj=json_data,
        evidence_type=EvidenceType.AXE_JSON,
    )
    assert Path(j_rec.file_path).exists()
    assert j_rec.evidence_type == EvidenceType.AXE_JSON


def test_provenance_creation():
    prov = ProvenanceTracker.create_provenance(
        field_name="website_category",
        derived_value="finance_and_revenue",
        evidence_ids=["ev-html-1234"],
        confidence=0.96,
        model="qwen3:4b",
    )
    assert prov.field_name == "website_category"
    assert prov.derived_value == "finance_and_revenue"
    assert prov.confidence == 0.96
    assert "ev-html-1234" in prov.evidence_ids

    # Should raise error if no evidence provided
    with pytest.raises(ValueError):
        ProvenanceTracker.create_provenance(
            field_name="category",
            derived_value="portal",
            evidence_ids=[],
        )
