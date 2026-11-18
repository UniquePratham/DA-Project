"""Deterministic measurement tools for BharatGov Access.

Each subpackage wraps one external instrument so the measurement code never
talks to a library directly:

* ``http`` — polite HTTP fetching, robots.txt compliance, TLS inspection,
  security-header analysis
* ``browser`` — headless Chromium session management and DOM inspection
* ``accessibility`` — axe-core WCAG audits
* ``performance`` — Lighthouse runs
* ``evidence`` — content-addressed storage and provenance
* ``metadata`` — language and entity detection
"""
