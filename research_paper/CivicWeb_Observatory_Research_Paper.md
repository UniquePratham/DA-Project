# CivicWeb Observatory: A Cross-Country Measurement of Public-Sector Web Infrastructure

**Pratham Agarwal**, **Amit Kumar Bairagi**, and **Vishwajeet Nand Yaduraj**  
*Department of Computer Science and Engineering, Indian Institute of Technology Kharagpur, West Bengal 721302, India*  
*Subject: Data Analytics*  
*Correspondence: `{pratham.agarwal, amit.bairagi, vishwajeet.yaduraj}@iitkgp.ac.in`*

---

## Abstract

Government services have moved online almost everywhere, but the quality of the websites delivering them is rarely measured outside a handful of rich countries. Existing studies look at small samples, and the ones that crawl from abroad run into perimeter filters that make live sites look dead.

This paper reports a cross-country measurement of public-sector web infrastructure. We assembled a registry of **93,365 government and public-sector domains across 93 countries** from auditable sources: Certificate Transparency logs, official agency directories, ministry indexes, and sector-targeted certificate queries. We measured **2,011 domains across 82 countries**, using a deterministic tool for each dimension: a DOM-signal accessibility index, a wall-clock timer for latency, the OWASP directive set for security headers, a real TLS handshake, and a headless-Chromium render for mobile behaviour.

The central methodological problem is that a cloud provider operates in only 20 countries. A domestic probe is therefore impossible in most of the world. Rather than exclude those countries or pretend a foreign probe is domestic, we classify every measurement by its **vantage point**:

- **domestic** (19 countries, 1,360 domains) — the probe sits inside the country and describes what a citizen sees;
- **nearest** (64 countries, 651 domains) — the probe sits in the closest available region, in another country, and describes what a foreign client sees;
- **unmeasurable** (50 countries) — the nearest region is more than 6,000 km away, so a latency figure would describe the path rather than the portal.

This distinction produces the paper's main result. The same kind of portal answers in **479 ms** from inside its country and **1,156 ms** from the nearest foreign region. The **677 ms gap is the cost of distance, not a difference in the portals.** Accessibility falls from 87.0 to 84.0 and security from 44.2 to 33.2 across the same split, consistent with foreign clients receiving a degraded or blocked response.

Three further findings hold across the measured population. Transport encryption is effectively universal at **99.8%**, but header hardening averages only **44.2 of 100** on domestic probes. **Education is the weakest sector on security** at 26.6 across 420 domains, the largest single-sector deficit in the study. And **76 domains were disallowed by robots.txt** while **46 were refused by a bot filter**, both recorded as distinct outcomes rather than as failures.

We release the dataset, the crawler, the discovery scripts and the vantage model so every figure can be recomputed from the raw responses.

**Keywords:** web measurement, e-governance, digital public infrastructure, web accessibility, WCAG 2.1, OWASP secure headers, internet measurement, vantage point, cross-country comparison.

---

## I. Introduction

A citizen applying for a benefit, checking a land record, or filing a grievance now does it through a government website. When that site works, it saves a journey. When it does not, there is no fallback.

The measurement literature has two blind spots. The first is sample size: most studies examine a few dozen ministry homepages in one country. The second is vantage point: a crawler running from a foreign cloud region sees timeouts and 502s that a domestic client never sees, because state gateways and perimeter filters treat foreign addresses differently. A study that reports reachability from outside the country is measuring the firewall as much as the website.

### A. What this paper does

We built a registry, measured it from the best vantage available for each country, and recorded which vantage produced each row. Our contributions are:

- **A registry that can be audited.** 93,365 domains across 93 countries, each traceable to a Certificate Transparency record, an official directory, or a ministry index. No hostname was guessed from a naming pattern.
- **A vantage model that makes the constraint explicit.** Rather than exclude countries where a domestic probe is impossible, we measure them from the nearest region and label the row. The label is enforced in code, not asserted in prose.
- **The vantage finding.** Measuring the same population from inside and outside its countries isolates the cost of distance from the quality of the portal.
- **A reproducible artefact.** The dataset ships as Parquet, CSV and JSON under CC-BY-4.0, with a Python package, a CLI and a public dashboard.
- **A canonical release, not a raw log.** The measurement log is append-only and contains duplicate hosts and empty-body responses. The release deduplicates to one row per host and refuses to score a document too small to audit. Both defects are documented in Section IV-D rather than silently corrected.

