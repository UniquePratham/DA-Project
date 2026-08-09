"""Master Safety Governor enforcing ethical, responsible, and compliant crawling."""

from __future__ import annotations

import re
from typing import Optional, Set
from urllib.parse import urlparse

import httpx

from configs.settings import settings
from services.safety.robots import RobotsManager
from services.safety.rate_limiter import DomainRateLimiter
from services.safety.budget import DomainBudgetTracker, CrawlBudgetExceeded


class SafetyViolationError(Exception):
    """Raised when an operation violates Safety Governor constraints."""
    pass


class SafetyGovernor:
    """Independent Safety Governor sitting between Agent/Crawler and the Network."""

    # Prohibited URL patterns & dangerous keywords (Section 16)
    PROHIBITED_PATH_PATTERNS = [
        re.compile(r"/admin/.*", re.IGNORECASE),
        re.compile(r"/wp-admin/.*", re.IGNORECASE),
        re.compile(r"/login/?$", re.IGNORECASE),
        re.compile(r"/signin/?$", re.IGNORECASE),
        re.compile(r"/auth/.*", re.IGNORECASE),
        re.compile(r"/pay(ment)?/.*", re.IGNORECASE),
        re.compile(r"/checkout/.*", re.IGNORECASE),
        re.compile(r"/submit-application/.*", re.IGNORECASE),
        re.compile(r"/generate-otp/.*", re.IGNORECASE),
        re.compile(r"/delete/.*", re.IGNORECASE),
        re.compile(r"/upload/.*", re.IGNORECASE),
    ]

    ALLOWED_METHODS = {"GET", "HEAD", "OPTIONS"}

    def __init__(
        self,
        user_agent: Optional[str] = None,
        requests_per_second: Optional[float] = None,
        max_concurrency: Optional[int] = None,
    ):
        ua = user_agent or settings.user_agent
        rps = requests_per_second or settings.requests_per_second_per_domain
        conc = max_concurrency or settings.domain_concurrency

        self.robots = RobotsManager(user_agent=ua)
        self.rate_limiter = DomainRateLimiter(requests_per_second=rps, max_concurrency=conc)
        self.budget_tracker = DomainBudgetTracker(
            max_pages=settings.max_pages_per_domain_per_cycle,
            max_extra_pages=settings.max_extra_pages_per_domain,
            max_agent_steps=settings.max_agent_steps_per_domain,
            max_runtime_seconds=settings.max_agent_runtime_seconds,
        )

    def is_action_allowed(self, method: str, url: str) -> tuple[bool, str]:
        """Check whether an intended network action is permitted under safety policy."""
        # 1. Method check: No destructive or mutating requests
        method_upper = method.upper()
        if method_upper not in self.ALLOWED_METHODS:
            return False, f"Method {method_upper} prohibited by Section 16 (Only GET/HEAD allowed)"

        # 2. Path pattern check: No sensitive endpoints (auth, payment, submissions)
        parsed = urlparse(url)
        path = parsed.path
        for pattern in self.PROHIBITED_PATH_PATTERNS:
            if pattern.search(path):
                return False, f"URL path matches prohibited pattern: {pattern.pattern}"

        return True, "Allowed"

    async def pre_request_guard(self, method: str, url: str, client: Optional[httpx.AsyncClient] = None) -> None:
        """Enforce complete pre-request safety checks before allowing network dispatch."""
        # 1. Prohibited action check
        allowed, reason = self.is_action_allowed(method, url)
        if not allowed:
            raise SafetyViolationError(f"Safety Governor Rejected Request: {reason}")

        # 2. Robots.txt check
        if not await self.robots.is_allowed(url, client):
            raise SafetyViolationError(f"Safety Governor Rejected Request: Prohibited by robots.txt for URL: {url}")

        # 3. Rate limiting and domain concurrency acquisition
        await self.rate_limiter.acquire(url)

    def post_request_record(self, url: str, status_code: int, byte_size: int = 0) -> None:
        """Record outcome, update budgets, backoff, and release concurrency."""
        try:
            self.budget_tracker.record_page(url, byte_size=byte_size)
        finally:
            self.rate_limiter.record_response(url, status_code)
            self.rate_limiter.release(url)
