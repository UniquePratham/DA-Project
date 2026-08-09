"""Deterministic Accessibility Auditor with axe-core integration."""

from __future__ import annotations

import json
from typing import Dict, Any, Optional
from playwright.async_api import Page

from schemas.observation import AccessibilityMeasurements


class AxeAccessibilityAuditor:
    """Executes axe-core WCAG audits on rendered pages and parses violations."""

    # Built-in lightweight axe-core runner script for headless browser execution
    AXE_RUNNER_SCRIPT = """
    async () => {
        if (!window.axe) {
            // Fetch and inject axe-core if not already present
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js';
            document.head.appendChild(script);
            await new Promise(resolve => script.onload = resolve);
        }
        const results = await window.axe.run();
        return results;
    }
    """

    @classmethod
    def parse_axe_results(cls, axe_data: Dict[str, Any], raw_evidence_id: Optional[str] = None) -> AccessibilityMeasurements:
        violations = axe_data.get("violations", [])

        critical = 0
        serious = 0
        moderate = 0
        minor = 0

        has_missing_alts = False
        has_form_label_violations = False
        has_aria_violations = False
        has_contrast_violations = False

        for v in violations:
            impact = v.get("impact", "minor")
            count = len(v.get("nodes", [])) or 1
            rule_id = v.get("id", "")

            if impact == "critical":
                critical += count
            elif impact == "serious":
                serious += count
            elif impact == "moderate":
                moderate += count
            else:
                minor += count

            if "image-alt" in rule_id or "alt" in rule_id:
                has_missing_alts = True
            if "label" in rule_id or "form" in rule_id:
                has_form_label_violations = True
            if "aria" in rule_id:
                has_aria_violations = True
            if "color-contrast" in rule_id:
                has_contrast_violations = True

        total_violations = critical + serious + moderate + minor

        # Compute normalized accessibility score (100 - weighted penalty)
        penalty = (critical * 10.0) + (serious * 5.0) + (moderate * 2.0) + (minor * 0.5)
        score = max(0.0, min(100.0, 100.0 - penalty))

        return AccessibilityMeasurements(
            axe_violations_count=total_violations,
            critical_violations=critical,
            serious_violations=serious,
            moderate_violations=moderate,
            minor_violations=minor,
            accessibility_score=round(score, 2),
            has_missing_alts=has_missing_alts,
            has_form_label_violations=has_form_label_violations,
            has_aria_violations=has_aria_violations,
            has_contrast_violations=has_contrast_violations,
            raw_evidence_id=raw_evidence_id,
        )

    @classmethod
    async def audit_page(cls, page: Page, raw_evidence_id: Optional[str] = None) -> tuple[AccessibilityMeasurements, Dict[str, Any]]:
        """Run axe-core on an active Playwright page."""
        try:
            axe_results = await page.evaluate(cls.AXE_RUNNER_SCRIPT)
            measurements = cls.parse_axe_results(axe_results, raw_evidence_id=raw_evidence_id)
            return measurements, axe_results
        except Exception as e:
            # Fallback for pages where external cdn is blocked or error occurs
            return AccessibilityMeasurements(raw_evidence_id=raw_evidence_id), {"error": str(e), "violations": []}
