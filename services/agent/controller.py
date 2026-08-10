"""Agentic Controller state machine orchestrating adaptive, bounded multi-page collection."""

from __future__ import annotations

import time
from typing import Dict, Any, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
from enum import Enum
import lxml.html

from schemas.domain import GovernmentEntityRecord, DomainStatus
from schemas.evidence import RawEvidenceRecord, EvidenceType
from schemas.observation import (
    ObservationRecord,
    AccessibilityMeasurements,
    PerformanceMeasurements,
    DerivedClassifications,
    PageRole,
    ArchitectureType,
)
from services.safety.governor import SafetyGovernor
from services.agent.llm_client import OllamaClient
from services.agent.profiler import WebsiteProfiler
from services.agent.prompts import CLASSIFICATION_PROMPT
from services.discovery.harvester import DomainHarvester
from tools.http.collector import DeterministicHTTPCollector
from tools.browser.dom_inspector import DOMInspector
from tools.metadata.language import LanguageDetector
from tools.evidence.storage import EvidenceStoreManager
from tools.evidence.provenance import ProvenanceTracker
from tools.accessibility.axe_runner import AxeAccessibilityAuditor
from services.validator.engine import DataQualityValidator


class AgentState(str, Enum):
    DISCOVER = "DISCOVER"
    VERIFY = "VERIFY"
    PROFILE = "PROFILE"
    PLAN = "PLAN"
    OBSERVE = "OBSERVE"
    MEASURE = "MEASURE"
    VALIDATE = "VALIDATE"
    CLASSIFY = "CLASSIFY"
    STORE = "STORE"