---

## II. Related Work and Background

### A. Accessibility standards

WCAG 2.1 organises accessibility into four principles: content must be perceivable, operable, understandable and robust. National guidelines add local requirements; India's GIGW 3.0, for example, mandates skip links, text resizing and a high-contrast mode.

Automated tools check only part of this. axe-core catches missing alternative text, unlabelled form controls, insufficient contrast and similar structural faults. It cannot judge whether a page makes sense when read aloud in order, and it cannot judge cognitive load. We describe what we measured as automated conformance signals, not as WCAG certification.

**What we actually ran.** The cross-country release uses a **DOM-signal accessibility index**, not an axe-core audit. It scores four structural signals that axe-core also tests — alternative-text coverage, form-control labelling, a declared `html[lang]`, and a skip link — plus a toolbar affordance. We ran a real axe-core 4.x audit on a separate 400-domain India sample and report it in Section V-E as a calibration check, not as the population measurement. The distinction matters: the index is a proxy, and Section VII states what it cannot see.

### B. Performance and Core Web Vitals

Google's Core Web Vitals give three user-centred thresholds: Largest Contentful Paint under 2.5 seconds, Interaction to Next Paint under 200 milliseconds, and Cumulative Layout Shift under 0.1. Measuring LCP properly requires a browser paint trace. We did not run one at this scale, so every LCP figure here is an estimate derived from time to first byte and document size.

### C. Vantage point

Internet measurement has long known that where you measure from changes what you see. CDN routing, censorship middleboxes and national firewalls all produce different responses depending on the client's address. For government sites this effect is strong enough that a foreign vantage point is not merely noisier, it is systematically different. Section IV-C describes how we handle this when a domestic probe is unavailable.

---

## III. The Five-Pillar Framework

We group the measurements into five pillars, each with two sub-features, giving twelve variables.

| Pillar | Sub-feature group | Raw variables | Tool |
| :--- | :--- | :--- | :--- |
| **1. Accessibility** | Conformance | $A_{\text{alt}}$, $A_{\text{label}}$, $I_{\text{lang}}$, $I_{\text{skip}}$ | DOM inspection |
| | Affordances | $F_{\text{toolbar}}$ | DOM inspection |
| **2. Performance** | Latency | $L_{\text{ttfb}}$ | `perf_counter` |
| | Paint estimate | $T_{\text{lcp}}$ | derived from TTFB and payload |
| **3. Security** | Transport | $I_{\text{https}}$, $T_{\text{tls}}$ | `ssl` handshake |
| | Header hardening | $S_{\text{sec}}$ | OWASP directive set |
| **4. Inclusion** | Language | $I_{\text{multi}}$ | `html[lang]`, `hreflang`, script detection |
| | Mobile | $I_{\text{mobile}}$ | 375 px Chromium render |
| **5. Architecture** | Platform | $A_{\text{cms}}$ | framework fingerprints |
| | Services | $I_{\text{services}}$ | DOM affordance scan |

### Pillar 1: Accessibility

**$S_{\text{axe}}$, the DOM-signal accessibility index.** Four structural signals, each read from the parsed document:

$$S_{\text{axe}} = 55 + 20 A_{\text{alt}} + 15 A_{\text{label}} + 5 I_{\text{lang}} + 5 I_{\text{skip}}$$

where $A_{\text{alt}}$ is the fraction of `<img>` elements with non-empty `alt`, $A_{\text{label}}$ is the fraction of form controls carrying an `aria-label`, `aria-labelledby`, `id` or `title`, $I_{\text{lang}}$ is 1 when `<html lang>` is declared, and $I_{\text{skip}}$ is 1 when a skip-to-content link is present. The result is clamped to $[0, 100]$.

The 55-point floor is deliberate and is a limitation, not a finding: a page with no images and no form fields scores 100 on the two coverage terms by vacuity. We therefore refuse to score a document smaller than 200 bytes at all (Section IV-D), because an empty body has nothing to audit and would otherwise score 90.

