"""HTTP collection and security analysis tools.

The package exposes the full collector for in-repo use, but the measurement
worker only needs :mod:`tools.http.polite` and :mod:`tools.http.robots`. Those
are imported lazily so the worker can run on a minimal instance where the
heavier collector dependencies are not installed.
"""

__all__ = [
    "DeterministicHTTPCollector",
    "HTTPCollectionResult",
    "TLSInspector",
    "SecurityHeadersAnalyzer",
]


def __getattr__(name: str):
    """Import the heavy collectors only when they are actually used."""
    if name in ("DeterministicHTTPCollector", "HTTPCollectionResult"):
        from tools.http.collector import (
            DeterministicHTTPCollector,
            HTTPCollectionResult,
        )

        return {
            "DeterministicHTTPCollector": DeterministicHTTPCollector,
            "HTTPCollectionResult": HTTPCollectionResult,
        }[name]
    if name == "TLSInspector":
        from tools.http.tls_inspector import TLSInspector

        return TLSInspector
    if name == "SecurityHeadersAnalyzer":
        from tools.http.headers import SecurityHeadersAnalyzer

        return SecurityHeadersAnalyzer
    raise AttributeError(name)
