"""Unit tests for the Agentic Controller state machine."""

import asyncio
import pytest

from schemas.domain import GovernmentEntityRecord, GovernmentLevel
from services.agent.controller import AgenticController


def test_agent_controller_session(tmp_path):
    async def run():
        controller = AgenticController()
        # Point evidence base_dir to temp
        controller.evidence_mgr.base_dir = tmp_path

        domain = GovernmentEntityRecord(
            domain_name="up.gov.in",
            base_url="https://up.gov.in",
            government_level=GovernmentLevel.STATE_UT,
            state_or_ut="Uttar Pradesh",
            entity_name="Government of Uttar Pradesh Portal",
        )

        simulated_html = """
        <html lang="hi">
        <head><title>उत्तर प्रदेश सरकार</title></head>
        <body>
            <h1>मुख्य पृष्ठ</h1>
            <p>उत्तर प्रदेश सरकार की आधिकारिक वेबसाइट।</p>
            <a href="/about">About</a>
            <a href="/schemes">Schemes</a>
        </body>
        </html>
        """

        obs, new_domains, subpages = await controller.execute_domain_session(domain, "crawl-agent-test", simulated_html=simulated_html)
        assert obs is not None
        assert obs.is_validated is True
        assert obs.language.detected_primary_language == "hi"
        assert obs.domain_id == domain.domain_id
        assert len(obs.classifications.provenances) >= 1
        assert obs.classifications.provenances[0].evidence_ids[0] in obs.raw_evidence_ids

        # Test multi-page session
        obs_list, multi_domains = await controller.execute_multi_page_domain_session(domain, "crawl-agent-multi", simulated_html=simulated_html)
        assert len(obs_list) >= 1

    asyncio.run(run())
