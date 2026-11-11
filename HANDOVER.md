# BharatGov Access — Agent Handover Document
**Project Domain:** National Government Web Infrastructure Observatory & Academic Benchmark  
**Institution:** Department of Data Analytics, Indian Institute of Technology Kharagpur (Group 12)  
**Authors:** Pratham Agarwal, Amit Kumar Bairagi, Vishwajeet Nand Yaduraj  
**Target Publication Venues:** ACM COMPASS / IEEE Internet Computing / Government Information Quarterly (GIQ)  
**Date:** November 2026 | Checkpoint 2 Review Ready  

---

## 1. Executive Summary & Purpose

This document provides a complete operational and technical handover for an incoming AI agent or developer continuing work on **BharatGov Access**. 

BharatGov Access is the first census-scale, longitudinal web observatory evaluating India's public digital infrastructure across **12,092 government web domains**. The platform resolves the historical **Geo-IP perimeter firewall blindspot** (which caused &gt;66% false-positive reachability failures when measured from overseas cloud vantage points) by executing ingestion within the Indian domestic peering fabric.

The project currently encompasses:
1. **A verified 12,092-portal census dataset** in Parquet, CSV, JSON, and bundled JS formats.
2. **A production holographic web dashboard** with interactive India Geo-Map, live telemetry, and zero horizontal scrollbar overflow.
3. **A publication-ready academic paper** (Markdown, LaTeX, and compiled IEEE 2-column PDF).
4. **A 6-slide academic presentation** in PPTX and vector 16:9 PDF formats.
5. **A live in-country deployment** accessible via Cloudflare tunnel.

---

## 2. Verified Census Scale & Dataset Architecture

### A. Governance Tiers Breakdown (Total N = 12,092)
The observatory categorizes sovereign Indian digital public infrastructure into 7 non-overlapping tiers:

| Administrative Governance Tier | Registered Census | Active Audited (%) | Inactive / Deprecated | Mean WCAG Acc. | GIGW Toolbar |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Central Ministries & Commissions** | 645 | 532 (82.5%) | 113 | 90.8 / 100 | 88.2% |
| **State Departments (36 States/UTs)** | 2,935 | 2,017 (68.7%) | 918 | 92.0 / 100 | 88.3% |
| **District Administrations (All 788 Districts)** | 7,468 | 6,716 (89.9%) | 752 | **95.0 / 100** | 94.7% |
| **Higher Education & Research (IITs, NITs)** | 352 | 342 (97.2%) | 10 | 91.6 / 100 | 71.1% |
| **Judiciary & Courts (High Courts, Tribunals)** | 292 | 271 (92.8%) | 21 | 91.0 / 100 | 78.2% |
| **Public Sector Enterprises & Banks** | 260 | 247 (95.0%) | 13 | 91.8 / 100 | 66.8% |
| **Urban Local Bodies (Municipalities)** | 140 | 122 (87.1%) | 18 | 90.1 / 100 | 80.3% |
| **National Total / Baseline** | **12,092** | **10,247 (84.7%)** | **1,845 (15.3%)** | **93.8 / 100** | **91.0%** |

> These figures are computed from `resources/bharatgov_access_clean.parquet` over reachable portals only. Reproduce with `bharatgov tiers` (see §4).

### B. Storage Files & Data Formats
All dataset artifacts are stored in the `resources/` directory and synchronized with `dashboard/static/`:
* `resources/bharatgov_access_clean.parquet` — High-efficiency Apache Parquet format (columnar, compressed with snappy).
* `resources/bharatgov_access_clean.csv` — Standard CSV file (12,092 rows, 20 clean columns).
* `resources/bharatgov_access_clean.json` — Structured JSON export for external APIs.
* `dashboard/static/dataset.json` — Compact JSON for the live HTTP web dashboard.
* `dashboard/static/dataset.js` — **Critical Local File Bundle:** Declares `window.RAW_DATASET = [...]` so that `dashboard/index.html` loads all 12,092 rows with **zero CORS issues** when opened directly as a `file:///` URL in Windows Explorer.
* `dashboard/static/india_map.js` — Generated state boundaries (36 States/UTs, 41 KB) for the atlas choropleth. Rebuild with `python scripts/build_india_map.py`.
* `dashboard/static/fonts/` — Self-hosted Newsreader, Public Sans and IBM Plex Mono woff2 subsets, so the dashboard renders identically offline. Refresh with `python scripts/fetch_fonts.py`.

### C. Installable Python Package
The census ships as a pip-installable package at `packages/bharatgov-access/`:

```bash
pip install bharatgov-access          # from PyPI, once published
pip install -e packages/bharatgov-access   # from this repo
```

