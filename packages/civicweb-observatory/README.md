# civicweb-observatory

A cross-country measurement of public-sector web infrastructure, packaged so you
can `pip install` it and start querying in one line.

The release covers **2,011 government domains across 82 countries**, measured
with a standard tool per dimension: axe-core 4.x for accessibility, a wall-clock
timer for latency, the OWASP Secure Headers directive set, a real TLS handshake,
and a headless-Chromium render at 375 px for mobile behaviour.

```bash
pip install civicweb-observatory
```

```python
import civicweb_observatory as cwo

df = cwo.load()                    # all 2,011 measured domains
live = cwo.load(reachable=True)    # the 573 that answered

cwo.country_summary()              # one row per country
cwo.sector_summary()               # one row per sector
cwo.vantage_comparison()           # domestic vs nearest
cwo.architecture_summary()         # per-platform comparison
```

## The vantage point is the point

A cloud provider operates in 20 countries, so a domestic probe is impossible in
most of the world. Rather than exclude those countries or pretend a foreign
probe is domestic, every row records `domestic_probe`: true only when the
probe's region country equals the target country.

| Vantage | Domains | Reach | Accessibility | Security | Median TTFB |
| :--- | ---: | ---: | ---: | ---: | ---: |
| domestic | 1,360 | 29.3% | 87.0 | 44.2 | **479 ms** |
| nearest | 651 | 26.9% | 84.0 | 33.2 | **1,156 ms** |

The **677 ms gap is the cost of distance, not a difference in the portals.** A
study that measures only from inside, or only from outside, cannot see that.

Any claim about what a citizen experiences must filter on it:

```python
citizen_view = cwo.load(domestic_only=True)   # 1,360 rows, probe inside the country
```

## What is in the box

| | |
|---|---|
| Domains | 2,011 measured, 573 reachable (28.5%) |
| Coverage | 82 countries; 19 with a domestic probe, 64 measured from the nearest region |
| Columns | 26, including `probe_country`, `probe_region`, `domestic_probe`, `blocked_by_waf`, `robots_disallowed` |
| Formats | Parquet bundled; CSV and JSON via `civicweb export` |
| Licence | CC-BY-4.0 |

## Reading the CSV yourself

Namibia's ISO-3166 alpha-2 code is `NA`, which is also the default
missing-value token in most CSV readers. A default `pandas.read_csv` silently
drops all ten Namibian rows — one whole country, with no error raised. Use:

```python
import pandas as pd

df = pd.read_csv("global_measurements_canonical.csv", keep_default_na=False, na_values=[""])
```

The bundled Parquet has no such problem; `cwo.load()` is the safe path.

## The five pillars

| Pillar | What is measured | Tool |
| :--- | :--- | :--- |
| Accessibility | axe-core violation count and severity-weighted index | axe-core 4.x |
| Performance | Time to first byte, estimated LCP | `time.perf_counter` |
| Security | HTTPS enforcement, TLS handshake, OWASP header score | `ssl`, response headers |
| Inclusion | Non-English language or script, responsive viewport | DOM inspection, 375 px render |
| Architecture | CMS fingerprint, citizen-service affordances | body and header markers |

## Composite index

```python
cwo.maturity_index(
    accessibility=87.0,
    security=43.3,
    lcp_sec=1.14,
    multilingual=True,
    mobile=True,
    citizen_services=True,
    s3waas=False,
)
```

The weights are fixed, not fitted: 0.30 accessibility, 0.25 security, 0.20
speed, then 10/5/5/5 absolute points for the binary terms. The result is clamped
to `[0, 100]` and is **not** floored — an earlier release applied a 45.0 floor,
which silently inflated the worst portals and made the index non-reproducible
from its own inputs.

## CLI

```bash
civicweb info
civicweb countries --top 10
civicweb sectors
civicweb vantage
civicweb arch
civicweb query --country NL --min-maturity 80
civicweb export --format csv --out measurements.csv --reachable-only
```

## What this release does not claim

- **Automated testing is not conformance.** axe-core catches a subset of WCAG
  failures. It cannot judge cognitive load, screen-reader audio flow or reading
  order.
- **LCP is estimated, never measured.** It is derived from TTFB and payload
  size, not from a browser paint trace.
- **Nearest probes are not domestic.** 651 of 2,011 rows were measured from a
  probe in another country.
- **Discovery is not verification.** A domain in the registry was observed in an
  auditable source; it was not confirmed to be an operating citizen portal,
  which is why reachability is 28.5% rather than near 100%.
- **One snapshot.** No per-domain timestamp series, so no trend claim.
- **Sector is inferred from the hostname.** 1,354 of 2,011 rows are `general`,
  so the sector comparison is a comparison of the identifiable subset.
