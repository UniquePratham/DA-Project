"""Robots.txt parser, validator, and caching manager."""

from __future__ import annotations

import time
from typing import Dict, Optional
import urllib.robotparser
from urllib.parse import urlparse

import httpx


class RobotsManager:
    """Manages fetching, caching, and evaluation of robots.txt for domain compliance."""

    def __init__(self, user_agent: str, cache_ttl_seconds: int = 86400):
        self.user_agent = user_agent
        self.cache_ttl = cache_ttl_seconds
        self._parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self._cache_times: Dict[str, float] = {}

    def get_domain_key(self, url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}".lower()

    async def get_parser(self, url: str, client: Optional[httpx.AsyncClient] = None) -> urllib.robotparser.RobotFileParser:
        domain_key = self.get_domain_key(url)
        now = time.time()

        if domain_key in self._parsers and (now - self._cache_times.get(domain_key, 0)) < self.cache_ttl:
            return self._parsers[domain_key]

        robots_url = f"{domain_key}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)

        try:
            if client is not None:
                resp = await client.get(robots_url, timeout=10.0, follow_redirects=True)
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                else:
                    # 404 or other errors mean allow all
                    rp.allow_all = True
            else:
                async with httpx.AsyncClient(headers={"User-Agent": self.user_agent}) as direct_client:
                    resp = await direct_client.get(robots_url, timeout=10.0, follow_redirects=True)
                    if resp.status_code == 200:
                        rp.parse(resp.text.splitlines())
                    else:
                        rp.allow_all = True
        except Exception:
            # If robots.txt cannot be fetched (e.g. timeout), default to allow all or polite mode
            rp.allow_all = True

        self._parsers[domain_key] = rp
        self._cache_times[domain_key] = now
        return rp

    async def is_allowed(self, url: str, client: Optional[httpx.AsyncClient] = None) -> bool:
        """Check if URL is allowed for crawling under our user agent."""
        rp = await self.get_parser(url, client)
        if getattr(rp, "allow_all", False):
            return True
        return rp.can_fetch(self.user_agent, url) or rp.can_fetch("*", url)