```python
import bharatgov_access as bga

bga.load()                  # 12,092 domains, 20 typed columns
bga.load(reachable=True)    # 10,247 that answered in-country
bga.tier_summary()          # Table I of the paper
bga.architecture_summary()  # Table II of the paper
bga.state_ranking()         # 36 States and UTs, ranked
bga.maturity_index(...)     # recompute the composite for your own portal
```

A CLI ships with it: `bharatgov info | tiers | arch | states | query | export`.
The package bundles the Parquet release (465 KB wheel) and carries 14 tests that
assert the published figures, so a loader regression fails loudly instead of
silently changing a paper table.

---

## 3. The 5-Pillar / 10-Sub-Feature Evaluation Standard

To prevent "metric bloat" (which previously had 70+ uncalibrated columns), the project enforces exactly **5 orthogonal pillars and 10 defensible sub-features**:

```
                    ┌────────────────────────────────────────────────────────┐
                    │               BharatGov Access Framework               │
                    └───────────────────────────┬────────────────────────────┘
                                                │
         ┌──────────────┬───────────────────────┼───────────────────────┬──────────────┐
         ▼              ▼                       ▼                       ▼              ▼
   ┌───────────┐  ┌───────────┐           ┌───────────┐           ┌───────────┐  ┌───────────┐
   │ Pillar 1: │  │ Pillar 2: │           │ Pillar 3: │           │ Pillar 4: │  │ Pillar 5: │
   │ Accessi-  │  │  Perform- │           │ Security  │           │ Inclusiv- │  │  Arch &   │
   │  bility   │  │   ance    │           │ & Crypto  │           │    ity    │  │ Services  │
   │(WCAG/GIGW)│  │ (CWV RTT) │           │ (CERT-In) │           │(Languages)│  │ (S3WaaS)  │
   └─────┬─────┘  └─────┬─────┘           └─────┬─────┘           └─────┬─────┘  └─────┬─────┘
         │              │                       │                       │              │
    ┌────┴────┐    ┌────┴────┐             ┌────┴────┐             ┌────┴────┐    ┌────┴────┐
    │Acc Score│    │TTFB (ms)│             │TLS/HTTPS│             │Multiling│    │S3WaaS CMS
    │Toolbar  │    │Est. LCP │             │Sec Head.│             │Viewport │    │Grievance│
    └─────────┘    └─────────┘             └─────────┘             └─────────┘    └─────────┘
```

1. **Pillar 1: Accessibility & Usability (WCAG 2.1 AA / GIGW 3.0)**
   * `sub_accessibility_score`: $0 \le S_{\text{acc}} \le 100$ based on image `alt` attributes, form `<label>`, `lang` tag, and skip links.
   * `sub_has_gigw_toolbar`: Boolean indicator for font resizing ($A+/A-$), high-contrast toggle, and screen-reader skip links.
2. **Pillar 2: Performance & Network Latency (Core Web Vitals)**
   * `sub_response_latency_ms`: Round-Trip Time / Time to First Byte (TTFB) in milliseconds over domestic peering.
   * `sub_lcp_est_sec`: Estimated Largest Contentful Paint derived from $T_{\text{lcp}} = \max(0.60, 1.30 \cdot \frac{\text{TTFB}}{1000} + \frac{\text{DOM Size}}{180})$.
3. **Pillar 3: Security & Cryptography (CERT-In Hardening)**
   * `sub_https_enforced`: Canonical HTTPS transport upgrade verification (Boolean).
   * `sub_security_headers_score`: Hardening score assessing HSTS ($25\text{pt}$), CSP ($15\text{pt}$), `X-Content-Type-Options` ($10\text{pt}$), and `X-Frame-Options` ($10\text{pt}$).
4. **Pillar 4: Linguistic & Mobile Inclusivity (Digital India Reach)**
   * `sub_is_multilingual`: Presence of India's 22 Eighth Schedule languages (Devanagari/Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, etc.).
   * `sub_mobile_responsive`: Standard mobile viewport configuration (`width=device-width, initial-scale=1.0`).
5. **Pillar 5: Architecture & Citizen Interactivity**
   * `sub_cms_architecture`: Categorical stack classification (`s3waas_drupal`, `custom_dynamic_cms`, `legacy_asp_net`, `modern_spa`, `wordpress`).
   * `sub_has_citizen_services`: Native search utilities and public grievance redressal integration (CPGRAMS, Samadhan, Jan Sunwai).
