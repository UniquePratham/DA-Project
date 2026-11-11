# BharatGov Access: An In-Country Measurement Study of India's Public Web Infrastructure

**Pratham Agarwal**, **Amit Kumar Bairagi**, and **Vishwajeet Nand Yaduraj**  
*Department of Computer Science and Engineering, Indian Institute of Technology Kharagpur, West Bengal 721302, India*  
*Subject: Data Analytics*  
*Correspondence: `{pratham.agarwal, amit.bairagi, vishwajeet.yaduraj}@iitkgp.ac.in`*

---

## Abstract

Most Indians who deal with the state now do so through a website. Welfare transfers, land records, exam results, tax filings and court listings all pass through government portals, and the quality of those portals decides whether a citizen can actually finish the task. Yet we know very little, in measured terms, about how good they are. Existing studies tend to look at a few dozen ministry homepages, and the ones that crawl from outside India run into perimeter filters that make live sites look dead.

This paper reports a measurement study of Indian government websites taken from a single cloud node inside the country. We assembled a registry of **14,489 government and public-sector domains** from three sources that can each be checked: public Certificate Transparency logs, a curated list of named institutions, and outbound links harvested from portals that were already responding. We did not invent any hostname from a naming pattern. Of the 14,489, **7,542 (52.1%)** answered a live HTTP request, and those are the portals we analyse.

We measured five things about each portal, using a standard tool for each rather than a proxy: accessibility with axe-core, latency with a wall-clock timer, security headers against the OWASP directive set, TLS with a real handshake, and mobile behaviour by rendering the page at 375 pixels in a headless browser.

Three results stand out.

First, accessibility is poor almost everywhere but not catastrophically so. An axe-core audit of 374 portals found a mean of **3.48 WCAG violations** per portal, and only **4.8%** passed with none. The distribution is narrow, which tells us the problem sits in shared templates rather than in a handful of neglected sites. Portals running NIC's S3WaaS/Drupal distribution score **95.4** on our severity-weighted index, against **82.0** for WordPress and **83.7** for legacy ASP.NET.

Second, security headers are the weakest link. Almost every portal serves HTTPS (**99.5%**), but the mean header-hardening score is only **43.1 out of 100**, and just **33.4%** set a Content-Security-Policy. Transport encryption is in place; the headers that stop clickjacking and script injection are not.

Third, latency has a long tail. Median time to first byte across all reachable portals is **416 ms**, but the mean is **1,144 ms**, because a small number of very slow hosts pull the average up. Only **18.4%** of portals carry text in a scheduled Indian language, and although **86.7%** declare a mobile viewport, **29.1%** still overflow horizontally when actually rendered on a phone-sized screen.

We release the dataset, the crawler and the discovery scripts so that every number here can be recomputed from the raw responses.

**Keywords:** web measurement, e-governance, digital public infrastructure, web accessibility, WCAG 2.1, Core Web Vitals, GIGW 3.0, internet measurement, cyber security.

---

## I. Introduction

Over the last fifteen years the Indian government has moved a large share of its citizen-facing work onto the web. A person applying for a scholarship, checking a land record, downloading a court order or filing a grievance now does it through a portal run by a ministry, a state department, a district collectorate or a municipal body. When those portals work, they save a journey and a bribe. When they do not, the citizen has no fallback.

The problem is that nobody has measured the whole estate. We have anecdotes, a few small studies, and the annual accessibility reports that civil-society groups publish. What we do not have is a systematic picture across administrative levels, and we certainly do not have one that separates the effect of the technology a portal runs on from the effect of who runs it.

### A. Why the existing evidence is thin

Three problems recur in the literature.

The first is sample size. Most studies look at between fifty and two hundred central ministry homepages. That is where the press attention is, but it is not where most citizens interact with the state. District and municipal portals carry the routine administrative work, and they are almost never measured.

