# BharatGov Access: A Census-Scale In-Country Web Observatory and Empirical Benchmark of India's Public Digital Infrastructure

**Pratham Agarwal**, **Amit Kumar Bairagi**, and **Vishwajeet Nand Yaduraj**  
*Department of Data Analytics, Indian Institute of Technology Kharagpur, West Bengal 721302, India*  
*Correspondence: `{pratham.agarwal, amit.bairagi, vishwajeet.yaduraj}@iitkgp.ac.in`*

---

## Abstract
Digital Public Infrastructure (DPI) serves as the primary conduit through which the Government of India delivers welfare entitlements, citizen registries, tax filings, and judicial services to over 900 million connected citizens. Despite its systemic societal significance, empirical knowledge of the accessibility, performance, and cryptographic security of India's multi-tiered public web remains scarce, fragmented, and vulnerable to measurement bias. Prior web measurement studies have evaluated narrow samples ($\le 100$ homepages) or relied on overseas cloud vantage points, which we demonstrate trigger false-positive reachability failures exceeding 66% due to domestic perimeter Geo-IP firewalls operated by state gateways and RailTel. 

To overcome these barriers, we present **BharatGov Access**, the first census-scale, longitudinal web observatory of India's public web infrastructure. Instrumented from domestic in-country cloud nodes deployed in Bangalore, India, the observatory continuously measures **12,092 government web domains** across Central Ministries, 36 States and Union Territories, all 788 District Administrations, Urban Local Bodies (ULBs), premier academic institutes, and the judiciary. We introduce a standardized, defensible **5-Pillar / 10-Sub-Feature** evaluation framework strictly aligned with W3C (WCAG 2.1 AA) and the Ministry of Electronics and Information Technology (MeitY) Guidelines for Indian Government Websites (GIGW 3.0).

Our empirical audit reveals three primary findings:

1. **The S3WaaS Standardization Dividend:** The National Informatics Centre's (NIC) *Secure, Scalable and Sugamya Website as a Service* (S3WaaS) framework, running on a hardened Drupal core across 6,480 active district portals (63.2%), acts as a transformative equalizer, elevating mean accessibility compliance to **95.2 / 100** with **100.0%** GIGW accessibility toolbar penetration, contrasted with legacy state ASP.NET deployments that languish at **84.3 / 100**. The dividend is real but bounded: S3WaaS does not lead on security headers, where it scores 66.8 against 85.1 for modern single-page applications.
2. **The Cryptographic Hardening Deficit:** While transport-layer encryption is ubiquitous (**100.0%** HTTPS enforcement across active nodes), defensive HTTP headers exhibit severe lag: the mean header-hardening score is **68.0 / 100**, and only **444 portals (4.3%)** set HSTS, a content security policy, frame options and MIME-sniffing protection together. The modal band, holding 60.0% of portals, scores between 50 and 75, leaving citizens exposed to SSL-stripping and cross-site scripting risks at the edge.
3. **Linguistic & Domestic Latency Performance:** Under authentic domestic Indian peering conditions, median Time to First Byte (TTFB) is **888 ms** (mean 1,186 ms; estimated LCP median 2.27 s, mean 2.67 s), with **86.0%** of active portals offering localization in regional Eighth Schedule Indian scripts. 

We release the entire 12,092-portal dataset in immutable Apache Parquet, CSV, and JSON formats under CC-BY-4.0 alongside an open-access interactive observatory to assist researchers, engineers, and policymakers in modernizing public digital infrastructure.

**Keywords:** Web Measurement, E-Governance, Digital Public Infrastructure, Web Accessibility, WCAG 2.1, Core Web Vitals, GIGW 3.0, Internet Measurement, Cyber Security, CERT-In.

---

## I. Introduction
The expansion of Digital India has transformed the web portal from a static institutional brochure into an indispensable vehicle for basic citizen rights. Millions of citizens interact daily with portals operated by Central Ministries, State Secretariats, District Collectorates, and Municipal Corporations to access Direct Benefit Transfer (DBT) subsidies, obtain birth and caste certificates, inspect revenue land records, verify exam rolls, and lodge public grievances through CPGRAMS.

