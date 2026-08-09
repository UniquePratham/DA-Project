# BharatGov Access
## Agentic, Longitudinal Observatory of India's Government Web Infrastructure

**Project Type:** Large-scale novel dataset + data analytics + working proof-of-concept product  
**Primary Track:** Track 1 — Contribute a large-scale novel dataset  
**Secondary Outcome:** A working data-driven product powered by the dataset  
**Target Platform:** DataHub KGP  
**Deployment:** Dockerized, self-hosted infrastructure  
**Local AI:** Ollama + open-weight model  
**Project Status:** Master technical specification

---

# 1. Executive Summary

**BharatGov Access** is a large-scale, longitudinal, evidence-first dataset and analytics platform designed to characterize the publicly observable digital infrastructure of Indian government websites.

The project will discover, verify, monitor, analyze, and document Indian government web portals across central government, states and union territories, districts, departments, public agencies, local-government bodies, public services, and other verifiable government web properties within the defined project scope.

The dataset will measure multiple dimensions rather than treating accessibility as a single problem:

- Digital accessibility
- Web performance
- Mobile readiness
- Reliability
- Language and multilingual support
- Web structure
- Publicly observable security/web-hygiene signals
- Government/service classification
- Page and service architecture
- Longitudinal changes

The collection system will use a **hybrid deterministic + agentic architecture**.

A lightweight open-weight model running locally through Ollama will act as an adaptive controller. It will inspect a website, infer its architecture, select appropriate inspection strategies, choose representative pages, request additional evidence when necessary, and interpret validated measurements.

Deterministic tools will perform the actual measurements.

A safety governor will control all network activity independently of the model.

The resulting evidence will pass validation before becoming part of the research dataset.

The project will then transform the collected data into:

1. A versioned large-scale dataset.
2. A comprehensive analytical layer.
3. An interactive visual observatory.
4. A working **BharatGov Inspector** proof-of-concept product.

The same underlying data pipeline will power all four components.

---

# 2. Core Research Question

The central question is:

> **What is the measurable state of India's public-facing government web infrastructure, how does it differ across government levels, states, departments, services, and website architectures, and how does it evolve over time?**

The project will answer this through empirical data rather than assumptions.

---

# 3. Project Objectives

## 3.1 Primary objectives

### Objective 1 — Comprehensive discovery

Build a continuously maintained registry of Indian government websites.

The project aims to identify **every verifiable government web property within the defined scope**, rather than selecting a convenient sample.

### Objective 2 — Adaptive collection

Build an agentic collection system capable of handling heterogeneous government websites.

The system should adapt to:

- static HTML;
- WordPress;
- Drupal;
- Angular;
- React;
- Next.js;
- JavaScript-heavy portals;
- legacy websites;
- multilingual websites;
- document-heavy portals;
- service directories;
- citizen-facing service portals;
- unusual navigation structures.

### Objective 3 — Evidence-first measurement

Collect deterministic measurements with complete provenance.

### Objective 4 — Large-scale dataset

Create a versioned, documented dataset suitable for integration with DataHub KGP and future research.

### Objective 5 — Data analytics

Identify meaningful:

- trends;
- patterns;
- correlations;
- differences;
- clusters;
- outliers;
- longitudinal changes;
- state-level and department-level differences.

### Objective 6 — Interactive observatory

Create a visually strong dashboard allowing users to explore India's government-web infrastructure.

### Objective 7 — Working product

Create **BharatGov Inspector**, a functioning proof-of-concept that accepts a government URL and produces an evidence-backed quality report and benchmark comparison.

---

# 4. What Makes BharatGov Access Distinct

Existing accessibility-testing tools and studies mean the project must not be positioned merely as:

> "A dataset of accessibility violations in Indian government websites."

That would be too narrow.

BharatGov Access combines:

```text
Comprehensive government-web discovery
+
Adaptive agentic collection
+
Accessibility
+
Performance
+
Reliability
+
Mobile readiness
+
Language analysis
+
Web structure
+
Public web-hygiene signals
+
Longitudinal observations
+
Evidence/provenance
+
Large-scale analytics
+
Interactive visualization
+
Working benchmark product
```

The research contribution is the **integrated, longitudinal, multi-dimensional, evidence-first dataset and observatory**.

The project will explicitly review prior work such as WAccess, SugamyaWeb, GIGW, and other Indian/international datasets before making final novelty claims.

---

# 5. Prior-Art and Reference Framework

The project will use authoritative and academic references to define measurement methodology.

Important references include:

- Government of India's Guidelines for Indian Government Websites and Apps (GIGW).
- SugamyaWeb and related government accessibility-testing resources.
- Academic work on accessibility of Indian government websites, including WAccess.
- WCAG and related accessibility standards.
- Core Web Vitals and standard web-performance measurements.
- Existing government open-data and website datasets internationally.

Novelty claims will only be made after a documented prior-art review.

---

# 6. Scope of Government Websites

