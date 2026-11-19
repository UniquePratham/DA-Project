"""Tests for crawler politeness.

These assert the three rules the spec requires and that the previous crawler
violated: honest identification, robots.txt compliance, and per-host rate
limiting. The robots tests use a real-world pattern set (gov.uk's) because the
standard library silently fails on it.
"""

from __future__ import annotations

import time

import pytest

from tools.http.polite import USER_AGENT, PoliteClient, RobotsDisallowed
from tools.http.robots import RobotsTxt


# ------------------------------------------------------------------- robots


def test_wildcard_star_matches_any_sequence():
    r = RobotsTxt("User-agent: *\nDisallow: /search/all*\n")
    assert r.can_fetch("bot", "https://x/search/all?q=tax") is False
    assert r.can_fetch("bot", "https://x/search/all/anything") is False
    assert r.can_fetch("bot", "https://x/government/") is True


def test_dollar_anchors_to_end_of_path():
    r = RobotsTxt("User-agent: *\nDisallow: /*/print$\n")
    assert r.can_fetch("bot", "https://x/a/print") is False
    assert r.can_fetch("bot", "https://x/a/print/extra") is True


def test_allow_beats_disallow_at_equal_specificity():
    r = RobotsTxt("User-agent: *\nDisallow: /search/all*\nAllow: /search/all/ok\n")
    assert r.can_fetch("bot", "https://x/search/all/ok") is True
    assert r.can_fetch("bot", "https://x/search/all/bad") is False


def test_longest_match_wins():
    r = RobotsTxt("User-agent: *\nDisallow: /a\nAllow: /a/b\n")
    assert r.can_fetch("bot", "https://x/a/b/c") is True
    assert r.can_fetch("bot", "https://x/a/z") is False


def test_specific_agent_beats_wildcard():
    txt = (
        "User-agent: *\nDisallow: /\n\n"
        "User-agent: CivicWebObservatory\nDisallow: /private\n"
    )
    r = RobotsTxt(txt)
    assert r.can_fetch(USER_AGENT, "https://x/public") is True
    assert r.can_fetch(USER_AGENT, "https://x/private") is False
    assert r.can_fetch("other-bot", "https://x/public") is False


def test_empty_disallow_allows_everything():
    r = RobotsTxt("User-agent: *\nDisallow:\n")
    assert r.can_fetch("bot", "https://x/anything") is True


def test_crawl_delay_is_parsed():
    r = RobotsTxt("User-agent: *\nCrawl-delay: 5\n")
    assert r.crawl_delay_for("bot") == 5.0


def test_govuk_real_patterns_are_enforced():
    """The exact rules gov.uk publishes, which the stdlib parser ignores."""
    txt = (
        "User-agent: *\n"
        "Disallow: /*/print$\n"
        "Disallow: /search/all*\n"
    )
    r = RobotsTxt(txt)
    assert r.can_fetch(USER_AGENT, "https://www.gov.uk/search/all?q=tax") is False
    assert r.can_fetch(USER_AGENT, "https://www.gov.uk/government/") is True


# ------------------------------------------------------------------- client


def test_user_agent_identifies_the_project():
    assert "CivicWebObservatory" in USER_AGENT
    assert "research-bot@" in USER_AGENT
    # It must not claim to be a browser.
    assert "Mozilla" not in USER_AGENT


def test_client_refuses_a_robots_disallowed_url():
    client = PoliteClient(timeout=10)
    # gov.uk disallows /search/all*
    with pytest.raises(RobotsDisallowed):
        client.get("https://www.gov.uk/search/all?q=tax")
    client.close()


def test_client_rate_limits_the_same_host():
    client = PoliteClient(timeout=20, min_host_interval=1.0)
    t0 = time.time()
    client.get("https://www.gov.uk/government/")
    first = time.time() - t0
    t1 = time.time()
    client.get("https://www.gov.uk/government/")
    second = time.time() - t1
    client.close()
    assert second >= 0.9, f"second request was not rate limited ({second:.2f}s)"
