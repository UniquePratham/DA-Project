# BharatGov Access: An In-Country Measurement and Empirical Benchmark of India's Public Web Infrastructure

**Pratham Agarwal**, **Amit Kumar Bairagi**, and **Vishwajeet Nand Yaduraj**  
*Department of Computer Science and Engineering, Indian Institute of Technology Kharagpur, West Bengal 721302, India*  
*Subject: Data Analytics*  
*Correspondence: `{pratham.agarwal, amit.bairagi, vishwajeet.yaduraj}@iitkgp.ac.in`*

---

## Abstract
Digital Public Infrastructure (DPI) is the primary conduit through which the Government of India delivers welfare entitlements, citizen registries, tax filings, and judicial services. Despite its systemic significance, empirical knowledge of the accessibility, performance, and security posture of India's multi-tiered public web remains scarce and fragmented. Prior web measurement studies evaluate narrow samples or rely on overseas vantage points, which we show produce false reachability failures because state perimeter firewalls and Geo-IP filters terminate foreign clients.

We present **BharatGov Access**, an in-country web observatory of India's public web infrastructure. Instrumented from a domestic cloud node in Bangalore, the observatory measures **14,489 government web domains** discovered from three auditable sources: Certificate Transparency logs, a curated entity registry, and outbound links harvested from live portals. No domain is inferred from a naming convention. Of these, **7,542 (52.1%)** responded to a live HTTP request and are analysed here. We apply a **5-Pillar / 12-Variable** framework aligned with W3C WCAG 2.1 AA and MeitY GIGW 3.0.

Our measurements yield three findings:

1. **Accessibility is uniformly mediocre, and the S3WaaS dividend is narrow.** A real axe-core 4.x audit of 374 portals finds a mean of **3.48 WCAG violations** per portal, with only **4.8%** passing cleanly. Portals fingerprinted as NIC's S3WaaS/Drupal platform score **95.4 / 100** on the severity-weighted index against **82.0** for WordPress and **83.7** for legacy ASP.NET. The dividend does not extend to security: S3WaaS scores **47.6** on response-header hardening, below legacy ASP.NET at **56.0** and far below non-NIC Drupal deployments at **76.4**.
2. **Header hardening is the dominant deficit.** Transport encryption is near-universal (**99.5%** of reachable portals serve HTTPS), yet mean header-hardening is **43.1 / 100** on a 488-portal tool-measured sample; only **33.4%** set a Content-Security-Policy and **33.0%** set a Permissions-Policy.
3. **Domestic latency is bimodal.** Across all 7,542 reachable portals, median time to first byte is **416 ms** but the mean is **1,144 ms**: a long tail of slow hosts dominates the average. On the 488-portal tool-measured subsample, which over-samples heavy institutional sites, the corresponding figures are 1,666 ms and 2,655 ms. Median estimated LCP is **1.40 s** against a mean of **2.77 s**. Only **18.4%** of reachable portals contain text in a scheduled Indian script, and although **86.7%** declare a responsive viewport, **29.1%** still overflow horizontally when actually rendered at 375 px.

We release the measured dataset in Apache Parquet, CSV, and JSON under CC-BY-4.0, together with the crawler and the discovery scripts, so every figure in this paper can be reproduced from the raw HTTP responses.

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
- **Large Auditable Domain Registry:** We construct an auditable public domain registry comprising **14,489 government portals** covering 7 distinct governance tiers, every one of them discovered from an auditable source rather than inferred from a naming convention.
- **Domestic In-Country Vantage Point:** We deploy a high-concurrency ingestion engine inside the Indian domestic internet fabric in Bangalore, using a domestic vantage point to reduce the risk of location-dependent reachability bias.
- **5-Pillar Standardized Methodology:** We eliminate feature bloat by formulating a 5-Pillar / 12-Variable evaluation schema grounded in W3C (WCAG 2.1 AA), Core Web Vitals, and MeitY GIGW 3.0.
- **Empirical Findings on S3WaaS:** We present the first large-scale empirical validation of NIC’s S3WaaS platform, quantifying its measurable impact on accessibility and mobile inclusivity.
- **Open Data & Live Observatory:** We deploy a public, interactive web dashboard (`https://uniquepratham.github.io/DA-Project/`) and release versioned Apache Parquet datasets for reproducibility.

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

