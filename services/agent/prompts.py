"""Structured prompt templates for the Agentic Controller."""

from __future__ import annotations

ARCHITECTURE_PROFILING_PROMPT = """
You are an expert web architecture classifier for India's public web infrastructure.
Analyze the following observed evidence from a government website and classify its architecture.

Observed Evidence:
- URL: {url}
- Title: {title}
- Detected Framework Markers: {frameworks}
- Structural Metrics: DOM Nodes: {node_count}, Max Depth: {max_depth}, Forms: {forms_count}, Scripts: {scripts_count}
- HTML Snippet:
```html
{html_snippet}
```

Return ONLY a JSON object with this exact schema:
{{
  "architecture_type": "static_html" | "wordpress" | "drupal" | "angular_spa" | "react_spa" | "nextjs" | "legacy_dynamic" | "custom_portal",
  "browser_required": true | false,
  "confidence": <float between 0.0 and 1.0>,
  "reasoning": "<brief explanation grounded in the evidence markers>"
}}
"""

PAGE_SELECTION_PROMPT = """
You are an adaptive web crawler planner for Indian government portals.
Given the extracted links on the homepage, select up to {max_pages} representative pages across key roles:
(About, Public Service / Citizen Form, Contact, Document / Circulars Directory, Language Switcher).

Homepage URL: {url}
Candidate Extracted Links:
{links_list}

Return ONLY a JSON object with this exact schema:
{{
  "selected_pages": [
    {{
      "url": "<absolute url>",
      "page_role": "about" | "public_service" | "citizen_form" | "contact" | "document_repository" | "language_switcher" | "sitemap_directory" | "other",
      "priority": <integer 1 to 5>
    }}
  ]
}}
"""

CLASSIFICATION_PROMPT = """
You are a government digital service classifier.
Classify the government entity category and produce an evidence-backed description.

Entity Details:
- Domain: {domain}
- Title: {title}
- Level: {level}
- Text Summary: {text_summary}

Return ONLY a JSON object with this exact schema:
{{
  "website_category": "national_portal" | "ministry" | "state_portal" | "district_administration" | "health_service" | "education" | "taxation_revenue" | "transport" | "judiciary" | "citizen_engagement" | "general_portal",
  "confidence": <float between 0.0 and 1.0>,
  "service_type": "information" | "transactional_portal" | "document_repository" | "directory",
  "explanation": "<1-2 sentence evidence-backed explanation>"
}}
"""
