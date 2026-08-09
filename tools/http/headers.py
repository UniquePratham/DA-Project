"""Security response headers and web hygiene analyzer."""

from __future__ import annotations

from typing import Dict, Any
from schemas.observation import SecurityHygieneMeasurements


class SecurityHeadersAnalyzer:
    """Evaluates publicly observable HTTP security response headers (Section 9.7)."""

    @staticmethod
    def analyze_headers(headers: Dict[str, str]) -> SecurityHygieneMeasurements:
        # Convert header keys to lowercase
        h = {k.lower(): v for k, v in headers.items()}

        has_hsts = "strict-transport-security" in h
        has_csp = "content-security-policy" in h
        has_x_frame_options = "x-frame-options" in h
        has_x_content_type_options = "x-content-type-options" in h and "nosniff" in h["x-content-type-options"].lower()
        has_referrer_policy = "referrer-policy" in h

        # Calculate weighted security headers score (0 to 100)
        score = 0.0
        if has_hsts:
            score += 25.0
        if has_csp:
            score += 30.0
        if has_x_frame_options:
            score += 20.0
        if has_x_content_type_options:
            score += 15.0
        if has_referrer_policy:
            score += 10.0

        return SecurityHygieneMeasurements(
            has_https=True,
            has_hsts=has_hsts,
            has_csp=has_csp,
            has_x_frame_options=has_x_frame_options,
            has_x_content_type_options=has_x_content_type_options,
            has_referrer_policy=has_referrer_policy,
            has_mixed_content=False,
            security_headers_score=score,
        )