The second is where the crawler sits. A large number of Indian government sites sit behind state data-centre gateways and perimeter filters that behave differently for foreign client addresses. A crawler running from a US cloud region will see timeouts and 502s that a domestic client never sees. Any study that reports reachability from outside India is measuring the firewall as much as the website.

The third is metric inflation. Some tools report seventy or more variables, many of them unvalidated, and then assign a zero to every variable of an unreachable site. That turns a network failure into an accessibility failure and quietly corrupts every downstream average.

### B. What this paper does

We built a registry, crawled it from inside India, and measured five dimensions with a real tool for each. Our contributions are:

- **A registry that can be audited.** 14,489 government and public-sector domains, each traceable to a Certificate Transparency record, a named institution, or a link found on a live portal. No hostname was guessed from a pattern.
- **Measurements taken from inside the country.** All requests originated from a cloud node in Bangalore on domestic transit, which removes the perimeter-filter confound.
- **A five-pillar framework with twelve measured variables.** Each variable is tied to a specific tool, and the mapping is published so a reader can see exactly what produced each number.
- **An empirical comparison of portal platforms.** We separate S3WaaS, Drupal, WordPress, legacy ASP.NET, custom CMS and modern SPAs, and show that the platform a department chooses predicts its accessibility far better than it predicts its security.
- **A reproducible artefact.** The dataset ships as Parquet, CSV and JSON under CC-BY-4.0, with a Python package, a command-line interface and a public dashboard.

---

## II. Related Work and Background

### A. Accessibility standards and GIGW

WCAG 2.1 organises accessibility into four principles: content must be perceivable, operable, understandable and robust. India's own Guidelines for Indian Government Websites, now at version 3.0, add requirements that matter locally, including skip links, text resizing controls, a high-contrast mode and provision for regional languages.

Automated tools can check only part of this. axe-core, which we use, catches missing alternative text, unlabelled form controls, insufficient contrast and similar structural faults. It cannot judge whether a page makes sense when read aloud in order, and it cannot judge cognitive load. We are careful throughout to describe what we measured as automated conformance signals, not as WCAG certification.

### B. Performance and Core Web Vitals

Google's Core Web Vitals give three user-centred thresholds: Largest Contentful Paint under 2.5 seconds, Interaction to Next Paint under 200 milliseconds, and Cumulative Layout Shift under 0.1. Measuring LCP properly requires a browser paint trace. We did not run one at this scale, so every LCP figure in this paper is an estimate derived from time to first byte and document size, and we label it as such wherever it appears.

### C. Measurement vantage point

Internet measurement has long known that where you measure from changes what you see. CDN routing, censorship middleboxes and national firewalls all produce different responses depending on the client's address. For Indian government sites this effect is strong enough that a foreign vantage point is not merely noisier, it is systematically wrong about reachability. We therefore measure from inside India and say so plainly, while acknowledging in Section VII that we did not run a paired overseas comparison and so cannot put a number on the size of the bias.

---

## III. The Five-Pillar Framework

We group the measurements into five pillars, each with two sub-features, giving twelve variables in total. The point of the grouping is to keep accessibility, speed, security, inclusion and platform separate, because they turn out to be largely independent of one another and averaging them too early hides the interesting variation.

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

### Pillar-to-variable mapping

The table below shows which raw measurement feeds which pillar, and which tool produced it. We publish this because a framework with twelve variables is easy to describe vaguely and hard to reproduce.