6. **Composite Maturity Index ($0 \le M \le 100$):**
   $$M = 0.30 S_{\text{acc}} + 0.25 S_{\text{sec}} + 0.20 \max(0, 100 - 15 T_{\text{lcp}}) + 10 I_{\text{multi}} + 5 I_{\text{mobile}} + 5 I_{\text{services}} + 5 \mathbb{I}(\text{S3WaaS})$$

---

## 4. Web Dashboard Architecture & Design Decisions

The dashboard was rebuilt as a printed statistical bulletin rather than a SaaS
product. The design language borrows from census atlases and government
bulletins: warm paper, hairline rules, one oxide accent, tabular figures, and
real geography. There are no gradients on surfaces, no glass panels, no glow, no
emoji, and no icon library mixed with a second icon library.

### A. File Layout

| File | Role |
| :--- | :--- |
| `dashboard/index.html` | Semantic markup only. No inline styles beyond a few layout utilities. |
| `dashboard/static/app.css` | Design tokens (OKLCH), type scale, layout, print stylesheet. |
| `dashboard/static/app.js` | Data engine, SVG chart renderers, atlas, ledger, palette, theme. |
| `dashboard/static/dataset.js` | `window.RAW_DATASET` bundle for zero-CORS `file://` loading. |
| `dashboard/static/india_map.js` | Generated state boundaries for the atlas. |
| `dashboard/static/fonts/` | Self-hosted woff2 subsets. |
| `dashboard/static/logo-mark.svg` | The Gateway / Datum mark. |
| `dashboard/static/favicon.svg` | Favicon tile. |

### B. Design System

* **Palette.** OKLCH tokens on a warm paper ground (`--paper`), warm near-black
  ink (`--ink` through `--ink-4`), and a single oxide accent (`--oxide`). A
  five-step sequential ramp (`--data-1` … `--data-5`) carries the choropleth.
  Contrast is verified: body 14.6:1, secondary 8.4:1, tertiary 5.5:1, quaternary
  3.7:1 against paper, in both themes.
* **Typography.** Newsreader (display), Public Sans (UI), IBM Plex Mono
  (figures). Three faces, each with a job. Headings are roman; italic is reserved
  for body-copy emphasis.
* **Light and dark.** An explicit segmented control in the rail, not a mystery
  icon. The choice persists in `localStorage`; the OS preference is followed only
  until the reader makes an explicit choice. `t` toggles from the keyboard.
* **No horizontal scroll.** `overflow-x: clip` on `html` and `body`, verified at
  320 / 375 / 414 / 768 / 1024 / 1280 / 1600 px across all five views.

### C. Five Views

1. **Overview** — headline band, five computed findings, tier maturity bars,
   LCP and TTFB distributions, security and platform charts, pillar coverage
   matrix.
2. **Atlas** — real Census state boundaries as a choropleth, a state dossier
   with meters, and a full 36-row ranking.
3. **Ledger** — the full census with search, tier and status filters, six sort
   orders, pagination, and CSV export.
4. **Standard** — the five pillars with live values, the composite formula, and
   the 20-column schema.
5. **Method** — vantage-point rationale, a reproduction snippet, and four
   documented limits.

### D. Data Integrity

Every figure is computed in the browser from `dataset.js` at load time. Nothing
is hardcoded. `scripts/verify_dashboard.py` recomputes the same figures
independently from `resources/bharatgov_access_clean.csv` with pandas and
compares them against the rendered DOM: **419 assertions across layout, data,
behaviour and accessibility**, all passing.

### E. Accessibility

Landmarks, a skip link, `role="tablist"` with arrow-key navigation, labelled
controls, `aria-label` on every SVG, visible focus rings, and WCAG AA contrast in
both themes. Verified by the `a11y` suite.

---

## 5. Academic Deliverables & Research Artifacts

1. **Academic Research Paper (submission ready):**
   * Markdown source of truth: `research_paper/BharatGov_Access_Research_Paper.md`
   * Rendered HTML: `research_paper/BharatGov_Access_Research_Paper.html`
   * Compiled PDF: `research_paper/BharatGov_Access_Research_Paper.pdf`
   * LaTeX: `research_paper/BharatGov_Access_Research_Paper.tex`
   * Regenerate with `python scripts/render_paper.py`. The Markdown is the single
     source; the HTML and PDF are derived, so a table correction propagates.
   * **Tables I and II were corrected against the released dataset.** An earlier
     draft carried figures that did not match the Parquet release (for example a
     96.1 district accessibility mean where the data says 95.0, and per-header
     HSTS/CSP percentages that the 20-column schema does not record). Every
     number in the paper is now reproducible with `bharatgov tiers` and
     `bharatgov arch`.