However, the rapid digitization of public administration across 36 States and Union Territories (UTs) has historically occurred in silos. Disparate legacy hosting architectures, decentralized software development vendors, and varying administrative technical capacity have generated significant heterogeneity in web quality, accessibility, responsiveness, and defense posture.

### A. The Empirical Vacuum in Public Web Measurement
While commercial web measurement platforms (such as HTTP Archive and Chrome User Experience Report) track the global top million domains, their coverage of sovereign public sector web ecosystems in the Global South is extraordinarily sparse. Furthermore, prior academic investigations of Indian government portals suffer from three crippling methodological limitations:
1. **Shallow, Non-Representative Samples:** Academic studies typically evaluate between 50 and 200 arbitrary central ministry homepages, completely bypassing the district and municipal portals where 80% of citizen administrative transactions occur.
2. **The Perimeter Firewall Blindspot (Geo-IP Bias):** Crawlers executing from overseas cloud instances (e.g., AWS us-east-1 or GCP us-central1) encounter aggressive edge perimeter Geo-IP drops enforced by RailTel, state National Informatics Centre (NIC) gates, and state data center (SDC) firewalls. These firewalls silently terminate TCP handshakes or return HTTP 502/504 errors, resulting in false unreachability estimates exceeding 66%.
3. **Metric Bloat and Measurement Conflation:** Many tools harvest 70+ arbitrary, uncalibrated variables, assigning misleading "zero scores" to unreachable domains rather than decoupling schema validation from network availability.

### B. Research Contributions
To address these challenges, this study makes the following contributions:
- **Census-Scale Domain Registry:** We construct and maintain India's largest verified public domain registry comprising **12,092 government portals** covering 7 distinct governance tiers.
- **Domestic In-Country Vantage Point:** We deploy a high-concurrency ingestion engine inside the Indian domestic internet fabric in Bangalore, demonstrating the complete elimination of artificial perimeter drops and establishing authentic domestic baseline latencies.
- **5-Pillar Standardized Methodology:** We eliminate feature bloat by formulating a 5-Pillar / 10-Sub-Feature evaluation schema grounded in W3C (WCAG 2.1 AA), Core Web Vitals, and MeitY GIGW 3.0.
- **Empirical Findings on S3WaaS:** We present the first large-scale empirical validation of NIC’s S3WaaS platform, quantifying its measurable impact on accessibility and mobile inclusivity.
- **Open Data & Live Observatory:** We deploy a public, interactive web dashboard (`quality-ampland-ashley-ought.trycloudflare.com`) and release versioned Apache Parquet datasets for reproducibility.

---

## II. Related Work & Background

### A. Web Accessibility & GIGW Standards
The World Wide Web Consortium's Web Content Accessibility Guidelines (WCAG 2.1) specify four core principles: Perceivable, Operable, Understandable, and Robust (POUR). In India, the Ministry of Electronics and Information Technology formulated the *Guidelines for Indian Government Websites* (GIGW), currently in version 3.0. GIGW mandates specific accessibility features, including primary navigation skip links, text resizers (A+/A-), high-contrast viewing modes, and regional language availability for linguistic inclusion.

### B. Web Performance & Core Web Vitals
Google's Core Web Vitals framework establishes user-centric latency benchmarks, focusing on Largest Contentful Paint (LCP $\le 2.5\text{s}$), First Input Delay / Interaction to Next Paint (INP), and Cumulative Layout Shift (CLS $\le 0.1$). Prior studies have highlighted how excessive JavaScript payload and bloated DOM structures degrade access for rural citizens relying on mobile broadband.

### C. Network Measurement Bias
Internet measurement literature has repeatedly established that vantage point location significantly skews empirical findings. Censorship, CDN routing policies, and perimeter firewalls frequently induce divergent responses depending on client IP origin. In this study, we specifically quantify and resolve the perimeter Geo-IP bias affecting sovereign Indian government portals.

---

## III. The 5-Pillar Evaluation Framework

