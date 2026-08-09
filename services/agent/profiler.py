"""Adaptive Website Profiler for intelligent strategy selection (Section 24)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Optional

from schemas.observation import ArchitectureType
from services.agent.llm_client import OllamaClient
from services.agent.prompts import ARCHITECTURE_PROFILING_PROMPT
from tools.browser.dom_inspector import WebStructureMeasurements


class WebsiteProfiler:
    """Profiles a domain's web architecture to choose the optimal crawl strategy."""

    def __init__(self, llm_client: Optional[OllamaClient] = None):
        self.llm = llm_client or OllamaClient()

    async def profile_domain(
        self,
        url: str,
        title: str,
        structure: WebStructureMeasurements,
        html_snippet: str,
    ) -> Dict[str, Any]:
        # 1. Deterministic heuristic fast-path
        if "angular_spa" in structure.detected_frameworks or "react_spa" in structure.detected_frameworks or "nextjs" in structure.detected_frameworks:
            return {
                "architecture_type": structure.detected_frameworks[0],
                "browser_required": True,
                "confidence": 0.96,
                "strategy": "browser_render_first",
            }

        # 2. LLM-assisted profiling
        prompt = ARCHITECTURE_PROFILING_PROMPT.format(
            url=url,
            title=title,
            frameworks=structure.detected_frameworks,
            node_count=structure.dom_node_count,
            max_depth=structure.max_dom_depth,
            forms_count=structure.forms_count,
            scripts_count=structure.script_tags_count,
            html_snippet=html_snippet[:1500],
        )

        profile = await self.llm.generate_json(prompt)
        arch = profile.get("architecture_type", "custom_portal")
        browser_req = profile.get("browser_required", False)

        return {
            "architecture_type": arch,
            "browser_required": browser_req,
            "confidence": profile.get("confidence", 0.85),
            "reasoning": profile.get("reasoning", "Inferred by Agent"),
            "strategy": "browser_render_first" if browser_req else "http_first",
        }
