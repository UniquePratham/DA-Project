"""Replace the India atlas with a global world view.

The World tab becomes the primary geographic view: a world map coloured by
vantage class, a country dossier, and a full country ranking. India becomes one
row in that ranking rather than the subject of the page.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "dashboard" / "index.html"

WORLD_VIEW = '''    <!-- =========================================================== 02 WORLD -->
    <section class="view" id="view-world" role="tabpanel" aria-labelledby="tab-world" tabindex="0" hidden>
      <div class="section" style="border-top:0; padding-top:0">
        <div class="section__head">
          <h2 class="section__title">World coverage</h2>
          <span class="section__note">249 countries &middot; 81 measured</span>
        </div>
        <p class="section__lede">
          Every country is classified by the vantage point that measured it. A
          <b>domestic</b> probe sits inside the country and describes what a citizen sees. A
          <b>nearest</b> probe sits in the closest available region and describes what a foreign
          client sees. The two are never conflated.
        </p>
      </div>

      <div class="world-wrap">
        <svg class="world-map" id="world-map" viewBox="0 0 1000 500" role="img"
             aria-label="World map of measurement coverage by vantage class"></svg>
        <div class="world-legend" id="world-legend"></div>
      </div>

      <div class="world-filters" id="world-filters" role="group" aria-label="Filter countries by status"></div>

      <div class="atlas" style="margin-top: var(--s5)">
        <div class="dossier" id="country-dossier">
          <div class="dossier__head">
            <h3 class="dossier__name" id="country-name">&mdash;</h3>
            <span class="dossier__rank" id="country-vantage"></span>
          </div>
          <div class="dossier__grid">
            <div class="dossier__cell">
              <span class="dossier__k">Domains</span>
              <div class="dossier__v" id="country-domains">&mdash;</div>
            </div>
            <div class="dossier__cell">
              <span class="dossier__k">Reachable</span>
              <div class="dossier__v" id="country-reach">&mdash;</div>
            </div>
            <div class="dossier__cell">
              <span class="dossier__k">Accessibility</span>
              <div class="dossier__v" id="country-acc">&mdash;</div>
            </div>
            <div class="dossier__cell">
              <span class="dossier__k">Security</span>
              <div class="dossier__v" id="country-sec">&mdash;</div>
            </div>
            <div class="dossier__cell">
              <span class="dossier__k">Maturity</span>
              <div class="dossier__v" id="country-mat">&mdash;</div>
            </div>
            <div class="dossier__cell">
              <span class="dossier__k">Median TTFB</span>
              <div class="dossier__v" id="country-ttfb">&mdash;</div>
            </div>
          </div>
          <p class="dossier__note" id="country-note"></p>
          <div style="margin-top: var(--s4); display:flex; gap: var(--s2); flex-wrap: wrap">
            <button class="btn" type="button" id="country-open-registry">
              <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="7" cy="7" r="4.6"/><path d="M10.4 10.4L14 14" stroke-linecap="round"/></svg>
              Open in registry
            </button>
            <button class="btn" type="button" id="country-copy">Copy summary</button>
          </div>
        </div>

        <div class="stack">
          <h3 class="section__title" style="font-size:var(--fs-h3); font-family:var(--font-ui); font-weight:600">
            What each vantage class can claim
          </h3>
          <div class="table-wrap">
            <table class="table" id="world-vantages">
              <thead>
                <tr><th>Vantage</th><th class="num">Countries</th><th>What it measures</th></tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
          <p class="future-note">
            A portal measured from both inside and outside its country answers how much of its measured
            quality is the portal and how much is the path to it. That comparison is the contribution.
          </p>
        </div>
      </div>

      <section class="section" style="margin-top: var(--s6)">
        <div class="section__head">
          <h2 class="section__title">Country ranking</h2>
          <span class="section__note">Measured countries, by accessibility</span>
        </div>
        <div class="ledger-scroll">
          <table class="ledger" id="country-rank">
            <thead>
              <tr>
                <th scope="col" style="width:3rem">#</th>
                <th scope="col">Country</th>
                <th scope="col">Vantage</th>
                <th scope="col" style="text-align:right">Domains</th>
                <th scope="col" style="text-align:right">Reachable</th>
                <th scope="col" style="text-align:right">Accessibility</th>
                <th scope="col" style="text-align:right">Security</th>
                <th scope="col" style="text-align:right">Median TTFB</th>
              </tr>
            </thead>
            <tbody id="country-rank-body"></tbody>
          </table>
        </div>
      </section>
    </section>

'''


def main() -> int:
    html = INDEX.read_text(encoding="utf-8")

    start = html.find("    <!-- =========================================================== 02 ATLAS -->")
    if start < 0:
        start = html.find('    <section class="view" id="view-world"')
    end = html.find("    <!-- ========================================================== 03 LEDGER -->")
    if end < 0:
        end = html.find('    <section class="view" id="view-registry"')

    if start < 0 or end < 0:
        print("could not locate the world view boundaries")
        return 1

    html = html[:start] + WORLD_VIEW + html[end:]
    INDEX.write_text(html, encoding="utf-8")
    print("world view rebuilt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