To eliminate ambiguous and noisy features, we synthesize web infrastructure evaluation into five orthogonal pillars, each containing exactly two defensible sub-features, plus a weighted composite index.

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
   └─────┬─────┘  └─────┬─────┘           └─────┬─────┘           └─────┬─────┘  └─────┬─────┘
         │              │                       │                       │              │
    ┌────┴────┐    ┌────┴────┐             ┌────┴────┐             ┌────┴────┐    ┌────┴────┐
    │Alt & Lbl│    │Latency  │             │TLS/HTTPS│             │Multiling│    │S3WaaS CMS
    │Toolbar  │    │Est. LCP │             │Sec Head.│             │Viewport │    │Grievance│
    └─────────┘    └─────────┘             └─────────┘             └─────────┘    └─────────┘
```

### Pillar 1: Accessibility & Usability (WCAG 2.1 AA / GIGW 3.0)
1. **$S_{\text{acc}}$ (Accessibility Compliance Score, $0 \le S_{\text{acc}} \le 100$):**  
   Computed from structural DOM inspection evaluating image alternative text coverage ($C_{\text{alt}}$), form control input labeling ($C_{\text{lbl}}$), document root language specification ($I_{\text{lang}} \in \{0, 1\}$), and skip-to-content bypass links ($I_{\text{skip}} \in \{0, 1\}$):
   $$S_{\text{acc}} = \min\left(98.5, \; 65.0 + 15.0 \cdot C_{\text{alt}} + 10.0 \cdot C_{\text{lbl}} + 4.0 \cdot I_{\text{lang}} + 6.0 \cdot I_{\text{skip}}\right)$$
2. **$F_{\text{toolbar}}$ (GIGW Accessibility Toolbar Presence, Boolean):**  
   Detects client-side accessibility widgets providing font resizing ($A+/A-$), high-contrast color toggling, and screen reader bypass mechanisms mandated by MeitY GIGW Section 5.

### Pillar 2: Performance & Network Latency (Core Web Vitals)
3. **$L_{\text{resp}}$ (Time to First Byte / Network Round-Trip Latency, ms):**  
   High-precision measurement of HTTP connection establishment, TLS negotiation, and initial server response time from the domestic Bangalore vantage point.
4. **$T_{\text{lcp}}$ (Estimated Largest Contentful Paint, seconds):**  
   Derived from measured network TTFB and payload HTML asset size ($S_{\text{kb}}$):
   $$T_{\text{lcp}} = \max\left(0.60, \; 1.30 \cdot \frac{L_{\text{resp}}}{1000} + \frac{S_{\text{kb}}}{180.0}\right)$$

### Pillar 3: Security & Cryptography (CERT-In Baseline)
5. **$I_{\text{https}}$ (Canonical HTTPS Enforcement, Boolean):**  
   Validates whether plaintext HTTP requests are strictly upgraded via 301/308 redirects to secure TLS transport.
6. **$S_{\text{sec}}$ (Security Headers Hardening Score, $0 \le S_{\text{sec}} \le 100$):**  
   Assesses compliance with CERT-In cyber security guidelines:
   $$S_{\text{sec}} = 40 \cdot I_{\text{https}} + 25 \cdot I_{\text{hsts}} + 15 \cdot I_{\text{csp}} + 10 \cdot I_{\text{xcto}} + 10 \cdot I_{\text{xfo}}$$
   where $I_{\text{hsts}}$ denotes `Strict-Transport-Security`, $I_{\text{csp}}$ denotes `Content-Security-Policy`, $I_{\text{xcto}}$ denotes `X-Content-Type-Options: nosniff`, and $I_{\text{xfo}}$ denotes `X-Frame-Options`.

### Pillar 4: Linguistic & Mobile Inclusivity (Digital India Reach)
7. **$I_{\text{multi}}$ (Regional Multilingual Localization, Boolean):**  
   Identifies navigation and body content localized into India's 22 Eighth Schedule languages (Devanagari/Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Odia, Punjabi, Assamese, Urdu).
8. **$I_{\text{mobile}}$ (Responsive Viewport Configuration, Boolean):**  
   Verifies standard mobile viewport declaration: `<meta name="viewport" content="width=device-width, initial-scale=1.0">`.

### Pillar 5: Architecture & Citizen Interactivity
9. **$A_{\text{cms}}$ (CMS & Framework Architecture, Categorical):**  
   Fingerprints web platforms: `s3waas_drupal` (NIC standardized distribution), `custom_dynamic_cms`, `legacy_asp_net` (older state portals), `modern_spa` (React/Angular client-rendered), or `wordpress`.
10. **$I_{\text{services}}$ (Citizen Online Services & Grievance Integration, Boolean):**  
    Detects integrated site search utilities and citizen grievance redressal integrations (e.g., CPGRAMS, Samadhan, Jan Sunwai, CM Helpline).

### Composite Observatory Maturity Score
To enable comparative governance analysis, we formulate a normalized composite maturity index ($0 \le M \le 100$):
$$M = 0.30 \cdot S_{\text{acc}} + 0.25 \cdot S_{\text{sec}} + 0.20 \cdot \max(0, 100 - 15 \cdot T_{\text{lcp}}) + 10 \cdot I_{\text{multi}} + 5 \cdot I_{\text{mobile}} + 5 \cdot I_{\text{services}} + 5 \cdot \mathbb{I}(A_{\text{cms}} = \text{s3waas})$$

The binary terms carry absolute point values (10 or 5), not percentages, so a portal with every binary term true and perfect scores on the three continuous terms reaches exactly 100. The index is clamped to a floor of 45.0. We verified the formula against the released values: it reproduces **99.96%** of the 10,247 reachable rows to within 0.15, and the four remaining rows are all clamped at the floor. The formula is exposed as `bharatgov_access.maturity_index()` so a reader can score a portal they measured themselves with the same methodology.

---

## IV. Measurement System Architecture

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      National Registry (N = 12,092)                    │
 │    Central Ministries (645) · State Depts (2,935) · Districts (7,468)   │
 │   Academic (352) · Judiciary (292) · PSUs (260) · Municipalities (140)  │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │            Domestic In-Country Ingestion Node (Bangalore, India)       │
 │   6 vCPUs · 60 GB RAM · 350 GB NVMe · Peered with National Fabric       │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
         ┌───────────────────────────┴───────────────────────────┐
         ▼                                                       ▼
 ┌──────────────────────────────┐        ┌──────────────────────────────┐
 │ Async Concurrency Workers    │        │ Rigorous Decoupled Parser    │
 │ • 64 async workers (httpx)   │        │ • Schema Validation Decoupled│
 │ • HTTP/1.1 & HTTP/2 negotiate│        │ • Structural DOM extraction  │
 │ • Canonical redirect tracking│        │ • Diagnostic failure coding  │
 └──────────────┬───────────────┘        └──────────────┬───────────────┘
                │                                       │
                └───────────────────┬───────────────────┘
                                    │
                                    ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                     Versioned Open Data Release                        │
 │       • Apache Parquet (Columnar) · CSV · JSON (CC-BY-4.0)             │
 │       • Live Dashboard Observatory (trycloudflare.com tunnel)          │
 └────────────────────────────────────────────────────────────────────────┘
```

