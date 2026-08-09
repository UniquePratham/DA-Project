"""Deterministic TLS/SSL Certificate Inspector."""

from __future__ import annotations

import socket
import ssl
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from urllib.parse import urlparse


class TLSInspector:
    """Inspects TLS/SSL certificate status, expiry, and negotiated protocols."""

    @staticmethod
    def inspect_url(url: str, timeout: float = 10.0) -> Dict[str, Any]:
        parsed = urlparse(url)
        if parsed.scheme.lower() != "https":
            return {
                "has_https": False,
                "tls_valid": False,
                "tls_version": None,
                "certificate_expiry_days": None,
                "issuer": None,
                "error": "Non-HTTPS URL",
            }

        hostname = parsed.netloc.split(":")[0]
        port = int(parsed.netloc.split(":")[1]) if ":" in parsed.netloc else 443

        ctx = ssl.create_default_context()
        try:
            with socket.create_connection((hostname, port), timeout=timeout) as sock:
                with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    tls_version = ssock.version()

                    # Extract expiry date
                    not_after_str = cert.get("notAfter", "")
                    expiry_dt = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    days_remaining = (expiry_dt - now).days

                    # Extract Issuer
                    issuer_tuples = cert.get("issuer", ())
                    issuer_dict = {t[0][0]: t[0][1] for t in issuer_tuples if t and t[0]}
                    issuer_name = issuer_dict.get("organizationName") or issuer_dict.get("commonName")

                    return {
                        "has_https": True,
                        "tls_valid": True,
                        "tls_version": tls_version,
                        "certificate_expiry_days": max(0, days_remaining),
                        "issuer": issuer_name,
                        "error": None,
                    }
        except Exception as e:
            return {
                "has_https": True,
                "tls_valid": False,
                "tls_version": None,
                "certificate_expiry_days": None,
                "issuer": None,
                "error": str(e),
            }
