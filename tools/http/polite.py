"""Polite HTTP client for the CivicWeb Access observatory.

This module exists because a measurement crawler that is rude produces bad data
as well as bad manners: a site that rate-limits you returns 429, and a 429
recorded as "unreachable" is a false negative that corrupts every average
downstream.

The rules, all enforced here rather than left to the caller:

1. **Identify honestly.** The User-Agent names the project and gives a contact
   address. It does not pretend to be a browser. A site operator who wants us
   to stop can find out who we are and ask.
2. **Respect robots.txt.** Fetched once per host, cached, and obeyed. A
   disallowed path is recorded as ``robots_disallowed``, not as a failure.
3. **One request per second per host.** Enforced with a per-host lock, so
   concurrency across hosts does not become concurrency against one host.
4. **Bounded global concurrency.** A semaphore caps requests in flight, so a
   large batch cannot turn into a burst.
5. **Honour Retry-After.** A 429 or 503 with a Retry-After header is waited out
   rather than retried immediately.
6. **Back off on repeated failure.** A host that fails twice gets a longer
   delay before the third attempt.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse

import requests

from .robots import RobotsCache, RobotsTxt

#: Honest identification. The contact address is the project's, so a site
#: operator can ask us to stop.
USER_AGENT = (
    "CivicWebObservatory/1.0 "
    "(+https://uniquepratham.github.io/DA-Project/; research-bot@civicweb.in)"
)

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en;q=0.9",
    "From": "research-bot@civicweb.in",
}

#: Minimum seconds between two requests to the same host.
MIN_HOST_INTERVAL = 1.0

#: Maximum requests in flight across all hosts.
MAX_GLOBAL_CONCURRENCY = 8

#: How long to cache a robots.txt result.
ROBOTS_TTL_SECONDS = 3600


@dataclass
class HostState:
    """Per-host politeness state."""

    lock: threading.Lock = field(default_factory=threading.Lock)
    last_request_at: float = 0.0
    consecutive_failures: int = 0
    crawl_delay: float | None = None


class PoliteClient:
    """A requests session that obeys robots.txt and rate limits per host."""

    def __init__(
        self,
        *,
        min_host_interval: float = MIN_HOST_INTERVAL,
        max_global_concurrency: int = MAX_GLOBAL_CONCURRENCY,
        timeout: float = 25.0,
        respect_robots: bool = True,
    ):
        self.min_host_interval = min_host_interval
        self.timeout = timeout
        self.respect_robots = respect_robots
        self._global = threading.Semaphore(max_global_concurrency)
        self._hosts: dict[str, HostState] = {}
        self._hosts_lock = threading.Lock()
        self._session = requests.Session()
        self._session.headers.update(DEFAULT_HEADERS)
        self._robots = RobotsCache(USER_AGENT, timeout=min(10.0, timeout))

    # ------------------------------------------------------------------ hosts

    def _state(self, host: str) -> HostState:
        with self._hosts_lock:
            if host not in self._hosts:
                self._hosts[host] = HostState()
            return self._hosts[host]

    # ---------------------------------------------------------------- robots

    def allowed(self, url: str) -> bool:
        """True when robots.txt permits fetching this URL."""
        if not self.respect_robots:
            return True
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        robots = self._robots.get(parsed.scheme, parsed.netloc)
        return robots.can_fetch(USER_AGENT, url)

    def crawl_delay(self, url: str) -> float | None:
        parsed = urlparse(url)
        robots = self._robots.get(parsed.scheme, parsed.netloc)
        return robots.crawl_delay_for(USER_AGENT)

    # ------------------------------------------------------------------ fetch

    def get(self, url: str, *, allow_redirects: bool = True) -> requests.Response:
        """Fetch a URL, obeying the per-host rate limit.

        Raises ``RobotsDisallowed`` when robots.txt forbids the path, so the
        caller can record that as a distinct outcome rather than a failure.
        """
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        if not host:
            raise ValueError(f"no host in {url!r}")

        if not self.allowed(url):
            raise RobotsDisallowed(url)

        state = self._state(host)

        # Serialise per host so concurrency across hosts never becomes
        # concurrency against one host.
        with state.lock:
            # A site's own Crawl-delay overrides our default interval.
            interval = self.min_host_interval
            if state.crawl_delay is None:
                state.crawl_delay = self.crawl_delay(url) or 0.0
            interval = max(interval, state.crawl_delay)

            wait = interval - (time.time() - state.last_request_at)
            if state.consecutive_failures:
                # Back off further after repeated failures.
                wait = max(wait, min(30.0, 2.0 ** state.consecutive_failures))
            if wait > 0:
                time.sleep(wait)

            with self._global:
                try:
                    resp = self._session.get(
                        url,
                        timeout=self.timeout,
                        allow_redirects=allow_redirects,
                        verify=False,
                    )
                except Exception:
                    state.consecutive_failures += 1
                    state.last_request_at = time.time()
                    raise
                state.last_request_at = time.time()

                if resp.status_code in (429, 503):
                    state.consecutive_failures += 1
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after:
                        try:
                            time.sleep(min(60.0, float(retry_after)))
                        except ValueError:
                            pass
                elif resp.status_code < 400:
                    state.consecutive_failures = 0

                return resp

    def close(self) -> None:
        self._session.close()


class RobotsDisallowed(Exception):
    """Raised when robots.txt forbids a URL."""

    def __init__(self, url: str):
        super().__init__(f"robots.txt disallows {url}")
        self.url = url