The project should aim for maximum coverage.

The discovery hierarchy is:

```text
India
│
├── Central Government
│   ├── Ministries
│   ├── Departments
│   ├── Agencies
│   └── Public organizations
│
├── States and Union Territories
│   ├── Government departments
│   ├── Agencies
│   └── Public service portals
│
├── District Administration
│   └── District portals
│
├── Local Government
│   ├── Municipal bodies
│   ├── Urban local bodies
│   └── Other government bodies
│
└── Other verifiable public government portals
```

The exact inclusion policy will be documented and versioned.

---

# 7. "All Government Websites" Requirement

Comprehensive coverage is a core project requirement.

However, the project must distinguish between:

- all known candidate domains;
- all verified government domains;
- all reachable domains;
- all successfully crawled domains.

The system must never silently drop difficult sites.

Every candidate should receive a status such as:

```text
VERIFIED
ACTIVE
TEMPORARILY_UNAVAILABLE
PERMANENTLY_UNAVAILABLE
REDIRECTED
ROBOTS_RESTRICTED
BLOCKED
TLS_ERROR
TIMEOUT
REQUIRES_AUTH
UNRESOLVED
RETIRED
```

Therefore:

> **Coverage includes unavailable and restricted sites in the registry rather than pretending they do not exist.**

This allows the project to honestly report coverage.

---

# 8. Coverage Audit

Every dataset release must contain a coverage report.

Example:

```text
Candidate domains             12,480
Verified government domains   10,921
Successfully observed           9,874
Temporarily unavailable           612
Restricted/blocked                181
Unresolved                        254
```

The numbers above are illustrative, not current project results.

The actual values must be generated from the collection system.

---

# 9. Data Dimensions

BharatGov Access will collect several measurement families.

## 9.1 Accessibility

Possible measurements include:

- WCAG-related automated violations;
- severity;
- missing alternative text;
- form labels;
- contrast;
- ARIA issues;
- landmark structure;
- heading hierarchy;
- keyboard-related automated checks;
- accessible names;
- document accessibility signals;
- accessibility score where a deterministic tool provides one.

Raw tool output must be retained.

---

## 9.2 Performance

Possible measurements:

- LCP;
- CLS;
- INP where available;
- FCP;
- TTFB;
- Speed Index;
- total page weight;
- request count;
- JavaScript size;
- CSS size;
- image weight;
- resource timing.

---

## 9.3 Mobile Readiness

Possible measurements:

- viewport configuration;
- mobile rendering;
- mobile performance;
- responsive layout;
- touch-target observations;
- mobile accessibility observations;
- horizontal overflow indicators.

---

## 9.4 Reliability

Possible measurements:

- HTTP status;
- redirects;
- DNS failures;
- TLS failures;
- timeout;
- broken links;
- broken assets;
- response latency;
- repeated availability observations.

---

## 9.5 Language and Multilingual Support

Detect:

- primary language;
- secondary languages;
- language selector;
- Indian regional languages;
- multilingual page availability;
- language-specific URLs;
- translation coverage where measurable.

Do not infer language solely from domain names.

---

## 9.6 Web Structure

Possible measurements:

- DOM node count;
- page depth;
- links;
- forms;
- tables;
- images;
- videos;
- PDFs;
- scripts;
- stylesheets;
- external dependencies;
- framework;
- rendering architecture.

---

## 9.7 Public Web-Hygiene Signals

Measure only publicly observable configuration signals.

Possible examples:

- HTTPS;
- TLS information;
- HSTS;
- CSP;
- X-Frame-Options or equivalent;
- security-related response headers;
- mixed-content observations.

This is **not a penetration test**.

---

## 9.8 Government/Service Classification

Derived classifications may include:

- ministry;
- department;
- district administration;
- municipality;
- education;
- health;
- judiciary;
- transport;
- taxation;
- agriculture;
- citizen services;
- information portal;
- document repository;
- service portal.

Every AI-derived classification requires evidence and confidence.

---

# 10. Data Architecture

The dataset will follow an evidence hierarchy.

```text
Level 1
RAW EVIDENCE

HTML
DOM
Screenshots
Headers
Tool outputs
Metadata
Network observations
       |
       v
Level 2
DETERMINISTIC MEASUREMENTS

LCP
CLS
violations
links
forms
language
page weight
etc.
       |
       v
Level 3
DERIVED CLASSIFICATIONS

website category
architecture
service type
page role
benchmark groups
       |
       v
Level 4
ANALYTICS

trends
correlations
clusters
rankings
outliers
statistical findings
```

Raw observations must never be overwritten by AI interpretation.

---

# 11. Hybrid Agentic Architecture

The system consists of five major layers.

