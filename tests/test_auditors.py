"""Unit tests for deterministic accessibility, performance, and language auditors."""

import pytest
from tools.accessibility.axe_runner import AxeAccessibilityAuditor
from tools.performance.lighthouse_runner import PerformanceAuditor
from tools.metadata.language import LanguageDetector


def test_axe_results_parsing():
    sample_axe = {
        "violations": [
            {
                "id": "image-alt",
                "impact": "critical",
                "nodes": [{"html": "<img src='a.png'>"}, {"html": "<img src='b.png'>"}],
            },
            {
                "id": "color-contrast",
                "impact": "serious",
                "nodes": [{"html": "<p>Low contrast</p>"}],
            },
            {
                "id": "label",
                "impact": "moderate",
                "nodes": [{"html": "<input type='text'>"}],
            },
        ]
    }

    res = AxeAccessibilityAuditor.parse_axe_results(sample_axe, raw_evidence_id="axe-ev-1")
    assert res.axe_violations_count == 4
    assert res.critical_violations == 2
    assert res.serious_violations == 1
    assert res.moderate_violations == 1
    assert res.has_missing_alts is True
    assert res.has_contrast_violations is True
    assert res.has_form_label_violations is True
    assert res.accessibility_score < 100.0


def test_lighthouse_report_parsing():
    sample_lh = {
        "categories": {
            "performance": {"score": 0.88}
        },
        "audits": {
            "largest-contentful-paint": {"numericValue": 1450.2},
            "cumulative-layout-shift": {"numericValue": 0.025},
            "first-contentful-paint": {"numericValue": 720.0},
            "server-response-time": {"numericValue": 180.5},
            "total-blocking-time": {"numericValue": 50.0},
            "speed-index": {"numericValue": 1100.0},
            "total-byte-weight": {"numericValue": 524288},
        }
    }

    res = PerformanceAuditor.parse_lighthouse_report(sample_lh, raw_evidence_id="lh-ev-1")
    assert res.lcp_ms == 1450.2
    assert res.cls == 0.025
    assert res.fcp_ms == 720.0
    assert res.ttfb_ms == 180.5
    assert res.lighthouse_performance_score == 88.0
    assert res.page_weight_bytes == 524288


def test_language_detection():
    hindi_html = """
    <html lang="hi">
    <head><title>भारत सरकार - स्वास्थ्य एवं परिवार कल्याण मंत्रालय</title></head>
    <body>
        <h1>मुख्य पृष्ठ</h1>
        <p>यह भारत सरकार का आधिकारिक पोर्टल है। सभी नागरिकों के लिए स्वास्थ्य सेवाएं।</p>
        <div>Select Language: <a href="?lang=en">English</a></div>
    </body>
    </html>
    """

    res = LanguageDetector.detect(hindi_html)
    assert res.detected_primary_language == "hi"
    assert "Hindi" in res.supported_indian_languages
    assert res.has_language_selector is True
    assert res.is_multilingual is True
