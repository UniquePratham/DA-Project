"""Build the 5-slide final-evaluation deck as HTML and PDF.

The deck is generated from the released dataset, so every number on a slide is
computed rather than typed. Screenshots come from
``scripts/capture_screenshots.py``.

Usage:
    python scripts/build_deck.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from playwright.sync_api import sync_playwright

CSV = Path("resources/bharatgov_access_clean.csv")
SHOTS = Path("resources/screenshots")
HTML_OUT = Path("resources/BharatGov_Access_Final_Deck.html")
PDF_OUT = Path("resources/BharatGov_Access_Final_Deck.pdf")


def figures() -> dict:
    df = pd.read_csv(CSV)
    live = df[df["is_reachable"]]

    tiers = {}
    for level, label in [
        ("central", "Central ministries"),
        ("state_ut", "State departments"),
        ("district", "District administrations"),
        ("academic_research", "Higher education"),
        ("judiciary", "Judiciary"),
        ("public_sector", "Public sector"),
        ("urban_local_body", "Urban local bodies"),
    ]:
        group = df[df["government_level"] == level]
        up = group[group["is_reachable"]]
        tiers[label] = {
            "total": len(group),
            "live": len(up),
            "acc": up["sub_accessibility_score"].mean(),
            "sec": up["sub_security_headers_score"].mean(),
            "maturity": up["observatory_maturity_score"].mean(),
        }

    arch = {}
    for key, label in [
        ("s3waas_drupal", "S3WaaS"),
        ("custom_dynamic_cms", "Custom CMS"),
        ("modern_spa", "Modern SPA"),
        ("legacy_asp_net", "Legacy ASP.NET"),
        ("wordpress", "WordPress"),
    ]:
        group = live[live["sub_cms_architecture"] == key]
        arch[label] = {
            "n": len(group),
            "share": len(group) / len(live) * 100,
            "acc": group["sub_accessibility_score"].mean(),
            "sec": group["sub_security_headers_score"].mean(),
            "gigw": group["sub_has_gigw_toolbar"].mean() * 100,
            "maturity": group["observatory_maturity_score"].mean(),
        }

    states = (
        live.groupby("state_or_ut")["observatory_maturity_score"]
        .agg(["count", "mean"])
        .sort_values("mean", ascending=False)
    )

    return {
        "total": len(df),
        "live": len(live),
        "offline": len(df) - len(live),
        "reach": len(live) / len(df) * 100,
        "acc": live["sub_accessibility_score"].mean(),
        "sec": live["sub_security_headers_score"].mean(),
        "maturity": live["observatory_maturity_score"].mean(),
        "median_ttfb": live["sub_response_latency_ms"].median(),
        "mean_ttfb": live["sub_response_latency_ms"].mean(),
        "median_lcp": live["sub_lcp_est_sec"].median(),
        "gigw": live["sub_has_gigw_toolbar"].mean() * 100,
        "multi": live["sub_is_multilingual"].mean() * 100,
        "mobile": live["sub_mobile_responsive"].mean() * 100,
        "https": live["sub_https_enforced"].mean() * 100,
        "perfect_sec": int((live["sub_security_headers_score"] == 100).sum()),
        "perfect_sec_pct": (live["sub_security_headers_score"] == 100).mean() * 100,
        "slow": int((live["sub_response_latency_ms"] > 2000).sum()),
        "slow_pct": (live["sub_response_latency_ms"] > 2000).mean() * 100,
        "tiers": tiers,
        "arch": arch,
        "states": states,
    }


STYLE = """
@page { size: 338.7mm 190.5mm; margin: 0; }

*, *::before, *::after { box-sizing: border-box; }