**Calibration against axe-core.** We ran a real axe-core 4.x audit on a separate 400-domain India sample. That sample and the cross-country release share only **five domains**, so the two cannot be calibrated against each other: there is no overlap to correlate. The axe-core result is therefore reported as an independent observation about a different population (Section V-E), not as validation of the index. This is a gap in the study, and Section VII states it as one.

### Pillar 2: Performance

**$L_{\text{ttfb}}$.** Wall-clock time from request dispatch to the first response byte, taken with `time.perf_counter()` on the probe.

**$T_{\text{lcp}}$, estimated Largest Contentful Paint.** Derived from the measured TTFB and the real document size:

$$T_{\text{lcp}} = \max\left(0.60, \; 1.30 \cdot \frac{L_{\text{ttfb}}}{1000} + \frac{S_{\text{kb}}}{180.0}\right)$$

This is an estimate. A true LCP needs a browser paint trace, which we did not run across the registry.

### Pillar 3: Security

**$I_{\text{https}}$.** True when the final URL after redirects is served over TLS.

**$S_{\text{sec}}$, the header-hardening score.** Scored against the OWASP Secure Headers Project directive set, read from the actual response headers:

$$S_{\text{sec}} = 25 I_{\text{hsts}} + 30 I_{\text{csp}} + 15 I_{\text{xfo}} + 10 I_{\text{xcto}} + 10 I_{\text{ref}} + 10 I_{\text{perm}}$$

**$T_{\text{tls}}$.** A real handshake via Python's `ssl` module records the issuer, the negotiated protocol, the cipher suite and the days remaining before expiry.

### Pillar 4: Inclusion

**$I_{\text{multi}}$.** True when `html[lang]` is a non-English tag, or the page declares `hreflang` alternates, or the text contains characters from a non-Latin script.

**$I_{\text{mobile}}$.** True when the page declares `width=device-width` and a real render at 375 pixels produces no horizontal overflow.

### Pillar 5: Architecture and services

**$A_{\text{cms}}$.** Fingerprinted from markers in the response body and headers. The matched marker is stored per domain so the classification can be checked.

**$I_{\text{services}}$.** True when the DOM contains a search input or a grievance affordance.

### The composite index

$$
\begin{aligned}
M = {} & 0.30 \cdot S_{\text{axe}} + 0.25 \cdot S_{\text{sec}} \\
       & + 0.20 \cdot \max(0,\; 100 - 15 \cdot T_{\text{lcp}}) \\
       & + 10 \cdot I_{\text{multi}} + 5 \cdot I_{\text{mobile}} \\
       & + 5 \cdot I_{\text{services}} + 5 \cdot \mathbb{I}(A_{\text{cms}} = \text{s3waas})
\end{aligned}
$$

The binary terms are worth absolute points, not percentages. The result is clamped to [0, 100]. The weights are our judgement, not a finding; every component is published separately so a reader can reweight.

Because $S_{\text{axe}}$ has a 55-point floor, the composite inherits it: the minimum observed maturity is 24.4 and the maximum 88.5, so the index orders portals but does not span the scale. A reader should treat it as a ranking, not as a percentage of quality.

---

## IV. Method

### A. Discovery

We used four sources, all auditable:

| Source | Domains | What it is |
| :--- | ---: | :--- |
| Certificate Transparency | 92,418 | Every TLS certificate ever issued in a government namespace |
| Sector-targeted CT | 574 | Certificate queries for health, judiciary, finance and similar labels |
| Agency directories | 424 | Official pages listing a government's own agencies |
| Ministry indexes | 373 | Official pages listing a government's own ministries |

We deliberately did **not** generate hostnames from naming conventions. An earlier version of this work did, producing candidates like `finance.up.gov.in` on the assumption that state departments follow a pattern. Most do not exist, and measuring them inflated the unreachable count with things that were never portals. All 4,806 such candidates were removed.

The consequence is that reachability is **28.5%**, not the 85% a curated list would give. Certificate Transparency records certificates for staging hosts, internal subdomains and sites that have since been retired. A domain in our registry was *observed in an auditable source*; it was not confirmed to be an operational citizen portal.

### B. Politeness

The crawler obeys three rules, enforced in code:

1. **Honest identification.** The User-Agent names the project and gives a contact address. It does not claim to be a browser.
2. **robots.txt compliance.** Python's standard `urllib.robotparser` does not implement `*` wildcards or `$` anchors, so it silently allows paths that robots.txt forbids. `gov.uk` publishes `Disallow: /*/print$` and `Disallow: /search/all*`; the standard library permits both. We implement RFC 9309 matching instead.
3. **One request per second per host**, with a site's own `Crawl-Delay` overriding the default, a global concurrency cap, `Retry-After` honoured on 429/503, and exponential backoff after repeated failures.

A robots-disallowed URL is recorded as `robots_disallowed` and a bot-filter refusal as `blocked_by_waf`, both distinct from a failure. In this release, **76 domains were robots-disallowed and 46 were WAF-blocked**.

### C. The vantage model

A cloud provider operates in 20 countries. A domestic probe is therefore impossible in the other 229. We classify every country by the vantage that measured it:

| Class | Countries | What the measurement means |
| :--- | ---: | :--- |
| **domestic** | 19 | Probe inside the country. Describes what a citizen sees. |
| **nearest** | 180 | Probe in the closest region, in another country. Describes a foreign client. |
| **unmeasurable** | 50 | Nearest region over 6,000 km away. A latency figure would describe the path. |

Of the 180 countries classified `nearest`, 64 were actually measured in this release; the remaining 116 are classified and ready but not yet probed.

The nearest region is chosen by great-circle distance from the country's centroid to each available region, using a haversine calculation. The distance is recorded on every row.

The rule is enforced structurally: a row is marked `domestic_probe = true` only when the probe's region country equals the target country. A foreign probe can never be presented as domestic.

### D. Keeping failure separate from measurement

When a domain does not respond, we record why and leave its metrics empty. A DNS failure is stored as `DNS or connection failure`, a timeout as `HTTP 504`, a blocked request as `WAF challenge (HTTP 403)`, and the accessibility and security columns stay `null`. We never write a zero into a metric we did not measure.

Two cases need care, and both were bugs before they were rules:

**A response with no document.** A host can return `HTTP 200` with a body under 200 bytes — an empty shell, a redirect stub, or a bot-check page. There is no DOM to audit, so the coverage terms in the accessibility index would score it 100 by vacuity and the page would land at 90.0, above the population mean. The canonical release refuses to score any document under 200 bytes: the row keeps its status, latency and the SHA-256 of what arrived, and every content score is `null`. 33 rows were affected.

**A host measured twice.** The measurement log is append-only, so a host measured in two jobs appears twice. 128 hosts were measured more than once, giving 2,143 rows for 2,011 distinct domains. The canonical release keeps the latest measurement per host, because a later observation supersedes an earlier one. Aggregating the raw log would double-count those hosts in every mean and inflate the population by 6.6%.

---

## V. Findings

The dataset contains **2,011 measured domains across 82 countries**, of which **573 (28.5%)** responded.

### A. The vantage finding

This is the paper's main result. The same measurement, taken from two vantage points:

| Vantage | n | Reach | Acc. | Sec. | Mat. | TTFB |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **domestic** | 1,360 | 29.3% | 87.0 | 44.2 | 61.3 | **479 ms** |
| **nearest** | 651 | 26.9% | 84.0 | 33.2 | 53.8 | **1,156 ms** |

The **677 ms latency gap** is the cost of distance. Accessibility falls by 3.0 points and security by 11.0 across the same split, which is consistent with foreign clients receiving a degraded or blocked response rather than a different population of portals.

A single-vantage study cannot separate these two effects. That separation is the contribution.

### B. Security is the weakest pillar

Transport encryption is effectively universal: **99.8%** of reachable domains serve HTTPS. Header hardening is not. Mean $S_{\text{sec}}$ is **44.2 of 100** on domestic probes, and the two strongest controls are the least deployed.

The practical consequence is concrete. A citizen on public Wi-Fi is protected in transit but not against a downgrade attack, because HSTS is missing on roughly half the estate. A portal with a login form is not protected against injected script, because most have no CSP. Both are edge configuration changes that need no application work.

### C. Sector differences

Sector is inferred from the hostname, so only sectors with a dedicated naming convention can be separated. We report a sector mean only when at least ten of its domains answered; below that the mean is one or two portals wearing a sector label.

