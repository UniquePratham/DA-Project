"""DataHub KGP Dataset Exporter producing versioned Parquet and JSONL releases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd

from configs.settings import settings
from schemas.observation import ObservationRecord
from schemas.domain import GovernmentEntityRecord
from services.analytics.coverage import CoverageAuditor


class DatasetExporter:
    """Exports validated observations into DataHub-ready versioned releases."""

    def __init__(self, releases_dir: Optional[Path] = None):
        self.releases_dir = releases_dir or settings.releases_dir
        self.releases_dir.mkdir(parents=True, exist_ok=True)

    def export_release(
        self,
        dataset_version: str,
        observations: List[ObservationRecord],
        registry: List[GovernmentEntityRecord],
    ) -> Dict[str, Path]:
        release_prefix = f"bharatgov_access_{dataset_version}"

        # 1. Flatten observations into tabular format for Parquet
        flat_records = []
        for o in observations:
            flat_records.append({
                "observation_id": o.observation_id,
                "crawl_id": o.crawl_id,
                "dataset_version": o.dataset_version,
                "domain_id": o.domain_id,
                "source_url": o.source_url,
                "canonical_url": o.canonical_url,
                "observed_at": o.observed_at.isoformat(),
                "page_role": o.page_role.value,
                "browser_rendered": o.browser_rendered,
                # Reliability
                "http_status_code": o.reliability.http_status_code,
                "response_latency_ms": o.reliability.response_latency_ms,
                "is_reachable": o.reliability.is_reachable,
                "tls_valid": o.reliability.tls_valid,
                "tls_version": o.reliability.tls_version,
                "certificate_expiry_days": o.reliability.certificate_expiry_days,
                # Accessibility
                "axe_violations_count": o.accessibility.axe_violations_count,
                "critical_violations": o.accessibility.critical_violations,
                "serious_violations": o.accessibility.serious_violations,
                "moderate_violations": o.accessibility.moderate_violations,
                "minor_violations": o.accessibility.minor_violations,
                "accessibility_score": o.accessibility.accessibility_score,
                "has_missing_alts": o.accessibility.has_missing_alts,
                # Performance
                "lcp_ms": o.performance.lcp_ms,
                "cls": o.performance.cls,
                "fcp_ms": o.performance.fcp_ms,
                "ttfb_ms": o.performance.ttfb_ms,
                "page_weight_bytes": o.performance.page_weight_bytes,
                "lighthouse_performance_score": o.performance.lighthouse_performance_score,
                # Language & Structure
                "detected_primary_language": o.language.detected_primary_language,
                "is_multilingual": o.language.is_multilingual,
                "dom_node_count": o.structure.dom_node_count,
                "links_count": o.structure.links_count,
                "forms_count": o.structure.forms_count,
                # Security Hygiene
                "has_https": o.security_hygiene.has_https,
                "has_hsts": o.security_hygiene.has_hsts,
                "has_csp": o.security_hygiene.has_csp,
                "security_headers_score": o.security_hygiene.security_headers_score,
                # Classifications
                "website_category": o.classifications.website_category,
                "architecture_type": o.classifications.architecture_type.value,
                "is_validated": o.is_validated,
            })

        df = pd.DataFrame(flat_records)

        # 2. Export to Apache Parquet & CSV
        parquet_path = self.releases_dir / f"{release_prefix}.parquet"
        df.to_parquet(parquet_path, index=False, compression="snappy")

        csv_path = self.releases_dir / f"{release_prefix}.csv"
        df.to_csv(csv_path, index=False)

        # 3. Export to JSONL (Full raw structures)
        jsonl_path = self.releases_dir / f"{release_prefix}.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for o in observations:
                dump_data = o.model_dump(mode="json") if hasattr(o, "model_dump") else o.dict()
                f.write(json.dumps(dump_data) + "\n")

        # 4. Generate Coverage Audit
        coverage_data = CoverageAuditor.calculate_coverage(registry, observations)
        coverage_path = self.releases_dir / f"coverage_audit_{dataset_version}.json"
        coverage_path.write_text(json.dumps(coverage_data, indent=2), encoding="utf-8")

        # 5. Generate DataHub Release Metadata
        manifest = {
            "dataset_name": "BharatGov Access",
            "dataset_version": dataset_version,
            "description": "Agentic, Longitudinal Observatory of India's Government Web Infrastructure",
            "total_observations": len(observations),
            "total_domains_observed": len(set(o.domain_id for o in observations)),
            "parquet_file": parquet_path.name,
            "csv_file": csv_path.name,
            "jsonl_file": jsonl_path.name,
            "coverage_audit_file": coverage_path.name,
            "target_platform": "DataHub KGP",
            "license": "CC-BY-4.0",
        }
        manifest_path = self.releases_dir / f"manifest_{dataset_version}.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        return {
            "parquet": parquet_path,
            "csv": csv_path,
            "jsonl": jsonl_path,
            "coverage": coverage_path,
            "manifest": manifest_path,
        }
