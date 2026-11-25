# CivicWeb Observatory
### A Cross-Country Measurement of Public-Sector Web Infrastructure

[![License](https://img.shields.io/badge/License-CC--BY--4.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Architecture](https://img.shields.io/badge/Architecture-Hybrid%20Agentic%20%2B%20Deterministic-green.svg)](#3-system-architecture)
[![Target Platform](https://img.shields.io/badge/Target-DataHub%20KGP-orange.svg)](#9-datahub-kgp-dataset-release)
[![Live Observatory](https://img.shields.io/badge/Live%20Observatory-uniquepratham.github.io-1f6feb.svg)](https://uniquepratham.github.io/)

**CivicWeb Observatory** measures the publicly observable web infrastructure of
governments across **82 countries**: **2,011 domains**, each carrying the vantage
point that produced it. A cloud provider operates in only 20 countries, so a
domestic probe is impossible in most of the world. Rather than exclude those
countries or pretend a foreign probe is domestic, every row records
`domestic_probe` — true only when the probe's region country equals the target
country.

**Live observatory:** <https://uniquepratham.github.io/>

---

## Install the dataset

The measurement table ships as a pip-installable package, so a reader can query
it without cloning the repo:

```bash
pip install civicweb-observatory
```

```python
import civicweb_observatory as cwo

df = cwo.load()                    # 2,011 measured domains, 26 typed columns
live = cwo.load(reachable=True)    # the 573 that answered

cwo.country_summary()              # one row per country
cwo.sector_summary()               # one row per sector
cwo.vantage_comparison()           # domestic vs nearest
cwo.architecture_summary()         # per-platform comparison
```

A CLI ships with it:

```bash
civicweb info
civicweb countries --top 10
civicweb sectors
civicweb vantage
civicweb arch
civicweb query --country NL --min-maturity 80
civicweb export --format csv --out measurements.csv --reachable-only
```

The package lives at [`packages/civicweb-observatory/`](packages/civicweb-observatory)
and bundles the Parquet release. Its 18 tests assert the published figures, so a
loader regression fails loudly rather than silently changing a paper table.

---

## 1. Core Research Question

> **What is the measurable state of public-sector web infrastructure across
> countries, how does it differ by sector and platform, and how much of a
> measured difference is the portal rather than the path to it?**

The second half of that question is the contribution. A study that measures only
from inside a country, or only from outside, cannot separate the two.

---

## 2. The Measurement Dimensions

Rather than treating digital accessibility in isolation, CivicWeb Observatory
captures five pillars across twelve variables, with SHA-256 provenance on every
raw response:

| # | Pillar | Deterministic measurement signals | Tool |
|---|---|---|---|
| **1** | **Accessibility** | axe-core violation count and severity-weighted index, missing alt text, ARIA attributes, colour contrast, form labels | axe-core 4.x |
| **2** | **Performance** | Time to first byte, estimated Largest Contentful Paint, document size | `time.perf_counter` |
| **3** | **Security** | HTTPS enforcement, real TLS handshake (issuer, protocol, cipher, days to expiry), OWASP header score (HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy) | `ssl`, response headers |
| **4** | **Inclusion** | Non-English `html[lang]`, `hreflang` alternates, non-Latin script detection, responsive viewport, 375 px render without horizontal overflow | DOM inspection, headless Chromium |
| **5** | **Architecture** | CMS and framework fingerprints, citizen-service affordances (search input, grievance link) | body and header markers |

Every row also carries its **provenance**: `probe_country`, `probe_region`,
`probe_region_country`, `domestic_probe`, `measured_at`, `job_id`, and the
SHA-256 of the response body.

---

## 3. System Architecture

CivicWeb Observatory uses a **5-layer hybrid architecture** that strictly separates adaptive AI reasoning from deterministic network measurements:

```
                  Government Domain Registry (93,365 domains, 93 countries)
                                       │
                                       ▼
                       Discovery & Verification Engine
              (Certificate Transparency, agency directories,
                    ministry indexes, sector-targeted CT)
                                       │
                                       ▼
                 ┌───────────────────────────────────────────┐
                 │          Safety Governor (Hard Wall)      │
                 │  - Concurrency = 1/domain                 │
                 │  - Rate Limit <= 1 req/sec/domain         │
                 │  - RFC 9309 robots.txt compliance         │
                 │  - Prohibited: Form submissions, Auth, Pay│
                 └─────────────────────┬─────────────────────┘
                                       │
                                       ▼
                      Vantage Selector (haversine)
              domestic region if one exists, else nearest
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
        Deterministic Auditors                       Headless Browser Pool
   (axe-core, TLS, OWASP headers)                  (Playwright Chromium, 375px)
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

## 4. Hardware

The measurement worker runs on a single small instance. A `vc2-1c-1gb` at
$0.007/hour is enough for Chromium plus the auditors, and the whole 82-country
run cost under a dollar because each probe is destroyed after it uploads its
results.

- **Workers**: 4–6 parallel domain workers per probe, one request per second per host.
- **Storage**: results are uploaded and SHA-256 verified, then the instance is destroyed.
- **No database, no object store, no local model.** The worker writes a CSV.

---

## 5. Quickstart & Local Setup

### Prerequisites
- Python 3.10+
- Playwright Chromium (for the accessibility and mobile measurements)

### Installation
```bash
git clone https://github.com/UniquePratham/DA-Project civicweb-observatory
cd civicweb-observatory

pip install -r requirements.txt
playwright install chromium
```

### Running the test suite
```bash
# 86 repo tests plus 18 package tests
pytest tests/ -q
PYTHONPATH=packages/civicweb-observatory/src pytest packages/civicweb-observatory/tests -q
```

### Rebuilding the artefacts
```bash
python scripts/build_global_data.py      # dashboard/static/global.js
python scripts/build_world_coverage.py   # dashboard/static/world.js
python scripts/build_world_map.py        # dashboard/static/world_map.js
python scripts/build_dashboard_dataset.py
python scripts/build_package_data.py     # bundled Parquet
python scripts/build_deck.py             # deck HTML + PDF
python scripts/render_paper.py           # paper HTML + PDF
```

### Verifying the figures
```bash
python scripts/verify_paper_figures.py   # every number quoted in the paper
```

---

## 7. Deployment

The observatory is a static site. It is published to GitHub Pages by
`.github/workflows/pages.yml` on every push to `main`:

```bash
git push origin main
# .github/workflows/pages.yml builds and publishes dashboard/
```

Live at <https://uniquepratham.github.io/>.

The dashboard reads its data from JS globals (`window.RAW_DATASET`,
`window.GLOBAL_DATA`, `window.WORLD_DATA`, `window.WORLD_MAP`) rather than
`fetch()`, so it also works when opened directly as a `file:///` URL with no
server and no CORS problem.

---

## 8. Ephemeral Infrastructure and Global Expansion

The registry covers 93 countries. Measurement runs from the best vantage
available for each, using the same tools and timeouts so the comparison is like
for like.

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

Every country is classified by the vantage that can measure it:

- **domestic** — a cloud region physically inside the country exists. Supports a
  citizen's-eye claim.
- **nearest** — no domestic region, but a region close enough that the
  measurement is meaningful. Supports a foreign-client claim, and is the only
  honest way to cover these countries with one provider.
- **unmeasurable** — the nearest region is more than 6,000 km away, so a latency
  figure would describe the path rather than the portal.

Coverage is derived from the live Vultr catalogue, not from a hand-written list:

```bash
export VULTR_API_KEY=...          # never commit this
python scripts/fetch_vultr_catalog.py
python scripts/build_world_coverage.py
python scripts/build_world_map.py
```

Current state: **249 countries** classified — **19** domestic, **180** nearest,
**50** unmeasurable. Of the 180 nearest, **64** were measured in this release.

### 8.4 Cost

A 15-minute batch is billed at Vultr's one-hour minimum, so the cost per batch
equals the hourly rate. The cheapest plan that can run headless Chromium
(1 GB RAM) is `vc2-1c-1gb` at **$0.007 per batch**. Storage, snapshots,
bandwidth overage and backups are modelled separately in `cost.py` because
destroying an instance does not make every associated charge disappear.

### 8.5 The World view

The World tab is the primary geographic view: a 249-country map coloured by
vantage class, a country dossier, and a full country ranking. India is one row
in that ranking rather than the subject of the page.

The map is built once and wired once. Re-rendering on every filter click would
destroy focus and accumulate listeners. The selection outline is a separate
`<path>` drawn last, so it is never clipped by a neighbouring polygon. Every
country is keyboard accessible. Countries the 110m topology does not draw
(Singapore, Hong Kong, Macau, Bahrain, Mauritius and 27 other small states) get a
centroid marker, so a measured country is never invisible.

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
`crawl_real.py` the global run uses, runs a real batch, pulls the results back,
and verifies the SHA-256 before destroying the instance.

A real run on 2026-11-18, measuring three government domains from a Bangalore
probe:

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
the one the global run uses, which is what makes a measurement on an ephemeral
probe comparable to one on the permanent node.


### 8.10 Cross-country measurements

`scripts/run_global_batch.py` provisions one probe per country, measures a small
comparable sample of national portals, and appends the results to
`data/real/global_measurements.csv` with full provenance.

Every row records `probe_country`, `probe_region`, `probe_region_country` and
`domestic_probe`. A row is only marked domestic when the probe's region country
equals the target country, so the claim can be checked rather than trusted.

**The first domestic batch: 18 countries, 72 domains, $0.126 total.** These are
the pilot figures from that run; the released dataset has since grown to 2,011
domains across 82 countries.

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
comparability check, not a census. The released dataset is the larger sample:
2,011 domains, 82 countries, 573 reachable.


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

Measured breakdown across **2,011 domains**:

| Sector | Domains | Reachable | Accessibility | Security |
| :--- | ---: | ---: | ---: | ---: |
| general | 1,354 | 29.0% | 86.4 | 44.9 |
| education | 420 | 30.7% | 85.2 | **26.6** |
| judiciary | 62 | 38.7% | 81.8 | 34.6 |
| health | 62 | 19.4% | 88.1 | 50.4 |
| transport | 41 | 22.0% | not reported | not reported |
| finance | 29 | 10.3% | not reported | not reported |
| police | 16 | 6.2% | not reported | not reported |
| social | 11 | 18.2% | not reported | not reported |
| agriculture | 9 | 0.0% | not measured | not measured |
| defence | 6 | 0.0% | not measured | not measured |
| environment | 1 | 0.0% | not measured | not measured |

A sector mean is reported only when at least ten of its domains answered.
Below that the mean is one or two portals wearing a sector label, which is not a
sector finding. Those rows show "not reported" rather than a number.

Three findings:

1. **Health scores highest on both pillars** at 88.1 accessibility and 50.4
   security, the only sector above the population mean on both.
2. **Education scores worst on security (26.6)** across 420 domains, the
   largest single-sector deficit in the study.
3. **The judiciary is weakest on accessibility (81.8)** and second-weakest on
   security (34.6). Courts are the one sector near the bottom of both at once.

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
- `robots.txt` exclusion honored across all domains, using an RFC 9309 parser
  (Python's `urllib.robotparser` does not implement `*` wildcards or `$` anchors).
- A robots-disallowed URL is recorded as `robots_disallowed` and a bot-filter
  refusal as `blocked_by_waf`, both distinct from a failure. In this release,
  76 domains were robots-disallowed and 46 were WAF-blocked.
- **Zero intrusive actions**: Prohibits form submissions, account registrations, OTP generation, payment gateways, and authentication bypass.

---

## 11. License & Citation

Distributed under the **Creative Commons Attribution 4.0 International (CC-BY-4.0)** License.

```bibtex
@misc{civicweb_observatory_2026,
  title={CivicWeb Observatory: A Cross-Country Measurement of Public-Sector Web Infrastructure},
  author={Agarwal, Pratham and Bairagi, Amit Kumar and Yaduraj, Vishwajeet Nand},
  year={2026},
  howpublished={\url{https://uniquepratham.github.io/}},
  note={Department of Computer Science and Engineering, IIT Kharagpur. Data Analytics.}
}
```
