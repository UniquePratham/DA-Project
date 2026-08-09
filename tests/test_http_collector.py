"""Unit tests for the Deterministic HTTP Collector and Security Headers Analyzer."""

import asyncio
import pytest

from tools.http.headers import SecurityHeadersAnalyzer
from tools.http.collector import DeterministicHTTPCollector
from services.safety.governor import SafetyGovernor


def test_security_headers_analyzer():
    headers = {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
    }
    result = SecurityHeadersAnalyzer.analyze_headers(headers)
    assert result.has_hsts is True
    assert result.has_csp is True
    assert result.has_x_frame_options is True
    assert result.has_x_content_type_options is True
    assert result.has_referrer_policy is True
    assert result.security_headers_score == 100.0


def test_security_headers_analyzer_partial():
    headers = {
        "X-Frame-Options": "SAMEORIGIN",
    }
    result = SecurityHeadersAnalyzer.analyze_headers(headers)
    assert result.has_hsts is False
    assert result.has_csp is False
    assert result.has_x_frame_options is True
    assert result.security_headers_score == 20.0


def test_http_collector_safety_integration():
    async def run():
        governor = SafetyGovernor()
        collector = DeterministicHTTPCollector(governor=governor, timeout_seconds=5.0)

        # Prohibited URL should be blocked immediately without network call
        with pytest.raises(Exception) as exc:
            await collector.fetch("https://example.gov.in/wp-admin/login.php")
        assert "Safety Governor" in str(exc.value)

    asyncio.run(run())
