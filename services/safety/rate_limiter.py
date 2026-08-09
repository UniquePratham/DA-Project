"""Per-domain rate limiting and exponential backoff manager."""

from __future__ import annotations

import asyncio
import time
from typing import Dict
from urllib.parse import urlparse


class DomainRateLimiter:
    """Enforces strict domain concurrency (max 1) and rate limits (<= 1 req/sec)."""

    def __init__(self, requests_per_second: float = 1.0, max_concurrency: int = 1):
        self.interval = 1.0 / requests_per_second
        self.max_concurrency = max_concurrency
        self._last_request_time: Dict[str, float] = {}
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
        self._cooldown_until: Dict[str, float] = {}
        self._failure_counts: Dict[str, int] = {}
        self._lock = asyncio.Lock()

    def get_netloc(self, url: str) -> str:
        return urlparse(url).netloc.lower()

    async def get_semaphore(self, netloc: str) -> asyncio.Semaphore:
        async with self._lock:
            if netloc not in self._semaphores:
                self._semaphores[netloc] = asyncio.Semaphore(self.max_concurrency)
            return self._semaphores[netloc]

    async def acquire(self, url: str) -> float:
        """Acquire permission to request a URL, respecting concurrency, cooldown, and delay."""
        netloc = self.get_netloc(url)
        sem = await self.get_semaphore(netloc)
        await sem.acquire()

        # Check cooldown
        now = time.time()
        cooldown = self._cooldown_until.get(netloc, 0.0)
        if cooldown > now:
            wait_time = cooldown - now
            await asyncio.sleep(wait_time)

        # Enforce rate limit interval
        now = time.time()
        last_time = self._last_request_time.get(netloc, 0.0)
        elapsed = now - last_time
        if elapsed < self.interval:
            wait_time = self.interval - elapsed
            await asyncio.sleep(wait_time)

        self._last_request_time[netloc] = time.time()
        return self._last_request_time[netloc]

    def release(self, url: str) -> None:
        """Release the domain concurrency semaphore."""
        netloc = self.get_netloc(url)
        if netloc in self._semaphores:
            try:
                self._semaphores[netloc].release()
            except ValueError:
                pass

    def record_response(self, url: str, status_code: int) -> None:
        """Update cooldown and exponential backoff based on status code."""
        netloc = self.get_netloc(url)
        now = time.time()

        if status_code == 429:  # Too Many Requests
            failures = self._failure_counts.get(netloc, 0) + 1
            self._failure_counts[netloc] = failures
            # Exponential backoff: 30s, 60s, 120s...
            backoff = min(300.0, 30.0 * (2 ** (failures - 1)))
            self._cooldown_until[netloc] = now + backoff
        elif 500 <= status_code <= 599:  # Server Error
            failures = self._failure_counts.get(netloc, 0) + 1
            self._failure_counts[netloc] = failures
            backoff = min(120.0, 15.0 * (2 ** (failures - 1)))
            self._cooldown_until[netloc] = now + backoff
        elif 200 <= status_code < 400:
            # Successful response clears failure counter
            self._failure_counts[netloc] = 0