```text
Government Domain Registry
          |
          v
Discovery and Verification
          |
          v
Safety Governor
          |
          v
Agentic Controller
          |
    +-----+-----+
    |     |     |
    v     v     v
 HTTP   Browser  Data Tools
 Tools   Tools   Parsers
    |     |     |
    +-----+-----+
          |
          v
Deterministic Auditors
          |
          v
Evidence Store
          |
          v
Validation
          |
          v
Data Warehouse
          |
    +-----+-----+
    |     |     |
    v     v     v
Analytics Dashboard DataHub
          |
          v
BharatGov Inspector
```

---

# 12. Agentic Controller

The agent uses a locally hosted open-weight model through Ollama.

The model is responsible for adaptive decisions.

It may:

- identify website architecture;
- choose HTTP vs browser inspection;
- select relevant page types;
- decide whether additional evidence is required;
- detect unusual structures;
- classify website/service types;
- reuse historical crawl profiles;
- identify meaningful changes;
- generate evidence-backed explanations.

The model does **not** directly control network traffic.

---

# 13. Deterministic Infrastructure

The following components remain deterministic:

- DNS;
- HTTP;
- TLS;
- robots.txt;
- rate limiting;
- concurrency;
- retries;
- timeouts;
- URL normalization;
- duplicate detection;
- HTML parsing;
- browser rendering;
- screenshots;
- axe-core;
- Lighthouse;
- link validation;
- language detection;
- hashing;
- timestamps;
- database writes;
- schema validation;
- statistical calculations.

This ensures reproducibility.

---

# 14. Safety Governor

The safety governor is independent of the LLM.

The flow is:

```text
Agent requests action
        |
        v
Safety Governor
        |
   +----+----+
   |         |
allowed    rejected/delayed
   |
   v
Scheduler
   |
   v
Network request
```

The model cannot override:

- request-rate limits;
- concurrency;
- robots restrictions;
- domain budgets;
- maximum pages;
- maximum bytes;
- maximum runtime;
- retry limits;
- cooldowns.

---

# 15. Responsible Crawling

The system must be designed to avoid accidental denial-of-service behavior.

Initial conservative defaults:

```text
Per-domain concurrency: 1
Initial request rate: <= 1 request/sec/domain
Retries: 2
Timeout: 20–30 seconds
Exponential backoff: enabled
Cooldown after repeated failure: enabled
```

These are starting values.

The scheduler may reduce the rate automatically.

### 429

Trigger cooldown and exponential backoff.

### 5xx

Use backoff and retry within limits.

### Repeated timeout

Reduce rate or pause the domain.

### Robots restriction

Do not crawl restricted paths.

### Server instability

Pause the domain.

The project does not perform stress testing.

---

# 16. Explicitly Prohibited Actions

BharatGov Access must not:

- bypass authentication;
- bypass access controls;
- exploit vulnerabilities;
- brute force;
- flood servers;
- perform stress tests;
- enumerate private endpoints aggressively;
- submit citizen-service forms;
- trigger payments;
- trigger applications;
- send OTPs;
- create accounts;
- delete records;
- upload documents;
- perform penetration testing.

Forms may be **inspected**, but not automatically submitted.

---

# 17. Agent State Machine

```text
DISCOVER
   |
VERIFY
   |
PROFILE
   |
PLAN
   |
OBSERVE
   |
   +----> MORE EVIDENCE NEEDED
   |               |
   |               v
   |            OBSERVE
   |
MEASURE
   |
VALIDATE
   |
   +----> INVALID
   |         |
   |         v
   |       RETRY
   |
CLASSIFY
   |
FINALIZE
   |
STORE
```

Every agent run has:

- maximum steps;
- maximum runtime;
- maximum browser sessions;
- maximum pages;
- maximum extra pages.

The agent cannot loop indefinitely.

---

# 18. Agent Tools

The agent receives a restricted tool registry.

Possible tools:

```text
inspect_domain()
fetch_url()
get_robots()
get_sitemap()
detect_framework()
render_page()
inspect_dom()
extract_links()
extract_forms()
extract_documents()
take_screenshot()
run_accessibility_audit()
run_lighthouse()
check_headers()
detect_language()
calculate_page_metrics()
request_additional_evidence()
finish_site()
```

Tool outputs must be structured.

Example:

```json
{
  "tool": "detect_framework",
  "status": "success",
  "framework": "angular",
  "confidence": 0.96,
  "evidence": [
    "Angular runtime markers",
    "ng-version attribute"
  ]
}
```

---

# 19. Recommended Open-Weight Model

## Primary: Qwen3 4B

Initial model:

```text
qwen3:4b
```

The Ollama Q4_K_M distribution is approximately 2.5 GB.

Use it for:

- architecture classification;
- tool selection;
- adaptive planning;
- structured JSON generation;
- page-role classification;
- evidence-grounded interpretation.

The LLM should not perform raw web measurements.

---

# 20. Secondary Model Benchmark

Benchmark:

```text
qwen3:8b
```

The larger model should only become the default if experiments demonstrate meaningful gains.

Measure:

- architecture accuracy;
- page selection;
- tool selection;
- invalid actions;
- latency;
- RAM;
- CPU;
- crawl completion;
- resource efficiency.

