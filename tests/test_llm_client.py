"""Unit tests for the Ollama Local AI Client."""

import asyncio
import pytest

from services.agent.llm_client import OllamaClient
from services.agent.prompts import ARCHITECTURE_PROFILING_PROMPT, CLASSIFICATION_PROMPT


def test_ollama_client_fallback_parsing():
    async def run():
        client = OllamaClient(base_url="http://127.0.0.1:99999")  # Intentionally unreachable port

        prompt = ARCHITECTURE_PROFILING_PROMPT.format(
            url="https://cowin.gov.in",
            title="CoWIN Portal",
            frameworks=["angular_spa"],
            node_count=250,
            max_depth=8,
            forms_count=1,
            scripts_count=5,
            html_snippet='<div ng-version="16.0.0"></div>',
        )

        res = await client.generate_json(prompt)
        assert res["architecture_type"] == "angular_spa"
        assert res["browser_required"] is True
        assert res["confidence"] >= 0.90

    asyncio.run(run())


def test_classification_prompt_generation():
    async def run():
        client = OllamaClient(base_url="http://127.0.0.1:99999")

        prompt = CLASSIFICATION_PROMPT.format(
            domain="varanasi.nic.in",
            title="District Varanasi Official Portal",
            level="district",
            text_summary="Official website of District Administration Varanasi Uttar Pradesh.",
        )

        res = await client.generate_json(prompt)
        assert res["website_category"] == "district_administration"
        assert "explanation" in res

    asyncio.run(run())
