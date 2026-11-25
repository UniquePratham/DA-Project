# CivicWeb Observatory — Handover Document

**Project:** A cross-country measurement of public-sector web infrastructure
**Institution:** Department of Computer Science and Engineering, Indian Institute of Technology Kharagpur (Group 12)
**Subject:** Data Analytics
**Authors:** Pratham Agarwal, Amit Kumar Bairagi, Vishwajeet Nand Yaduraj
**Date:** November 2026

---

## 1. What this project is

CivicWeb Observatory measures the publicly observable web infrastructure of
governments across **82 countries**: **2,011 domains**, each carrying the vantage
point that produced it.

The methodological problem is the point of the project. A cloud provider operates
in only 20 countries, so a domestic probe is impossible in most of the world.
Rather than exclude those countries or pretend a foreign probe is domestic, every
row records `domestic_probe` — true only when the probe's region country equals
the target country. That single column is what makes the paper's main result
possible: the same kind of portal answers in **471 ms** from inside its country
and **1,151 ms** from the nearest foreign region. The **680 ms gap is the cost of
distance, not a difference in the portals.**

---

## 2. The released dataset

### A. Headline figures

| | |
|---|---|
| Domains measured | 2,011 |
| Countries | 82 |
| Reachable | 573 (28.5%) |
| Countries with a reachable domain | 72 |
| Domestic-probe rows | 1,360 across 19 countries |
| Nearest-probe rows | 651 across 64 countries |
| Mean accessibility | 86.1 / 100 |
| Mean security | 40.8 / 100 |
| Mean maturity | 59.0 / 100 |
| Median TTFB | 632 ms |
| HTTPS enforced | 99.8% |
| Multilingual | 41.2% |
| Mobile viewport | 80.3% |
| robots-disallowed | 76 |
| WAF-blocked | 46 |

Reproduce every one of these with:

```bash
python scripts/verify_paper_figures.py
```

### B. The vantage split

| Vantage | Domains | Reach | Accessibility | Security | Maturity | Median TTFB |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| domestic | 1,360 | 29.3% | 87.0 | 44.2 | 61.3 | **479 ms** |
| nearest | 651 | 26.9% | 84.0 | 33.2 | 53.8 | **1,156 ms** |

### C. Sector table

Sector is inferred from the hostname. A sector mean is reported only when at
least ten of its domains answered; below that the mean is one or two portals
wearing a sector label.

| Sector | Domains | Reachable | Accessibility | Security |
| :--- | ---: | ---: | ---: | ---: |
| general | 1,354 | 393 | 86.4 | 44.9 |
| education | 420 | 129 | 85.2 | **26.6** |
| judiciary | 62 | 24 | 81.8 | 34.6 |
| health | 62 | 12 | 88.1 | 50.4 |

Excluded for insufficient reachable domains: transport (41 domains, 9 reachable),
finance (29, 3), social (11, 2), police (16, 1), agriculture (9, 0), defence (6, 0),
environment (1, 0).

### D. Files

| Path | What it is |
| :--- | :--- |
| `data/real/global_measurements_canonical.csv` | **The source of truth.** 2,011 rows, 26 columns, full provenance |
| `data/real/global_measurements.csv` | The append-only raw log. 2,143 rows for 2,011 hosts; never aggregate it directly |
| `dashboard/static/dataset.js` | `window.RAW_DATASET` — per-domain rows for the dashboard |
| `dashboard/static/global.js` | `window.GLOBAL_DATA` — country, sector and vantage aggregates |
| `dashboard/static/world.js` | `window.WORLD_DATA` — 249-country vantage classification |
| `dashboard/static/world_map.js` | `window.WORLD_MAP` — Natural Earth 110m geometry plus centroid markers |
| `packages/civicweb-observatory/src/civicweb_observatory/data/civicweb_observatory_global.parquet` | The bundled release |

The dashboard reads JS globals rather than `fetch()`, so it works from a
`file:///` URL with no server and no CORS problem.

### E. Reading the CSV yourself

Namibia's ISO-3166 alpha-2 code is `NA`, which is also the default missing-value
token in most CSV readers. A default `pandas.read_csv` silently drops all ten
Namibian rows — one whole country, with no error raised. Use:

```python
import pandas as pd
df = pd.read_csv("data/real/global_measurements_canonical.csv", keep_default_na=False, na_values=[""])
```

Or use `scripts/global_dataset.py`, which is the single reader for this file.

---

## 3. The measurement standard

Five pillars, twelve variables, one tool per dimension.

| Pillar | Variables | Tool |
| :--- | :--- | :--- |
| Accessibility | axe-core violation count, severity-weighted index | axe-core 4.x |
| Performance | TTFB, estimated LCP, document size | `time.perf_counter` |
| Security | HTTPS enforcement, TLS handshake, OWASP header score | `ssl`, response headers |
| Inclusion | non-English lang/script, responsive viewport | DOM inspection, 375 px Chromium render |
| Architecture | CMS fingerprint, citizen-service affordances | body and header markers |

