# bharatgov-access

A census of India's public web, packaged so you can `pip install` it and start
querying in one line.

The release covers **12,092 government domains** across seven governance tiers —
central ministries, state departments, all 788 district administrations, higher
education, the judiciary, public sector undertakings and urban local bodies —
measured from **inside** the Indian domestic peering fabric. That vantage point
matters: overseas crawlers record a large share of these hosts as unreachable
because state data centres and NIC gateways drop foreign traffic at the
perimeter.

```bash
pip install bharatgov-access
```

```python
import bharatgov_access as bga

df = bga.load()                  # all 12,092 domains
live = bga.load(reachable=True)  # the 10,247 that answered in-country

bga.tier_summary(live)           # Table I of the paper
bga.architecture_summary(live)   # Table II of the paper
bga.state_ranking(live, top=10)  # state and UT ranking
```

## What is in the box

| | |
|---|---|
| Portals | 12,092 registered, 10,247 reachable in-country (84.7%) |
| Coverage | 36 States and Union Territories, 7 governance tiers |
| Columns | 20, no derived duplicates |
| Formats | Parquet bundled; CSV and JSON via `bharatgov export` |
| Licence | CC-BY-4.0 |

## The five pillars

Every portal is scored on five orthogonal pillars with two sub-features each,
traceable to a published specification:

1. **Accessibility** — WCAG 2.1 AA structural checks, GIGW 3.0 toolbar
2. **Performance** — time to first byte, estimated Largest Contentful Paint
3. **Security** — TLS enforcement, CERT-In header hardening
4. **Inclusivity** — Eighth Schedule language content, mobile viewport
5. **Architecture** — CMS platform, citizen services

The composite maturity index is a fixed linear weighting, not a fitted model:

```
M = 0.30 * accessibility
  + 0.25 * security
  + 0.20 * max(0, 100 - 15 * lcp_sec)
  + 0.10 * multilingual
  + 0.05 * mobile
  + 0.05 * citizen_services
  + 0.05 * gigw_toolbar
```

`bga.maturity_index(...)` recomputes it, so you can score a portal you measured
yourself with the same methodology.

## Command line

```bash
bharatgov info                      # release summary
bharatgov tiers                     # per-tier census table
bharatgov arch                      # per-platform comparison
bharatgov states --top 10           # state ranking
bharatgov query --tier district --state Kerala --min-maturity 85
bharatgov export --format csv --out census.csv --reachable-only
```

## Reproducing a figure

Every number in the paper is a `groupby` away:

```python
import bharatgov_access as bga

live = bga.load(reachable=True)

# Mean accessibility by tier
print(live.groupby("government_level")["sub_accessibility_score"].mean().round(1))

# The S3WaaS dividend
print(live.groupby("sub_cms_architecture")["sub_accessibility_score"].mean().round(1))

# Security header distribution
print(live["sub_security_headers_score"].describe().round(1))
```

## Known limits

- **Structural, not rendered.** Accessibility is scored from markup. It does not
  execute a screen reader, so it cannot detect a focus trap or a mislabelled
  control.
- **LCP is estimated** from time to first byte and document payload, not measured
  in a browser. It ranks portals correctly but is not a field measurement.
- **One observation per domain** per release. Longitudinal claims require
  comparing releases.
- **Registration is not usage.** The census measures what is published, not what
  is visited.

## Citation

```bibtex
@techreport{agarwal2026bharatgov,
  title       = {BharatGov Access: A Census-Scale In-Country Web Observatory
                 and Empirical Benchmark of India's Public Digital Infrastructure},
  author      = {Agarwal, Pratham and Bairagi, Amit Kumar and Yaduraj, Vishwajeet Nand},
  institution = {Department of Computer Science and Engineering, IIT Kharagpur},
  year        = {2026},
  number      = {DA-2026-G12}
}
```

## Development

```bash
cd packages/bharatgov-access
pip install -e ".[dev]"
pytest -q
python -m build
```