### A. In-Country Vantage Point Elimination of Geo-IP Bias
The primary engineering challenge encountered during initial audits was the severe distortion caused by state perimeter security devices. When crawled from an Atlanta (US) node, 1,592 out of 2,390 domains (66.6%) returned HTTP 502/504 errors. 

Deploying an equivalent measurement agent in a Bangalore datacenter connected to domestic tier-1 Indian internet transit eliminated these drops entirely. Active reachability jumped to **84.7%** across the census dataset, and latencies dropped from over 15,000 ms (timeout threshold) to authentic domestic values (median TTFB 888 ms, mean 1,186 ms).

### B. Decoupled Validation Rigor
To ensure academic integrity, BharatGov Access strictly decouples **Schema Registration** from **Measurement Success**. When a portal is unreachable or its DNS lease has expired, the observatory assigns explicit status diagnostic codes (`DNS Inactive`, `504 Timeout`, `502 Bad Gateway`, `403 WAF Challenge`) and records sub-feature metrics as `null` / `NaN`, preventing the propagation of artificial zero scores.

---

## V. Empirical Findings & Analysis

The census dataset comprises **12,092 government web domains**, with **10,247 actively evaluated in-country**. Table I provides a comprehensive breakdown across administrative levels.

### TABLE I: Comprehensive Breakdown Across Governance Tiers
All figures are computed from the released dataset (`bharatgov_access_clean.parquet`) over reachable portals only. Reproduce with `bharatgov tiers`.

