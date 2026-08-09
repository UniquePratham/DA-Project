# BharatGov Access — Data Dictionary

This document details the exact schema, types, descriptions, and provenance rules for all published dataset releases (`.parquet` and `.jsonl`).

---

## 1. Identifiers and Metadata

| Column Name | Type | Description | Example |
|---|---|---|---|
| `observation_id` | String (UUID) | Unique observation identifier | `obs-a1b2c3d4e5f6` |
| `crawl_id` | String | Unique crawl batch session ID | `crawl-master-20260809-120000` |
| `dataset_version` | String | Semantic dataset release version | `0.1.0` |
| `domain_id` | String | Registry domain identifier | `dom-india-gov` |
| `source_url` | String | Requested target URL | `https://india.gov.in` |
| `canonical_url` | String | Final URL after redirect resolution | `https://india.gov.in/` |
| `observed_at` | Timestamp (ISO-8601 UTC) | Timestamp of observation | `2026-08-09T16:45:00Z` |
| `page_role` | String (Enum) | Functional role of inspected page | `homepage`, `citizen_form`, `about` |
| `browser_rendered` | Boolean | True if page required Playwright Chromium rendering | `true` |

---

## 2. Reliability Measurements (Deterministic Level 2)

| Column Name | Type | Description | Range |
|---|---|---|---|
| `http_status_code` | Integer | HTTP response status code | $100 - 599$ |
| `response_latency_ms` | Float | Round-trip response time in ms | $\ge 0.0$ |
| `is_reachable` | Boolean | True if status is $2\text{xx}$ or $3\text{xx}$ | `true` / `false` |
| `tls_valid` | Boolean | True if TLS certificate is valid and unexpired | `true` / `false` |
| `tls_version` | String | Negotiated TLS version | `TLSv1.3`, `TLSv1.2` |
| `certificate_expiry_days`| Integer | Days remaining before SSL certificate expiry | $\ge 0$ |

---

## 3. Accessibility Measurements (axe-core WCAG Level 2)

| Column Name | Type | Description | Range |
|---|---|---|---|
| `axe_violations_count` | Integer | Total automated axe-core violations | $\ge 0$ |
| `critical_violations` | Integer | Critical severity WCAG violations | $\ge 0$ |
| `serious_violations` | Integer | Serious severity WCAG violations | $\ge 0$ |
| `moderate_violations` | Integer | Moderate severity WCAG violations | $\ge 0$ |
| `minor_violations` | Integer | Minor severity WCAG violations | $\ge 0$ |
| `accessibility_score` | Float | Normalized accessibility score ($0 - 100$) | $0.0 - 100.0$ |
| `has_missing_alts` | Boolean | Missing image `alt` attributes detected | `true` / `false` |

---

## 4. Web Performance Measurements (Core Web Vitals Level 2)

| Column Name | Type | Description | Unit |
|---|---|---|---|
| `lcp_ms` | Float | Largest Contentful Paint | Milliseconds |
| `cls` | Float | Cumulative Layout Shift | Score ($\ge 0$) |
| `fcp_ms` | Float | First Contentful Paint | Milliseconds |
| `ttfb_ms` | Float | Time to First Byte | Milliseconds |
| `page_weight_bytes` | Integer | Total page transfer size | Bytes |
| `lighthouse_performance_score` | Float | Normalized performance score | $0.0 - 100.0$ |

---

## 5. Language & Structural Measurements

| Column Name | Type | Description |
|---|---|---|
| `detected_primary_language` | String | Primary ISO 639-1 code (`hi`, `en`, `bn`, `ta`, etc.) |
| `is_multilingual` | Boolean | True if regional script or language switcher found |
| `dom_node_count` | Integer | Total DOM nodes in page tree |
| `links_count` | Integer | Total hyperlinks on page |
| `forms_count` | Integer | Total interactive forms on page |

---

## 6. Security & Hygiene Measurements

| Column Name | Type | Description |
|---|---|---|
| `has_https` | Boolean | True if HTTPS scheme is enforced |
| `has_hsts` | Boolean | `Strict-Transport-Security` header present |
| `has_csp` | Boolean | `Content-Security-Policy` header present |
| `security_headers_score` | Float | Weighted security headers score ($0 - 100$) |

---

## 7. Derived Classifications (Agentic Level 3)

| Column Name | Type | Description |
|---|---|---|
| `website_category` | String | Classification category (`national_portal`, `district_administration`, etc.) |
| `architecture_type` | String | Inferred architecture (`angular_spa`, `wordpress`, `static_html`, etc.) |
| `is_validated` | Boolean | True if observation passed all data quality validation rules |
