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
| **Central Ministries & Commissions** | 645 | 622 (96.4%) | 23 | 92.0 / 100 | 78.4% |
| **State Departments (36 States/UTs)** | 2,935 | 2,758 (94.0%) | 177 | 93.2 / 100 | 84.2% |
| **District Administrations (All 788 Districts)** | 7,468 | 6,180 (82.8%) | 1,288 | **96.1 / 100** | **98.2%** |
| **Higher Education & Research (IITs, NITs)** | 352 | 344 (97.7%) | 8 | 91.5 / 100 | 74.0% |
| **Judiciary & Courts (High Courts, Tribunals)** | 292 | 278 (95.2%) | 14 | 92.0 / 100 | 92.0% |
| **Public Sector Enterprises & Banks** | 260 | 255 (98.1%) | 5 | 90.5 / 100 | 65.0% |
| **Urban Local Bodies (Municipalities)** | 140 | 128 (91.4%) | 12 | 89.0 / 100 | 70.0% |
| **National Total / Baseline** | **12,092** | **10,247 (84.7%)** | **1,845 (15.3%)** | **93.8 / 100** | **91.0%** |

### B. Storage Files & Data Formats
All dataset artifacts are stored in the `resources/` directory and synchronized with `dashboard/static/`:
* `resources/bharatgov_access_clean.parquet` — High-efficiency Apache Parquet format (columnar, compressed with snappy).
* `resources/bharatgov_access_clean.csv` — Standard CSV file (12,092 rows, 20 clean columns).
* `resources/bharatgov_access_clean.json` — Structured JSON export for external APIs.
* `dashboard/static/dataset.json` — Compact JSON for the live HTTP web dashboard.
* `dashboard/static/dataset.js` — **Critical Local File Bundle:** Declares `window.RAW_DATASET = [...]` so that `dashboard/index.html` loads all 12,092 rows with **zero CORS issues** when opened directly as a `file:///` URL in Windows Explorer.

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

### A. Core File: `dashboard/index.html`
* **Zero Horizontal Scrollbar Lockdown:** The document strictly enforces:
  ```css
  html, body {
    width: 100%;
    max-width: 100vw;
    overflow-x: hidden !important;
  }
  ::-webkit-scrollbar:horizontal {
    display: none !important;
    height: 0px !important;
  }
  ```
* **Dual Ingestion Mode (Offline `file:///` + Live HTTP):**
  Loads `static/dataset.js` via `<script>`. If `window.RAW_DATASET` is available in memory, it uses it immediately; otherwise, it falls back to `fetch('static/dataset.json')`. This prevents Chrome/Edge CORS errors when opened from local disk.
* **Six Structured Views:**
  1. `📊 Benchmarks` — Executive scorecards, 5-Pillar Spider Radar, State Maturity index, CMS architecture doughnut, CWV LCP breakdown, CERT-In security header stats.
  2. `🗺️ India Geo-Map` — Interactive Vector SVG topological network connecting the Central National Gateway to 20 key state nodes with animated radar beams. Clicking any node updates the **Node Telemetry Inspector** with real data.
  3. `🏛️ State Scorecards` — Interactive dropdown for all 36 States/UTs displaying citizen utility penetration and actionable GIGW modernization blueprints.
  4. `🛡️ 5-Pillar Standards` — Clear explanation of the research methodology and scoring formulas.
  5. `📋 National Registry` — High-performance table with search, tier filter, status filter, CSV export, and pagination across 12,092 records.
  6. `📖 Guide` — Python quickstart script using Pandas/PyArrow and complete 20-column data dictionary.
* **SVG Hover Fix:** State nodes use pure SVG stroke/fill transitions on hover instead of CSS `transform: scale()`, permanently eliminating the cursor jitter/flicker issue.

---

## 5. Academic Deliverables & Research Artifacts

1. **Academic Research Paper (Submission Ready):**
   * Markdown: `research_paper/BharatGov_Access_Research_Paper.md` (10-page comprehensive paper, mathematical formulations, Tables I & II, 10 formal academic citations).
   * LaTeX: `research_paper/BharatGov_Access_Research_Paper.tex` (IEEE conference format).
   * Compiled PDF: `research_paper/BharatGov_Access_Research_Paper.pdf` (Rendered using Playwright into a two-column IEEE format).
2. **Academic Presentation (6 Widescreen Slides):**
   * PowerPoint: `resources/DA Check 02.pptx` and `resources/BharatGov_Access_Checkpoint_2_Presentation.pptx`.
   * Vector 16:9 PDF: `resources/BharatGov.pdf`.
   * HTML Deck: `resources/checkpoint_2_presentation.html`.

---

## 6. Live Cloud Deployment & Infrastructure

* **Cloud Node:** Deployed domestically inside India (Ubuntu 22.04 LTS, 6 vCPUs, 60 GB RAM, 350 GB NVMe).
* **Remote Path:** `/opt/bharatgov-bangalore/dashboard/`
* **Daemon Process:** `python3 -m http.server 8088`
* **Live Tunnel:** Cloudflare Quick Tunnel  
  **URL:** `https://quality-ampland-ashley-ought.trycloudflare.com` (Status: HTTP 200 OK)
* **File Sync Workflow:** Files are synchronized from local to remote via Paramiko SFTP. Temporary sync scripts must be deleted immediately after execution and never committed to Git.

---

## 7. Strict Operating Guidelines for the Incoming Agent

> [!CAUTION]
> **CRITICAL SECURITY REQUIREMENT: ZERO CREDENTIALS IN GIT**  
> Never stage, commit, or push any server passwords, root credentials, private SSH keys, or server IP addresses to the Git repository. An automated pre-commit scan is in place:
> ```powershell
> python -c "forbidden=['REDACTED_ROTATE_THIS_PASSWORD','REDACTED_SERVER_IP']; ..."
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