| Pillar | Sub-feature group | Raw variables | Tool |
| :--- | :--- | :--- | :--- |
| **1. Accessibility** | Conformance | $V_{\text{axe}}$, $S_{\text{axe}}$ | axe-core 4.x |
| | GIGW affordances | $F_{\text{toolbar}}$ | DOM inspection |
| **2. Performance** | Latency | $L_{\text{ttfb}}$ | `perf_counter` |
| | Paint estimate | $T_{\text{lcp}}$ | derived from TTFB and payload |
| **3. Security** | Transport | $I_{\text{https}}$, $T_{\text{tls}}$ | `ssl` handshake |
| | Header hardening | $S_{\text{sec}}$ | OWASP directive set |
| **4. Inclusion** | Language | $I_{\text{multi}}$ | `html[lang]`, `hreflang`, script detection |
| | Mobile | $I_{\text{mobile}}$ | 375 px Chromium render |
| **5. Architecture** | Platform | $A_{\text{cms}}$ | framework fingerprints |
| | Services | $I_{\text{services}}$ | DOM affordance scan |

### Pillar 1: Accessibility

**$V_{\text{axe}}$, the violation count.** We run axe-core 4.x in headless Chromium against the rendered DOM, restricted to the `wcag2a`, `wcag2aa`, `wcag21a` and `wcag21aa` rule tags, and count violations by impact level.

**$S_{\text{axe}}$, the severity-weighted index.** axe-core does not produce a single score, so we define one and state the weights openly:

$$S_{\text{axe}} = \max\left(0, \; 100 - 12 V_{\text{crit}} - 6 V_{\text{ser}} - 3 V_{\text{mod}} - 1 V_{\text{min}}\right)$$

The weights reflect how much each impact level matters for conformance. They are a convention, not a measurement, and we report the raw counts alongside so a reader can apply different weights.

**$F_{\text{toolbar}}$, the GIGW toolbar.** A boolean for whether the page offers font resizing, a contrast toggle or a skip link, as GIGW Section 5 requires.

### Pillar 2: Performance

**$L_{\text{ttfb}}$, time to first byte.** Wall-clock time from request dispatch to the first response byte, taken with `time.perf_counter()` on the Bangalore node.

**$T_{\text{lcp}}$, estimated Largest Contentful Paint.** Derived from the measured TTFB and the real document size:

$$T_{\text{lcp}} = \max\left(0.60, \; 1.30 \cdot \frac{L_{\text{ttfb}}}{1000} + \frac{S_{\text{kb}}}{180.0}\right)$$

This is an estimate. A true LCP needs a browser paint trace, which we did not run across the registry.

### Pillar 3: Security

**$I_{\text{https}}$.** True when the final URL after redirects is served over TLS.

**$S_{\text{sec}}$, the header-hardening score.** Scored against the OWASP Secure Headers Project directive set, read from the actual response headers:

$$S_{\text{sec}} = 25 I_{\text{hsts}} + 30 I_{\text{csp}} + 15 I_{\text{xfo}} + 10 I_{\text{xcto}} + 10 I_{\text{ref}} + 10 I_{\text{perm}}$$

The indicators are `Strict-Transport-Security`, `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options: nosniff`, `Referrer-Policy` and `Permissions-Policy`.

**$T_{\text{tls}}$, the certificate.** A real handshake via Python's `ssl` module records the issuer, the negotiated protocol, the cipher suite and the days remaining before expiry.

### Pillar 4: Inclusion

**$I_{\text{multi}}$.** True when `html[lang]` is a non-English tag, or the page declares `hreflang` alternates, or the text contains characters from a scheduled Indian script.

**$I_{\text{mobile}}$.** True when the page declares `width=device-width` and a real render at 375 pixels produces no horizontal overflow. Both conditions are required, because declaring a viewport is not the same as fitting on a phone.

### Pillar 5: Architecture and services

**$A_{\text{cms}}$.** Fingerprinted from markers in the response body and headers: `s3waas` and `sites/all/themes` for S3WaaS, `wp-content` and `wp-json` for WordPress, `drupal` and `core/misc/drupal` for Drupal, `__VIEWSTATE` and `.aspx` for legacy ASP.NET, `_next/static` and `ng-version` for modern SPAs. The matched marker is stored per portal so the classification can be checked.

**$I_{\text{services}}$.** True when the DOM contains a search input or a grievance affordance such as CPGRAMS, Samadhan or a helpline.

