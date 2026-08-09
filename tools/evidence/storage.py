"""Evidence storage manager preserving Level 1 raw data with SHA256 integrity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Union, Dict, Any

from configs.settings import settings
from schemas.evidence import RawEvidenceRecord, EvidenceType


class EvidenceStoreManager:
    """Stores raw evidence on filesystem/MinIO and generates immutable RawEvidenceRecords."""

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or settings.raw_evidence_dir

    def store_bytes(
        self,
        crawl_id: str,
        domain_id: str,
        source_url: str,
        data: bytes,
        evidence_type: EvidenceType,
        extension: str,
        content_type: str,
        metadata: Dict[str, Any] | None = None,
    ) -> RawEvidenceRecord:
        sha256_hash = hashlib.sha256(data).hexdigest()
        filename = f"{domain_id}_{sha256_hash[:12]}.{extension}"
        sub_dir = self.base_dir / evidence_type.value
        sub_dir.mkdir(parents=True, exist_ok=True)
        file_path = sub_dir / filename

        file_path.write_bytes(data)

        return RawEvidenceRecord(
            crawl_id=crawl_id,
            domain_id=domain_id,
            source_url=source_url,
            evidence_type=evidence_type,
            file_path=str(file_path.as_posix()),
            sha256_hash=sha256_hash,
            byte_size=len(data),
            content_type=content_type,
            metadata=metadata or {},
        )

    def store_text(
        self,
        crawl_id: str,
        domain_id: str,
        source_url: str,
        text: str,
        evidence_type: EvidenceType,
        extension: str = "html",
        content_type: str = "text/html",
        metadata: Dict[str, Any] | None = None,
    ) -> RawEvidenceRecord:
        return self.store_bytes(
            crawl_id=crawl_id,
            domain_id=domain_id,
            source_url=source_url,
            data=text.encode("utf-8"),
            evidence_type=evidence_type,
            extension=extension,
            content_type=content_type,
            metadata=metadata,
        )

    def store_json(
        self,
        crawl_id: str,
        domain_id: str,
        source_url: str,
        json_obj: Dict[str, Any],
        evidence_type: EvidenceType,
        metadata: Dict[str, Any] | None = None,
    ) -> RawEvidenceRecord:
        encoded = json.dumps(json_obj, indent=2).encode("utf-8")
        return self.store_bytes(
            crawl_id=crawl_id,
            domain_id=domain_id,
            source_url=source_url,
            data=encoded,
            evidence_type=evidence_type,
            extension="json",
            content_type="application/json",
            metadata=metadata,
        )
