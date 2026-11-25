# CivicWeb Observatory — Data Dictionary

The exact schema of the released dataset. Every column below exists in
`data/real/global_measurements_canonical.csv` and in the bundled Parquet; nothing is
described that is not shipped.

> **Granularity:** one row per measured domain. A domain that did not answer
> keeps its row, with `is_reachable = false`, a `measurement_reason`, and every
> content metric `null`.

---

## 1. Identity and response

| Column | Type | Description | Example |
|---|---|---|---|
| `domain_name` | string | The hostname that was measured | `gov.uk` |
| `final_url` | string \| null | URL after redirects; null when nothing was served | `https://www.gov.uk/` |
| `status_code` | int \| null | Final HTTP status; null on DNS or connection failure | `200` |
| `is_reachable` | boolean | True when a page was served and scored | `true` |
| `measurement_reason` | string | Why the row is unreachable, or the status text | `HTTP 404`, `DNS or connection failure`, `WAF challenge (HTTP 403)` |
| `html_bytes` | int \| null | Size of the served document | `48213` |
| `sha256` | string \| null | SHA-256 of the response body, so the evidence is reproducible | `9f2c…` |

---

## 2. Accessibility

| Column | Type | Description | Range |
|---|---|---|---|
| `sub_accessibility_score` | float \| null | Severity-weighted axe-core index | 0–100 |
| `sub_has_gigw_toolbar` | boolean \| null | Font-resize or contrast control detected | `true` / `false` |

The index is $S_{\text{axe}} = \max(0, 100 - 12V_{\text{crit}} - 6V_{\text{ser}} - 3V_{\text{mod}} - 1V_{\text{min}})$,
where $V$ is the count of axe-core violations at each impact level, restricted
to the `wcag2a`, `wcag2aa`, `wcag21a` and `wcag21aa` rule tags. The weights are a
convention, not a measurement.

---

## 3. Performance

| Column | Type | Description | Unit |
|---|---|---|---|
| `sub_response_latency_ms` | float \| null | Wall-clock time to first byte, measured on the probe | ms |
| `sub_lcp_est_sec` | float \| null | **Estimated** Largest Contentful Paint | seconds |

$T_{\text{lcp}} = \max(0.60, 1.30 \cdot L_{\text{ttfb}}/1000 + S_{\text{kb}}/180.0)$.
This is an estimate derived from TTFB and document size. A true LCP needs a
browser paint trace, which was not run across the registry.

A host that answered `HTTP 404` or a WAF challenge has a real latency but no
content to score, so it keeps `sub_response_latency_ms` and leaves every content
metric null.

---

## 4. Security

| Column | Type | Description | Range |
|---|---|---|---|
| `sub_https_enforced` | boolean \| null | Final URL served over TLS | `true` / `false` |
| `sub_security_headers_score` | float \| null | OWASP Secure Headers directive score | 0–100 |

$S_{\text{sec}} = 25 I_{\text{hsts}} + 30 I_{\text{csp}} + 15 I_{\text{xfo}} + 10 I_{\text{xcto}} + 10 I_{\text{ref}} + 10 I_{\text{perm}}$,
read from the actual response headers.

---

## 5. Inclusion

| Column | Type | Description |
|---|---|---|
| `sub_is_multilingual` | boolean \| null | Non-English `html[lang]`, `hreflang` alternates, or non-Latin script |
| `sub_mobile_responsive` | boolean \| null | `width=device-width` and no horizontal overflow at 375 px |

---

## 6. Architecture and services

| Column | Type | Description | Values |
|---|---|---|---|
| `sub_cms_architecture` | string \| null | Fingerprinted platform | `custom_dynamic_cms`, `wordpress`, `legacy_asp_net`, `modern_spa`, `drupal`, `s3waas_drupal` |
| `sub_has_citizen_services` | boolean \| null | Search input or grievance affordance in the DOM | `true` / `false` |

---

## 7. Composite index

| Column | Type | Description | Range |
|---|---|---|---|
| `observatory_maturity_score` | float \| null | Composite maturity | 0–100 |

$$M = 0.30 S_{\text{axe}} + 0.25 S_{\text{sec}} + 0.20 \max(0, 100 - 15 T_{\text{lcp}}) + 10 I_{\text{multi}} + 5 I_{\text{mobile}} + 5 I_{\text{services}} + 5 \mathbb{I}(A_{\text{cms}} = \text{s3waas})$$

The binary terms are worth absolute points, not percentages. The result is
clamped to `[0, 100]` and is **not** floored — an earlier release applied a 45.0
floor, which silently inflated the worst portals and made the index
non-reproducible from its own inputs.

---

## 8. Provenance — read this before making a claim

| Column | Type | Description |
|---|---|---|
| `probe_country` | string | ISO-3166 alpha-2 of the country measured |
| `probe_region` | string | Vultr region id that ran the probe, e.g. `blr`, `ams` |
| `probe_region_country` | string | ISO-3166 alpha-2 of the region's country |
| `domestic_probe` | boolean | **True only when `probe_region_country == probe_country`** |
| `measured_at` | string | UTC timestamp, ISO 8601 |
| `job_id` | string | The measurement job that produced the row |

`domestic_probe` is the column that decides what a row can support:

- `true` — the probe sat inside the country. The row describes what a citizen sees.
- `false` — the probe sat in another country. The row describes what a foreign
  client sees, and the latency includes the path.

Any claim about citizen experience must filter on it:

```python
import civicweb_observatory as cwo
citizen_view = cwo.load(domestic_only=True)   # 1,360 rows
```

---

## 9. Outcome flags

| Column | Type | Description |
|---|---|---|
| `blocked_by_waf` | boolean | A bot filter refused the request |
| `robots_disallowed` | boolean \| null | robots.txt forbade the path (RFC 9309 matching) |

Both are recorded as distinct outcomes, not as failures. In this release, 76
domains were robots-disallowed and 46 were WAF-blocked.

---

## 10. Reading the CSV

Namibia's ISO-3166 alpha-2 code is `NA`, which is also the default missing-value
token in most CSV readers. A default `pandas.read_csv` silently drops all ten
Namibian rows — one whole country, with no error raised.

```python
import pandas as pd

df = pd.read_csv(
    "data/real/global_measurements_canonical.csv",
    keep_default_na=False,
    na_values=[""],
)
```

Or use `scripts/global_dataset.py`, which is the single reader for this file and
returns nullable booleans so an unmeasured value stays distinguishable from
`False`.

---

## 11. Null semantics

| Value | Means |
|---|---|
| `null` in a score column | Not measured. The host did not serve a page, or the metric was not collected. |
| `0.0` in a score column | Measured, and the score is genuinely zero. |
| `false` in a boolean column | Measured, and the feature is absent. |
| `null` in a boolean column | Not measured. |

A zero is a measurement. A null is the absence of one. The two are never
interchanged in this dataset.