---

# 21. Optional Vision Model

Evaluate:

```text
gemma3:4b
```

for screenshot-based tasks such as:

- visual page classification;
- layout archetype detection;
- visual anomaly assistance;
- navigation pattern classification.

Vision analysis is optional and should not be allowed to invent accessibility measurements.

---

# 22. Model Abstraction

The agent must not be hardcoded to one model.

```text
LLMProvider
   |
   +-- Qwen3 4B
   +-- Qwen3 8B
   +-- Gemma 3 4B
   +-- future model
```

Configuration:

```text
AGENT_MODEL=qwen3:4b
```

Changing the model should not require rewriting the crawler.

---

# 23. Evidence-First Rule

Never allow:

```text
LLM
 |
unsupported claim
 |
dataset
```

Use:

```text
Website
 |
Observed evidence
 |
Deterministic measurement
 |
Validation
 |
AI interpretation
 |
Structured record
```

Example:

```json
{
  "axe_violations": 74,
  "serious_violations": 18,
  "critical_violations": 3,
  "evidence_ids": [
    "axe-run-001"
  ]
}
```

For AI classification:

```json
{
  "website_category": "public_health_service",
  "confidence": 0.91,
  "evidence_ids": [
    "page-001",
    "service-directory-001"
  ],
  "model": "qwen3:4b"
}
```

---

# 24. Adaptive Website Profiling

For every domain, create a crawl profile.

Example:

```json
{
  "domain": "example.gov.in",
  "architecture": {
    "type": "angular_spa",
    "confidence": 0.94
  },
  "strategy": {
    "browser_required": true,
    "sitemap_first": true,
    "representative_pages": [
      "homepage",
      "service",
      "form",
      "contact"
    ]
  }
}
```

Store the profile.

During the next crawl:

```text
Previous profile
      |
      v
Lightweight verification
      |
   +--+--+
   |     |
same   changed
   |     |
reuse   re-profile
```

---

# 25. Representative Page Selection

The system should avoid blindly crawling every page.

Prioritize:

1. Homepage
2. About
3. Contact
4. Public service page
5. Search
6. Citizen-facing form
7. Important information page
8. Document/PDF page
9. Language-selection page
10. Sitemap/category page

The agent may select additional pages where evidence indicates that they are important.

Every selection must be recorded.

---

# 26. Domain Crawl Budget

Each domain receives:

```text
max_concurrent_requests
requests_per_second
requests_per_minute
max_pages_per_cycle
max_bytes_per_cycle
max_runtime
max_retries
cooldown_seconds
```

Initial agent budget:

```text
max_agent_steps: 20
max_browser_sessions: 3
max_selected_pages: 10
max_extra_pages: 5
max_agent_runtime: 5 minutes
```

The values must be configurable.

---

# 27. Local AI Infrastructure

Use:

```text
Ollama
Qwen3 4B
```

The initial command is:

```bash
ollama pull qwen3:4b
```

The model should run entirely on our server.

No external paid LLM API is required.

---

# 28. Vultr Infrastructure Requirements

## Minimum serious CPU-first setup

```text
CPU:    8 vCPU
RAM:    32 GB
Disk:   150 GB SSD/NVMe
GPU:    not required
OS:     Ubuntu 24.04 LTS
```

Suitable for:

- Qwen3 4B;
- PostgreSQL;
- Redis;
- Playwright;
- Lighthouse;
- moderate crawling;
- API;
- dashboard;
- initial experiments.

## Recommended semester setup

```text
CPU:    16 vCPU
RAM:    64 GB
Disk:   300 GB NVMe/SSD
GPU:    optional
OS:     Ubuntu 24.04 LTS
```

This is the preferred target.

---

# 29. GPU Requirements

GPU is optional.

If using a GPU:

```text
VRAM: >= 12 GB
RAM:  >= 32 GB
CPU:  >= 8 vCPU
```

A GPU primarily improves:

- LLM throughput;
- concurrent agent sessions;
- vision inference.

The system must remain functional without a GPU.

---

# 30. Why 32–64 GB RAM

The model is only one process.

The same server must also run:

- Chromium;
- Playwright;
- Python workers;
- PostgreSQL;
- Redis;
- API;
- dashboard;
- analytics;
- evidence processing;
- operating system.

Therefore:

> 32 GB is the practical minimum for the complete stack; 64 GB is preferred.

---

# 31. Docker Architecture

Initial production stack:

```text
postgres
redis
ollama
worker
api
dashboard
```

The worker contains the browser and deterministic audit tooling during the initial implementation.

Later, components can be separated if profiling demonstrates a real need.

---

# 32. Expanded Service Architecture

The logical services are:

```text
discovery
scheduler
safety-governor
agent
crawler-http
crawler-browser
audit-accessibility
audit-performance
parser
validator
api
analytics
dashboard
postgres
redis
minio
ollama
```

Do not create one Docker container per Python module prematurely.