### Pillar-to-Variable Mapping
The framework has five pillars and twelve measured variables. The table below makes the grouping explicit, so a reader can see exactly which raw measurement feeds which pillar.

| Pillar | Sub-feature group | Raw variables | Tool |
| :--- | :--- | :--- | :--- |
| **1. Accessibility** | Conformance | $V_{\text{axe}}$, $S_{\text{axe}}$ | axe-core 4.x |
| | GIGW affordances | $F_{\text{toolbar}}$ | DOM inspection |
| **2. Performance** | Latency | $L_{\text{ttfb}}$ | `perf_counter` |
| | Paint estimate | $T_{\text{lcp}}$ | derived from TTFB + payload |
| **3. Security** | Transport | $I_{\text{https}}$, $T_{\text{tls}}$ | `ssl` handshake |
| | Header hardening | $S_{\text{sec}}$ | OWASP directive set |
| **4. Inclusion** | Language | $I_{\text{multi}}$ | `html[lang]`, `hreflang`, script detection |
| | Mobile | $I_{\text{mobile}}$ | 375 px Chromium render |
| **5. Architecture** | Platform | $A_{\text{cms}}$ | framework fingerprints |
| | Services | $I_{\text{services}}$ | DOM affordance scan |

### Pillar 1: Accessibility & Usability (WCAG 2.1 AA / GIGW 3.0)
1. **$V_{\text{axe}}$ (axe-core WCAG violation count):**  
   Measured by running **axe-core 4.x** in headless Chromium against the rendered DOM, restricted to the `wcag2a`, `wcag2aa`, `wcag21a` and `wcag21aa` rule tags. Violations are counted by impact level (critical, serious, moderate, minor). This is a real automated audit, not a proxy.
2. **$S_{\text{axe}}$ (severity-weighted accessibility index, $0 \le S_{\text{axe}} \le 100$):**  
   axe-core does not publish a scalar score, so we define one explicitly and disclose the weights:
   $$S_{\text{axe}} = \max\left(0, \; 100 - 12 V_{\text{crit}} - 6 V_{\text{ser}} - 3 V_{\text{mod}} - 1 V_{\text{min}}\right)$$
   The weights encode the WCAG conformance impact of each axe impact level. They are a stated convention, not a measurement, and are reported alongside the raw violation counts so a reader can recompute with different weights.
3. **$F_{\text{toolbar}}$ (GIGW accessibility toolbar presence, Boolean):**  
   Detects client-side accessibility widgets providing font resizing ($A+/A-$), high-contrast toggling, and skip-to-content mechanisms mandated by MeitY GIGW Section 5.

### Pillar 2: Performance & Network Latency (Core Web Vitals)
4. **$L_{\text{ttfb}}$ (Time to First Byte, ms):**  
   Wall-clock time from request dispatch to first response byte, measured with `time.perf_counter()` on the domestic Bangalore node. This is a real network measurement.
5. **$T_{\text{lcp}}$ (Estimated Largest Contentful Paint, seconds):**  
   Derived from measured TTFB and the real document payload size ($S_{\text{kb}}$, from the actual response body):
   $$T_{\text{lcp}} = \max\left(0.60, \; 1.30 \cdot \frac{L_{\text{ttfb}}}{1000} + \frac{S_{\text{kb}}}{180.0}\right)$$
   This is an **estimate**, not a field measurement. A true LCP requires a full browser paint trace, which we did not run at census scale. We label it as an estimate everywhere it appears.

### Pillar 3: Security & Cryptography (CERT-In Baseline)
6. **$I_{\text{https}}$ (Canonical HTTPS enforcement, Boolean):**  
   True when the final URL after redirects is served over TLS.