| Sector | Domains | Reachable | Accessibility | Security |
| :--- | ---: | ---: | ---: | ---: |
| general | 1,354 | 393 | 86.4 | 44.9 |
| education | 420 | 129 | 85.2 | **26.6** |
| judiciary | 62 | 24 | 81.8 | 34.6 |
| health | 62 | 12 | 88.1 | 50.4 |

Three findings:

1. **Education is the weakest sector on security** at 26.6 across 420 domains, the largest single-sector deficit in the study. That is a template-level defect, not individual neglect.
2. **The judiciary is the weakest on accessibility** at 81.8, and it is second-weakest on security at 34.6. Courts are the one sector near the bottom of both pillars at once.
3. **Health leads on both pillars** at 88.1 accessibility and 50.4 security, the only sector above the population mean on both.

Sectors with fewer than ten reachable domains — transport (41 domains, 9 reachable), finance (29, 3), social (11, 2), police (16, 1), agriculture (9, 0), defence (6, 0), environment (1, 0) — are excluded from the table. Their reachability is reported in the dataset but their pillar means are not, because a mean over one or two portals is not a sector finding.

### D. Inclusion

**41.2%** of reachable domains carry content in a non-English language or script, and **80.3%** declare a responsive viewport. Language inclusion is the weakest pillar by a wide margin, and it is the one most likely to matter to the citizens who need government services most.

### E. Calibration: a real axe-core audit

The cross-country release scores accessibility with a DOM-signal index, not axe-core. To check whether that index is measuring something real, we ran a genuine axe-core 4.x audit on a separate 400-domain India sample in headless Chromium, restricted to the `wcag2a`, `wcag2aa`, `wcag21a` and `wcag21aa` rule tags.

| Measure | Value |
| :--- | ---: |
| Domains audited | 400 |
| Mean WCAG violations per portal | **3.48** |
| Mean critical violations | 0.91 |
| Mean serious violations | 2.30 |
| Portals with zero violations | **4.5%** |
| Mean axe-core score | 74.5 |

Two things follow. First, the accessibility problem is real and severe: fewer than one portal in twenty passes a machine audit with no violations. Second, the index and axe-core measure different things. The two samples share only five domains, so they cannot be correlated, and the index cannot be validated against axe-core with this data. The axe-core figure is an independent observation about a different population, and it is the more trustworthy of the two because it comes from a standard tool.

---

## VI. What Should Change

**Set security headers at the reverse proxy.** Mean hardening is 44.2 and the strongest controls are the least deployed. None of this requires touching application code. A baseline CSP and HSTS with `max-age=31536000; includeSubDomains` at the edge would move the whole estate.

**Treat accessibility as a template decision.** The tightness of the violation distribution means the fix is templated rather than individual. Where a good template is used, accessibility is good. Education's 420 domains scoring 26.6 on security is a procurement problem, not 420 separate problems.

**Measure from inside the country, and say which vantage you used.** A point-in-time audit from abroad measures the firewall. A domestic probe measures the portal. Where a domestic probe is impossible, label the row rather than excluding the country.

---

## VII. Limitations

1. **Automated testing is not conformance.** axe-core catches a subset of WCAG failures. It cannot judge cognitive load, screen-reader audio flow or reading order. A domain scoring well here is free of the machine-detectable defects we tested for; it is not thereby WCAG-conformant.

2. **LCP is estimated, never measured.** $T_{\text{lcp}}$ is derived from TTFB and payload size. A true LCP needs a browser paint trace, which we did not run at scale.

3. **Nearest probes are not domestic.** 651 of 2,011 rows were measured from a probe in another country. The `domestic_probe` column says which. Any claim about what a citizen experiences must filter on it.

4. **Discovery is not verification.** A domain in the registry was observed in an auditable source. It was not confirmed to be an operational citizen portal, which is why reachability is 28.5% rather than near 100%.

5. **One snapshot.** This release is a single observation. The dataset carries no per-domain timestamp series, so no trend claim is supported.

6. **Sector is inferred from the hostname.** It is reliable for dedicated domains (`health.`, `court.`) and puts general portals in `general`. 1,354 of 2,011 rows are `general`, so the sector comparison is a comparison of the identifiable subset, not the whole population.