2. **Final Evaluation Deck (5 widescreen slides):**
   * PDF: `resources/BharatGov_Access_Final_Deck.pdf`
   * HTML: `resources/BharatGov_Access_Final_Deck.html`
   * Regenerate with `python scripts/build_deck.py`. Every number on a slide is
     computed from the dataset, and the screenshots come from
     `python scripts/capture_screenshots.py`.
3. **Screenshots:** `resources/screenshots/` — five views in light and dark, a
   full-page overview, and a mobile proof shot.

---

## 6. Live Cloud Deployment & Infrastructure

The observatory is hosted twice, from the same `dashboard/` source. Both hosts
serve the identical static build; neither needs a build step.

### A. Primary — GitHub Pages (permanent, no tunnel)

* **URL:** `https://uniquepratham.github.io/` (Status: HTTP 200 OK)
* **Source:** the `dashboard/` directory of this repository, published by
  `.github/workflows/pages.yml`.
* **Why this is primary:** GitHub Pages is permanent, HTTPS-enforced, and has no
  process to keep alive. A Quick Tunnel URL changes every time `cloudflared`
  restarts, so it cannot be printed on a slide or a paper.
* **Deploy:** push to `main`. The workflow copies `dashboard/` to `_site/`,
  drops the Flask dev server, writes `.nojekyll`, asserts the critical assets
  exist, and publishes. A failed asset assertion fails the build rather than
  shipping an unstyled page.
* **Verify:** `python scripts/verify_dashboard.py` runs against the local file;
  the live host is checked with the same assertions in a browser.

### B. Secondary — Cloudflare Tunnel on the Vultr node

* **Cloud Node:** Deployed domestically inside India (Ubuntu 22.04 LTS, 6 vCPUs, 60 GB RAM, 350 GB NVMe).
* **Remote Path:** `/opt/bharatgov-bangalore/dashboard/`
* **Live Tunnel:** Cloudflare Quick Tunnel
  **URL:** `https://weeks-privacy-transcription-improved.trycloudflare.com` (Status: HTTP 200 OK)
* **Supervision:** two systemd units, both `enabled` and `active`:
  * `bharatgov-dashboard.service` — `python3 -m http.server 8088 --bind 127.0.0.1`
  * `bharatgov-tunnel.service` — `cloudflared tunnel --url http://127.0.0.1:8088`
  Both restart on failure and start on boot. The origin binds to loopback only,
  so the tunnel is the sole ingress.
* **Caveat:** a Quick Tunnel hostname is ephemeral. It changes when the tunnel
  restarts, so treat the GitHub Pages URL as the citable one. A stable
  `access.<domain>` hostname requires a Cloudflare-managed zone plus a named
  tunnel (`cloudflared tunnel create` + `cloudflared tunnel route dns`), which
  needs account credentials that are deliberately not stored in this repository.
* **File Sync Workflow:** Files are synchronized from local to remote via Paramiko SFTP. Temporary sync scripts must be deleted immediately after execution and never committed to Git.
* **Deploying the rebuilt dashboard:** the new dashboard is fully static and needs no build step. Upload `dashboard/index.html` plus the whole `dashboard/static/` directory (including `fonts/`, `india_map.js`, `app.css`, `app.js`, `logo-mark.svg`, `favicon.svg`). The old single-file dashboard had no external assets; this one does, so a partial upload will render unstyled.

---

## 7. Strict Operating Guidelines for the Incoming Agent

> [!CAUTION]
> **CRITICAL SECURITY REQUIREMENT: ZERO CREDENTIALS IN GIT**  
> Never stage, commit, or push any server passwords, root credentials, private SSH keys, or server IP addresses to the Git repository. An automated pre-commit scan is in place:
> ```powershell
> python -c "forbidden=['<ROOT_PASSWORD>','<SERVER_IP>']; ..."
> ```
> Always ensure `git status` shows a clean tree before pushing.

> [!IMPORTANT]
> **SOVEREIGN NATIONAL BRANDING ONLY**  
> Do **NOT** reintroduce localized city names (e.g., "Bangalore Node", "Bangalore Latency"). Use sovereign, national terminology:  
> * `"National Egress Peering"`  
> * `"Domestic Peering Fabric"`  
> * `"National Web Infrastructure Observatory"`  
> * `"National Gateway"`

> [!NOTE]
> **NO ARBITRARY VERSION LABELS**  
> Do **NOT** add "v3.0", "Version 3.0", or "Checkpoint 2" in user-facing production UI titles. The observatory represents the live national monitoring system.

> [!TIP]
> **MAINTAIN DUAL DATA LOADING**  
> Whenever regenerating or updating the census dataset, always update both `dashboard/static/dataset.json` AND `dashboard/static/dataset.js` so that local `file:///` browsing works out of the box without requiring a web server.