### The composite index

We combine the pillars into a single maturity score:

$$
\begin{aligned}
M = {} & 0.30 \cdot S_{\text{axe}} + 0.25 \cdot S_{\text{sec}} \\
       & + 0.20 \cdot \max(0,\; 100 - 15 \cdot T_{\text{lcp}}) \\
       & + 10 \cdot I_{\text{multi}} + 5 \cdot I_{\text{mobile}} \\
       & + 5 \cdot I_{\text{services}} + 5 \cdot \mathbb{I}(A_{\text{cms}} = \text{s3waas})
\end{aligned}
$$

The binary terms are worth absolute points, not percentages, so a portal that satisfies all of them and scores perfectly on the three continuous terms reaches exactly 100. The result is clamped to [0, 100].

Two things should be said about this index. The weights are our judgement, not a finding; we think accessibility and security matter most, and a reader who disagrees can recompute $M$ from the published per-pillar columns. And because accessibility is uniformly high across the registry, the composite compresses differences between tiers. We therefore report the pillars separately in Section V and treat the composite as a summary rather than a verdict.

The formula is available as `bharatgov_access.maturity_index()` so anyone can score a portal they measured themselves.

---

## IV. How the Measurement Was Built

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      Discovered Registry (N = 14,489)                  │
 │    State Depts (7,340) · Academic (6,771) · Judiciary (203)            │
 │    Central (60) · Districts (62) · Municipalities (30) · PSUs (23)     │
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
 │       • Live Observatory (uniquepratham.github.io/DA-Project)          │
 └────────────────────────────────────────────────────────────────────────┘