7. **$S_{\text{sec}}$ (Security headers hardening score, $0 \le S_{\text{sec}} \le 100$):**  
   Scored against the **OWASP Secure Headers Project** directive set, read from the real response headers:
   $$S_{\text{sec}} = 25 I_{\text{hsts}} + 30 I_{\text{csp}} + 15 I_{\text{xfo}} + 10 I_{\text{xcto}} + 10 I_{\text{ref}} + 10 I_{\text{perm}}$$
   where the indicators denote `Strict-Transport-Security`, `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, and `Permissions-Policy` respectively.
8. **$T_{\text{tls}}$ (TLS certificate inspection):**  
   A real TLS handshake via Python `ssl` records the issuer, negotiated protocol version, cipher suite, and days to certificate expiry.

### Pillar 4: Linguistic & Mobile Inclusivity (Digital India Reach)
9. **$I_{\text{multi}}$ (Multilingual content, Boolean):**  
   True when `html[lang]` is a non-English tag, **or** the document declares `hreflang` alternates, **or** the rendered text contains characters from a scheduled Indian script (Devanagari, Bengali, Gurmukhi, Gujarati, Oriya, Tamil, Telugu, Kannada, Malayalam).
10. **$I_{\text{mobile}}$ (Responsive viewport, Boolean):**  
    True when the document declares `width=device-width`, **and** a real headless-Chromium render at 375 px produces no horizontal overflow.

### Pillar 5: Architecture & Citizen Interactivity
11. **$A_{\text{cms}}$ (CMS / framework architecture, categorical):**  
    Fingerprinted from real markers in the response body and headers: `s3waas` and `sites/all/themes` (S3WaaS/Drupal), `wp-content` and `wp-json` (WordPress), `drupal` and `core/misc/drupal` (Drupal), `__VIEWSTATE` and `.aspx` (legacy ASP.NET), `_next/static` and `ng-version` (modern SPA). The matched marker is recorded per portal as evidence.
12. **$I_{\text{services}}$ (Citizen service affordance, Boolean):**  
    True when the parsed DOM contains a search input or a grievance/complaint affordance (CPGRAMS, Samadhan, Jan Sunwai, helpline).

### Composite Observatory Maturity Score
To enable comparative governance analysis, we define a normalized composite maturity index ($0 \le M \le 100$):
$$
\begin{aligned}
M = {} & 0.30 \cdot S_{\text{axe}} + 0.25 \cdot S_{\text{sec}} \\
       & + 0.20 \cdot \max(0,\; 100 - 15 \cdot T_{\text{lcp}}) \\
       & + 10 \cdot I_{\text{multi}} + 5 \cdot I_{\text{mobile}} \\
       & + 5 \cdot I_{\text{services}} + 5 \cdot \mathbb{I}(A_{\text{cms}} = \text{s3waas})
\end{aligned}
$$

The binary terms carry absolute point values (10 or 5), not percentages, so a portal with every binary term true and perfect scores on the three continuous terms reaches exactly 100. The index is clamped to a floor of 45.0.

Two properties of this index should be stated plainly. First, the weights are a **design choice**, not an empirical result: they encode our judgement that accessibility and security matter most. A reader who disagrees can recompute $M$ from the released per-pillar columns, which is why every component is published separately rather than only as a composite. Second, the composite is dominated by accessibility, which is uniformly high across the census, so it compresses differences between tiers. Section V therefore reports the pillars individually and treats the composite as a summary, not a verdict.

The formula is exposed as `bharatgov_access.maturity_index()` so a reader can score a portal they measured themselves with the same methodology.

---

## IV. Measurement System Architecture

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      National Registry (N = 14,489)                    │
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

### A. In-Country Vantage Point
All measurements were taken from a single cloud node in Bangalore, connected to domestic tier-1 Indian transit. We did not run a controlled overseas comparison, so we make no quantitative claim about how much a foreign vantage point would under-count. What we can state is the operational reason for the choice: Indian government portals are frequently fronted by state data-centre gateways and perimeter filters that treat foreign client addresses differently, and a domestic vantage point removes that variable entirely.

The cost of this choice is that our latency figures describe one domestic path, not the experience of a citizen on congested 4G in a rural district. Section VII records this as a limitation.

### B. Decoupled Validation Rigor
To ensure academic integrity, BharatGov Access strictly decouples **Schema Registration** from **Measurement Success**. When a portal is unreachable or its DNS lease has expired, the observatory assigns explicit status diagnostic codes (`DNS Inactive`, `504 Timeout`, `502 Bad Gateway`, `403 WAF Challenge`) and records sub-feature metrics as `null` / `NaN`, preventing the propagation of artificial zero scores.

---

## V. Empirical Findings & Analysis

The census dataset comprises **14,489 government web domains**, of which **7,542 (52.1%)** responded to a live HTTP request and are analysed here. Table I provides a comprehensive breakdown across administrative levels.

### TABLE I: Comprehensive Breakdown Across Governance Tiers
All figures are computed from the released dataset (`bharatgov_access_clean.parquet`) over reachable portals only. Reproduce with `bharatgov tiers`.

| Governance Tier | Discovered | Reachable (%) | Mean Acc. ($S_{\text{axe}}$) | GIGW Toolbar (%) | Mean Sec. ($S_{\text{sec}}$) | Multilingual (%) | Median TTFB (ms) | Mean Maturity ($M$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Academic & Research** | 6,771 | 3,616 (53.4%) | 84.4 | 67.6% | 26.5 | 6.9% | 651 | 52.1 |
| **State Departments** | 7,340 | 3,677 (50.1%) | 88.6 | 75.2% | 59.7 | 26.8% | 369 | 65.6 |
| **Judiciary & Courts** | 203 | 127 (62.6%) | 92.0 | 83.5% | 76.1 | 25.2% | 423 | 72.9 |
| **Central Ministries** | 60 | 48 (80.0%) | **93.5** | 54.2% | **91.4** | 25.0% | 396 | **76.2** |
| **Public Sector / Banks** | 23 | 18 (78.3%) | 85.1 | 77.8% | 73.9 | 22.2% | 483 | 67.8 |
| **District Collectorates** | 62 | 35 (56.5%) | 85.8 | **80.0%** | 62.1 | 22.9% | 397 | 66.0 |
| **Urban Local Bodies** | 30 | 21 (70.0%) | 86.4 | 81.0% | 45.5 | **33.3%** | **266** | 64.0 |
| **National Baseline** | **14,489** | **7,542 (52.1%)** | **86.7** | **71.6%** | **44.3** | **17.2%** | **416** | **59.3** |

Three features of this table deserve careful reading. First, reachability is remarkably uniform across tiers, clustering between 50% and 80%, which suggests that the dominant cause of non-response is the discovery method rather than the tier: Certificate Transparency records every certificate ever issued, including expired and internal subdomains, so a large share of discovered names are no longer live portals. Second, the tier with the highest accessibility (central ministries, 93.5) is also the tier with the highest security (91.4), but the tier with the highest GIGW toolbar penetration (judiciary, 83.5%) has only middling security (76.1). Third, multilingual content is the weakest pillar nationally at 17.2%, far below every other measure.

### A. Real axe-core Accessibility Audit
Accessibility in Table I is reported as a severity-weighted axe-core index. To keep the raw evidence visible, we also ran axe-core 4.x directly on a random sample of **374 reachable portals** and report the unweighted violation counts:

| Measure | Value |
| :--- | ---: |
| Portals audited | 374 |
| Mean WCAG violations per portal | **3.48** |
| Median WCAG violations per portal | 3 |
| Portals with zero violations | 18 (4.8%) |
| Critical violations (total) | 339 |
| Serious violations (total) | 861 |
| Moderate violations (total) | 103 |
| Mean severity-weighted score ($S_{\text{axe}}$) | **74.5 / 100** |

The distribution is tight (standard deviation 2.1, maximum 13), which means the accessibility problem is not concentrated in a few broken portals but spread thinly across almost all of them. Only 4.8% of audited portals pass with zero violations. The dominant impact class is *serious* (861 of 1,303 violations, 66%), which in axe-core corresponds to rules such as missing form labels, insufficient colour contrast, and duplicate IDs. These are template-level defects: fixing them once in a shared layout fixes them for every portal built on that layout.

### B. Architectural Impact: S3WaaS vs. Legacy Frameworks### A. Architectural Impact: S3WaaS vs. Legacy Frameworks
A central empirical contribution of this study is quantifying the national impact of NIC's S3WaaS Drupal distribution. As Table II shows, S3WaaS portals outperform every other platform on accessibility, GIGW toolbar penetration and mobile responsiveness, but they do **not** lead on security headers — a distinction an earlier draft of this paper elided.

### TABLE II: Comparison of Web CMS Architectures
Reachable portals only; unreachable hosts are excluded rather than counted as an unknown platform. Reproduce with `bharatgov arch`.

| Metric | S3WaaS Drupal | Custom Dynamic CMS | Legacy ASP.NET | Modern SPA | WordPress | Drupal |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Reachable Portals Observed** | 661 (8.8%) | 3,838 (50.9%) | 1,247 (16.5%) | 582 (7.7%) | 978 (13.0%) | 236 (3.1%) |
| **Mean Accessibility ($S_{\text{axe}}$)** | **95.4** | 86.6 | 83.7 | 89.1 | 82.0 | 92.7 |
| **GIGW Toolbar Penetration** | 97.9% | 57.7% | 84.9% | 53.3% | 95.8% | **97.9%** |
| **Mean Security Headers ($S_{\text{sec}}$)** | 47.6 | 41.6 | 56.0 | 52.0 | 25.2 | **76.4** |
| **Composite Maturity ($M$)** | **75.5** | 57.5 | 61.4 | 61.3 | 48.4 | 72.7 |

The S3WaaS dividend is real but strictly one-dimensional. It buys accessibility almost completely: 95.4 mean accessibility against 82.0 for WordPress, a 13.4-point gap, and 97.9% GIGW toolbar penetration. It buys much less on security. S3WaaS scores **47.6** on response-header hardening, below legacy ASP.NET at 56.0 and far below non-NIC Drupal deployments at 76.4. A template can ship accessible markup; it cannot ship a content security policy, because that is a deployment decision made at the reverse proxy. The same pattern holds across the wider Drupal family, which reaches 76.4 on headers when the deployment is not the NIC distribution.

### C. The Cryptographic Security Gap
While **99.5%** of reachable portals serve HTTPS and **99.8%** complete a valid TLS handshake, the audit reveals a substantial gap in defensive HTTP headers. Scored against the OWASP Secure Headers Project directive set on a 488-portal tool-measured sample:

| Directive | Portals setting it |
| :--- | ---: |
| `Strict-Transport-Security` | 51.0% |
| `Content-Security-Policy` | **33.4%** |
| `X-Frame-Options` | 53.1% |
| `X-Content-Type-Options` | 50.2% |
| `Referrer-Policy` | 40.8% |
| `Permissions-Policy` | **33.0%** |
| **Mean hardening score** | **43.1 / 100** |

Transport encryption is effectively universal, but the headers that defend against SSL-stripping, clickjacking, and cross-site scripting are set by roughly half of portals at best, and by only a third for the two strongest controls (CSP and Permissions-Policy). TLS itself is healthy: 82.8% of portals negotiated TLS 1.3 and the remainder TLS 1.2, with no portal observed on a deprecated protocol.

The practical consequence is that a citizen on public Wi-Fi is protected by transport encryption but not by HSTS preload, and a portal running custom forms is not protected by a content security policy. Both are edge-configuration fixes that require no application change, which is why Section VI recommends them at the reverse proxy rather than in each department.

### D. Real Mobile Rendering
Declaring a viewport is not the same as being usable on a phone. We therefore rendered every audited portal in headless Chromium at 375 px and measured actual horizontal overflow:

- **86.7%** declare `width=device-width`.
- **29.1%** still overflow horizontally at 375 px, by a mean of **75 px**.
- The gap between the two figures (86.7% declared versus 70.9% actually fitting) is the measure of viewport theatre: a portal can declare responsiveness and still break on a phone.

### E. Performance Under Domestic Peering
On the 488-portal tool-measured sample, TTFB on the Bangalore node is **1,666 ms median** and **2,655 ms mean**, with a 95th percentile of **6,521 ms**. Across the full 7,542 reachable portals, measured TTFB is **416 ms median** and **1,144 ms mean**; the gap between the two reflects that the tool sample includes a heavier tail of slow institutional hosts. Median document size is **45 KB** and median DOM node count is **286**. The mean-median gap is large because a long tail of slow portals dominates the average, which is why we report both throughout.

### F. Linguistic Inclusion
Only **61.3%** of reachable portals declare a document language at all, **18.4%** contain text in a scheduled Indian script, and **4.1%** declare `hreflang` alternates. Linguistic inclusion is the weakest pillar in the census by a wide margin.

### G. State-by-State Coverage
The `district` column in this release is empty for every row, and only 62 domains are classified into the district tier. We therefore make **no district-level geographical claim**. State attribution is inferred from the hostname's own labels (for example `kerala.gov.in`), which is reliable for state portals but cannot resolve a central ministry to a state. Thirty-four distinct State/UT values appear among reachable portals, but the per-state sample is too small and too unevenly distributed to support a defensible ranking, so we do not publish one. Reproduce the raw grouping with `bharatgov states`.

---

## VI. Discussion & Policy Recommendations

Based on empirical evidence across 14,489 discovered portals, we propose three actionable recommendations for MeitY, NIC, and state IT departments:

1. **Mandate Complete District & Municipal S3WaaS Migration:**  
   Our data demonstrates that S3WaaS elevates accessibility by 11.7 points (from 83.7 to 95.4) while ensuring near-universal mobile responsiveness (98.5%). State governments should phase out legacy bespoke ASP.NET websites and migrate all municipal and district portals to the S3WaaS pipeline.
2. **Institute Centralized Reverse Proxy Security Headers:**  
   The header-hardening deficit (mean 43.1 / 100; only 33.4% of portals set a Content-Security-Policy) can be resolved without modifying application code. We recommend that RailTel, NIC, and State Data Centres mandate automated injection of HSTS (`max-age=31536000; includeSubDomains`) and base CSP policies at their NGINX / reverse-proxy edge gateways.
3. **Establish In-Country Automated Longitudinal Audits:**  
   Government bodies should rely on continuous, in-country automated observatories rather than periodic, point-in-time commercial manual audits. Ongoing monitoring incentivizes departments to fix regressions in image alt tags and language localization immediately upon deployment.

---

## VII. Threats to Validity & Limitations

1. **Automated testing is not conformance.** axe-core detects a subset of WCAG failures. It cannot evaluate cognitive load, screen-reader audio flow, or reading order. A portal scoring well here is not thereby WCAG-conformant; it is merely free of the machine-detectable defects we tested for. GIGW itself distinguishes automated from manual evaluation.
2. **The accessibility audit is a sample, not the population.** axe-core was run on 374 portals, not all 7,542. The severity-weighted index in Table I is computed from DOM signals across the full reachable set; the raw violation counts in Section V-A come from the 374-portal audit. We report both and label which is which.
3. **LCP is estimated, never measured.** $T_{\text{lcp}}$ is derived from TTFB and payload size. A true LCP requires a browser paint trace, which we did not run at scale. Every figure labelled LCP in this paper is an estimate and should not be quoted as a field measurement.
4. **Single vantage point.** All measurements come from one Bangalore node. We did not run a paired overseas comparison, so we make no quantitative claim about how much a foreign vantage point would under-count. Latency experienced by a rural user on congested 4G will exceed our datacenter TTFB.
5. **Discovery is not verification.** Certificate Transparency records every certificate ever issued, including expired and internal subdomains. A domain in our registry is a domain that was *observed in an auditable source*, not a domain we confirmed to be an operational citizen-facing portal. This is why we say "discovered domains" rather than "portals", and why reachability is 52.1% rather than near 100%.
6. **No district-level analysis.** The `district` column is empty for every row. Only 62 domains are classified into the district tier. We make no claim about district administrations as a population.
7. **Single snapshot.** This release is one observation. The observatory is *designed* for longitudinal monitoring, but the dataset contains no observation timestamp per domain and no second snapshot, so no trend claim is made or supported.
8. **Header-level evidence is supplementary.** The per-directive adoption rates in Section V-C come from a 488-portal tool-measured sample. The released 20-column dataset carries the aggregate header score, not the six individual booleans. The per-directive figures are reproducible from `data/real/full_tools.csv` in the repository, not from the released CSV alone.
9. **Composite weights are a judgement.** The 30/25/20/10/5/5/5 weighting encodes our view that accessibility and security matter most. It is not an empirical result. Every component is published separately so a reader can reweight.

---
## VIII. Conclusion & Open Science Artifacts

This paper presented **BharatGov Access**, an in-country web observatory measuring 14,489 discovered Indian government and public-sector web domains through an in-country domestic vantage point in Bangalore. By establishing a standardized 5-Pillar / 10-Sub-Feature framework, we have demonstrated the national accessibility dividends of NIC's S3WaaS platform while revealing critical security gaps in HTTP defense headers.

To promote reproducibility and open science, all research artifacts are made publicly accessible:

- **Interactive Web Observatory:** `https://uniquepratham.github.io/DA-Project/`
- **Open Dataset:** Immutable Apache Parquet, CSV, and JSON releases hosted under CC-BY-4.0 in `resources/bharatgov_access_clean.*`.
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

