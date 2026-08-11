# BharatGov Access — Data Dictionary

This document details the exact schema, types, descriptions, and feature definitions for all published dataset releases (`.parquet` and `.csv`).

> **Dataset Granularity**: **1 Row per Unique Government Website (Domain)**.
> Multi-page metrics (Homepage, About, Contact, Services, Circulars) are represented as structured feature columns.

---

## 1. Identity & Domain Hierarchy Structure

| Column Name | Type | Description | Example |
|---|---|---|---|
| `domain_name` | String | Full canonical government hostname | `police.up.gov.in`, `varanasi.nic.in` |
| `subdomain` | String | Extracted sub-domain prefix (`root` if top-level) | `police`, `varanasi`, `rodelhi`, `root` |
| `root_domain` | String | Parent root domain for hierarchical clustering | `up.gov.in`, `nic.in`, `kvs.gov.in`, `aiims.edu` |
| `tld_type` | String | Top-level domain type | `.gov.in`, `.nic.in`, `.ac.in`, `.edu.in`, `.res.in` |
| `domain_depth`| Integer | Hierarchy depth ($0 = \text{apex}, 1 = \text{subdomain}, 2 = \text{nested}$) | `0`, `1`, `2` |
| `base_url` | String | Root URL for the domain | `https://police.up.gov.in` |
| `entity_name` | String | Official administrative entity name | `Police Department (UP)` |
| `government_level` | String | Governance tier (`central`, `state_ut`, `district`, `autonomous_body`, `local_body`, `psu`) | `state_ut` |
| `state_or_ut` | String | State or Union Territory | `Uttar Pradesh` |
| `district` | String | District name (if applicable) | `Varanasi` |
| `website_category` | String | AI-classified administrative function | `law_enforcement`, `district_administration`, `ministry` |
| `architecture_type` | String | Web framework / CMS architecture | `wordpress`, `angular_spa`, `drupal`, `static_html` |

---

## 2. Overall Website Scores & Reliability

| Column Name | Type | Description | Range / Unit |
|---|---|---|---|
| `overall_accessibility_score` | Float | Mean accessibility score across all audited pages | $0.0 - 100.0$ |
| `overall_performance_score` | Float | Mean Lighthouse performance score across all audited pages | $0.0 - 100.0$ |
| `total_pages_audited` | Integer | Number of distinct functional pages audited for this website | $1 - 5$ |
| `is_reachable` | Boolean | True if domain returned successful HTTP response | `true` / `false` |
| `http_status_code` | Integer | Root HTTP status code | $200, 403, 502, 504$ |
| `response_latency_ms` | Float | Root response latency | Milliseconds ($\ge 0.0$) |
| `primary_language` | String | ISO 639-1 language code | `hi`, `en`, `bn`, `ta`, `te` |
| `is_multilingual` | Boolean | True if regional Indian script or language toggle detected | `true` / `false` |

---

## 3. Security & Public Hygiene (Website Level)

| Column Name | Type | Description | Values / Range |
|---|---|---|---|
| `has_https` | Boolean | True if HTTPS is supported | `true` / `false` |
| `tls_valid` | Boolean | True if TLS certificate is valid and unexpired | `true` / `false` |
| `tls_version` | String | Negotiated TLS version | `TLSv1.3`, `TLSv1.2` |
| `certificate_expiry_days`| Integer | Days remaining before SSL certificate expiry | Integer ($\ge 0$) |
| `has_hsts` | Boolean | Strict-Transport-Security header present | `true` / `false` |
| `has_csp` | Boolean | Content-Security-Policy header present | `true` / `false` |
| `security_headers_score`| Float | Composite security headers score ($0 - 100$) | $0.0 - 100.0$ |

---

## 4. Aggregate Complexity & WCAG Violations

| Column Name | Type | Description | Unit |
|---|---|---|---|
| `total_wcag_violations` | Integer | Sum of automated axe-core violations across all audited pages | Count ($\ge 0$) |
| `total_critical_violations`| Integer | Sum of Critical severity WCAG violations | Count ($\ge 0$) |
| `total_serious_violations` | Integer | Sum of Serious severity WCAG violations | Count ($\ge 0$) |
| `has_missing_alts` | Boolean | Missing image `alt` attributes found on any page | `true` / `false` |
| `total_dom_nodes` | Integer | Total DOM elements counted across audited pages | Count |
| `total_forms_count` | Integer | Total interactive HTML forms counted across audited pages | Count |
| `total_pdf_circulars` | Integer | Total PDF download links counted across audited pages | Count |

---

## 5. Page-Specific Feature Columns

### Homepage
| Column Name | Type | Description |
|---|---|---|
| `homepage_url` | String | Canonical URL of the homepage |
| `homepage_accessibility_score` | Float | WCAG compliance score of homepage ($0 - 100$) |
| `homepage_lcp_ms` | Float | Largest Contentful Paint (LCP) of homepage |
| `homepage_dom_nodes` | Integer | Total DOM nodes on homepage |

### About Us Page
| Column Name | Type | Description |
|---|---|---|
| `has_about_page` | Boolean | True if About Us / Leadership page was discovered |
| `about_page_url` | String | Discovered About Us page URL |
| `about_accessibility_score` | Float | WCAG compliance score of About Us page |

### Contact Directory Page
| Column Name | Type | Description |
|---|---|---|
| `has_contact_page` | Boolean | True if Contact / Directory page was discovered |
| `contact_page_url` | String | Discovered Contact page URL |
| `contact_accessibility_score` | Float | WCAG compliance score of Contact page |

### Citizen Services & Forms Page
| Column Name | Type | Description |
|---|---|---|
| `has_services_page` | Boolean | True if Citizen Services / Online Schemes page was discovered |
| `services_page_url` | String | Discovered Citizen Services page URL |
| `services_accessibility_score` | Float | WCAG compliance score of Citizen Services page |
| `services_forms_count` | Integer | Number of interactive application forms on services page |

### Gazette & Circulars Page
| Column Name | Type | Description |
|---|---|---|
| `has_circulars_page` | Boolean | True if Gazette / Orders / Circulars repository page was discovered |
| `circulars_page_url` | String | Discovered Circulars page URL |
| `circulars_accessibility_score` | Float | WCAG compliance score of Circulars page |
| `circulars_pdf_count` | Integer | Number of PDF documents on circulars page |

---

## 6. Provenance & Dataset Metadata

| Column Name | Type | Description |
|---|---|---|
| `domain_id` | String | Unique registry domain identifier (`dom-xxxx`) |
| `crawl_id` | String | Crawl batch session ID |
| `dataset_version` | String | Semantic release version (e.g., `2.0.0`) |
| `observed_at` | Timestamp | Timestamp of crawl execution |
| `is_validated` | Boolean | True if passed 100% schema & provenance validator checks |