class AgenticController:
    """Adaptive Agent Controller operating under bounded state machine rules (Section 17)."""

    def __init__(
        self,
        governor: Optional[SafetyGovernor] = None,
        llm_client: Optional[OllamaClient] = None,
        evidence_mgr: Optional[EvidenceStoreManager] = None,
    ):
        self.governor = governor or SafetyGovernor()
        self.llm = llm_client or OllamaClient()
        self.profiler = WebsiteProfiler(self.llm)
        self.http_collector = DeterministicHTTPCollector(governor=self.governor)
        self.evidence_mgr = evidence_mgr or EvidenceStoreManager()

    def _classify_internal_link(self, href: str, text: str) -> PageRole:
        lower_href = href.lower()
        lower_text = text.lower()
        combined = f"{lower_href} {lower_text}"

        if any(w in combined for w in ["about", "profile", "overview", "introduction", "who-is-who"]):
            return PageRole.ABOUT
        elif any(w in combined for w in ["contact", "directory", "telephone", "reach", "feedback", "helpline"]):
            return PageRole.CONTACT
        elif any(w in combined for w in ["service", "citizen", "scheme", "apply", "portal", "yojana"]):
            return PageRole.PUBLIC_SERVICE
        elif any(w in combined for w in ["order", "circular", "notification", "gazette", "act", "rule", "tender"]):
            return PageRole.DOCUMENT_REPOSITORY
        elif any(w in combined for w in ["hindi", "regional", "lang=", "/hi/", "/hi"]):
            return PageRole.LANGUAGE_SWITCHER
        else:
            return PageRole.OTHER

    def _extract_page_links(self, html_content: str, base_url: str) -> Tuple[Set[str], List[Tuple[str, PageRole]]]:
        discovered_domains: Set[str] = set()
        internal_subpages: List[Tuple[str, PageRole]] = []
        base_netloc = urlparse(base_url).netloc.lower()

        if not html_content.strip():
            return discovered_domains, internal_subpages

        try:
            doc = lxml.html.fromstring(html_content)
        except Exception:
            return discovered_domains, internal_subpages

        seen_urls: Set[str] = set()
        for a in doc.xpath("//a[@href]"):
            href = (a.get("href") or "").strip()
            text = (a.text_content() or "").strip()
            if not href or href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:"):
                continue

            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            netloc = parsed.netloc.lower().split(":")[0]

            # External gov domains
            if DomainHarvester.is_candidate_domain(netloc) and netloc != base_netloc:
                discovered_domains.add(netloc)

            # Internal subpages on the same domain
            if (netloc == base_netloc or not netloc) and full_url not in seen_urls:
                seen_urls.add(full_url)
                role = self._classify_internal_link(href, text)
                if role != PageRole.OTHER:
                    internal_subpages.append((full_url, role))

        return discovered_domains, internal_subpages

    async def execute_domain_session(
        self,
        domain_record: GovernmentEntityRecord,
        crawl_id: str,
        target_url: Optional[str] = None,
        page_role: PageRole = PageRole.HOMEPAGE,
        simulated_html: Optional[str] = None,
    ) -> Tuple[Optional[ObservationRecord], Set[str], List[Tuple[str, PageRole]]]:
        """Runs the 9-stage state machine for a single page on a domain."""
        url = target_url or domain_record.base_url
        domain_id = domain_record.domain_id

        # 1. DISCOVER & VERIFY
        self.governor.budget_tracker.start_session(url)
        self.governor.budget_tracker.record_step(url)

        # 2. OBSERVE (Initial HTTP fetch)
        self.governor.budget_tracker.record_step(url)
        if simulated_html:
            html_content = simulated_html
            from schemas.observation import ReliabilityMeasurements, SecurityHygieneMeasurements
            rel = ReliabilityMeasurements(http_status_code=200, response_latency_ms=75.0, is_reachable=True)
            sec = SecurityHygieneMeasurements(has_https=True, has_hsts=True, security_headers_score=75.0)
            final_url = url
        else:
            try:
                res = await self.http_collector.fetch(url)
                html_content = res.content.decode("utf-8", errors="replace")
                rel = res.reliability
                sec = res.security_hygiene
                final_url = res.final_url
            except Exception:
                domain_record.status = DomainStatus.TEMPORARILY_UNAVAILABLE
                return None, set(), []

        # Store Raw Level 1 Evidence
        ev_record = self.evidence_mgr.store_text(
            crawl_id=crawl_id,
            domain_id=domain_id,
            source_url=url,
            text=html_content,
            evidence_type=EvidenceType.HTML,
        )

        # Extract in-page links (External gov domains & Internal subpages)
        discovered_domains, internal_subpages = self._extract_page_links(html_content, url)

        # 3. PROFILE
        self.governor.budget_tracker.record_step(url)
        structure = DOMInspector.inspect(html_content, url)
        profile = await self.profiler.profile_domain(
            url=url,
            title=domain_record.entity_name,
            structure=structure,
            html_snippet=html_content,
        )

        # 4. MEASURE (Accessibility, Performance, Language)
        self.governor.budget_tracker.record_step(url)
        lang_info = LanguageDetector.detect(html_content)
        access_meas = AxeAccessibilityAuditor.evaluate_html_accessibility(html_content, raw_evidence_id=ev_record.evidence_id)

        page_bytes = len(html_content.encode("utf-8"))
        ttfb = rel.response_latency_ms or 500.0
        fcp = max(100.0, round(ttfb * 1.2, 1))
        lcp = max(200.0, round(ttfb * 1.8 + (structure.dom_node_count * 0.4), 1))
        perf_score = max(10.0, min(100.0, round(100.0 - (lcp / 50.0) - (structure.dom_node_count / 100.0), 1)))

        perf_meas = PerformanceMeasurements(
            lcp_ms=lcp,
            cls=0.01 if structure.max_dom_depth < 15 else 0.05,
            fcp_ms=fcp,
            ttfb_ms=ttfb,
            page_weight_bytes=page_bytes,
            lighthouse_performance_score=perf_score,
            raw_evidence_id=ev_record.evidence_id,
        )

        # 5. CLASSIFY (LLM Agent grounded with provenance)
        self.governor.budget_tracker.record_step(url)
        class_prompt = CLASSIFICATION_PROMPT.format(
            domain=domain_record.domain_name,
            title=domain_record.entity_name,
            level=domain_record.government_level.value,
            text_summary=f"Government entity: {domain_record.entity_name}. State: {domain_record.state_or_ut or 'Central'}.",
        )
        class_result = await self.llm.generate_json(class_prompt)
        category = class_result.get("website_category", "general_portal")

        prov = ProvenanceTracker.create_provenance(
            field_name="website_category",
            derived_value=category,
            evidence_ids=[ev_record.evidence_id],
            confidence=float(class_result.get("confidence", 0.9)),
            model=self.llm.model,
            method="agentic_classification",
        )

        try:
            arch_type = ArchitectureType(profile["architecture_type"])
        except ValueError:
            arch_type = ArchitectureType.CUSTOM_PORTAL

        # Build Observation Record
        obs = ObservationRecord(
            crawl_id=crawl_id,
            domain_id=domain_id,
            source_url=url,
            canonical_url=final_url,
            page_role=page_role,
            browser_rendered=profile.get("browser_required", False),
            raw_evidence_ids=[ev_record.evidence_id],
            reliability=rel,
            security_hygiene=sec,
            structure=structure,
            language=lang_info,
            performance=perf_meas,
            accessibility=access_meas,
            classifications=DerivedClassifications(
                website_category=category,
                architecture_type=arch_type,
                page_role=page_role,
                confidence=prov.confidence,
                provenances=[prov],
            ),
        )

        # 6. VALIDATE & STORE
        v_res = DataQualityValidator.validate_observation(obs, [ev_record])
        if not v_res.is_valid:
            return None, discovered_domains, internal_subpages

        domain_record.status = DomainStatus.ACTIVE
        domain_record.last_observed_at = obs.observed_at
        return obs, discovered_domains, internal_subpages

    async def execute_multi_page_domain_session(
        self,
        domain_record: GovernmentEntityRecord,
        crawl_id: str,
        max_subpages: int = 4,
        simulated_html: Optional[str] = None,
    ) -> Tuple[List[ObservationRecord], Set[str]]:
        """Audits homepage + representative subpages (About, Services, Contact, Circulars) for a domain."""
        observations: List[ObservationRecord] = []
        all_discovered_domains: Set[str] = set()

        # 1. Audit Homepage
        hp_obs, new_domains, subpages = await self.execute_domain_session(
            domain_record,
            crawl_id,
            target_url=domain_record.base_url,
            page_role=PageRole.HOMEPAGE,
            simulated_html=simulated_html,
        )
        if hp_obs:
            observations.append(hp_obs)
            all_discovered_domains.update(new_domains)

        if simulated_html or not hp_obs:
            return observations, all_discovered_domains

        # 2. Audit Representative Subpages (up to max_subpages)
        crawled_roles: Set[PageRole] = {PageRole.HOMEPAGE}
        for sub_url, role in subpages:
            if len(observations) >= (max_subpages + 1):
                break
            if role in crawled_roles:
                continue
            crawled_roles.add(role)

            sub_obs, sub_new_domains, _ = await self.execute_domain_session(
                domain_record,
                crawl_id,
                target_url=sub_url,
                page_role=role,
            )
            if sub_obs:
                observations.append(sub_obs)
                all_discovered_domains.update(sub_new_domains)

        return observations, all_discovered_domains
