# CivicWeb Observatory
### Agentic, Longitudinal Observatory of India's Government Web Infrastructure

[![License](https://img.shields.io/badge/License-CC--BY--4.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Architecture](https://img.shields.io/badge/Architecture-Hybrid%20Agentic%20%2B%20Deterministic-green.svg)](#system-architecture)
[![Target Platform](https://img.shields.io/badge/Target-DataHub%20KGP-orange.svg)](#datahub-kgp-dataset-release)
[![Live Observatory](https://img.shields.io/badge/Live%20Observatory-uniquepratham.github.io-1f6feb.svg)](https://uniquepratham.github.io/)

**CivicWeb Observatory** is a large-scale, longitudinal, evidence-first observatory and dataset platform characterizing the publicly observable digital infrastructure of Indian government websites across **Central Ministries**, **36 States/UTs**, and **785+ District Administrations**.

**Live observatory:** <https://uniquepratham.github.io/>

---

## Install the dataset

The census ships as a pip-installable package, so a reader can query it without cloning the repo:

```bash
pip install civicweb-observatory
```

```python
import civicweb_observatory as bga

df = bga.load()                  # 14,489 domains, 20 typed columns
live = bga.load(reachable=True)  # 7,542 that answered in-country

bga.tier_summary()               # Table I of the paper
bga.architecture_summary()       # Table II of the paper
bga.state_ranking()              # 36 States and UTs, ranked
```

A CLI ships with it:

```bash
civicweb info
civicweb tiers
civicweb arch
civicweb states --top 10
civicweb query --tier district --state Kerala --min-maturity 85
civicweb export --format csv --out census.csv --reachable-only
```

The package lives at [`packages/civicweb-observatory/`](packages/civicweb-observatory) and bundles the Parquet release in a 465 KB wheel. Its 14 tests assert the published figures, so a loader regression fails loudly rather than silently changing a paper table.

---

## 1. Core Research Question

> **What is the measurable state of India's public-facing government web infrastructure, how does it differ across governance levels, states, departments, and website architectures, and how does it evolve over time?**

---

## 2. The 10 Measurement Dimensions

Rather than treating digital accessibility in isolation, CivicWeb Observatory captures 10 multi-dimensional measurement families with complete cryptographic SHA-256 raw evidence provenance:

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

CivicWeb Observatory uses a **5-layer hybrid architecture** that strictly separates adaptive AI reasoning from deterministic network measurements:

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
git clone <REPO_URL> civicweb-observatory
cd civicweb-observatory

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
git clone <REPO_URL> /opt/civicweb-observatory
cd /opt/civicweb-observatory

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

1. **Ownership.** Every instance carries the tag `civicweb-ephemeral`. The
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


### 8.6 Region selection

The measurement region is chosen per country, and the choice is recorded so it
can be audited.

1. **Only a domestic region is eligible.** A region in a neighbouring country is
   never substituted, because a foreign probe cannot support a domestic claim.
2. **Within the eligible set**, regions are ranked by fewest observed WAF
   blocks, then lowest observed median latency, then provider order.
3. **With no history**, the choice is recorded as `no_history` rather than
   implying a measured preference.

`services/infrastructure/selection.py` implements this. `RegionHistory` is
populated from real measurement outcomes, so the ranking improves as the
observatory runs.

### 8.7 Verified end-to-end

`scripts/prove_ephemeral.py` provisions one real instance, waits for it to
become active, marks the job running, verifies the results, and destroys the
instance. A real run on 2026-11-14:

| Step | Result |
| :--- | :--- |
| Region selected | `blr` (Bangalore), reason `no_history` |
| Plan | `vc2-1c-1gb`, 1 GB RAM, $0.007/hr |
| Instance | `28bfbed8-…`, public IP `139.84.150.147` |
| Ready in | 28 s |
| Destroyed | yes, confirmed gone |
| Actual cost | **$0.0070** |
| Production servers touched | **0 of 5** |

The first attempt hit Vultr's `409 Server is currently locked` on delete, which
is a transient state while an instance settles. `destroy_instance()` now retries
with backoff instead of treating the lock as a permanent failure, because a
failed destroy leaves a billable instance running.


### 8.8 Restart safety and reconciliation

A process that dies mid-run leaves the ledger disagreeing with reality: a job
claiming an instance exists when it was deleted by hand, or an instance billing
with no job that knows about it. Both are wrong, and both cost money or lose
data.

`InfrastructureManager.reconcile()` resolves both:

| Situation | Action |
| :--- | :--- |
| Job says active, instance gone | Job marked `FAILED` with the reason recorded |
| Instance exists, no job knows it | Destroyed, but only if it carries the ownership tag |
| Job says active, instance exists | Left alone |

```bash
VULTR_API_KEY=... python scripts/reconcile_infra.py --dry-run   # report
VULTR_API_KEY=... python scripts/reconcile_infra.py             # act
```

Run it after any crash, or on a schedule. Five tests cover it, including that a
foreign instance is never touched.

### 8.9 Remote measurement

`scripts/run_remote_measurement.py` closes the last gap: it provisions an
instance, injects a throwaway SSH keypair through cloud-init, uploads the same
`crawl_real.py` used for the India census, runs a real batch, pulls the results
back, and verifies the SHA-256 before destroying the instance.

A real run on 2026-11-18, measuring three Indian government domains from a
Bangalore probe:

| Step | Result |
| :--- | :--- |
| Instance | `66d0b6de-…`, IP `139.84.158.177`, `blr` |
| SSH | connected, deps installed by cloud-init |
| Worker | uploaded, 3 domains |
| Measured | 3/3 in under a second |
| Reachable | 2 of 3 |
| Checksum | **MATCH** |
| Destroyed | yes, confirmed gone |
| Cost | **$0.0070** |

The measurements themselves:

| Domain | Status | TTFB | Accessibility | Security | Maturity |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `meity.gov.in` | 200 | 262 ms | 95.0 | 100.0 | 77.3 |
| `india.gov.in` | 200 | 330 ms | 97.8 | 85.0 | 69.8 |
| `nic.in` | — | — | — | — | — |

`nic.in` did not resolve from the probe, which is recorded as a real outcome
rather than a zero. The two that answered produced genuine SHA-256 hashes of
their response bodies, so the evidence is reproducible.

The keypair is generated per run and exists only in memory, so a leaked
instance cannot be reached after the job ends. The worker is byte-identical to
the India one, which is what makes a measurement on an ephemeral probe
comparable to one on the permanent node.


### 8.10 Cross-country measurements

`scripts/run_global_batch.py` provisions one probe per country, measures a small
comparable sample of national portals, and appends the results to
`data/real/global_measurements.csv` with full provenance.

Every row records `probe_country`, `probe_region`, `probe_region_country` and
`domestic_probe`. A row is only marked domestic when the probe's region country
equals the target country, so the claim can be checked rather than trusted.

**18 countries measured, 72 domains, all from domestic probes, $0.126 total.**

| Country | Probe | Reachable | Accessibility | Security | Median TTFB |
| :--- | :--- | ---: | ---: | ---: | ---: |
| India | `blr` | 3/4 | 97.8 | 85.0 | 476 ms |
| Singapore | `sgp` | 2/4 | 96.0 | 50.0 | 971 ms |
| Australia | `mel` | 4/4 | 91.8 | 66.2 | 155 ms |
| South Korea | `icn` | 4/4 | 90.8 | 5.0 | 262 ms |
| France | `cdg` | 1/4 | 89.3 | 70.0 | 135 ms |
| Poland | `waw` | 4/4 | 86.9 | 32.5 | 85 ms |
| United States | `atl` | 4/4 | 86.7 | 52.5 | 187 ms |
| Sweden | `sto` | 4/4 | 86.1 | 58.8 | 240 ms |
| Brazil | `sao` | 3/4 | 86.0 | 90.0 | 196 ms |
| United Kingdom | `lhr` | 3/4 | 85.7 | 71.7 | 91 ms |
| Japan | `itm` | 2/4 | 84.4 | 35.0 | 187 ms |
| Netherlands | `ams` | 4/4 | 83.3 | 100.0 | 136 ms |
| Israel | `tlv` | 3/4 | 83.3 | 53.3 | 293 ms |
| South Africa | `jnb` | 3/4 | 83.1 | 23.3 | 1,508 ms |
| Canada | `yto` | 3/4 | 81.7 | 40.0 | 78 ms |
| Mexico | `mex` | 3/4 | 81.4 | 23.3 | 291 ms |
| Spain | `mad` | 3/4 | 79.5 | 45.0 | 58 ms |
| Germany | `fra` | 2/4 | 69.6 | 87.5 | 109 ms |

Two countries were skipped rather than faked: **Italy** had no plan meeting the
1 GB floor in its region, and **Chile** timed out during provisioning. Both are
recorded as skipped, not as zeros.

The sample is four domains per country by design. This is a cross-country
comparability check, not a census; the India census in the other views remains
the large sample.


### 8.11 Crawler politeness

The crawler obeys three rules, enforced in `tools/http/polite.py` and
`tools/http/robots.py` rather than left to the caller:

1. **Honest identification.** The User-Agent names the project and gives a
   contact address. It does not claim to be a browser.
2. **robots.txt compliance.** Python's standard `urllib.robotparser` does not
   implement `*` wildcards or `$` anchors, so it silently allows paths that
   robots.txt forbids. `gov.uk` publishes `Disallow: /*/print$` and
   `Disallow: /search/all*`; the standard library permits both. The parser here
   implements RFC 9309 matching: wildcards, end anchors, longest-match wins,
   Allow beats Disallow on a tie, and specific agents beat `*`.
3. **One request per second per host**, with a site's own `Crawl-delay`
   overriding the default, a global concurrency cap, `Retry-After` honoured on
   429/503, and exponential backoff after repeated failures.

A robots-disallowed URL is recorded as `robots_disallowed`, not as a failure,
so it stays out of the reachability denominator rather than being counted as a
dead portal.

Eleven tests cover this, including the exact gov.uk patterns the standard
library gets wrong.


### 8.12 Sector coverage

Sector is inferred from the hostname and, where a ministry index supplied it,
from the link text. It is reliable for dedicated domains (`health.`, `court.`,
`police.`) and puts general portals in `general`.

Measured breakdown across **1,492 domains**:

| Sector | Domains | Reachable | Accessibility | Security |
| :--- | ---: | ---: | ---: | ---: |
| general | 958 | 31.6% | 87.6 | 49.0 |
| education | 343 | 32.9% | 86.1 | 28.8 |
| judiciary | 53 | 47.2% | 80.9 | 32.6 |
| health | 51 | 19.6% | 90.8 | 56.5 |
| transport | 34 | 26.5% | 91.6 | 47.8 |
| finance | 23 | 13.0% | 90.7 | 61.7 |
| social | 10 | 20.0% | 90.6 | 12.5 |
| police | 11 | 0.0% | not measured | not measured |
| agriculture | 5 | 0.0% | not measured | not measured |
| defence | 3 | 0.0% | not measured | not measured |
| environment | 1 | 0.0% | not measured | not measured |

Three findings:

1. **Health scores highest on accessibility (90.8) and second on security
   (56.5)**, contrary to the assumption that health portals lag.
2. **Education scores worst on security (28.8)** across 343 domains, the
   largest single-sector deficit in the study.
3. **Finance has the lowest reachability (13.0%)** but the highest security
   (61.7) among sectors with data. Tax and treasury portals are heavily
   protected, which is why they are hard to reach and well hardened.

A sector with no reachable domains shows "not measured" rather than a zero, so
an empty sample cannot be mistaken for a bad score.

#### Why sector coverage is uneven, and what was tried

Four discovery methods were attempted:

| Method | Result |
| :--- | :--- |
| Certificate Transparency, sector labels | 574 domains, but crt.sh now takes ~38 s per query and often returns nothing |
| National sitemaps | 39 domains; a sitemap lists its own pages, not other agencies |
| Agency directories | 424 domains; Poland alone yielded 315 |
| Ministry indexes | 373 domains; Canada 34, Poland 303 |

The structural limit is that **modern governments use path-based routing on one
domain rather than a separate domain per agency**. `gov.uk/government/organisations`
links to `/government/organisations/xxx`, not to `health.gov.uk`. A
domain-based census therefore cannot reach every ministry in every country, and
this is a property of how governments deploy websites, not a gap in the method.


### 8.13 Coverage with one provider: the vantage model

The account is Vultr, which operates in 20 countries. A domestic probe is
therefore impossible in the other 229. That is a constraint on the vantage
point, not on whether the country can be measured.

`services/infrastructure/vantage.py` classifies every country into one of three
vantage classes, derived from real geography rather than asserted:

| Class | Countries | What the measurement means |
| :--- | ---: | :--- |
| **domestic** | 19 | Probe inside the country. Supports a claim about what a citizen experiences. |
| **nearest** | 180 | Probe in the closest region, in another country. Real data, but it describes a foreign client's view. |
| **unmeasurable** | 50 | Nearest region over 6,000 km away. A latency figure would describe the path, not the portal. |

The nearest region is chosen by great-circle distance from the country's
centroid to each Vultr region, using a haversine calculation. The distance is
recorded on every row, so a reader can see how far the probe was.

#### Why this is a contribution, not a workaround

A portal measured from both inside and outside its country answers a question
no single-vantage study can: **how much of the measured quality is the portal,
and how much is the path to it?**

For the 19 countries with both, the dataset supports that comparison directly.
For the 180 with only a nearest probe, the row is labelled `vantage_class =
nearest` and can never be mistaken for a domestic measurement.

#### What the nearest class actually measures

It is the correct data for questions about cross-border access:

- Does a government portal serve foreign clients at all?
- Does it geo-block, and with what status code?
- How much latency does distance add?
- Do CDN and edge configurations differ for foreign traffic?

These are real research questions, and the nearest probe answers them honestly.

#### Running it

```bash
VULTR_API_KEY=... python scripts/measure_nearest.py --per-country 10
```

Countries are grouped by the probe region that will measure them, so one
instance serves many countries rather than one instance per country. A batch of
180 countries across 20 regions costs roughly $0.14.

---

## 9. DataHub KGP Dataset Release

Every release generated by `services/analytics/exporter.py` produces:
1. **`civicweb_observatory_vX.Y.Z.parquet`**: Columnar dataset ready for high-performance SQL, Pandas, Polars, DuckDB queries.
2. **`civicweb_observatory_vX.Y.Z.jsonl`**: Complete hierarchical records with full nested measurements.
3. **`coverage_audit_vX.Y.Z.json`**: Section 8 coverage report logging verified, observed, unavailable, and restricted percentages.
4. **`manifest_vX.Y.Z.json`**: Dataset provenance, versioning metadata, and citation references.

---

## 10. Ethical & Responsible Crawling Guarantee

CivicWeb Observatory adheres to strict responsible crawling standards:
- $\le 1.0\text{ req/sec}$ per domain with exponential backoff on 429/5xx status codes.
- Concurrency strictly locked to 1 per domain.
- `robots.txt` exclusion honored across all domains.
- **Zero intrusive actions**: Prohibits form submissions, account registrations, OTP generation, payment gateways, and authentication bypass.

---

## 11. License & Citation

Distributed under the **Creative Commons Attribution 4.0 International (CC-BY-4.0)** License.

```bibtex
@misc{civicweb_observatory_2026,
  title={CivicWeb Observatory: Agentic, Longitudinal Observatory of India's Government Web Infrastructure},
  author={CivicWeb Observatory Research Team},
  year={2026},
  howpublished={\url{https://datahub.kgp/civicweb-observatory}},
  note={DataHub KGP Research Dataset}
}
```