---

# 33. Storage Architecture

Separate:

```text
Raw Evidence
Processed Observations
Analytics Tables
Dataset Releases
```

Recommended:

```text
/data/
├── raw/
│   ├── html/
│   ├── screenshots/
│   ├── lighthouse/
│   ├── axe/
│   ├── headers/
│   └── metadata/
├── processed/
├── releases/
├── quarantine/
└── logs/
```

Use:

- PostgreSQL for structured records;
- MinIO for large binary evidence;
- Parquet for analytics releases;
- JSONL for flexible evidence exports.

---

# 34. Repository Structure

```text
bharatgov-access/
│
├── README.md
├── LICENSE
├── docker-compose.yml
├── .env.example
├── Makefile
│
├── docs/
│   ├── PROJECT_SPEC.md
│   ├── ARCHITECTURE.md
│   ├── DATA_DICTIONARY.md
│   ├── COLLECTION.md
│   ├── VALIDATION.md
│   ├── SAFETY.md
│   └── ANALYTICS.md
│
├── services/
│   ├── agent/
│   ├── crawler/
│   ├── scheduler/
│   ├── safety/
│   ├── validator/
│   ├── api/
│   ├── analytics/
│   └── dashboard/
│
├── tools/
│   ├── http/
│   ├── browser/
│   ├── accessibility/
│   ├── performance/
│   ├── metadata/
│   └── evidence/
│
├── schemas/
├── migrations/
├── configs/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── agent/
│   ├── safety/
│   └── benchmark/
│
├── data/
│   ├── samples/
│   └── fixtures/
│
└── scripts/
```

---

# 35. Data Model

Every observation should contain:

```text
crawl_id
dataset_version
domain_id
page_id
observed_at
source_url
canonical_url
government_entity
government_level
state_ut
organization_category
page_role
architecture
language
raw_evidence_refs
deterministic_measurements
derived_classifications
validation_status
```

---

# 36. Provenance

Every derived value must have provenance.

Example:

```json
{
  "field": "website_category",
  "value": "health",
  "method": "agentic_classification",
  "model": "qwen3:4b",
  "confidence": 0.91,
  "evidence_ids": [
    "page-001",
    "metadata-001"
  ]
}
```

---

# 37. Data Quality Validation

Every observation passes:

## Schema validation

Types and required fields.

## Range validation

Examples:

```text
CLS >= 0
score between 0 and 100
latency >= 0
HTTP status 100–599
```

## Cross-field validation

Example:

```text
browser_required = false
```

must not result in fabricated browser-only measurements.

## Provenance validation

Derived fields must reference evidence.

## Temporal validation

Every observation contains:

```text
observed_at
crawl_id
dataset_version
```

## Duplicate validation

Duplicate observations are detected and handled explicitly.

---

# 38. Agent Benchmark

Create a manually verified benchmark of at least:

```text
100 websites
```

Include:

- static HTML;
- WordPress;
- Drupal;
- Angular;
- React;
- Next.js;
- JavaScript-heavy portals;
- multilingual sites;
- PDF-heavy sites;
- legacy websites;
- service portals.

Human reviewers label:

```text
architecture
website category
important page types
language
browser necessity
crawl strategy
```

Compare the agent's decisions against the benchmark.

---

# 39. Agent Metrics

Measure:

### Architecture

```text
accuracy
macro F1
confusion matrix
```

### Page selection

```text
precision
recall
coverage
```

### Tool selection

```text
correct tool rate
unnecessary tool rate
invalid tool rate
```

### Efficiency

```text
agent steps/site
seconds/site
requests/site
browser sessions/site
CPU
RAM
```

### Reliability

```text
successful completion
partial completion
fatal failure
```

### Evidence grounding

```text
supported claims / total claims
```

Target:

> **100% of published derived claims must have deterministic provenance or explicit evidence.**

---

# 40. Deterministic vs Agentic Experiment

Build two collection strategies:

### Baseline

```text
fixed crawler
```

### Experimental

```text
agentic crawler
```

Run both against the same benchmark.

Compare:

```text
coverage
accuracy
time
requests
failures
resource usage
important-page discovery
architecture handling
```

This establishes whether the agentic design actually provides measurable benefits.

---

# 41. Model Benchmark

Run:

```text
Qwen3 4B
Qwen3 8B
Gemma 3 4B
```

against the same benchmark.

Compare:

| Metric | Qwen3 4B | Qwen3 8B | Gemma 3 4B |
|---|---:|---:|---:|
| Architecture accuracy | measure | measure | measure |
| Page selection F1 | measure | measure | measure |
| Tool selection | measure | measure | measure |
| Invalid actions | measure | measure | measure |
| Avg. steps | measure | measure | measure |
| Avg. latency | measure | measure | measure |
| RAM | measure | measure | measure |
| CPU | measure | measure | measure |
| Completion rate | measure | measure | measure |

Production model is selected based on measured quality and resource efficiency.