| Governance Tier | Total Registered | Active Audited (%) | Mean Acc. Score ($S_{\text{acc}}$) | GIGW Toolbar (%) | Mean Sec. Score ($S_{\text{sec}}$) | Multilingual (%) | Median TTFB (ms) | Mean Maturity ($M$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Central Ministries** | 645 | 532 (82.5%) | 90.8 | 88.2% | 78.6 | 75.9% | 971 | 74.9 |
| **State Departments** | 2,935 | 2,017 (68.7%) | 92.0 | 88.3% | 68.4 | 84.6% | 1,059 | 75.7 |
| **District Collectorates** | 7,468 | 6,716 (89.9%) | **95.0** | 94.7% | 65.8 | 86.9% | 880 | **80.1** |
| **Academic & Research** | 352 | 342 (97.2%) | 91.6 | 71.1% | 84.7 | 90.6% | **487** | **83.3** |
| **Judiciary & Courts** | 292 | 271 (92.8%) | 91.0 | 78.2% | 63.2 | 88.6% | 1,024 | 71.9 |
| **Public Sector / Banks** | 260 | 247 (95.0%) | 91.8 | 66.8% | 84.4 | 89.9% | 496 | **83.2** |
| **Urban Local Bodies** | 140 | 122 (87.1%) | 90.1 | 80.3% | 65.8 | 77.9% | 1,096 | 71.6 |
| **National Baseline** | **12,092** | **10,247 (84.7%)** | **93.8** | **91.0%** | **68.0** | **86.0%** | **888** | **78.8** |

Two figures in this table deserve careful reading. First, the national reachability rate of 84.7% is not uniform: state departments sit at 68.7% while higher education reaches 97.2%, so the national average conceals a 28-point spread across tiers. Second, the tier with the highest accessibility (district collectorates, 95.0) is not the tier with the highest security (higher education, 84.7). Accessibility and security are effectively uncorrelated across tiers, which is the central finding of Section V-B.

### A. Architectural Impact: S3WaaS vs. Legacy Frameworks
A central empirical contribution of this study is quantifying the national impact of NIC's S3WaaS Drupal distribution. As Table II shows, S3WaaS portals outperform every other platform on accessibility, GIGW toolbar penetration and mobile responsiveness, but they do **not** lead on security headers — a distinction an earlier draft of this paper elided.

### TABLE II: Comparison of Web CMS Architectures
Reachable portals only; unreachable hosts are excluded rather than counted as an unknown platform. Reproduce with `bharatgov arch`.

| Metric | S3WaaS Drupal | Custom Dynamic CMS | Legacy ASP.NET | Modern SPA | WordPress |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Active Portals Observed** | 6,480 (63.2%) | 2,671 (26.1%) | 399 (3.9%) | 651 (6.4%) | 46 (0.4%) |
| **Mean Accessibility ($S_{\text{acc}}$)** | **95.2 / 100** | 92.6 / 100 | 84.3 / 100 | 91.6 / 100 | 90.8 / 100 |
| **GIGW Toolbar Penetration** | **100.0%** | 77.4% | 67.7% | 71.4% | 95.7% |
| **Mean Security Headers ($S_{\text{sec}}$)** | 66.8 / 100 | 67.6 / 100 | 60.3 / 100 | **85.1 / 100** | 74.5 / 100 |
| **Median TTFB Latency** | 914 ms | 909 ms | 1,060 ms | **529 ms** | 1,259 ms |
| **Mobile Responsiveness** | 98.8% | 96.1% | 90.5% | **100.0%** | 97.8% |
| **Composite Maturity ($M$)** | 81.0 / 100 | 74.4 / 100 | 68.5 / 100 | **82.3 / 100** | 70.8 / 100 |

The S3WaaS dividend is real but narrower than a single composite score suggests. It buys accessibility and mobile compliance almost completely — 100.0% toolbar penetration and 95.2 mean accessibility against 84.3 for legacy ASP.NET, a 10.9-point gap. It buys nothing on security: S3WaaS scores 66.8 on headers, below the custom-CMS mean of 67.6 and far below the modern-SPA mean of 85.1. A template can ship accessible markup; it cannot ship a content security policy, because that is a deployment decision made at the reverse proxy.

### B. The Cryptographic Security Gap
While 100.0% of reachable portals mandate TLS/HTTPS, the audit reveals a substantial gap in defensive HTTP headers. The released schema records a composite header score rather than per-directive booleans, so the figures below are distributional rather than per-directive:

- **Mean header score:** **68.0 / 100** across 10,247 reachable portals.
- **Full hardening:** only **444 portals (4.3%)** score 100, meaning they set HSTS, a content security policy, `X-Frame-Options` and `X-Content-Type-Options` together.
- **Partial hardening:** **29.5%** score 75 or above; the modal band is 50–75, holding 6,144 portals (60.0%).

The practical consequence is that a citizen on public Wi-Fi is protected by transport encryption but not by HSTS preload, and a portal running custom forms is not protected by a content security policy. Both are edge-configuration fixes that require no application change, which is why Section VI recommends them at the reverse proxy rather than in each department.

### C. State-by-State Governance Maturity Rankings
Benchmarking composite maturity across the 36 States and UTs shows a narrow band: the top state (Meghalaya, 79.9) and the bottom (Himachal Pradesh, 78.4) differ by only 1.5 points on the composite index. That compression is itself the finding — the composite is dominated by accessibility, which is uniformly high, so it cannot discriminate between states. Security headers, by contrast, span 62.8 to 86.2 across states, a 23-point range, and median latency spans 758 ms to 1,846 ms.

| Rank | State / UT | Portals | Maturity | Accessibility | Security | Median TTFB |
| :---: | :--- | ---: | ---: | ---: | ---: | ---: |
| 1 | Meghalaya | 210 | 79.9 | 93.9 | 67.4 | 758 ms |
| 2 | Odisha | 252 | 79.8 | 94.5 | 67.8 | 868 ms |
| 3 | Uttar Pradesh | 389 | 79.6 | 94.7 | 62.8 | 771 ms |
| 4 | Nagaland | 210 | 79.5 | 94.3 | 68.1 | 864 ms |
| 5 | Maharashtra | 279 | 79.5 | 94.3 | 67.1 | 866 ms |
| … | … | … | … | … | … | … |
| 36 | Himachal Pradesh | 275 | 78.4 | 93.6 | 66.5 | 1,015 ms |

Reproduce with `bharatgov states`.

---

## VI. Discussion & Policy Recommendations

Based on empirical evidence across 12,092 portals, we propose three actionable recommendations for MeitY, NIC, and state IT departments:

1. **Mandate Complete District & Municipal S3WaaS Migration:**  
   Our data demonstrates that S3WaaS elevates accessibility compliance by 10.9 points (from 84.3 to 95.2) while ensuring near-universal mobile responsiveness (98.8%). State governments should phase out legacy bespoke ASP.NET websites and migrate all municipal and district portals to the S3WaaS pipeline.
2. **Institute Centralized Reverse Proxy Security Headers:**  
   The header-hardening deficit (mean 68.0 / 100; only 4.3% of portals fully hardened) can be resolved without modifying application code. We recommend that RailTel, NIC, and State Data Centres mandate automated injection of HSTS (`max-age=31536000; includeSubDomains`) and base CSP policies at their NGINX / reverse-proxy edge gateways.
3. **Establish In-Country Automated Longitudinal Audits:**  
   Government bodies should rely on continuous, in-country automated observatories rather than periodic, point-in-time commercial manual audits. Ongoing monitoring incentivizes departments to fix regressions in image alt tags and language localization immediately upon deployment.

---

## VII. Threats to Validity & Limitations

1. **Automated vs. Manual Usability Testing:**  
   Automated DOM inspection reliably identifies structural WCAG failures (missing alt attributes, empty links, form control labeling). However, nuanced cognitive usability barriers and complex screen-reader audio flows still require human evaluation.
2. **Single Vantage Point Scope:**  
   Although our Bangalore vantage point provides authentic domestic egress without perimeter blocking, latency experienced by rural users over congested 2G/4G radio access networks may exceed datacenter TTFB measurements.
3. **Dynamic Single-Page Applications:**  
   A subset of modern SPAs (6.4%) render content client-side using JavaScript frameworks. While our crawler tracks dynamic redirects, full JS evaluation on every sub-route requires significant headless browser resources.

---

## VIII. Conclusion & Open Science Artifacts

This paper presented **BharatGov Access**, a census-scale web observatory evaluating 12,092 Indian government portals through an in-country domestic vantage point in Bangalore. By establishing a standardized 5-Pillar / 10-Sub-Feature framework, we have demonstrated the national accessibility dividends of NIC's S3WaaS platform while revealing critical security gaps in HTTP defense headers.

To promote reproducibility and open science, all research artifacts are made publicly accessible:

- **Interactive Web Observatory:** `https://quality-ampland-ashley-ought.trycloudflare.com`
- **Census Open Dataset:** Immutable Apache Parquet, CSV, and JSON releases hosted under CC-BY-4.0 in `resources/bharatgov_access_clean.*`.
- **Installable Python package:** `pip install bharatgov-access` bundles the Parquet release and exposes the loader, the tier and platform tables, the state ranking and the maturity index. Every figure in this paper is one call away:

```python
import bharatgov_access as bga

bga.tier_summary()          # Table I
bga.architecture_summary()  # Table II
bga.state_ranking()         # Section V-C
```

A command-line interface ships with the package, so the tables are reachable without writing Python:

```bash
bharatgov tiers
bharatgov arch
bharatgov states --top 10
bharatgov query --tier district --state Kerala --min-maturity 85
```

The package carries a test suite that asserts the published figures, so a regression in the loader fails loudly rather than silently changing a table in this paper.

---

## References

1. World Wide Web Consortium (W3C), "Web Content Accessibility Guidelines (WCAG) 2.1," W3C Recommendation, June 2018. [Online]. Available: https://www.w3.org/TR/WCAG21/
2. Ministry of Electronics and Information Technology (MeitY), Government of India, "Guidelines for Indian Government Websites (GIGW 3.0)," National Informatics Centre (NIC), New Delhi, 2023.
3. Indian Computer Emergency Response Team (CERT-In), "Cyber Security Guidelines for Government Entities," Ministry of Electronics and Information Technology, New Delhi, 2023.
4. National Informatics Centre (NIC), "S3WaaS: Secure, Scalable and Sugamya Website as a Service," Ministry of Electronics and Information Technology, 2024. [Online]. Available: https://s3waas.gov.in/
5. P. Agarwal, A. K. Bairagi, and V. N. Yaduraj, "BharatGov Access: National Government Web Infrastructure Observatory," Indian Institute of Technology Kharagpur, Tech. Rep. DA-2026-G12, 2026.
6. Google Developers, "Web Vitals: Essential metrics for a healthy site," 2023. [Online]. Available: https://web.dev/vitals/
7. M. A. Fagan, "Web Accessibility of State and Local Government Websites: An Empirical Longitudinal Study," *Government Information Quarterly*, vol. 38, no. 3, p. 101584, 2021.
8. S. Scheitle et al., "A Long Way to the Top: Significance, Structure, and Stability of Internet Top Lists," in *Proc. ACM Internet Measurement Conference (IMC)*, 2018, pp. 478–493.
9. R. Padmanabhan et al., "Residential Alternatives to CDN-Hosted Public Infrastructure in Developing Regions," in *Proc. ACM SIGCOMM*, 2020.
10. E. B. V. Kumar and S. K. Gupta, "Digital India: Empirical Evaluation of Public Grievance Portals and Citizen Engagement," *IEEE Transactions on Technology and Society*, vol. 3, no. 2, pp. 112–124, 2022.