7. **The composite weights are a judgement.** The 30/25/20/10/5/5/5 weighting encodes our view that accessibility and security matter most. It is not an empirical result.

8. **The 50 unmeasurable countries are genuinely out of reach** with one provider. A latency figure from 4,000 km describes the ocean cable, not the portal.

9. **A country code can collide with a missing-value sentinel.** Namibia's ISO-3166 alpha-2 code is `NA`, which is also the default missing-value token in most CSV readers. Every Namibian row was silently dropped from the first build of these aggregates — ten domains and one whole country, with no error raised. The released reader disables the default sentinel list and treats only an empty field as missing. Anyone re-analysing the CSV with a default reader will reproduce the bug, so the reader ships with the dataset.

10. **The accessibility index is a proxy, not an audit.** The cross-country release scores four structural signals read from the parsed DOM. It is not axe-core, and it cannot be validated against axe-core with this data because the two samples share only five domains. The 400-domain axe-core audit in Section V-E is the trustworthy accessibility measurement, and it covers one country. A reader who needs a defensible accessibility figure should use that, not the index.

11. **The 55-point floor in the index is a design choice, not a finding.** A page with no images and no form fields scores 100 on the two coverage terms by vacuity. This is why the index compresses the population into a narrow band (55–100) and why its mean of 86.1 should not be read as "86% accessible". It is a relative ordering, not an absolute level.

12. **An empty body is not an accessible page.** A host returning `HTTP 200` with a body under 200 bytes has no DOM to audit. The crawler's coverage terms scored such a page at 90.0 because there was nothing to fail. The canonical release refuses to score any document under 200 bytes and records it as `HTTP 200 with an empty body`; 33 rows were affected. A reader using the raw append-only log will reproduce the inflated score.

13. **The raw log is append-only and must not be aggregated directly.** 128 hosts were measured in more than one job, giving 2,143 rows for 2,011 distinct domains. The canonical release keeps the latest measurement per host. Aggregating the raw log double-counts those hosts in every mean and inflates the population by 6.6%.

---

## VIII. Conclusion

We measured 2,011 public-sector web domains across 82 countries, from the best vantage available for each, and recorded which vantage produced every row.

The picture is not one of collapse but of unevenness. Transport encryption is essentially solved at 99.8%. Header hardening is not, at 44.2. Accessibility is mediocre almost everywhere and excellent almost nowhere, and the tightness of that distribution means the fix is templated rather than individual.

The methodological result is that **distance costs 677 ms**. A study that measures only from inside, or only from outside, cannot see that. Recording the vantage on every row is what makes the comparison possible, and it is the difference between a measurement and an assertion.

Everything in this paper can be recomputed from the released data. The dataset ships as Parquet, CSV and JSON under CC-BY-4.0; the crawler, discovery scripts and vantage model are in the repository; and the observatory is live at `https://uniquepratham.github.io/`.

```python
import civicweb_observatory as cwo

cwo.load()                    # 2,011 measured domains
cwo.load(reachable=True)      # 573 that answered
cwo.country_summary()         # one row per country
cwo.sector_summary()          # one row per sector
cwo.vantage_comparison()      # domestic vs nearest
```

---

## References

1. World Wide Web Consortium, "Web Content Accessibility Guidelines (WCAG) 2.1," W3C Recommendation, June 2018. [Online]. Available: https://www.w3.org/TR/WCAG21/
2. Deque Systems, "axe-core: Accessibility Engine for Automated Web UI Testing," version 4.x. [Online]. Available: https://github.com/dequelabs/axe-core
3. Google, "Core Web Vitals," web.dev. [Online]. Available: https://web.dev/vitals/
4. OWASP Foundation, "OWASP Secure Headers Project." [Online]. Available: https://owasp.org/www-project-secure-headers/
5. Certificate Transparency, crt.sh query interface. [Online]. Available: https://crt.sh/
6. RFC 9309, "Robots Exclusion Protocol," IETF, September 2022.
7. Ministry of Electronics and Information Technology, Government of India, "Guidelines for Indian Government Websites (GIGW) 3.0," 2019.
8. National Informatics Centre, "S3WaaS: Secure, Scalable and Sugamya Website as a Service." [Online]. Available: https://s3waas.gov.in/
