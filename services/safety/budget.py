"""Domain crawl budget and resource consumption tracking."""

from __future__ import annotations

import time
from typing import Dict
from urllib.parse import urlparse


class CrawlBudgetExceeded(Exception):
    """Raised when a domain has exhausted its assigned crawl budget."""
    pass


class DomainBudgetTracker:
    """Tracks page count, agent steps, total bytes, and elapsed runtime per domain."""

    def __init__(
        self,
        max_pages: int = 10,
        max_extra_pages: int = 5,
        max_agent_steps: int = 20,
        max_runtime_seconds: int = 300,
    ):
        self.max_total_pages = max_pages + max_extra_pages
        self.max_agent_steps = max_agent_steps
        self.max_runtime_seconds = max_runtime_seconds

        self._start_times: Dict[str, float] = {}
        self._pages_crawled: Dict[str, int] = {}
        self._steps_taken: Dict[str, int] = {}
        self._total_bytes: Dict[str, int] = {}

    def get_netloc(self, domain_or_url: str) -> str:
        if "://" in domain_or_url:
            return urlparse(domain_or_url).netloc.lower()
        return domain_or_url.lower()

    def start_session(self, domain_or_url: str) -> None:
        netloc = self.get_netloc(domain_or_url)
        self._start_times[netloc] = time.time()
        self._pages_crawled[netloc] = 0
        self._steps_taken[netloc] = 0
        self._total_bytes[netloc] = 0

    def record_step(self, domain_or_url: str) -> None:
        netloc = self.get_netloc(domain_or_url)
        steps = self._steps_taken.get(netloc, 0) + 1
        self._steps_taken[netloc] = steps
        if steps > self.max_agent_steps:
            raise CrawlBudgetExceeded(f"Exceeded max agent steps ({self.max_agent_steps}) for {netloc}")

    def record_page(self, domain_or_url: str, byte_size: int = 0) -> None:
        netloc = self.get_netloc(domain_or_url)
        pages = self._pages_crawled.get(netloc, 0) + 1
        self._pages_crawled[netloc] = pages
        self._total_bytes[netloc] = self._total_bytes.get(netloc, 0) + byte_size

        if pages > self.max_total_pages:
            raise CrawlBudgetExceeded(f"Exceeded max pages ({self.max_total_pages}) for {netloc}")

        elapsed = time.time() - self._start_times.get(netloc, time.time())
        if elapsed > self.max_runtime_seconds:
            raise CrawlBudgetExceeded(f"Exceeded max runtime ({self.max_runtime_seconds}s) for {netloc}")

    def get_summary(self, domain_or_url: str) -> dict:
        netloc = self.get_netloc(domain_or_url)
        return {
            "netloc": netloc,
            "pages_crawled": self._pages_crawled.get(netloc, 0),
            "steps_taken": self._steps_taken.get(netloc, 0),
            "total_bytes": self._total_bytes.get(netloc, 0),
            "elapsed_seconds": time.time() - self._start_times.get(netloc, time.time()),
        }
