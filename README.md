# BharatGov Access
### Agentic, Longitudinal Observatory of India's Government Web Infrastructure

[![License](https://img.shields.io/badge/License-CC--BY--4.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Architecture](https://img.shields.io/badge/Architecture-Hybrid%20Agentic%20%2B%20Deterministic-green.svg)](#system-architecture)
[![Target Platform](https://img.shields.io/badge/Target-DataHub%20KGP-orange.svg)](#datahub-kgp-dataset-release)
[![Live Observatory](https://img.shields.io/badge/Live%20Observatory-uniquepratham.github.io-1f6feb.svg)](https://uniquepratham.github.io/)

**BharatGov Access** is a large-scale, longitudinal, evidence-first observatory and dataset platform characterizing the publicly observable digital infrastructure of Indian government websites across **Central Ministries**, **36 States/UTs**, and **785+ District Administrations**.

**Live observatory:** <https://uniquepratham.github.io/>

---

## Install the dataset

The census ships as a pip-installable package, so a reader can query it without cloning the repo:

```bash
pip install bharatgov-access
```

```python
import bharatgov_access as bga

df = bga.load()                  # 14,489 domains, 20 typed columns
live = bga.load(reachable=True)  # 7,542 that answered in-country

bga.tier_summary()               # Table I of the paper
bga.architecture_summary()       # Table II of the paper
bga.state_ranking()              # 36 States and UTs, ranked
```

A CLI ships with it:

```bash
bharatgov info
bharatgov tiers
bharatgov arch
bharatgov states --top 10
bharatgov query --tier district --state Kerala --min-maturity 85
bharatgov export --format csv --out census.csv --reachable-only
```

The package lives at [`packages/bharatgov-access/`](packages/bharatgov-access) and bundles the Parquet release in a 465 KB wheel. Its 14 tests assert the published figures, so a loader regression fails loudly rather than silently changing a paper table.

---

## 1. Core Research Question

> **What is the measurable state of India's public-facing government web infrastructure, how does it differ across governance levels, states, departments, and website architectures, and how does it evolve over time?**

---

## 2. The 10 Measurement Dimensions

Rather than treating digital accessibility in isolation, BharatGov Access captures 10 multi-dimensional measurement families with complete cryptographic SHA-256 raw evidence provenance:

| # | Dimension | Deterministic Measurement Signals |
|---|---|---|
| **1** | **Digital Accessibility** | Automated WCAG violations (axe-core), critical/serious/moderate/minor breakdown, missing alt text, ARIA attributes, color contrast, and form labels. |
| **2** | **Web Performance** | Core Web Vitals (LCP, CLS, FCP, TTFB, TBT), Speed Index, total page weight, JS/CSS/image transfer byte breakdowns. |
| **3** | **Mobile Readiness** | Viewport configuration, mobile layout responsiveness, horizontal overflow detection, touch-target observations. |
| **4** | **Reliability** | HTTP status codes, response latency, TLS certificate validity, certificate expiry countdown, redirect hop chains. |
| **5** | **Language & Multilingual** | Primary language, Indian scheduled languages script detection (Hindi, Bengali, Tamil, Telugu, Kannada, etc.), language selector widgets. |
| **6** | **Web Structure** | Total DOM node count, maximum DOM depth, internal/external link ratios, PDF circular counts, form counts, table layouts. |
| **7** | **Security & Hygiene** | Publicly observable HTTP headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, HTTPS enforcement). |
| **8** | **Entity Classification** | Grounded classification across governance levels (Central, State, District, Local Body, Statutory Agency). |
| **9** | **Architecture Profiling** | Framework and CMS marker detection (Angular SPA, React SPA, Next.js, WordPress, Drupal, Legacy Dynamic). |
| **10**| **Longitudinal Tracking** | Temporal change detection across daily availability, weekly structural shifts, and monthly full multi-page audits. |

---

## 3. System Architecture

BharatGov Access uses a **5-layer hybrid architecture** that strictly separates adaptive AI reasoning from deterministic network measurements:

```
                  Government Domain Registry (10,000+ Domains)
                                       │
                                       ▼
                       Discovery & Verification Engine
                                       │
                                       ▼
                 ┌───────────────────────────────────────────┐
                 │          Safety Governor (Hard Wall)      │
                 │  - Concurrency = 1/domain                 │
                 │  - Rate Limit <= 1 req/sec/domain         │
                 │  - robots.txt compliance                  │
                 │  - Prohibited: Form submissions, Auth, Pay│
                 └─────────────────────┬─────────────────────┘
                                       │
                                       ▼
                      Agent Controller (Local Qwen3 4B)
                    Adaptive Profiling & Page Selection
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
        Deterministic Auditors                       Headless Browser Pool
   (axe-core, Lighthouse, TLS)                     (Playwright Chromium)
                │                                             │
                └──────────────────────┬──────────────────────┘
                                       │
                                       ▼
                       Raw Evidence Store (/data/raw/)
                    (HTML, Screenshots, JSON, SHA-256)
                                       │
                                       ▼
                      Data Quality Validation Engine
                   (Range, Cross-Field, Provenance Check)
                                       │
                                       ▼
                     Data Warehouse & Exporter (Parquet)
                  (DataHub KGP Versioned Dataset Releases)
```

---

## 4. Hardware Optimization (Vultr 24 vCPU / 96 GB RAM)

The platform is designed to run self-hosted on a dedicated Linux instance (e.g. Vultr `vc2-24c-96gb`):
- **CPU Workers**: 16 parallel domain workers.
- **Memory Allocation**: PostgreSQL 16 (8 GB shared buffers, 128 MB work mem), Redis 7 (4 GB LRU cache), MinIO S3 object store, and Ollama local AI container (16 GB allocation for `qwen3:4b`/`qwen3:8b`).
- **Storage**: 1600 GB NVMe for raw HTML, WebP screenshots, and versioned Parquet releases.

---

## 5. Quickstart & Local Setup

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (optional for local mock testing)

### Installation
```bash
# 1. Clone repository
git clone <REPO_URL> bharatgov-access
cd bharatgov-access

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Initialize environment and directory trees
cp .env.example .env
python -c "from configs.settings import settings; settings.ensure_dirs()"
```

### Running Test Suite
```bash
# Run all 28 automated tests
pytest tests/ -v
```

---

## 6. Running Pipelines

### A. Run 10-Site Heterogeneous Pilot
```bash
# Dry-run with built-in fixtures
python scripts/run_pilot.py --dry-run

# Live network collection
python scripts/run_pilot.py
```

### B. Run Master Discovery & Observatory Pipeline
```bash
# Inspect first 15 government domains and export DataHub release
python scripts/run_pipeline.py --limit 15 --version 0.1.0

# Live full run
python scripts/run_pipeline.py --live --limit 100 --version 0.1.0
```

---

## 7. Production Deployment (Vultr VM)

```bash
# 1. SSH into the server
ssh root@<YOUR_VM_IP>

# 2. Clone and enter directory
git clone <REPO_URL> /opt/bharatgov-access
cd /opt/bharatgov-access

# 3. Initialize all infrastructure & pull local AI model
chmod +x scripts/init_infra.sh
./scripts/init_infra.sh

# 4. Start production Docker stack
docker compose up -d

# 5. Execute production collection batch
python scripts/run_pipeline.py --live --limit 1000 --version 1.0.0
```

---

## 8. Ephemeral Infrastructure and Global Expansion

The India census is complete. The next phase measures other countries from
inside those countries, using the same tools and timeouts so the comparison is
like for like.

### 8.1 Ephemeral compute, persistent data

Measurement jobs are short-lived, so compute is provisioned on demand and
destroyed afterwards. The dataset, the provenance and the methodology are
permanent; only the worker is disposable.

`services/infrastructure/` implements the lifecycle:

| Module | Responsibility |
| :--- | :--- |
| `provider.py` | Provider-neutral interface (`CloudProvider`) |
| `vultr.py` | Vultr v2 adapter, with a dry-run mode |
| `lifecycle.py` | State machine, ownership checks, reaping |
| `budget.py` | Per-job and monthly spend ceilings, persisted ledger |
| `cost.py` | Itemised cost model (compute, storage, snapshots, egress, backups) |
| `regions.py` | Country probe status derived from real regions |
| `catalog.py` | Loads the live region and plan catalogue |

The state machine is:

```
IDLE -> PROVISIONING -> INITIALIZING -> READY -> RUNNING
     -> UPLOADING_RESULTS -> VERIFYING_RESULTS -> TERMINATING -> DESTROYED
```

Any state may transition to `FAILED`, which preserves the instance so logs can
be recovered. A failed instance is never auto-destroyed.

### 8.2 Safety rules, enforced in code

These are not conventions; they are structural.

1. **Ownership.** Every instance carries the tag `bharatgov-ephemeral`. The
   reaper only ever considers tagged instances, so an unrelated server in the
   same account is invisible to it. `_assert_owned()` raises before any destroy.
2. **Data before destruction.** `destroy()` refuses unless
   `results_verified` is true. The `force=True` escape hatch is logged loudly
   and exists only for the case where an operator has already recovered the
   data by hand.
3. **Budget before the API call.** `BudgetGuard.check()` runs before
   `create_instance()`. A refusal means no instance is created, which the tests
   assert directly.
4. **Idempotency.** `provision()` is keyed on `job_id`, so a duplicate
   scheduler tick returns the existing record rather than provisioning twice.
5. **Restart safety.** Job state is persisted to disk and reloaded on start, so
   a crash does not orphan an instance or double-spend.
6. **No secrets in logs.** The API key is read from `VULTR_API_KEY` and never
   appears in a log line, an exception message or a `repr`.

### 8.3 Country coverage

A country is marked **operational** only when a cloud region physically inside
it exists. Where none exists, the country is **planned** (on the roadmap) or
**unsupported**. A nearby region is recorded for operational convenience but is
always labelled with the country it actually sits in, so a foreign probe can
never be presented as a domestic one.

Coverage is derived from the live Vultr catalogue, not from a hand-written list:

```bash
export VULTR_API_KEY=...          # never commit this
python scripts/fetch_vultr_catalog.py
python scripts/build_world_coverage.py
python scripts/build_world_map.py
python scripts/build_future_data.py
```

Current state: **249 countries** classified, **20** with a domestic region,
**40** planned, **189** unsupported.

### 8.4 Cost

A 15-minute batch is billed at Vultr's one-hour minimum, so the cost per batch
equals the hourly rate. The cheapest plan that can run headless Chromium
(1 GB RAM) is `vc2-1c-1gb` at **$0.007 per batch**. Storage, snapshots,
bandwidth overage and backups are modelled separately in `cost.py` because
destroying an instance does not make every associated charge disappear.

### 8.5 The Future dashboard view

`dashboard/index.html` gains a sixth view, **Future — Global Observatory**,
with five sections: what changes and what does not, a world map of probe
availability, the eight research dimensions, live infrastructure counters with
the real instance catalogue, and the research roadmap.

Every value is either measured or explicitly labelled planned. The
infrastructure counters read zero because nothing has been provisioned, not
because the panel is a mock-up.

---

## 9. DataHub KGP Dataset Release

Every release generated by `services/analytics/exporter.py` produces:
1. **`bharatgov_access_vX.Y.Z.parquet`**: Columnar dataset ready for high-performance SQL, Pandas, Polars, DuckDB queries.
2. **`bharatgov_access_vX.Y.Z.jsonl`**: Complete hierarchical records with full nested measurements.
3. **`coverage_audit_vX.Y.Z.json`**: Section 8 coverage report logging verified, observed, unavailable, and restricted percentages.
4. **`manifest_vX.Y.Z.json`**: Dataset provenance, versioning metadata, and citation references.

---

## 10. Ethical & Responsible Crawling Guarantee

BharatGov Access adheres to strict responsible crawling standards:
- $\le 1.0\text{ req/sec}$ per domain with exponential backoff on 429/5xx status codes.
- Concurrency strictly locked to 1 per domain.
- `robots.txt` exclusion honored across all domains.
- **Zero intrusive actions**: Prohibits form submissions, account registrations, OTP generation, payment gateways, and authentication bypass.

---

## 11. License & Citation

Distributed under the **Creative Commons Attribution 4.0 International (CC-BY-4.0)** License.

```bibtex
@misc{bharatgov_access_2026,
  title={BharatGov Access: Agentic, Longitudinal Observatory of India's Government Web Infrastructure},
  author={BharatGov Access Research Team},
  year={2026},
  howpublished={\url{https://datahub.kgp/bharatgov-access}},
  note={DataHub KGP Research Dataset}
}
```