```

### A. Where the domains came from

This is the part of the study most likely to be questioned, so we describe it in full.

We used three sources. The first was Certificate Transparency, the public append-only log of every TLS certificate ever issued. Querying the `gov.in`, `nic.in`, `ac.in`, `res.in`, `edu.in`, `org.in`, `ernet.in`, `drdo.in`, `cdac.in` and `mil.in` namespaces through crt.sh yielded 7,803 unique hostnames. The second was a curated registry of named Indian institutions, which contributed 633 domains with real entity names and tiers. The third was a link crawl: we took the 4,238 portals that had already responded, fetched each one, and extracted every outbound government link from the HTML. That produced 6,018 further domains.

We deliberately did **not** generate hostnames from naming conventions. An earlier version of this work did exactly that, producing candidates like `finance.up.gov.in` on the assumption that state departments follow a pattern. Most of those do not exist, and measuring them inflated the unreachable count with things that were never portals. We removed all 4,806 such candidates.

The consequence is that our reachability rate is 52.1%, not the 85% a curated list would give. That is the honest number for a registry built this way: Certificate Transparency records certificates for staging hosts, internal subdomains and sites that have since been retired. A domain in our registry is a domain that was *observed in an auditable source*, not a domain we confirmed to be an operational citizen portal. We use the word "discovered" rather than "census" for exactly this reason.

### B. The vantage point

Every request originated from one cloud node in Bangalore on domestic tier-1 transit. We did not run a paired overseas comparison, so we make no claim about how much a foreign vantage point would under-count. What we can say is why we chose a domestic node: Indian government portals are frequently fronted by state gateways that treat foreign addresses differently, and measuring from inside removes that variable.

The cost is that our latency figures describe one domestic path, not the experience of a citizen on a congested 4G connection in a rural district. Section VII records this.

### C. Keeping failure separate from measurement

When a portal does not respond, we record why and leave its metrics empty. A DNS failure is stored as `DNS Inactive`, a timeout as `504 Timeout`, a blocked request as `403 WAF Challenge`, and the accessibility and security columns stay `null`. We never write a zero into a metric we did not measure, because a zero would silently drag down every average it touches.

---

## V. Findings

The registry contains **14,489 government and public-sector domains**, of which **7,542 (52.1%)** responded and are analysed here.

### TABLE I: Breakdown by governance tier

All figures are computed from the released dataset over reachable portals only. Reproduce with `bharatgov tiers`.

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

Three things in this table are worth pausing on.

Reachability is fairly flat across tiers, sitting between 50% and 80% everywhere. That flatness is itself informative: it suggests the main reason a domain fails is the discovery method rather than the tier, since Certificate Transparency contributes dead hosts to every category roughly equally.

Central ministries lead on both accessibility (93.5) and security (91.4), which is what one would hope from the best-funded tier. But the judiciary has the highest GIGW toolbar penetration (83.5%) with only middling security (76.1), and academic institutions, which are the largest group by far, have the worst security score of any tier at 26.5.

Multilingual content is the weakest measure nationally at 17.2%, well below everything else.

### A. What axe-core actually found

Table I reports accessibility as a severity-weighted index. To keep the raw evidence visible, we also ran axe-core directly on a random sample of **374 reachable portals** and report the unweighted counts:

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

The distribution is tight: standard deviation 2.1, maximum 13. That tightness is the finding. If a few portals were badly broken and the rest were fine, we would see a long tail. Instead the violations are spread thinly across almost every portal, which points at shared templates rather than individual neglect. Only 4.8% of audited portals pass cleanly.

The dominant impact class is *serious*, at 861 of 1,303 violations, or 66%. In axe-core that class covers missing form labels, insufficient colour contrast and duplicate IDs. These are exactly the defects a template fixes once for every site built on it.

### B. Platform matters for accessibility, not for security

Table II compares the six platforms we could fingerprint.

### TABLE II: Comparison of web platforms

Reachable portals only; unreachable hosts are excluded rather than counted as an unknown platform. Reproduce with `bharatgov arch`.

| Metric | S3WaaS Drupal | Custom Dynamic CMS | Legacy ASP.NET | Modern SPA | WordPress | Drupal |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Reachable Portals Observed** | 661 (8.8%) | 3,838 (50.9%) | 1,247 (16.5%) | 582 (7.7%) | 978 (13.0%) | 236 (3.1%) |
| **Mean Accessibility ($S_{\text{axe}}$)** | **95.4** | 86.6 | 83.7 | 89.1 | 82.0 | 92.7 |
| **GIGW Toolbar Penetration** | 97.9% | 57.7% | 84.9% | 53.3% | 95.8% | **97.9%** |
| **Mean Security Headers ($S_{\text{sec}}$)** | 47.6 | 41.6 | 56.0 | 52.0 | 25.2 | **76.4** |
| **Composite Maturity ($M$)** | **75.5** | 57.5 | 61.4 | 61.3 | 48.4 | 72.7 |

The S3WaaS dividend is real, but it is one-dimensional. S3WaaS scores 95.4 on accessibility against 82.0 for WordPress, a 13.4-point gap, and reaches 97.9% GIGW toolbar penetration. On security it scores 47.6, which is below legacy ASP.NET at 56.0 and far below non-NIC Drupal deployments at 76.4.

The explanation is not mysterious. A template can ship accessible markup, because markup is what a template is. It cannot ship a content security policy, because that is set at the reverse proxy by whoever operates the deployment. NIC controls the template; state data centres control the edge. The accessibility dividend therefore travels with the template, and the security deficit stays with the operator.

### C. The security gap

Almost every reachable portal serves HTTPS (**99.5%**) and completes a valid TLS handshake (**99.8%**). The headers are a different story. On the 488-portal tool-measured sample:

| Directive | Portals setting it |
| :--- | ---: |
| `Strict-Transport-Security` | 51.0% |
| `Content-Security-Policy` | **33.4%** |
| `X-Frame-Options` | 53.1% |
| `X-Content-Type-Options` | 50.2% |
| `Referrer-Policy` | 40.8% |
| `Permissions-Policy` | **33.0%** |
| **Mean hardening score** | **43.1 / 100** |

Transport encryption is effectively universal, but the headers that defend against SSL-stripping, clickjacking and cross-site scripting are set by about half of portals at best, and by only a third for the two strongest controls. TLS itself is healthy: 82.8% negotiated TLS 1.3 and the rest TLS 1.2, with nothing observed on a deprecated protocol.

The practical consequence is concrete. A citizen on public Wi-Fi is protected in transit but not against a downgrade attack, because HSTS is missing on half the estate. A portal with a login form is not protected against injected script, because two-thirds have no CSP. Both are edge configuration changes that need no application work, which is why Section VI recommends them at the proxy.

### D. Mobile: declared versus actual

Declaring a viewport is not the same as fitting on a phone, so we rendered every audited portal at 375 pixels and measured the overflow.

- **86.7%** declare `width=device-width`.
- **29.1%** still overflow horizontally, by a mean of **75 px**.
- The gap between those two numbers, 86.7% declared against 70.9% actually fitting, is the measure of what we call viewport theatre.

### E. Latency has a long tail

On the 488-portal tool-measured sample, TTFB is **1,666 ms median** and **2,655 ms mean**, with a 95th percentile of **6,521 ms**. Across all 7,542 reachable portals it is **416 ms median** and **1,144 ms mean**. The difference between the two samples is that the tool sample over-represents heavy institutional hosts.

Median document size is **45 KB** and median DOM node count is **286**. Throughout this paper we report both median and mean, because the gap between them is itself a finding: a small number of very slow portals dominate the average, and quoting only the mean would misrepresent the typical experience.

### F. Language is the weakest pillar

Only **61.3%** of reachable portals declare a document language at all. **18.4%** contain text in a scheduled Indian script, and **4.1%** declare `hreflang` alternates. For a country with twenty-two scheduled languages, this is the largest gap in the study.

### G. What we cannot say about states and districts

The `district` column is empty for every row in this release, and only 62 domains are classified into the district tier. We therefore make no district-level claim at all.

State attribution is inferred from the hostname's own labels, which works for `kerala.gov.in` but cannot resolve a central ministry to a state. Thirty-four distinct State/UT values appear among reachable portals, but the per-state samples are too small and too unevenly distributed to support a ranking, so we do not publish one. The raw grouping is available with `bharatgov states` for anyone who wants to look.

---

## VI. What Should Change

Three recommendations follow from the data.

**Move district and municipal portals onto S3WaaS.** The accessibility gap between S3WaaS and legacy ASP.NET is 11.7 points, and S3WaaS reaches 98.5% mobile responsiveness. State governments still running bespoke ASP.NET sites are paying to maintain a worse product. Migration is the single highest-leverage accessibility intervention available.

**Set security headers at the reverse proxy.** The mean hardening score is 43.1 and only 33.4% of portals set a CSP. None of this requires touching application code. RailTel, NIC and the State Data Centres can inject HSTS with `max-age=31536000; includeSubDomains` and a baseline CSP at their NGINX or equivalent edge. This is a configuration change with a measurable effect on the whole estate.

**Audit continuously, from inside the country.** A point-in-time commercial audit tells you what was wrong last quarter. A continuous in-country observatory tells you when a department breaks its own alt text after a redeploy. The second is what changes behaviour.

---

## VII. Limitations

We would rather state these plainly than have a reviewer find them.

1. **Automated testing is not conformance.** axe-core catches a subset of WCAG failures. It cannot judge cognitive load, screen-reader audio flow or reading order. A portal that scores well here is free of the machine-detectable defects we tested for; it is not thereby WCAG-conformant. GIGW itself distinguishes automated from manual evaluation.

2. **The accessibility audit is a sample.** axe-core ran on 374 portals, not all 7,542. The severity-weighted index in Table I comes from DOM signals across the full reachable set; the raw violation counts in Section V-A come from the 374-portal audit. We label which is which throughout.

3. **LCP is estimated, never measured.** $T_{\text{lcp}}$ is derived from TTFB and payload size. A true LCP needs a browser paint trace, which we did not run at scale. Every LCP figure here is an estimate and should not be quoted as a field measurement.

4. **One vantage point.** All measurements come from a single Bangalore node. We did not run a paired overseas comparison, so we cannot quantify the bias a foreign crawler would introduce. Latency for a rural user on congested 4G will exceed our datacenter TTFB.

5. **Discovery is not verification.** Certificate Transparency records every certificate ever issued, including expired and internal subdomains. A domain in our registry was observed in an auditable source; it was not confirmed to be an operational citizen portal. This is why reachability is 52.1% and why we say "discovered" rather than "census".

6. **No district-level analysis.** The `district` column is empty and only 62 domains are in the district tier. We make no claim about district administrations as a population.

7. **One snapshot.** This release is a single observation. The observatory is designed for longitudinal monitoring, but the dataset carries no per-domain timestamp and no second snapshot, so no trend claim is made or supported.

8. **Header-level evidence is supplementary.** The per-directive rates in Section V-C come from a 488-portal sample. The released 20-column dataset carries the aggregate header score, not the six individual booleans. The per-directive figures reproduce from `data/real/full_tools.csv` in the repository, not from the released CSV alone.

9. **The composite weights are a judgement.** The 30/25/20/10/5/5/5 weighting encodes our view that accessibility and security matter most. It is not an empirical result. Every component is published separately so a reader can reweight.

---

## VIII. Conclusion

We measured 14,489 discovered Indian government and public-sector web domains from inside the country, and 7,542 of them responded. The picture that emerges is not one of collapse but of unevenness.

Accessibility is mediocre almost everywhere and excellent almost nowhere: a mean of 3.48 axe-core violations per portal, with only 4.8% passing cleanly. The tightness of that distribution is the important part, because it means the fix is templated rather than individual. Where a good template is used, accessibility is good; S3WaaS portals score 95.4 against 82.0 for WordPress.

Security is the real deficit. Transport encryption is essentially solved at 99.5%, but header hardening sits at 43.1 out of 100 and only a third of portals set a content security policy. These are proxy configuration changes, not application rewrites, and they are the cheapest improvement available to the estate.

Language inclusion is the weakest pillar by a wide margin, at 18.4%.

Everything in this paper can be recomputed from the released data. The dataset ships as Parquet, CSV and JSON under CC-BY-4.0; the crawler and discovery scripts are in the repository; and the observatory is live at `https://uniquepratham.github.io/DA-Project/`.

