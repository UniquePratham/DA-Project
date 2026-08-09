"""Domain Registry Manager for storing and querying verified government domains."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Optional, Set

from schemas.domain import GovernmentEntityRecord, GovernmentLevel, DomainStatus
from services.discovery.harvester import DomainHarvester


class DomainRegistryManager:
    """Manages government domains in memory and file/database storage."""

    def __init__(self, registry_file: Path | None = None):
        self.registry_file = registry_file or Path("data/processed/domain_registry.json")
        self._domains: Dict[str, GovernmentEntityRecord] = {}

    def load_seeds(self, verify_dns: bool = False) -> int:
        records = DomainHarvester.harvest_seed_registry(verify_dns=verify_dns)
        for r in records:
            self._domains[r.domain_name] = r
        return len(self._domains)

    def add_domain(self, record: GovernmentEntityRecord) -> None:
        self._domains[record.domain_name] = record

    def get_domain(self, domain_name: str) -> Optional[GovernmentEntityRecord]:
        return self._domains.get(domain_name.lower().strip())

    def list_domains(
        self,
        level: Optional[GovernmentLevel] = None,
        state: Optional[str] = None,
        status: Optional[DomainStatus] = None,
    ) -> List[GovernmentEntityRecord]:
        results = list(self._domains.values())
        if level:
            results = [r for r in results if r.government_level == level]
        if state:
            results = [r for r in results if (r.state_or_ut or "").lower() == state.lower()]
        if status:
            results = [r for r in results if r.status == status]
        return results

    def save_to_file(self, target_path: Optional[Path] = None) -> Path:
        out_path = target_path or self.registry_file
        out_path.parent.mkdir(parents=True, exist_ok=True)
        data = [r.model_dump(mode="json") if hasattr(r, "model_dump") else r.dict() for r in self._domains.values()]
        out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return out_path