---

# 42. Agentic Collection Metadata

Store operational information:

```text
model
model_version
agent_steps
tools_called
architecture
crawl_strategy
pages_selected
pages_measured
crawl_duration
request_count
browser_time
failure_reason
validation_failures
```

This creates an additional research dataset about adaptive web collection.

---

# 43. Longitudinal Collection

The system should not be a one-time crawler.

Recommended cadence:

## Daily

Lightweight:

- DNS/HTTP availability;
- status;
- basic latency;
- certificate observations.

## Weekly

Moderate:

- homepage;
- structural fingerprint;
- major architecture changes;
- selected performance metrics.

## Monthly

Full:

- representative pages;
- accessibility;
- performance;
- mobile;
- language;
- reliability;
- web structure;
- evidence capture.

This is the default operating policy.

---

# 44. Change Detection

Before expensive crawling:

```text
Previous fingerprint
        |
        v
Current lightweight fingerprint
        |
     +--+--+
     |     |
   same  changed
     |     |
 reduced  re-profile
 crawl
```

Potential fingerprints:

- normalized DOM;
- framework signature;
- sitemap hash;
- homepage content hash;
- navigation hash;
- language selector;
- HTML size;
- important response headers.

Do not treat harmless analytics changes as meaningful architecture changes.

---

# 45. Analytics

The dataset is only the foundation.

Analytics will include:

## National

- accessibility distributions;
- performance distributions;
- reliability;
- language coverage;
- architecture distribution;
- website category distribution.

## State

- rankings;
- distributions;
- department comparisons;
- temporal trends;
- outliers.

## Organization

- historical measurements;
- detected issues;
- architecture;
- page types;
- benchmark position.

## Issue analysis

- WCAG issue frequencies;
- performance bottlenecks;
- broken-link patterns;
- mobile problems;
- language gaps.

---

# 46. Research Questions

Possible questions include:

1. Which government levels have the strongest accessibility performance?
2. Which states have the strongest overall public web infrastructure?
3. Which website categories are most accessible?
4. Does accessibility correlate with performance?
5. Does multilingual support correlate with accessibility?
6. Are modern web architectures associated with better performance?
7. Which accessibility violations dominate?
8. Which government categories have the highest reliability?
9. How much do government websites change month-to-month?
10. Which sites improve or regress most strongly?
11. Are rankings stable over time?
12. Which website architectures produce the most difficult crawl behavior?
13. Does agentic collection improve coverage over fixed collection strategies?
14. What resource cost is required for adaptive collection?

---

# 47. Statistical Methods

Use deterministic analytics tools for:

- mean;
- median;
- quantiles;
- standard deviation;
- confidence intervals;
- correlation;
- regression;
- hypothesis testing;
- clustering;
- PCA/UMAP where justified;
- outlier detection;
- time-series analysis;
- change-point detection;
- ranking analysis.

Do not ask the LLM to calculate important statistics.

---

# 48. Automated Data Explanation

The dashboard may generate explanations such as:

> Accessibility decreased by 8.2 percentage points between August and September. The largest contributor was an increase in missing form-label violations across the district-administration category.

But the system must calculate:

- the 8.2 points;
- sample size;
- comparison period;
- contributing groups;

using SQL/Python.

The LLM may turn validated results into readable prose.

Every explanation should provide:

- metric;
- time window;
- sample size;
- method;
- evidence references.

---

# 49. Dashboard

The dashboard is a core deliverable.

It should feel like an **India Digital Observatory**, not a generic student dashboard.

## National overview

Show:

```text
Government websites monitored
Pages analyzed
Observations
Accessibility issues
Average/median performance
States/UTs
Languages
Latest crawl
```

## Interactive India map

Filters:

```text
dimension
state
government level
organization type
language
time
```

## State page

Show:

- ranking;
- distribution;
- department comparison;
- trends;
- issue profile;
- outliers.

## Organization page

Show:

- current metrics;
- historical trend;
- architecture;
- page types;
- issues;
- evidence.

## Issue explorer

Filter by:

```text
issue
severity
state
department
organization
date
```

---

# 50. Dashboard Visual Design

The dashboard should use:

- clean typography;
- responsive cards;
- interactive charts;
- India choropleth;
- time-series plots;
- distribution plots;
- ranking tables;
- drill-down interactions;
- clear legends;
- accessible colors;
- tooltips;
- evidence links.

Avoid meaningless decorative charts.

Every visualization must answer a question.

---

# 51. BharatGov Inspector

The working product will accept:

```text
government URL
```

and produce:

```text
BharatGov Report
```

Possible output:

```text
Accessibility
Performance
Mobile
Reliability
Language
Architecture
Major issues
Benchmark percentile
Historical trend
Evidence
```

The same production pipeline must power the Inspector.

There must not be a fake hardcoded demo.

---

# 52. Benchmarking

A key product feature is comparison.

Example:

```text
Website
    |
    +--> India percentile
    +--> State percentile
    +--> Organization-type percentile
    +--> Service-category percentile
```

This makes the dataset directly useful.

---

# 53. Product Architecture

```text
User
 |
 v
BharatGov Inspector API
 |
 v
Safety Governor
 |
 v
Agent
 |
 +--> deterministic tools
 |
 v
Validation
 |
 v
Benchmark Engine
 |
 v
Report
```

---

# 54. DataHub KGP Release

The dataset should be packaged with:

```text
README.md
LICENSE
DATA_DICTIONARY.md
METHODOLOGY.md
COLLECTION.md
VALIDATION.md
CHANGELOG.md
CITATION.cff
schema/
samples/
parquet/
metadata/
```

Separate:

```text
raw evidence
structured observations
derived metrics
agentic classifications
analytics outputs
```

The DataHub release must be reproducible and documented.

---

# 55. Dataset Versioning

Example:

```text
v0.1.0
v0.2.0
v1.0.0
v1.1.0
```

Every observation has:

```text
crawl_id
dataset_version
observed_at
tool_versions
model
configuration_hash
```

---

# 56. Reproducibility

Example metadata:

```json
{
  "crawl_id": "crawl-2026-08-09-000001",
  "dataset_version": "0.1.0",
  "agent_model": "qwen3:4b",
  "crawler_version": "git-sha",
  "axe_version": "x.y.z",
  "lighthouse_version": "x.y.z",
  "configuration_hash": "..."
}
```

---

# 57. Failure Handling

Websites may be:

- offline;
- slow;
- blocked;
- moved;
- malformed;
- TLS-invalid;
- JavaScript-dependent;
- CDN-protected;
- retired.

Never silently drop them.

Record explicit states.

---

# 58. Forms and Transactions

The crawler may inspect forms.

It must never automatically submit:

- applications;
- payments;
- OTP requests;
- emails;
- account creation;
- document uploads;
- citizen-service transactions.

Forms are measurement targets, not actions.

---

# 59. Personal Data Minimization

The project focuses on website infrastructure.

Do not intentionally collect:

- passwords;
- OTPs;
- authentication tokens;
- citizen IDs;
- unnecessary personal information;
- private records.

Public pages that contain incidental personal information should be minimized, redacted, hashed, or excluded where practical.

---

# 60. Security

The project itself should use:

- secrets through environment variables;
- no secrets in Git;
- restricted database ports;
- HTTPS for dashboard/API;
- firewall rules;
- least-privilege service accounts;
- container isolation;
- audit logs;
- regular dependency updates.

---

# 61. Monitoring

Monitor:

```text
crawler health
agent health
queue length
crawl throughput
failure rate
domain cooldowns
CPU
RAM
disk
database
Redis
Ollama
browser workers
```

Alert on:

- disk exhaustion;
- repeated crawl failures;
- agent loops;
- database errors;
- abnormal request volume;
- memory exhaustion.

---

# 62. First Pilot

Do not begin with thousands of websites.

First run:

```text
10 heterogeneous government websites
```

The pilot should include:

- static;
- CMS;
- SPA;
- multilingual;
- legacy;
- document-heavy;
- service portal;
- slow website;
- redirecting site;
- difficult website.

The objective is to prove the complete pipeline.

---

# 63. Pilot Acceptance Criteria

### Agent

- architecture classification works;
- valid structured output;
- bounded actions;
- appropriate tool selection.

### Safety

- domain concurrency never exceeds configured limit;
- rate limiting works;
- 429/5xx triggers backoff;
- robots restrictions work.

### Measurements

- axe output stored;
- Lighthouse output stored;
- screenshots linked;
- raw evidence preserved.

### Validation

- invalid output rejected;
- unsupported claims rejected;
- missing evidence detected.

### Storage

- every record has crawl ID;
- provenance exists;
- failures remain represented.

### Reproducibility

A second run with identical configuration produces an auditable equivalent result, subject to naturally changing websites.

---

# 64. Scaling Strategy

Scale gradually:

```text
10
 |
100
 |
500
 |
1,000
 |
2,500
 |
5,000
 |
10,000+
```

At each stage measure:

- throughput;
- resource consumption;
- failure rate;
- safety;
- database growth;
- evidence storage;
- agent efficiency.

Scale only after validation.

---

# 65. Semester Roadmap

## Phase 0 — Prior Art

Week 1

- literature review;
- existing dataset review;
- GIGW review;
- SugamyaWeb review;
- exact novelty statement.

## Phase 1 — Infrastructure

Weeks 1–2

- Git repository;
- Docker;
- PostgreSQL;
- Redis;
- Ollama;
- Qwen3 4B;
- logging.

## Phase 2 — Deterministic Baseline

Weeks 2–3

- HTTP;
- robots;
- rate limiting;
- HTML;
- screenshots;
- axe;
- Lighthouse;
- evidence.

## Phase 3 — Agent

Weeks 3–5