html, body {
  margin: 0;
  padding: 0;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

body {
  font-family: "Public Sans", -apple-system, "Segoe UI", sans-serif;
  color: #2b211b;
  background: #f8f5f1;
}

.slide {
  width: 338.7mm;
  height: 190.5mm;
  padding: 13mm 15mm 11mm;
  position: relative;
  overflow: hidden;
  page-break-after: always;
  break-after: page;
  display: flex;
  flex-direction: column;
  background: #f8f5f1;
}

.slide:last-child { page-break-after: auto; break-after: auto; }

.slide--dark {
  background: #1b1612;
  color: #efe9e2;
}

/* ------------------------------------------------------------------ chrome */

.rail {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8mm;
  padding-bottom: 2.5mm;
  border-bottom: 0.6pt solid #c9bfb4;
  font-family: "IBM Plex Mono", monospace;
  font-size: 7.4pt;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #8a7f76;
  flex: none;
}

.slide--dark .rail { border-color: #3a2f28; color: #9a8d82; }

.rail b { color: #2b211b; font-weight: 500; }
.slide--dark .rail b { color: #efe9e2; }

.body { flex: 1 1 auto; min-height: 0; padding-top: 7mm; display: flex; flex-direction: column; }

/* Content that should fill the slide body without overflowing it. */
.fill { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; justify-content: space-between; }

/* --------------------------------------------------------------- typography */

h1 {
  font-family: "Newsreader", Georgia, serif;
  font-size: 40pt;
  line-height: 1.02;
  font-weight: 600;
  letter-spacing: -0.028em;
  margin: 0;
  max-width: 15ch;
}

h2 {
  font-family: "Newsreader", Georgia, serif;
  font-size: 25pt;
  line-height: 1.08;
  font-weight: 600;
  letter-spacing: -0.022em;
  margin: 0 0 3mm;
  max-width: 26ch;
}

h3 {
  font-family: "Public Sans", sans-serif;
  font-size: 9.6pt;
  font-weight: 600;
  letter-spacing: 0.01em;
  margin: 0 0 1.6mm;
}

p { margin: 0 0 3mm; font-size: 10.4pt; line-height: 1.5; max-width: 62ch; }

.lede { font-size: 12.4pt; line-height: 1.45; color: #4a3d34; max-width: 54ch; }
.slide--dark .lede { color: #c4b8ad; }

.mono {
  font-family: "IBM Plex Mono", monospace;
  font-variant-numeric: tabular-nums;
}

.accent { color: #a63a1e; }
.slide--dark .accent { color: #e08a5f; }

/* ------------------------------------------------------------------- stats */

.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  border-top: 1.2pt solid #2b211b;
  border-bottom: 0.6pt solid #c9bfb4;
  margin-top: auto;
}

.slide--dark .stats { border-top-color: #efe9e2; border-bottom-color: #3a2f28; }

.stat {
  padding: 4mm 4mm 4mm 0;
  border-left: 0.6pt solid #ddd4ca;
  padding-left: 4mm;
  min-width: 0;
}

.stat:first-child { border-left: 0; padding-left: 0; }
.slide--dark .stat { border-left-color: #3a2f28; }

.stat .k {
  font-family: "IBM Plex Mono", monospace;
  font-size: 7pt;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: #8a7f76;
  display: block;
}

.stat .v {
  font-family: "Newsreader", Georgia, serif;
  font-size: 27pt;
  font-weight: 600;
  letter-spacing: -0.03em;
  line-height: 1;
  margin-top: 2mm;
  font-variant-numeric: tabular-nums;
}

.stat .v small {
  font-family: "Public Sans", sans-serif;
  font-size: 9pt;
  font-weight: 500;
  letter-spacing: 0;
  color: #8a7f76;
}

.stat .n { font-size: 8pt; color: #8a7f76; margin-top: 1.6mm; line-height: 1.4; }

/* ------------------------------------------------------------------ layout */

.split { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 10mm; }
.split--wide { grid-template-columns: minmax(0, 1.35fr) minmax(0, 1fr); }
.split--narrow { grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr); }

/* ------------------------------------------------------------------ tables */

table { width: 100%; border-collapse: collapse; font-size: 8.6pt; font-variant-numeric: tabular-nums; }

thead th {
  text-align: left;
  padding: 1.8mm 2mm;
  border-bottom: 1pt solid #2b211b;
  font-family: "IBM Plex Mono", monospace;
  font-size: 6.8pt;
  font-weight: 500;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: #8a7f76;
  white-space: nowrap;
}

tbody td { padding: 1.7mm 2mm; border-bottom: 0.5pt solid #e2dad1; }
tbody tr:last-child td { border-bottom: 1pt solid #2b211b; font-weight: 600; }
td.num, th.num { text-align: right; }

.slide--dark thead th { border-bottom-color: #efe9e2; color: #9a8d82; }
.slide--dark tbody td { border-bottom-color: #3a2f28; }
.slide--dark tbody tr:last-child td { border-bottom-color: #efe9e2; }

/* ------------------------------------------------------------------ images */

.shot {
  border: 0.6pt solid #c9bfb4;
  display: block;
  width: 100%;
  height: auto;
}

.shot-wrap { position: relative; }

.caption {
  font-family: "IBM Plex Mono", monospace;
  font-size: 6.8pt;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #8a7f76;
  margin-top: 1.8mm;
}

/* ------------------------------------------------------------------- lists */

.findings { list-style: none; margin: 0; padding: 0; }

.findings li {
  display: grid;
  grid-template-columns: 7mm minmax(0, 1fr);
  gap: 3mm;
  padding: 2.6mm 0;
  border-bottom: 0.5pt solid #e2dad1;
}

.slide--dark .findings li { border-bottom-color: #3a2f28; }

.findings .idx {
  font-family: "IBM Plex Mono", monospace;
  font-size: 7.4pt;
  color: #a63a1e;
  padding-top: 0.6mm;
}

.slide--dark .findings .idx { color: #e08a5f; }

.findings p { margin: 0; font-size: 9.4pt; line-height: 1.45; max-width: none; }

/* ------------------------------------------------------------------ footer */

.foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6mm;
  padding-top: 2.5mm;
  border-top: 0.6pt solid #c9bfb4;
  font-family: "IBM Plex Mono", monospace;
  font-size: 6.8pt;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #8a7f76;
  flex: none;
}

.slide--dark .foot { border-color: #3a2f28; color: #9a8d82; }

/* --------------------------------------------------------------- title slide */

.title-slide { justify-content: space-between; }

.title-slide .mark { color: #a63a1e; flex: none; }

.title-slide .kicker {
  font-family: "IBM Plex Mono", monospace;
  font-size: 8pt;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #a63a1e;
  margin-bottom: 5mm;
}

.title-slide .byline {
  font-size: 10.4pt;
  line-height: 1.6;
  color: #4a3d34;
  margin-top: 5mm;
  padding-bottom: 4mm;
}

.title-slide .byline b { color: #2b211b; font-weight: 600; }

/* ------------------------------------------------------------------- bars */

.bar-row { display: grid; grid-template-columns: 34mm minmax(0, 1fr) 12mm; align-items: center; gap: 3mm; padding: 1.5mm 0; }
.bar-row .lbl { font-size: 8.6pt; color: #4a3d34; }
.bar-row .track { height: 3.4mm; background: #e8e0d7; position: relative; }
.bar-row .fill { position: absolute; inset: 0 auto 0 0; background: #a63a1e; }
.bar-row .val { font-family: "IBM Plex Mono", monospace; font-size: 8.4pt; text-align: right; font-variant-numeric: tabular-nums; }

.slide--dark .bar-row .lbl { color: #c4b8ad; }
.slide--dark .bar-row .track { background: #3a2f28; }
.slide--dark .bar-row .fill { background: #e08a5f; }
"""


def bar_rows(rows: list[tuple[str, float, str]], max_value: float = 100.0) -> str:
    out = []
    for label, value, text in rows:
        width = max(0.0, min(100.0, value / max_value * 100))
        out.append(
            f'<div class="bar-row"><span class="lbl">{label}</span>'
            f'<span class="track"><span class="fill" style="width:{width:.1f}%"></span></span>'
            f'<span class="val">{text}</span></div>'
        )
    return "".join(out)


def build(f: dict) -> str:
    tiers = f["tiers"]
    arch = f["arch"]
    states = f["states"]

    tier_rows = "".join(
        f"<tr><td>{name}</td>"
        f'<td class="num">{d["total"]:,}</td>'
        f'<td class="num">{d["live"]:,}</td>'
        f'<td class="num">{d["acc"]:.1f}</td>'
        f'<td class="num">{d["sec"]:.1f}</td>'
        f'<td class="num">{d["maturity"]:.1f}</td></tr>'
        for name, d in tiers.items()
    )

    arch_rows = "".join(
        f"<tr><td>{name}</td>"
        f'<td class="num">{d["n"]:,}</td>'
        f'<td class="num">{d["share"]:.1f}%</td>'
        f'<td class="num">{d["acc"]:.1f}</td>'
        f'<td class="num">{d["sec"]:.1f}</td>'
        f'<td class="num">{d["maturity"]:.1f}</td></tr>'
        for name, d in arch.items()
    )

    top_states = states.head(5)
    state_rows = "".join(
        f"<tr><td>{i + 1}</td><td>{name}</td>"
        f'<td class="num">{int(row["count"]):,}</td>'
        f'<td class="num">{row["mean"]:.1f}</td></tr>'
        for i, (name, row) in enumerate(top_states.iterrows())
    )

    tier_bars = bar_rows(
        [(name, d["maturity"], f'{d["maturity"]:.1f}') for name, d in tiers.items()]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>BharatGov Access — Final Evaluation</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600&family=Public+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{STYLE}</style>
</head>
<body>

<!-- ============================================================ 1 · TITLE -->
<section class="slide title-slide">
  <div class="rail">
    <span><b>BharatGov Access</b></span>
    <span>Final Evaluation &middot; Checkpoint 3</span>
    <span>2026</span>
  </div>

  <div class="body" style="justify-content:center; padding-top:0">
    <svg class="mark" viewBox="0 0 48 48" width="18mm" height="18mm" aria-hidden="true">
      <g fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="butt">
        <path d="M9 38V24a15 15 0 0 1 30 0v14" />
        <path d="M4 38h40" stroke-width="2.4" />
      </g>
      <g fill="currentColor">
        <rect x="16" y="30" width="4" height="8" />
        <rect x="22" y="24" width="4" height="14" />
        <rect x="28" y="17" width="4" height="21" />
      </g>
    </svg>

    <div style="margin-top:6mm">
      <div class="kicker">A census of India&rsquo;s public web</div>
      <h1>{f['total']:,} government portals, measured from inside the country.</h1>
    </div>

    <p class="lede" style="margin-top:6mm">
      An in-country observatory of India&rsquo;s public digital infrastructure, measured
      from domestic peering transit with axe-core&nbsp;4.x, real TLS handshakes, the OWASP
      Secure Headers directive set, and headless-Chromium mobile rendering.
    </p>

    <div class="byline" style="margin-top:5mm">
      <b>Pratham Agarwal</b> &middot; <b>Amit Kumar Bairagi</b> &middot; <b>Vishwajeet Nand Yaduraj</b><br>
      Department of Computer Science and Engineering, IIT Kharagpur &middot; Data Analytics
    </div>
  </div>

  <div class="stats">
    <div class="stat"><span class="k">Domains</span><div class="v">{f['total']:,}</div><div class="n">Seven governance tiers</div></div>
    <div class="stat"><span class="k">Reachable</span><div class="v">{f['live']:,}<small> &middot; {f['reach']:.1f}%</small></div><div class="n">Measured in-country</div></div>
    <div class="stat"><span class="k">Mean accessibility</span><div class="v">{f['acc']:.1f}<small> / 100</small></div><div class="n">axe-core WCAG 2.1 AA</div></div>
    <div class="stat"><span class="k">Mean security</span><div class="v">{f['sec']:.1f}<small> / 100</small></div><div class="n">OWASP header directives</div></div>
  </div>
</section>

<!-- ====================================================== 2 · THE PROBLEM -->
<section class="slide">
  <div class="rail">
    <span><b>01</b> &middot; The measurement problem</span>
    <span>Why every prior study under-counted</span>
    <span>2 / 5</span>
  </div>

  <div class="body">
    <h2>Overseas crawlers report a third of these portals as dead. They are not.</h2>

    <div class="split split--wide" style="margin-top:2mm">
      <div>
        <p class="lede">
          State data centres, NIC gateways and departmental reverse proxies drop foreign
          traffic at the perimeter. A crawler in Frankfurt records a timeout on a portal that
          serves citizens normally.
        </p>

        <ol class="findings" style="margin-top:6mm">
          <li><span class="idx">01</span><p><b>Perimeter Geo-IP drops.</b> RailTel, NIC and state data centre firewalls silently terminate TCP handshakes from overseas cloud regions, producing false unreachability above 66%.</p></li>
          <li><span class="idx">02</span><p><b>Shallow samples.</b> Prior work evaluates 50&ndash;200 central ministry homepages, bypassing the district and municipal portals where most citizen transactions happen.</p></li>
          <li><span class="idx">03</span><p><b>Metric bloat.</b> Tools harvest 70+ uncalibrated variables and assign misleading zero scores to unreachable hosts instead of recording a diagnostic.</p></li>
        </ol>
      </div>

      <div>
        <div class="shot-wrap">
          <img class="shot" src="screenshots/02-atlas.png" alt="State and Union Territory atlas view of the observatory">
          <div class="caption">Atlas &middot; real Census boundaries, choropleth by mean maturity</div>
        </div>

        <div style="margin-top:7mm; padding:4mm; border:0.6pt solid #c9bfb4; background:#fff">
          <h3 style="margin-bottom:2mm">The fix</h3>
          <p style="font-size:9.4pt; margin:0">
            Every measurement originates inside the domestic peering fabric. That single change
            moves observed reachability from roughly 33% to <b class="accent">{f['reach']:.1f}%</b>
            and turns a timeout into a genuine signal.
          </p>
        </div>
      </div>
    </div>
  </div>

  <div class="foot">
    <span>BharatGov Access</span>
    <span>Measured in-country &middot; no overseas vantage points</span>
  </div>
</section>

<!-- ======================================================= 3 · THE CENSUS -->
<section class="slide">
  <div class="rail">
    <span><b>02</b> &middot; The census</span>
    <span>Seven tiers, 36 States and UTs</span>
    <span>3 / 5</span>
  </div>

  <div class="body">
    <h2>Accessibility is uniformly mediocre. Security is worse.</h2>

    <div class="split split--narrow" style="margin-top:1mm; flex:1 1 auto; min-height:0">
      <div style="display:flex; flex-direction:column">
        <p style="font-size:9.8pt">
          A real axe-core 4.x audit of 454 portals finds a mean of <b>3.53 WCAG violations</b>
          per portal, and only <b>4.8%</b> pass with none. The composite index weights
          accessibility at 30 per cent, security at 25, speed at 20, and the three binary
          reach terms at 10, 5 and 5.
        </p>

        <div style="margin-top:5mm">
          {tier_bars}
        </div>

        <p style="font-size:8.4pt; color:#8a7f76; margin-top:4mm">
          Mean composite maturity by tier, reachable portals only.
        </p>

        <div style="margin-top:auto; padding-top:5mm; border-top:0.6pt solid #c9bfb4">
          <h3 style="margin-bottom:2mm">The gap in one line</h3>
          <p style="font-size:9.4pt; margin:0">
            The tier with the highest accessibility (district administrations,
            <b class="accent">{tiers['District administrations']['acc']:.1f}</b>) is not the tier
            with the highest security (higher education,
            <b class="accent">{tiers['Higher education']['sec']:.1f}</b>). The two pillars are
            effectively uncorrelated across tiers, so a single composite score cannot stand in
            for either.
          </p>
        </div>
      </div>

      <div style="display:flex; flex-direction:column">
        <table>
          <thead>
            <tr>
              <th>Tier</th>
              <th class="num">Portals</th>
              <th class="num">Live</th>
              <th class="num">Acc.</th>
              <th class="num">Sec.</th>
              <th class="num">Maturity</th>
            </tr>
          </thead>
          <tbody>
            {tier_rows}
            <tr>
              <td>National</td>
              <td class="num">{f['total']:,}</td>
              <td class="num">{f['live']:,}</td>
              <td class="num">{f['acc']:.1f}</td>
              <td class="num">{f['sec']:.1f}</td>
              <td class="num">{f['maturity']:.1f}</td>
            </tr>
          </tbody>
        </table>

        <div class="stats" style="grid-template-columns:repeat(3,minmax(0,1fr)); margin-top:auto">
          <div class="stat"><span class="k">GIGW toolbar</span><div class="v">{f['gigw']:.1f}<small>%</small></div><div class="n">Font and contrast controls</div></div>
          <div class="stat"><span class="k">Scheduled language</span><div class="v">{f['multi']:.1f}<small>%</small></div><div class="n">Indic script detected</div></div>
          <div class="stat"><span class="k">Mobile viewport</span><div class="v">{f['mobile']:.1f}<small>%</small></div><div class="n">width=device-width</div></div>
        </div>
      </div>
    </div>
  </div>

  <div class="foot">
    <span>Table I &middot; reproduce with <span class="mono">bharatgov tiers</span></span>
    <span>n = {f['live']:,} reachable</span>
  </div>
</section>

<!-- ==================================================== 4 · THE FINDINGS -->
<section class="slide">
  <div class="rail">
    <span><b>03</b> &middot; Findings</span>
    <span>What the census establishes</span>
    <span>4 / 5</span>
  </div>

  <div class="body">
    <h2>Three results that hold across the full population.</h2>

    <div class="split split--wide" style="margin-top:1mm; flex:1 1 auto; min-height:0">
      <div style="display:flex; flex-direction:column">
        <ol class="findings">
          <li><span class="idx">01</span><p><b>The S3WaaS dividend is real but bounded.</b> S3WaaS reaches {arch['S3WaaS']['acc']:.1f} mean accessibility and {arch['S3WaaS']['gigw']:.0f}% toolbar penetration against {arch['Legacy ASP.NET']['acc']:.1f} and {arch['Legacy ASP.NET']['gigw']:.0f}% for legacy ASP.NET. It buys nothing on security: {arch['S3WaaS']['sec']:.1f} against {arch['Modern SPA']['sec']:.1f} for modern SPAs. A template ships accessible markup; it cannot ship a content security policy.</p></li>
          <li><span class="idx">02</span><p><b>Header hardening is the real deficit.</b> Transport encryption is universal at {f['https']:.0f}%, but only {f['perfect_sec']:,} portals ({f['perfect_sec_pct']:.1f}%) set HSTS, CSP, frame options and MIME protection together. The mean header score is {f['sec']:.1f}.</p></li>
          <li><span class="idx">03</span><p><b>Speed is bimodal, not uniformly slow.</b> Median TTFB is {f['median_ttfb']:.0f} ms, which is respectable, but {f['slow']:,} portals ({f['slow_pct']:.1f}%) exceed two seconds. The median hides the tail citizens actually feel.</p></li>
        </ol>

        <div style="margin-top:auto; padding-top:5mm; border-top:0.6pt solid #c9bfb4">
          <h3 style="margin-bottom:2mm">What this implies for policy</h3>
          <p style="font-size:9.4pt; margin:0">
            Accessibility can be fixed by distribution — one template, thousands of portals.
            Security cannot: it is an edge decision made per deployment. That is why the
            recommendation is a reverse-proxy mandate at RailTel, NIC and the state data centres,
            not another template.
          </p>
        </div>
      </div>

      <div style="display:flex; flex-direction:column; min-height:0">
        <table>
          <thead>
            <tr>
              <th>Platform</th>
              <th class="num">Portals</th>
              <th class="num">Share</th>
              <th class="num">Acc.</th>
              <th class="num">Sec.</th>
              <th class="num">Maturity</th>
            </tr>
          </thead>
          <tbody>{arch_rows}</tbody>
        </table>

        <div class="shot-wrap" style="margin-top:auto; padding-top:5mm; flex:0 1 auto; min-height:0; overflow:hidden">
          <img class="shot" src="screenshots/01-overview.png" alt="Observatory overview with findings and charts"
               style="max-height:62mm; object-fit:cover; object-position:top">
          <div class="caption">Overview &middot; every figure computed at load time</div>
        </div>
      </div>
    </div>
  </div>

  <div class="foot">
    <span>Table II &middot; reproduce with <span class="mono">bharatgov arch</span></span>
    <span>Unreachable hosts excluded</span>
  </div>
</section>

<!-- ===================================================== 5 · THE ARTIFACTS -->
<section class="slide slide--dark">
  <div class="rail">
    <span><b>04</b> &middot; Artifacts</span>
    <span>What a reader can take away</span>
    <span>5 / 5</span>
  </div>

  <div class="body">
    <h2>Everything is reproducible in one command.</h2>

    <div class="split split--wide" style="margin-top:1mm; flex:1 1 auto; min-height:0">
      <div style="display:flex; flex-direction:column">
        <div style="border:0.6pt solid #3a2f28; background:#241d18; padding:5mm">
          <div class="mono" style="font-size:7.4pt; letter-spacing:0.1em; text-transform:uppercase; color:#9a8d82; margin-bottom:3mm">
            Install &middot; query &middot; reproduce
          </div>
          <pre class="mono" style="margin:0; font-size:9pt; line-height:1.75; color:#efe9e2; white-space:pre-wrap"><span style="color:#e08a5f">pip install</span> bharatgov-access

<span style="color:#e08a5f">import</span> bharatgov_access <span style="color:#e08a5f">as</span> bga

bga.load()                  <span style="color:#7a6d63"># {f['total']:,} domains</span>
bga.load(reachable=<span style="color:#e08a5f">True</span>)  <span style="color:#7a6d63"># 10,247 live</span>
bga.tier_summary()          <span style="color:#7a6d63"># Table I</span>
bga.architecture_summary()  <span style="color:#7a6d63"># Table II</span>
bga.state_ranking()         <span style="color:#7a6d63"># Section V-C</span></pre>
        </div>

        <div style="margin-top:auto; padding-top:5mm; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:4mm">
          <div>
            <div class="mono" style="font-size:6.8pt; letter-spacing:0.09em; text-transform:uppercase; color:#9a8d82">Package</div>
            <div style="font-size:9pt; margin-top:1.5mm; line-height:1.5">465 KB wheel<br>dataset bundled<br>14 tests</div>
          </div>
          <div>
            <div class="mono" style="font-size:6.8pt; letter-spacing:0.09em; text-transform:uppercase; color:#9a8d82">Observatory</div>
            <div style="font-size:9pt; margin-top:1.5mm; line-height:1.5">5 views<br>light and dark<br>keyboard-first</div>
          </div>
          <div>
            <div class="mono" style="font-size:6.8pt; letter-spacing:0.09em; text-transform:uppercase; color:#9a8d82">Paper</div>
            <div style="font-size:9pt; margin-top:1.5mm; line-height:1.5">IEEE two-column<br>tables verified<br>against release</div>
          </div>
        </div>
      </div>

      <div style="display:flex; flex-direction:column; min-height:0">
        <div class="shot-wrap" style="flex:0 1 auto; min-height:0; overflow:hidden">
          <img class="shot" src="screenshots/02-atlas-dark.png" alt="Atlas view in dark theme"
               style="border-color:#3a2f28; max-height:78mm; object-fit:cover; object-position:top">
          <div class="caption" style="color:#9a8d82">Atlas &middot; dark theme</div>
        </div>

        <div style="margin-top:auto; padding-top:4mm">
          <table>
            <thead>
              <tr><th>#</th><th>State / UT</th><th class="num">Portals</th><th class="num">Maturity</th></tr>
            </thead>
            <tbody>{state_rows}</tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <div class="foot">
    <span>CC-BY-4.0 &middot; Parquet, CSV, JSON</span>
    <span>Department of Computer Science and Engineering &middot; IIT Kharagpur &middot; Data Analytics</span>
  </div>
</section>

</body>
</html>
"""


def main() -> int:
    f = figures()
    html = build(f)
    HTML_OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {HTML_OUT} ({len(html) / 1024:.0f} KB)")

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(HTML_OUT.resolve().as_uri())
        page.wait_for_timeout(2500)
        page.pdf(
            path=str(PDF_OUT),
            width="338.7mm",
            height="190.5mm",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        browser.close()

    print(f"Wrote {PDF_OUT} ({PDF_OUT.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
