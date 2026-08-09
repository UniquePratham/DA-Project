"""Unit tests for the Safety Governor."""

import asyncio
import time
import pytest

from services.safety.governor import SafetyGovernor, SafetyViolationError
from services.safety.budget import DomainBudgetTracker, CrawlBudgetExceeded
from services.safety.rate_limiter import DomainRateLimiter


def test_prohibited_methods():
    governor = SafetyGovernor()
    allowed, reason = governor.is_action_allowed("POST", "https://example.gov.in/service")
    assert allowed is False
    assert "POST prohibited" in reason

    allowed, reason = governor.is_action_allowed("DELETE", "https://example.gov.in/item/1")
    assert allowed is False

    allowed, reason = governor.is_action_allowed("GET", "https://example.gov.in/about")
    assert allowed is True


def test_prohibited_paths():
    governor = SafetyGovernor()
    allowed, _ = governor.is_action_allowed("GET", "https://example.gov.in/wp-admin/install.php")
    assert allowed is False

    allowed, _ = governor.is_action_allowed("GET", "https://example.gov.in/payment/gateway")
    assert allowed is False

    allowed, _ = governor.is_action_allowed("GET", "https://example.gov.in/submit-application/form1")
    assert allowed is False

    allowed, _ = governor.is_action_allowed("GET", "https://example.gov.in/departments/health")
    assert allowed is True


def test_domain_budget_limits():
    tracker = DomainBudgetTracker(max_pages=2, max_extra_pages=0, max_runtime_seconds=60)
    tracker.start_session("https://test.gov.in")

    tracker.record_page("https://test.gov.in", byte_size=100)
    tracker.record_page("https://test.gov.in", byte_size=200)

    # 3rd page should exceed max_pages
    with pytest.raises(CrawlBudgetExceeded):
        tracker.record_page("https://test.gov.in", byte_size=100)


def test_rate_limiter_interval():
    async def run():
        # 2 requests per second = 0.5s interval
        limiter = DomainRateLimiter(requests_per_second=2.0, max_concurrency=1)
        url = "https://rate-test.gov.in/page1"

        t0 = time.time()
        await limiter.acquire(url)
        limiter.release(url)

        await limiter.acquire(url)
        limiter.release(url)
        elapsed = time.time() - t0

        assert elapsed >= 0.45  # Must wait for interval

    asyncio.run(run())
