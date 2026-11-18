"""A robots.txt parser that implements the wildcards the standard omits.

Python's :mod:`urllib.robotparser` does not support ``*`` wildcards or ``$``
end-anchors, which the Robots Exclusion Protocol allows and which real sites
use. ``gov.uk`` publishes ``Disallow: /*/print$`` and
``Disallow: /search/all*``; the standard library silently allows both, so a
crawler built on it is not actually obeying robots.txt.

This module implements the matching rules from RFC 9309:

* ``*`` matches any sequence of characters
* ``$`` anchors the pattern to the end of the path
* the longest matching rule wins
* ``Allow`` beats ``Disallow`` when the match lengths are equal
* a rule for a specific user-agent beats a rule for ``*``

It is deliberately small and has no dependencies, so it can be audited.
"""

from __future__ import annotations

import re
import threading
import time
from dataclasses import dataclass, field
from urllib.parse import urlparse

import requests


@dataclass
class Rule:
    """One Allow or Disallow line."""

    allow: bool
    pattern: str
    regex: re.Pattern[str]
    specificity: int


@dataclass
class AgentRules:
    """The rules that apply to one user-agent group."""

    rules: list[Rule] = field(default_factory=list)
    crawl_delay: float | None = None

    def decision(self, path: str) -> tuple[bool, int]:
        """Return (allowed, match_length) for a path.

        The longest matching rule wins; on a tie, Allow wins.
        """
        best_allow: bool | None = None
        best_len = -1
        for rule in self.rules:
            m = rule.regex.match(path)
            if not m:
                continue
            length = m.end()
            if length > best_len:
                best_len = length
                best_allow = rule.allow
            elif length == best_len and rule.allow:
                # Allow beats Disallow at equal specificity.
                best_allow = True
        if best_allow is None:
            return True, 0
        return best_allow, best_len


def _compile(pattern: str) -> tuple[re.Pattern[str], int]:
    """Turn a robots pattern into a regex, honouring * and $."""
    anchored = pattern.endswith("$")
    body = pattern[:-1] if anchored else pattern

    # Escape everything, then restore the wildcard.
    parts = []
    for ch in body:
        if ch == "*":
            parts.append(".*")
        else:
            parts.append(re.escape(ch))
    regex = "^" + "".join(parts)
    if anchored:
        regex += "$"

    # Specificity is the number of literal characters, used only for ordering
    # within a group; the RFC uses match length, which we compute at match time.
    specificity = len(body.replace("*", ""))
    return re.compile(regex), specificity


class RobotsTxt:
    """A parsed robots.txt with correct wildcard handling."""

    def __init__(self, text: str = ""):
        self.groups: dict[str, AgentRules] = {}
        self._parse(text)

    def _parse(self, text: str) -> None:
        current_agents: list[str] = []
        current_rules = AgentRules()
        in_agent_block = False

        def flush() -> None:
            nonlocal current_agents, current_rules
            if current_agents:
                for agent in current_agents:
                    existing = self.groups.get(agent)
                    if existing is None:
                        self.groups[agent] = AgentRules(
                            rules=list(current_rules.rules),
                            crawl_delay=current_rules.crawl_delay,
                        )
                    else:
                        existing.rules.extend(current_rules.rules)
                        if current_rules.crawl_delay is not None:
                            existing.crawl_delay = current_rules.crawl_delay
            current_agents = []
            current_rules = AgentRules()

        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip().lower()
            value = value.strip()

            if key == "user-agent":
                if not in_agent_block:
                    flush()
                    in_agent_block = True
                current_agents.append(value.lower())
            elif key in ("allow", "disallow"):
                in_agent_block = False
                if not value:
                    # An empty Disallow means "allow everything".
                    continue
                regex, spec = _compile(value)
                current_rules.rules.append(
                    Rule(allow=(key == "allow"), pattern=value, regex=regex, specificity=spec)
                )
            elif key == "crawl-delay":
                in_agent_block = False
                try:
                    current_rules.crawl_delay = float(value)
                except ValueError:
                    pass
            else:
                in_agent_block = False

        flush()

    def rules_for(self, user_agent: str) -> AgentRules:
        """The rules for a user-agent, falling back to ``*``."""
        ua = user_agent.lower()
        # Exact or prefix match on the agent token, longest token first.
        candidates = [
            (agent, rules)
            for agent, rules in self.groups.items()
            if agent != "*" and agent and agent in ua
        ]
        if candidates:
            candidates.sort(key=lambda kv: len(kv[0]), reverse=True)
            return candidates[0][1]
        return self.groups.get("*", AgentRules())

    def can_fetch(self, user_agent: str, url: str) -> bool:
        parsed = urlparse(url)
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"
        allowed, _ = self.rules_for(user_agent).decision(path)
        return allowed

    def crawl_delay_for(self, user_agent: str) -> float | None:
        return self.rules_for(user_agent).crawl_delay


class RobotsCache:
    """Fetches and caches robots.txt per host."""

    TTL_SECONDS = 3600

    def __init__(self, user_agent: str, timeout: float = 10.0):
        self.user_agent = user_agent
        self.timeout = timeout
        self._cache: dict[str, tuple[RobotsTxt, float]] = {}
        self._lock = threading.Lock()

    def get(self, scheme: str, host: str) -> RobotsTxt:
        key = f"{scheme}://{host}"
        now = time.time()
        with self._lock:
            hit = self._cache.get(key)
            if hit and now - hit[1] < self.TTL_SECONDS:
                return hit[0]

        text = ""
        try:
            resp = requests.get(
                f"{key}/robots.txt",
                timeout=self.timeout,
                headers={"User-Agent": self.user_agent},
            )
            if resp.status_code == 200:
                text = resp.text
            elif resp.status_code in (401, 403):
                # Access-controlled robots.txt: treat as disallow-all.
                text = "User-agent: *\nDisallow: /\n"
            # 404 and other errors mean no restriction.
        except Exception:  # noqa: BLE001
            text = ""

        robots = RobotsTxt(text)
        with self._lock:
            self._cache[key] = (robots, now)
        return robots
