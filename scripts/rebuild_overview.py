"""Rebuild the Overview as a global-first page.

The old overview was an India census: "36 States and Union Territories",
"domestic peering fabric", "NIC gateways". The project now measures 81
countries, so the overview leads with the global picture and treats India as
one country among many.

New overview:

1. Headline band — countries measured, domains, reachability, accessibility
2. The vantage finding — domestic vs nearest, the core result
3. What the measurement found — findings computed from the data
4. Coverage by vantage class
5. Sector breakdown
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "dashboard" / "index.html"

OVERVIEW = '''    <!-- ======================================================== 01 OVERVIEW -->
    <section class="view" id="view-overview" role="tabpanel" aria-labelledby="tab-overview" tabindex="0">

      <div class="band" aria-label="Headline figures">
        <div class="band__cell">
          <span class="band__label">Countries measured</span>
          <div class="band__value" data-bind="countries">&mdash;</div>
          <p class="band__note">Of 249 classified. 19 measured domestically, the rest from nearest probes.</p>
        </div>
        <div class="band__cell">
          <span class="band__label">Domains measured</span>
          <div class="band__value" data-bind="total">&mdash;</div>
          <p class="band__note">Every row carries the probe region, distance and vantage class.</p>
        </div>
        <div class="band__cell">
          <span class="band__label">Reachable</span>
          <div class="band__value"><span data-bind="reachable">&mdash;</span><span class="band__unit" data-bind="reachablePct">&mdash;</span></div>
          <p class="band__note"><em data-bind="unreachable">&mdash;</em> returned no response from their probe.</p>
        </div>
        <div class="band__cell">
          <span class="band__label">Mean accessibility</span>
          <div class="band__value"><span data-bind="acc">&mdash;</span><span class="band__unit">/ 100</span></div>
          <p class="band__note">axe-core 4.x WCAG 2.1 AA across reachable domains.</p>
        </div>
      </div>

      <div class="stack" style="margin-top: var(--s6)">

        <section class="section">
          <div class="section__head">
            <h2 class="section__title">The vantage finding</h2>
            <span class="section__note">Same portals, two vantage points</span>
          </div>
          <p class="section__lede">
            A portal measured from inside its country and from the nearest foreign region gives two
            different answers. The gap is the cost of distance, not a difference in the portals &mdash;
            and it is the result a single-vantage study cannot produce.
          </p>
          <div class="table-wrap">
            <table class="table" id="overview-vantage">
              <thead>
                <tr>
                  <th>Vantage</th><th class="num">Domains</th>
                  <th class="num">Reachable</th><th class="num">Accessibility</th>
                  <th class="num">Security</th><th class="num">Median TTFB</th>
                </tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </section>

        <section class="section">
          <div class="section__head">
            <h2 class="section__title">What the measurement found</h2>
            <span class="section__note">n = <span data-bind="reachable">&mdash;</span> reachable</span>
          </div>
          <p class="section__lede">
            Results that hold across the measured population. Every figure is computed from the released
            dataset at load time &mdash; nothing on this page is illustrative.
          </p>
          <ol class="findings" id="findings"></ol>
        </section>

        <section class="section">
          <div class="section__head">
            <h2 class="section__title">Coverage by vantage class</h2>
            <span class="section__note">249 countries classified</span>
          </div>
          <div class="table-wrap">
            <table class="table" id="overview-coverage">
              <thead>
                <tr><th>Vantage</th><th class="num">Countries</th><th>What it measures</th></tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </section>

        <section class="section">
          <div class="section__head">
            <h2 class="section__title">By sector</h2>
            <span class="section__note">Inferred from hostname</span>
          </div>
          <div class="table-wrap">
            <table class="table" id="overview-sectors">
              <thead>
                <tr>
                  <th>Sector</th><th class="num">Domains</th>
                  <th class="num">Reachable</th><th class="num">Accessibility</th>
                  <th class="num">Security</th><th class="num">Median TTFB</th>
                </tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </section>

        <section class="section">
          <div class="section__head">
            <h2 class="section__title">Top and bottom countries</h2>
            <span class="section__note">By mean accessibility</span>
          </div>
          <div class="split split--even">
            <figure class="figure">
              <div id="chart-top-countries"></div>
              <figcaption class="figure__caption"><b>Figure 1.</b> Highest mean accessibility.</figcaption>
            </figure>
            <figure class="figure">
              <div id="chart-bottom-countries"></div>
              <figcaption class="figure__caption"><b>Figure 2.</b> Lowest mean accessibility.</figcaption>
            </figure>
          </div>
        </section>

      </div>
    </section>

'''


def main() -> int:
    html = INDEX.read_text(encoding="utf-8")
    start = html.find("    <!-- ======================================================== 01 OVERVIEW -->")
    end = html.find("    <!-- =========================================================== 02 WORLD -->")
    if start < 0 or end < 0:
        print("could not locate overview boundaries")
        return 1
    html = html[:start] + OVERVIEW + html[end:]
    INDEX.write_text(html, encoding="utf-8")
    print("overview rebuilt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