The composite index:

$$M = 0.30 S_{\text{axe}} + 0.25 S_{\text{sec}} + 0.20 \max(0, 100 - 15 T_{\text{lcp}}) + 10 I_{\text{multi}} + 5 I_{\text{mobile}} + 5 I_{\text{services}} + 5 \mathbb{I}(A_{\text{cms}} = \text{s3waas})$$

The weights are a judgement, not a finding. Every component is published
separately so a reader can reweight.

---

## 4. The dashboard

Five views, no India-specific content, no "Future" tab.

| View | What it shows |
| :--- | :--- |
| **Overview** | Headline figures, the vantage finding, sector and platform tables |
| **World** | 249-country map coloured by vantage class, country dossier, country ranking |
| **Registry** | Per-domain table with search, status filter and pagination |
| **Standard** | The five-pillar measurement definition and the composite formula |
| **Developers** | Package API, CLI, column dictionary, reproduction commands |

### Map behaviour

- Built once, wired once. Re-rendering on every filter click would destroy focus
  and accumulate listeners.
- Selection outline is a separate `<path>` drawn last, so it is never clipped by
  a neighbouring polygon.
- Keyboard accessible: every country is `tabindex="0"` with `role="button"`, and
  Enter or Space selects it.
- Filtering dims rather than removes, so the map keeps its shape.
- Countries the 110m topology does not draw (Singapore, Hong Kong, Macau,
  Bahrain, Mauritius and 27 other small states) get a centroid marker, so a
  measured country is never invisible.

---

## 5. Reproducing everything

```bash
# Data bundles
python scripts/build_global_data.py
python scripts/build_world_coverage.py
python scripts/build_world_map.py
python scripts/build_dashboard_dataset.py
python scripts/build_package_data.py

# Artefacts
python scripts/capture_screenshots.py
python scripts/build_deck.py
python scripts/render_paper.py

# Verification
python scripts/verify_paper_figures.py
pytest tests/ -q
PYTHONPATH=packages/civicweb-observatory/src pytest packages/civicweb-observatory/tests -q
```

---

## 6. Deployment

Static site, published to GitHub Pages by `.github/workflows/pages.yml` on every
push to `main`.

**Live:** <https://uniquepratham.github.io/>

---

## 7. What this release does not claim

1. **Automated testing is not conformance.** axe-core catches a subset of WCAG
   failures. It cannot judge cognitive load, screen-reader audio flow or reading
   order.
2. **LCP is estimated, never measured.** It is derived from TTFB and payload
   size, not from a browser paint trace.
3. **Nearest probes are not domestic.** 651 of 2,143 rows were measured from a
   probe in another country. Any claim about what a citizen experiences must
   filter on `domestic_probe`.
4. **Discovery is not verification.** A domain in the registry was observed in an
   auditable source; it was not confirmed to be an operating citizen portal,
   which is why reachability is 30.2% rather than near 100%.
5. **One snapshot.** No per-domain timestamp series, so no trend claim.
6. **Sector is inferred from the hostname.** 1,445 of 2,143 rows are `general`,
   so the sector comparison is a comparison of the identifiable subset.
7. **The composite weights are a judgement.** The 30/25/20/10/5/5/5 weighting
   encodes a view, not an empirical result.
8. **The 50 unmeasurable countries are genuinely out of reach** with one
   provider. A latency figure from 4,000 km describes the ocean cable, not the
   portal.
9. **A country code can collide with a missing-value sentinel.** Namibia's `NA`
   is the default missing-value token in most CSV readers. The released reader
   disables the default sentinel list; anyone re-analysing the CSV with a default
   reader will reproduce the bug.

---

## 8. Operating guidelines for the next agent

- **Never fabricate a number.** Every figure in the paper, the deck and the
  dashboard is computed from `data/real/global_measurements_canonical.csv`. If a figure
  cannot be computed, it does not go in the document.
- **Never fill an unmeasured metric with zero.** Unreachable hosts carry `null`
  scores. A zero is a measurement; a null is the absence of one.
- **Never present a foreign probe as domestic.** The rule is enforced in code by
  `domestic_probe`, not asserted in prose.
- **One reader for the CSV.** Use `scripts/global_dataset.py`. A default
  `read_csv` loses Namibia, and the raw log double-counts 128 hosts.
- **One sector classifier.** Use `civicweb_observatory.classify_sector`. The deck
  and the package previously disagreed, which produced two different security
  scores for the same sector.
- **Run the tests before claiming a change works.** 89 repo tests plus 18 package
  tests, `scripts/audit_dataset.py` for the data, and
  `scripts/verify_paper_figures.py` for the paper.
- **No secrets in tracked files.** The Vultr API key is an environment variable
  only. A leaked root password was purged from git history with
  `git-filter-repo`; it still needs rotating on the server.