- tools;
- state machine;
- structured output;
- architecture profiling;
- adaptive strategy.

## Phase 4 — Benchmark

Week 5

- 100-site benchmark;
- model comparison;
- fixed-vs-agentic experiment.

## Phase 5 — Discovery

Weeks 5–7

- central;
- states/UTs;
- districts;
- local bodies;
- verification;
- deduplication.

## Phase 6 — Scale

Weeks 7–10

```text
100 -> 500 -> 1,000 -> 2,500 -> 5,000+
```

## Phase 7 — Analytics

Weeks 9–11

- statistics;
- correlations;
- rankings;
- clustering;
- anomalies;
- longitudinal analysis.

## Phase 8 — Dashboard

Weeks 10–12

- India map;
- state views;
- rankings;
- issue explorer;
- time series;
- explanations.

## Phase 9 — Inspector

Weeks 11–13

- URL analysis;
- benchmark;
- report.

## Phase 10 — Release

Weeks 13–14

- validation;
- documentation;
- dataset package;
- DataHub preparation;
- final presentation.

---

# 66. Final Definition of Done

## Dataset

- [ ] comprehensive government registry;
- [ ] verification;
- [ ] large-scale observations;
- [ ] raw evidence;
- [ ] structured schema;
- [ ] versioning;
- [ ] provenance;
- [ ] coverage audit.

## Agent

- [ ] Ollama;
- [ ] Qwen3 4B;
- [ ] tool calling;
- [ ] bounded loop;
- [ ] architecture profiling;
- [ ] adaptive page selection;
- [ ] evidence-grounded classification;
- [ ] model benchmark.

## Safety

- [ ] robots;
- [ ] rate limiting;
- [ ] concurrency;
- [ ] backoff;
- [ ] budgets;
- [ ] no form submission;
- [ ] no authentication bypass;
- [ ] audit logs.

## Validation

- [ ] schema;
- [ ] range;
- [ ] provenance;
- [ ] duplicates;
- [ ] cross-field validation;
- [ ] agent benchmark;
- [ ] deterministic analytics.

## Analytics

- [ ] national statistics;
- [ ] state comparisons;
- [ ] organization comparisons;
- [ ] accessibility trends;
- [ ] performance trends;
- [ ] language analysis;
- [ ] correlations;
- [ ] clustering/outliers;
- [ ] longitudinal analysis.

## Dashboard

- [ ] interactive India map;
- [ ] filters;
- [ ] rankings;
- [ ] drill-down;
- [ ] time series;
- [ ] issue explorer;
- [ ] evidence;
- [ ] explanations.

## Product

- [ ] BharatGov Inspector;
- [ ] working URL analysis;
- [ ] benchmark;
- [ ] report.

## Release

- [ ] DataHub-ready package;
- [ ] data dictionary;
- [ ] methodology;
- [ ] validation report;
- [ ] reproducibility metadata;
- [ ] citation metadata.

---

# 67. What BharatGov Access Is

BharatGov Access is:

> **A continuously evolving, evidence-first dataset and observatory that uses a locally hosted lightweight AI agent to adaptively study India's heterogeneous government websites while deterministic tools, safety controls, and validation systems provide reproducibility, responsible collection, and trustworthy analytics.**

---

# 68. What BharatGov Access Is Not

It is not:

- a penetration-testing platform;
- a vulnerability exploitation tool;
- a DDoS/stress-testing tool;
- an unrestricted autonomous browser;
- a citizen-data harvesting platform;
- a form-submission bot;
- a search engine;
- an LLM-only dataset generator.

It is a controlled research and measurement platform.

---

# 69. Immediate Implementation Order

The correct implementation order is:

```text
1. Repository
        |
2. Docker Compose
        |
3. PostgreSQL + Redis
        |
4. Ollama + Qwen3 4B
        |
5. Safety Governor
        |
6. Deterministic HTTP collector
        |
7. Playwright
        |
8. axe + Lighthouse
        |
9. Evidence storage
        |
10. Validator
        |
11. Agent tool layer
        |
12. Agent state machine
        |
13. 10-site pilot
        |
14. 100-site benchmark
        |
15. Scale
        |
16. Analytics
        |
17. Dashboard
        |
18. BharatGov Inspector
        |
19. DataHub release
```

Do not start large-scale collection before the 10-site pilot passes validation.

---

# 70. Final Engineering Principle

The system must always follow:

```text
Website
   |
   v
Observed evidence
   |
   v
Deterministic measurement
   |
   v
Validation
   |
   v
Agentic interpretation
   |
   v
Validated structured record
   |
   v
Statistical analysis
   |
   v
Visualization
   |
   v
Evidence-backed explanation
```

The LLM provides adaptability.

The deterministic tools provide measurements.

The safety governor controls network behavior.

The validator controls data quality.

The analytics engine controls numerical conclusions.

The dashboard communicates the findings.

The product demonstrates practical value.

That separation is the foundation of BharatGov Access.
