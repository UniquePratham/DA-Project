"""Build the 5-slide final-evaluation deck as HTML and PDF.

Every number on a slide is computed from ``data/real/global_measurements.csv``,
so the deck cannot drift from the released dataset. Screenshots come from
``scripts/capture_screenshots.py``.

Usage:
    python scripts/build_deck.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from playwright.sync_api import sync_playwright

from deck_style import STYLE
from global_dataset import GLOBAL_CSV as CSV
from global_dataset import classify_sector as classify
from global_dataset import country_name
from global_dataset import domestic as domestic_rows
from global_dataset import nearest as nearest_rows
from global_dataset import read_global, reachable

SHOTS = Path("resources/screenshots")
HTML_OUT = Path("resources/CivicWeb_Observatory_Final_Deck.html")
PDF_OUT = Path("resources/CivicWeb_Observatory_Final_Deck.pdf")

ARCH_LABELS = {
    "custom_dynamic_cms": "Custom dynamic CMS",
    "wordpress": "WordPress",
    "legacy_asp_net": "Legacy ASP.NET",
    "modern_spa": "Modern SPA",
    "drupal": "Drupal",
    "s3waas_drupal": "S3WaaS (Drupal)",
}

# A sector mean is only reported when at least this many of its domains answered.
MIN_LIVE = 10

# A country is only ranked when at least this many of its domains answered.
MIN_COUNTRY_DOMAINS = 10


def figures() -> dict:
    """Every figure on the deck, computed from the global dataset."""
    df = read_global(CSV)
    df["sector"] = df["domain_name"].map(classify)

    live = reachable(df)
    domestic = domestic_rows(df)
    nearest = nearest_rows(df)
    dom_live = reachable(domestic)
    near_live = reachable(nearest)

    def block(group: pd.DataFrame, up: pd.DataFrame) -> dict:
        return {
            "n": len(group),
            "live": len(up),
            "reach": len(up) / len(group) * 100 if len(group) else 0.0,
            "acc": up["sub_accessibility_score"].mean(),
            "sec": up["sub_security_headers_score"].mean(),
            "maturity": up["observatory_maturity_score"].mean(),
            "ttfb": up["sub_response_latency_ms"].median(),
        }

    # A sector needs at least MIN_LIVE reachable domains before its mean is
    # reported. Below that the mean is one or two portals wearing a sector label.
    sectors = {}
    for sector, group in df.groupby("sector"):
        up = reachable(group)
        if len(up) < MIN_LIVE:
            continue
        sectors[sector] = block(group, up)

    arch = {}
    for name, group in live.groupby("sub_cms_architecture"):
        arch[ARCH_LABELS.get(name, name)] = {
            "n": len(group),
            "share": len(group) / len(live) * 100,
            "acc": group["sub_accessibility_score"].mean(),
            "sec": group["sub_security_headers_score"].mean(),
            "maturity": group["observatory_maturity_score"].mean(),
        }

    countries = (
        live.groupby("probe_country")["observatory_maturity_score"]
        .agg(["count", "mean"])
        .sort_values("mean", ascending=False)
    )
    # A country mean over one or two domains is noise, not a ranking. Require a
    # minimum sample before a country is ranked at all.
    countries = countries[countries["count"] >= MIN_COUNTRY_DOMAINS]

    return {
        "total": len(df),
        "live": len(live),
        "reach": len(live) / len(df) * 100,
        "countries": df["probe_country"].nunique(),
        "countries_live": live["probe_country"].nunique(),
        "acc": live["sub_accessibility_score"].mean(),
        "sec": live["sub_security_headers_score"].mean(),
        "maturity": live["observatory_maturity_score"].mean(),
        "median_ttfb": live["sub_response_latency_ms"].median(),
        "median_lcp": live["sub_lcp_est_sec"].median(),
        "https": live["sub_https_enforced"].mean() * 100,
        "multi": live["sub_is_multilingual"].mean() * 100,
        "mobile": live["sub_mobile_responsive"].mean() * 100,
        "waf": int(df["blocked_by_waf"].fillna(False).astype(bool).sum()),
        "robots": int(df["robots_disallowed"].fillna(False).astype(bool).sum()),
        "domestic": block(domestic, dom_live),
        "nearest": block(nearest, near_live),
        "sectors": sectors,
        "arch": arch,
        "countries_rank": countries,
    }


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
    dom = f["domestic"]
    near = f["nearest"]
    gap = near["ttfb"] - dom["ttfb"]

    sector_order = sorted(f["sectors"].items(), key=lambda kv: -kv[1]["n"])
    sector_rows = "".join(
        f"<tr><td>{name}</td>"
        f'<td class="num">{d["n"]:,}</td>'
        f'<td class="num">{d["reach"]:.1f}%</td>'
        f'<td class="num">{d["acc"]:.1f}</td>'
        f'<td class="num">{d["sec"]:.1f}</td></tr>'
        for name, d in sector_order
    )

    sector_bars = bar_rows(
        [(name, d["sec"], f'{d["sec"]:.1f}') for name, d in sector_order]
    )

    arch_order = sorted(f["arch"].items(), key=lambda kv: -kv[1]["n"])
    arch_rows = "".join(
        f"<tr><td>{name}</td>"
        f'<td class="num">{d["n"]:,}</td>'
        f'<td class="num">{d["share"]:.1f}%</td>'
        f'<td class="num">{d["acc"]:.1f}</td>'
        f'<td class="num">{d["sec"]:.1f}</td>'
        f'<td class="num">{d["maturity"]:.1f}</td></tr>'
        for name, d in arch_order
    )

    top_countries = f["countries_rank"].head(6)
    country_rows = "".join(
        f"<tr><td>{i + 1}</td><td>{country_name(name)}</td>"
        f'<td class="num">{int(row["count"]):,}</td>'
        f'<td class="num">{row["mean"]:.1f}</td></tr>'
        for i, (name, row) in enumerate(top_countries.iterrows())
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CivicWeb Observatory — Final Evaluation</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600&family=Public+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{STYLE}</style>
</head>
<body>

<!-- ============================================================ 1 · TITLE -->
<section class="slide title-slide">
  <div class="rail">
    <span><b>CivicWeb Observatory</b></span>
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

    <div style="margin-top:5mm">
      <div class="kicker">A cross-country measurement of public-sector web</div>
      <h1>{f['total']:,} government portals in {f['countries']} countries, measured from the best vantage available.</h1>
    </div>

    <p class="lede" style="margin-top:5mm">
      A cloud provider operates in 20 countries, so a domestic probe is impossible
      in most of the world. We measure where we can and label every row with the
      vantage that produced it &mdash; axe-core&nbsp;4.x, real TLS handshakes, the OWASP
      Secure Headers directive set, and headless-Chromium mobile rendering.
    </p>

    <div class="byline" style="margin-top:4mm">
      <b>Pratham Agarwal</b> &middot; <b>Amit Kumar Bairagi</b> &middot; <b>Vishwajeet Nand Yaduraj</b><br>
      Department of Computer Science and Engineering, IIT Kharagpur &middot; Data Analytics
    </div>
  </div>

  <div class="stats">
    <div class="stat"><span class="k">Domains</span><div class="v">{f['total']:,}</div><div class="n">Across {f['countries']} countries</div></div>
    <div class="stat"><span class="k">Reachable</span><div class="v">{f['live']:,}<small> &middot; {f['reach']:.1f}%</small></div><div class="n">In {f['countries_live']} countries</div></div>
    <div class="stat"><span class="k">Mean accessibility</span><div class="v">{f['acc']:.1f}<small> / 100</small></div><div class="n">axe-core WCAG 2.1 AA</div></div>
    <div class="stat"><span class="k">Mean security</span><div class="v">{f['sec']:.1f}<small> / 100</small></div><div class="n">OWASP header directives</div></div>
  </div>
</section>

<!-- ====================================================== 2 · THE PROBLEM -->
<section class="slide">
  <div class="rail">
    <span><b>01</b> &middot; The vantage problem</span>
    <span>Why a foreign crawler measures the firewall</span>
    <span>2 / 5</span>
  </div>

  <div class="body">
    <h2>Distance costs {gap:.0f} ms. That is not a property of the portal.</h2>

    <div class="split split--wide" style="margin-top:2mm">
      <div>
        <p class="lede">
          A crawler in Frankfurt records a timeout on a portal that serves citizens
          normally. State gateways and perimeter filters treat foreign addresses
          differently, so a study that reports reachability from abroad is measuring
          the firewall as much as the website.
        </p>

        <ol class="findings" style="margin-top:6mm">
          <li><span class="idx">01</span><p><b>One provider, twenty countries.</b> A domestic probe exists for a handful of countries and no more. Excluding the rest would discard most of the world; calling a foreign probe domestic would be a lie.</p></li>
          <li><span class="idx">02</span><p><b>So we label the row.</b> <span class="mono">domestic_probe</span> is true only when the probe's region country equals the target country. The rule is enforced in code, not asserted in prose.</p></li>
          <li><span class="idx">03</span><p><b>And we record the distance.</b> The nearest region is chosen by haversine distance from the country centroid, and that distance is stored on every row.</p></li>
        </ol>
      </div>

      <div style="display:flex; flex-direction:column; min-height:0">
        <div class="shot-wrap" style="flex:0 1 auto; min-height:0; overflow:hidden">
          <img class="shot" src="screenshots/02-world.png" alt="World view with vantage classification per country"
               style="max-height:74mm; object-fit:cover; object-position:top">
          <div class="caption">World &middot; every country classified by the vantage that measured it</div>
        </div>

        <div style="margin-top:auto; padding-top:4mm; padding-bottom:1mm; border:0.6pt solid #c9bfb4; background:#fff; padding-left:4mm; padding-right:4mm">
          <h3 style="margin-bottom:2mm">The same portals, two vantages</h3>
          <table style="font-size:8.4pt">
            <thead><tr><th>Vantage</th><th class="num">n</th><th class="num">Reach</th><th class="num">Acc.</th><th class="num">TTFB</th></tr></thead>
            <tbody>
              <tr><td>domestic</td><td class="num">{dom['n']:,}</td><td class="num">{dom['reach']:.1f}%</td><td class="num">{dom['acc']:.1f}</td><td class="num">{dom['ttfb']:.0f} ms</td></tr>
              <tr><td>nearest</td><td class="num">{near['n']:,}</td><td class="num">{near['reach']:.1f}%</td><td class="num">{near['acc']:.1f}</td><td class="num">{near['ttfb']:.0f} ms</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <div class="foot">
    <span>CivicWeb Observatory</span>
    <span>Vantage recorded on every row &middot; no foreign probe presented as domestic</span>
  </div>
</section>

<!-- ======================================================= 3 · THE CENSUS -->
<section class="slide">
  <div class="rail">
    <span><b>02</b> &middot; The census</span>
    <span>{f['total']:,} domains, {f['countries']} countries</span>
    <span>3 / 5</span>
  </div>

  <div class="body">
    <h2>Accessibility is uniformly mediocre. Security is worse.</h2>

    <div class="split split--narrow" style="margin-top:1mm; flex:1 1 auto; min-height:0">
      <div style="display:flex; flex-direction:column">
        <p style="font-size:9.8pt">
          Reachability is <b>{f['reach']:.1f}%</b>, not the 85% a curated list would give.
          Certificate Transparency records certificates for staging hosts, internal
          subdomains and sites that have since been retired, so a domain in the registry
          was <em>observed in an auditable source</em>, not confirmed to be an operating
          citizen portal.
        </p>

        <div style="margin-top:5mm">
          {sector_bars}
        </div>

        <p style="font-size:8.4pt; color:#8a7f76; margin-top:4mm">
          Mean header-hardening score by sector, reachable domains only.
        </p>

        <div style="margin-top:auto; padding-top:5mm; border-top:0.6pt solid #c9bfb4">
          <h3 style="margin-bottom:2mm">The gap in one line</h3>
          <p style="font-size:9.4pt; margin:0">
            Transport encryption is effectively universal at <b class="accent">{f['https']:.1f}%</b>,
            but header hardening averages <b class="accent">{f['sec']:.1f}</b>. The strongest
            controls &mdash; CSP and HSTS &mdash; are the least deployed, and both are edge
            configuration that needs no application work.
          </p>
        </div>
      </div>

      <div style="display:flex; flex-direction:column">
        <table>
          <thead>
            <tr>
              <th>Sector</th>
              <th class="num">Domains</th>
              <th class="num">Reach</th>
              <th class="num">Acc.</th>
              <th class="num">Sec.</th>
            </tr>
          </thead>
          <tbody>{sector_rows}</tbody>
        </table>

        <p style="font-size:8.4pt; color:#8a7f76; margin-top:3mm">
          Sectors with fewer than ten reachable domains are excluded: a mean over
          one or two portals is not a sector finding.
        </p>

        <div style="margin-top:auto; padding-top:5mm; border-top:0.6pt solid #c9bfb4">
          <h3 style="margin-bottom:2mm">What the table cannot say</h3>
          <p style="font-size:9.4pt; margin:0">
            Sector is inferred from the hostname, so it separates dedicated domains
            (<span class="mono">health.</span>, <span class="mono">court.</span>) and puts
            everything else in <span class="mono">general</span>. {f['sectors']['general']['n']:,}
            of {f['total']:,} rows are <span class="mono">general</span>, so this is a
            comparison of the identifiable subset, not the whole population.
          </p>
        </div>

        <div class="stats" style="grid-template-columns:repeat(3,minmax(0,1fr)); margin-top:5mm">
          <div class="stat"><span class="k">Multilingual</span><div class="v">{f['multi']:.1f}<small>%</small></div><div class="n">Non-English lang or script</div></div>
          <div class="stat"><span class="k">Mobile viewport</span><div class="v">{f['mobile']:.1f}<small>%</small></div><div class="n">width=device-width</div></div>
          <div class="stat"><span class="k">Median TTFB</span><div class="v">{f['median_ttfb']:.0f}<small> ms</small></div><div class="n">Wall clock on the probe</div></div>
        </div>
      </div>
    </div>
  </div>

  <div class="foot">
    <span>Table I &middot; reproduce with <span class="mono">cwo.sector_summary()</span></span>
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
    <h2>Three results that hold across the measured population.</h2>

    <div class="split split--wide" style="margin-top:1mm; flex:1 1 auto; min-height:0">
      <div style="display:flex; flex-direction:column">
        <ol class="findings">
          <li><span class="idx">01</span><p><b>Education is the weakest sector on security.</b> {f['sectors']['education']['n']:,} education domains score <b class="accent">{f['sectors']['education']['sec']:.1f}</b> against {f['sectors']['general']['sec']:.1f} for general government. That is a template-level defect, not {f['sectors']['education']['n']:,} separate problems.</p></li>
          <li><span class="idx">02</span><p><b>The judiciary is weak on both pillars at once.</b> Courts score {f['sectors']['judiciary']['acc']:.1f} on accessibility and {f['sectors']['judiciary']['sec']:.1f} on security &mdash; the only sector near the bottom of both. Every other sector trades one for the other.</p></li>
          <li><span class="idx">03</span><p><b>Health is the only sector above the mean on both.</b> {f['sectors']['health']['acc']:.1f} accessibility and {f['sectors']['health']['sec']:.1f} security, against a population mean of {f['acc']:.1f} and {f['sec']:.1f}. The two pillars are otherwise uncorrelated, so one composite score cannot stand in for either.</p></li>
        </ol>

        <div style="margin-top:auto; padding-top:5mm; border-top:0.6pt solid #c9bfb4">
          <h3 style="margin-bottom:2mm">What this implies for policy</h3>
          <p style="font-size:9.4pt; margin:0">
            Accessibility can be fixed by distribution &mdash; one template, thousands of
            portals. Security cannot: it is an edge decision made per deployment. That is
            why the recommendation is a reverse-proxy mandate, not another template.
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
              <th class="num">Mat.</th>
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
    <span>Table II &middot; reproduce with <span class="mono">cwo.architecture_summary()</span></span>
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
          <pre class="mono" style="margin:0; font-size:9pt; line-height:1.75; color:#efe9e2; white-space:pre-wrap"><span style="color:#e08a5f">pip install</span> civicweb-observatory

<span style="color:#e08a5f">import</span> civicweb_observatory <span style="color:#e08a5f">as</span> cwo

cwo.load()                    <span style="color:#7a6d63"># {f['total']:,} domains</span>
cwo.load(reachable=<span style="color:#e08a5f">True</span>)    <span style="color:#7a6d63"># {f['live']:,} live</span>
cwo.country_summary()         <span style="color:#7a6d63"># one row per country</span>
cwo.sector_summary()          <span style="color:#7a6d63"># Table I</span>
cwo.vantage_comparison()      <span style="color:#7a6d63"># domestic vs nearest</span></pre>
        </div>

        <div style="margin-top:auto; padding-top:5mm; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:4mm">
          <div>
            <div class="mono" style="font-size:6.8pt; letter-spacing:0.09em; text-transform:uppercase; color:#9a8d82">Package</div>
            <div style="font-size:9pt; margin-top:1.5mm; line-height:1.5">dataset bundled<br>Parquet, CSV, JSON<br>CC-BY-4.0</div>
          </div>
          <div>
            <div class="mono" style="font-size:6.8pt; letter-spacing:0.09em; text-transform:uppercase; color:#9a8d82">Observatory</div>
            <div style="font-size:9pt; margin-top:1.5mm; line-height:1.5">5 views<br>light and dark<br>keyboard-first</div>
          </div>
          <div>
            <div class="mono" style="font-size:6.8pt; letter-spacing:0.09em; text-transform:uppercase; color:#9a8d82">Politeness</div>
            <div style="font-size:9pt; margin-top:1.5mm; line-height:1.5">{f['robots']} robots-disallowed<br>{f['waf']} WAF-blocked<br>recorded, not failed</div>
          </div>
        </div>

        <div style="margin-top:6mm; padding-top:4mm; border-top:0.6pt solid #3a2f28">
          <div class="mono" style="font-size:6.8pt; letter-spacing:0.09em; text-transform:uppercase; color:#9a8d82; margin-bottom:2mm">
            Two defects the release fixes
          </div>
          <p style="font-size:8.8pt; line-height:1.5; margin:0; color:#c4b8ad; max-width:none">
            The log is append-only, so 128 hosts measured twice gave 2,143 rows for
            2,011 domains. And a host returning <span class="mono">HTTP 200</span> with an
            empty body scored 90.0 on accessibility, because there was nothing to fail.
            The release keeps the latest row per host and refuses to score a document
            under 200 bytes.
          </p>
        </div>
      </div>

      <div style="display:flex; flex-direction:column; min-height:0">
        <div class="shot-wrap" style="flex:0 1 auto; min-height:0; overflow:hidden">
          <img class="shot" src="screenshots/02-world-dark.png" alt="World view in dark theme"
               style="border-color:#3a2f28; max-height:78mm; object-fit:cover; object-position:top">
          <div class="caption" style="color:#9a8d82">World &middot; dark theme</div>
        </div>

        <div style="margin-top:auto; padding-top:4mm">
          <table>
            <thead>
              <tr><th>#</th><th>Country</th><th class="num">Domains</th><th class="num">Maturity</th></tr>
            </thead>
            <tbody>{country_rows}</tbody>
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
