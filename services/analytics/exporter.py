"""DataHub KGP Dataset Exporter producing website-level (1 row per domain) releases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict

import pandas as pd

from configs.settings import settings
from schemas.observation import ObservationRecord, PageRole
from schemas.domain import GovernmentEntityRecord
from services.analytics.coverage import CoverageAuditor


class DatasetExporter:
    """Exports validated website-level observations into DataHub-ready versioned releases (1 row per website)."""

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

        # 1. Build lookup map of registry entity records
        registry_map: Dict[str, GovernmentEntityRecord] = {r.domain_id: r for r in registry}
        # Also index by domain_name if domain_id differs
        registry_by_name: Dict[str, GovernmentEntityRecord] = {r.domain_name.lower().strip(): r for r in registry}

        # 2. Group observations by domain_id
        domain_obs_map: Dict[str, List[ObservationRecord]] = defaultdict(list)
        for o in observations:
            domain_obs_map[o.domain_id].append(o)

        # 3. Build Website-Level Records (Exactly 1 row per unique website)
        website_rows: List[Dict[str, Any]] = []

        for domain_id, obs_list in domain_obs_map.items():
            if not obs_list:
                continue

            # Find representative homepage and subpages
            homepage_obs = next((o for o in obs_list if o.page_role == PageRole.HOMEPAGE), obs_list[0])
            about_obs = next((o for o in obs_list if o.page_role == PageRole.ABOUT), None)
            contact_obs = next((o for o in obs_list if o.page_role == PageRole.CONTACT), None)
            services_obs = next((o for o in obs_list if o.page_role == PageRole.PUBLIC_SERVICE or o.page_role == PageRole.CITIZEN_FORM), None)
            circulars_obs = next((o for o in obs_list if o.page_role == PageRole.DOCUMENT_REPOSITORY), None)

            # Retrieve domain metadata from registry
            entity_rec = registry_map.get(domain_id)
            if not entity_rec and homepage_obs.source_url:
                from urllib.parse import urlparse
                netloc = urlparse(homepage_obs.source_url).netloc.lower().split(":")[0]
                entity_rec = registry_by_name.get(netloc)

            domain_name = entity_rec.domain_name if entity_rec else urlparse(homepage_obs.source_url).netloc.split(":")[0]
            entity_name = entity_rec.entity_name if entity_rec else domain_name
            gov_level = entity_rec.government_level.value if entity_rec else "unknown"
            state_or_ut = entity_rec.state_or_ut if entity_rec else ("Central" if gov_level == "central" else "National")
            district = entity_rec.district if entity_rec else None

            # Calculate aggregated scores across all audited pages for this website
            acc_scores = [o.accessibility.accessibility_score for o in obs_list if o.accessibility and o.accessibility.accessibility_score is not None]
            perf_scores = [o.performance.lighthouse_performance_score for o in obs_list if o.performance and o.performance.lighthouse_performance_score is not None]
            
            avg_acc_score = round(sum(acc_scores) / len(acc_scores), 2) if acc_scores else None
            avg_perf_score = round(sum(perf_scores) / len(perf_scores), 2) if perf_scores else None

            total_violations = sum(o.accessibility.axe_violations_count for o in obs_list if o.accessibility)
            total_critical = sum(o.accessibility.critical_violations for o in obs_list if o.accessibility)
            total_serious = sum(o.accessibility.serious_violations for o in obs_list if o.accessibility)
            any_missing_alts = any(o.accessibility.has_missing_alts for o in obs_list if o.accessibility)
            
            total_nodes = sum(o.structure.dom_node_count for o in obs_list if o.structure)
            total_forms = sum(o.structure.forms_count for o in obs_list if o.structure)
            total_pdfs = sum(o.structure.pdf_links_count for o in obs_list if o.structure)
            any_multilingual = any(o.language.is_multilingual for o in obs_list if o.language)

            row = {
                # Identity & Governance
                "domain_name": domain_name,
                "base_url": entity_rec.base_url if entity_rec else f"https://{domain_name}",
                "entity_name": entity_name,
                "government_level": gov_level,
                "state_or_ut": state_or_ut,
                "district": district,
                "website_category": homepage_obs.classifications.website_category,
                "architecture_type": homepage_obs.classifications.architecture_type.value,
                
                # Overall Website Scores & Reliability
                "overall_accessibility_score": avg_acc_score,
                "overall_performance_score": avg_perf_score,
                "total_pages_audited": len(obs_list),
                "is_reachable": homepage_obs.reliability.is_reachable,
                "http_status_code": homepage_obs.reliability.http_status_code,
                "response_latency_ms": homepage_obs.reliability.response_latency_ms,
                "primary_language": homepage_obs.language.detected_primary_language,
                "is_multilingual": any_multilingual,

                # Security & Public Hygiene (Website Level)
                "has_https": homepage_obs.security_hygiene.has_https,
                "tls_valid": homepage_obs.reliability.tls_valid,
                "tls_version": homepage_obs.reliability.tls_version,
                "certificate_expiry_days": homepage_obs.reliability.certificate_expiry_days,
                "has_hsts": homepage_obs.security_hygiene.has_hsts,
                "has_csp": homepage_obs.security_hygiene.has_csp,
                "security_headers_score": homepage_obs.security_hygiene.security_headers_score,

                # Aggregate Complexity & Violations
                "total_wcag_violations": total_violations,
                "total_critical_violations": total_critical,
                "total_serious_violations": total_serious,
                "has_missing_alts": any_missing_alts,
                "total_dom_nodes": total_nodes,
                "total_forms_count": total_forms,
                "total_pdf_circulars": total_pdfs,

                # Page Feature: Homepage
                "homepage_url": homepage_obs.canonical_url,
                "homepage_accessibility_score": homepage_obs.accessibility.accessibility_score if homepage_obs.accessibility else None,
                "homepage_lcp_ms": homepage_obs.performance.lcp_ms if homepage_obs.performance else None,
                "homepage_dom_nodes": homepage_obs.structure.dom_node_count if homepage_obs.structure else None,

                # Page Feature: About Page
                "has_about_page": about_obs is not None,
                "about_page_url": about_obs.canonical_url if about_obs else None,
                "about_accessibility_score": about_obs.accessibility.accessibility_score if about_obs and about_obs.accessibility else None,

                # Page Feature: Contact Directory
                "has_contact_page": contact_obs is not None,
                "contact_page_url": contact_obs.canonical_url if contact_obs else None,
                "contact_accessibility_score": contact_obs.accessibility.accessibility_score if contact_obs and contact_obs.accessibility else None,

                # Page Feature: Citizen Services / Schemes
                "has_services_page": services_obs is not None,
                "services_page_url": services_obs.canonical_url if services_obs else None,
                "services_accessibility_score": services_obs.accessibility.accessibility_score if services_obs and services_obs.accessibility else None,
                "services_forms_count": services_obs.structure.forms_count if services_obs and services_obs.structure else 0,

                # Page Feature: Gazette / Circulars / Orders
                "has_circulars_page": circulars_obs is not None,
                "circulars_page_url": circulars_obs.canonical_url if circulars_obs else None,
                "circulars_accessibility_score": circulars_obs.accessibility.accessibility_score if circulars_obs and circulars_obs.accessibility else None,
                "circulars_pdf_count": circulars_obs.structure.pdf_links_count if circulars_obs and circulars_obs.structure else 0,

                # Provenance & Metadata
                "domain_id": domain_id,
                "crawl_id": homepage_obs.crawl_id,
                "dataset_version": dataset_version,
                "observed_at": homepage_obs.observed_at.isoformat(),
                "is_validated": all(o.is_validated for o in obs_list),
            }
            website_rows.append(row)

        df = pd.DataFrame(website_rows)

        # 4. Export to Apache Parquet & CSV (Website Level)
        parquet_path = self.releases_dir / f"{release_prefix}.parquet"
        df.to_parquet(parquet_path, index=False, compression="snappy")

        csv_path = self.releases_dir / f"{release_prefix}.csv"
        df.to_csv(csv_path, index=False)

        # 5. Export to JSONL (Full raw structures)
        jsonl_path = self.releases_dir / f"{release_prefix}.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for o in observations:
                dump_data = o.model_dump(mode="json") if hasattr(o, "model_dump") else o.dict()
                f.write(json.dumps(dump_data) + "\n")

        # 6. Generate Coverage Audit
        coverage_data = CoverageAuditor.calculate_coverage(registry, observations)
        coverage_data["total_unique_websites_in_dataset"] = len(website_rows)
        coverage_path = self.releases_dir / f"coverage_audit_{dataset_version}.json"
        coverage_path.write_text(json.dumps(coverage_data, indent=2), encoding="utf-8")

        # 7. Generate DataHub Release Metadata
        manifest = {
            "dataset_name": "BharatGov Access",
            "dataset_version": dataset_version,
            "description": "Agentic, Longitudinal Observatory of India's Government Web Infrastructure (Website Level)",
            "dataset_granularity": "1 row per unique government website / domain",
            "total_unique_websites": len(website_rows),
            "total_page_observations": len(observations),
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
