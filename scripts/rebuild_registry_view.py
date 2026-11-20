"""Rebuild the Registry view to match the new JS.

The old ledger had India-specific columns (Tier, State, Platform, Checks). The
registry now shows the global schema: domain, country, vantage, reachability,
accessibility, security, latency.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "dashboard" / "index.html"

REGISTRY = '''    <!-- ========================================================= 03 REGISTRY -->
    <section class="view" id="view-registry" role="tabpanel" aria-labelledby="tab-registry" tabindex="0" hidden>
      <div class="section" style="border-top:0; padding-top:0">
        <div class="section__head">
          <h2 class="section__title">Domain registry</h2>
          <span class="section__note">Every measured domain</span>
        </div>
        <p class="section__lede">
          Every domain with its measured values and the probe that produced them. A domain that did not
          answer keeps its diagnostic reason instead of a zero score, so a missing number always means
          &ldquo;not measured&rdquo; rather than &ldquo;measured as zero&rdquo;.
        </p>
      </div>

      <div class="ledger-tools">
        <div class="field">
          <label class="field__label" for="registry-search">Search</label>
          <input class="input input--search" id="registry-search" type="search"
                 placeholder="domain, entity, country&hellip;" autocomplete="off">
        </div>
        <div class="field">
          <label class="field__label" for="registry-tier">Tier</label>
          <select class="select" id="registry-tier">
            <option value="all">All tiers</option>
          </select>
        </div>
        <div class="field">
          <label class="field__label" for="registry-status">Status</label>
          <select class="select" id="registry-status">
            <option value="all">All</option>
            <option value="reachable" selected>Reachable</option>
            <option value="unreachable">Unreachable</option>
          </select>
        </div>
        <div class="field">
          <label class="field__label" for="registry-sort">Sort</label>
          <select class="select" id="registry-sort">
            <option value="domain">Domain, A to Z</option>
            <option value="acc">Accessibility, high to low</option>
            <option value="sec">Security, high to low</option>
            <option value="lat">Latency, low to high</option>
          </select>
        </div>
        <button class="btn" type="button" id="registry-export">
          <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M8 2v8M4.8 7.2L8 10.4l3.2-3.2M2.5 12.5h11" stroke-linecap="round" stroke-linejoin="round"/></svg>
          Export CSV
        </button>
      </div>

      <div class="ledger-scroll">
        <table class="ledger" id="registry-table">
          <thead>
            <tr>
              <th scope="col">Domain</th>
              <th scope="col">Entity</th>
              <th scope="col">Tier</th>
              <th scope="col">Country</th>
              <th scope="col" style="text-align:right">Reachable</th>
              <th scope="col" style="text-align:right">Access.</th>
              <th scope="col" style="text-align:right">Security</th>
              <th scope="col" style="text-align:right">TTFB</th>
            </tr>
          </thead>
          <tbody id="registry-body"></tbody>
        </table>
      </div>

      <div class="pager">
        <span class="pager__count" id="registry-count">&mdash;</span>
        <div class="pager__nav">
          <button class="btn" type="button" id="registry-prev">Previous</button>
          <span class="pager__pos" id="registry-page">&mdash;</span>
          <button class="btn" type="button" id="registry-next">Next</button>
        </div>
      </div>
    </section>

'''


def main() -> int:
    html = INDEX.read_text(encoding="utf-8")
    start = html.find("    <!-- ========================================================== 03 LEDGER -->")
    end = html.find("    <!-- ======================================================== 04 STANDARD -->")
    if start < 0 or end < 0:
        print("could not locate registry boundaries")
        return 1
    html = html[:start] + REGISTRY + html[end:]
    INDEX.write_text(html, encoding="utf-8")
    print("registry view rebuilt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
