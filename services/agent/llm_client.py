"""Ollama Local AI Client with Model Abstraction and Intelligent Offline Fallback."""

from __future__ import annotations

import json
import re
import time
from typing import Dict, Any, Optional
import httpx

from configs.settings import settings


class OllamaClient:
    """Interfaces with local Ollama daemon for open-weight model inference."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.agent_model
        self.timeout = timeout
        self._last_offline_check: float = 0.0
        self._is_offline: bool = False

    async def is_available(self) -> bool:
        now = time.time()
        # Cache availability for 30s
        if self._is_offline and (now - self._last_offline_check) < 30.0:
            return False

        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                self._is_offline = (res.status_code != 200)
                self._last_offline_check = now
                return not self._is_offline
        except Exception:
            self._is_offline = True
            self._last_offline_check = now
            return False

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Request structured JSON from Ollama local model with fast fallback."""
        # Fast path if Ollama is known to be offline
        if not await self.is_available():
            return self._mock_fallback(prompt)

        endpoint = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        timeout_cfg = httpx.Timeout(self.timeout, connect=2.0)
        try:
            async with httpx.AsyncClient(timeout=timeout_cfg) as client:
                resp = await client.post(endpoint, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    raw_text = data.get("response", "{}").strip()
                    return self._parse_json_safe(raw_text)
                else:
                    return self._mock_fallback(prompt)
        except Exception:
            self._is_offline = True
            self._last_offline_check = time.time()
            return self._mock_fallback(prompt)

    def _parse_json_safe(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
            return {}

    def _mock_fallback(self, prompt: str) -> Dict[str, Any]:
        """Deterministic rule-based fallback when Ollama is offline."""
        prompt_lower = prompt.lower()
        if "angular" in prompt_lower or "ng-version" in prompt_lower:
            return {
                "architecture_type": "angular_spa",
                "browser_required": True,
                "confidence": 0.95,
                "reasoning": "Detected Angular runtime marker (deterministic fallback)",
            }
        elif "wordpress" in prompt_lower or "wp-content" in prompt_lower:
            return {
                "architecture_type": "wordpress",
                "browser_required": False,
                "confidence": 0.92,
                "reasoning": "Detected WordPress theme markers (deterministic fallback)",
            }
        elif "selected_pages" in prompt_lower or "candidate extracted links" in prompt_lower:
            return {
                "selected_pages": [
                    {"url": "/about", "page_role": "about", "priority": 1},
                    {"url": "/contact", "page_role": "contact", "priority": 2},
                    {"url": "/services", "page_role": "public_service", "priority": 1},
                ]
            }
        elif "district" in prompt_lower or ".nic.in" in prompt_lower:
            return {
                "website_category": "district_administration",
                "confidence": 0.95,
                "service_type": "information",
                "explanation": "District administration portal providing citizen information and circulars.",
            }
        else:
            return {
                "architecture_type": "custom_portal",
                "browser_required": False,
                "confidence": 0.85,
                "website_category": "general_portal",
                "service_type": "information",
                "explanation": "General Indian government web property.",
            }