```python
import bharatgov_access as bga

bga.load()                  # 14,489 discovered domains
bga.load(reachable=True)    # 7,542 that answered
bga.tier_summary()          # Table I
bga.architecture_summary()  # Table II
```

---

## References

1. World Wide Web Consortium, "Web Content Accessibility Guidelines (WCAG) 2.1," W3C Recommendation, June 2018. [Online]. Available: https://www.w3.org/TR/WCAG21/
2. Ministry of Electronics and Information Technology, Government of India, "Guidelines for Indian Government Websites (GIGW) 3.0," 2019.
3. Deque Systems, "axe-core: Accessibility Engine for Automated Web UI Testing," version 4.x. [Online]. Available: https://github.com/dequelabs/axe-core
4. Google, "Core Web Vitals," web.dev. [Online]. Available: https://web.dev/vitals/
5. OWASP Foundation, "OWASP Secure Headers Project." [Online]. Available: https://owasp.org/www-project-secure-headers/
6. National Informatics Centre, "S3WaaS: Secure, Scalable and Sugamya Website as a Service." [Online]. Available: https://s3waas.gov.in/
7. Certificate Transparency, crt.sh query interface. [Online]. Available: https://crt.sh/
8. CERT-In, "Guidelines on Information Security Practices for Government Entities," Ministry of Electronics and Information Technology.
