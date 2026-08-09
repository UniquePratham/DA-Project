"""Deterministic HTTP Collector for BharatGov Access."""

from __future__ import annotations

import hashlib
import time
from typing import Optional, Dict, Any
from urllib.parse import urlparse

import httpx

from configs.settings import settings
from services.safety.governor import SafetyGovernor
from tools.http.tls_inspector import TLSInspector
from tools.http.headers import SecurityHeadersAnalyzer
from schemas.observation import ReliabilityMeasurements, SecurityHygieneMeasurements


class HTTPCollectionResult:
    def __init__(
        self,
        url: str,
        final_url: str,
        status_code: int,
        latency_ms: float,
        headers: Dict[str, str],
        content: bytes,
        sha256_hash: str,
        reliability: ReliabilityMeasurements,
        security_hygiene: SecurityHygieneMeasurements,
        error: Optional[str] = None,
    ):
        self.url = url
        self.final_url = final_url
        self.status_code = status_code
        self.latency_ms = latency_ms
        self.headers = headers
        self.content = content
        self.sha256_hash = sha256_hash
        self.reliability = reliability
        self.security_hygiene = security_hygiene
        self.error = error


class DeterministicHTTPCollector:
    """Collects HTTP/TLS evidence while strictly obeying the Safety Governor."""

    def __init__(
        self,
        governor: Optional[SafetyGovernor] = None,
        timeout_seconds: Optional[float] = None,
    ):
        self.governor = governor or SafetyGovernor()
        self.timeout = timeout_seconds or float(settings.crawl_timeout_seconds)

    async def fetch(self, url: str) -> HTTPCollectionResult:
        t0 = time.perf_counter()
        redirect_chain = []

        # 1. Enforce Safety Governor pre-request guard
        await self.governor.pre_request_guard("GET", url)

        status_code = 0
        byte_size = 0
        content = b""
        final_url = url
        headers: Dict[str, str] = {}
        error_msg: Optional[str] = None

        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": settings.user_agent},
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                resp = await client.get(url)
                status_code = resp.status_code
                content = resp.content
                byte_size = len(content)
                final_url = str(resp.url)
                headers = dict(resp.headers)

                for r in resp.history:
                    redirect_chain.append(str(r.url))

        except httpx.TimeoutException:
            status_code = 504
            error_msg = "Request timed out"
        except httpx.ConnectError:
            status_code = 502
            error_msg = "Connection failed"
        except Exception as e:
            status_code = 500
            error_msg = str(e)
        finally:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            # 2. Record post-request metrics in Safety Governor
            self.governor.post_request_record(url, status_code, byte_size=byte_size)

        # 3. Compute cryptographic SHA256 integrity hash
        sha256_hash = hashlib.sha256(content).hexdigest()

        # 4. Perform TLS Inspection if HTTPS
        tls_info = TLSInspector.inspect_url(final_url)

        # 5. Build Reliability Measurements
        is_reachable = (200 <= status_code < 400)
        reliability = ReliabilityMeasurements(
            http_status_code=status_code if status_code > 0 else 500,
            response_latency_ms=latency_ms,
            is_reachable=is_reachable,
            tls_valid=tls_info.get("tls_valid", False),
            tls_version=tls_info.get("tls_version"),
            certificate_expiry_days=tls_info.get("certificate_expiry_days"),
            redirect_hops=len(redirect_chain),
            redirect_chain=redirect_chain,
        )

        # 6. Build Security Hygiene Measurements
        security_hygiene = SecurityHeadersAnalyzer.analyze_headers(headers)
        security_hygiene.has_https = (urlparse(final_url).scheme.lower() == "https")

        return HTTPCollectionResult(
            url=url,
            final_url=final_url,
            status_code=status_code,
            latency_ms=latency_ms,
            headers=headers,
            content=content,
            sha256_hash=sha256_hash,
            reliability=reliability,
            security_hygiene=security_hygiene,
            error=error_msg,
        )
