"""Rebuild the Developers view as a real developer resource.

The old Method tab was prose about India. A developer page should let someone
actually use the data: install the package, query it, understand the schema,
call the API, and reproduce a figure.

Sections:

1. Quick start — install and load in three lines
2. Schema — every column, its type and meaning
3. Query recipes — the questions people actually ask
4. CLI — the commands
5. Reproduce — the exact code behind each figure
6. Limits — what the data cannot tell you
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "dashboard" / "index.html"

DEVELOPERS = '''    <!-- ====================================================== 05 DEVELOPERS -->
    <section class="view" id="view-developers" role="tabpanel" aria-labelledby="tab-developers" tabindex="0" hidden>
      <div class="section" style="border-top:0; padding-top:0">
        <div class="section__head">
          <h2 class="section__title">Developers</h2>
          <span class="section__note">Dataset &middot; package &middot; CLI</span>
        </div>
        <p class="section__lede">
          The dataset ships as Parquet, CSV and JSON, with a Python package and a CLI. Everything on this
          site is computed from the same release, so any figure can be reproduced without trusting the
          interface.
        </p>
      </div>

      <div class="stack">

        <section class="section">
          <div class="section__head">
            <h2 class="section__title">Quick start</h2>
            <span class="section__note">Python 3.9+</span>
          </div>
          <div class="code">
            <div class="code__bar"><span>shell</span><span>pip</span></div>
            <pre>pip install civicweb-observatory</pre>
          </div>
          <div class="code" style="margin-top:var(--s3)">
            <div class="code__bar"><span>Python</span><span>pandas &middot; pyarrow</span></div>
            <pre><span class="k">import</span> civicweb_observatory <span class="k">as</span> cwo

df   = cwo.load()                    <span class="c"># every measured domain</span>
live = cwo.load(reachable=<span class="k">True</span>)      <span class="c"># only those that answered</span>

cwo.country_summary()                <span class="c"># one row per country</span>
cwo.sector_summary()                 <span class="c"># one row per sector</span>
cwo.vantage_comparison()             <span class="c"># domestic vs nearest</span></pre>
          </div>
        </section>

        <section class="section">
          <div class="section__head">
            <h2 class="section__title">Schema</h2>
            <span class="section__note">20 columns</span>
          </div>
          <div class="table-wrap">
            <table class="table" id="schema-table">
              <thead>
                <tr><th>Column</th><th>Type</th><th>Meaning</th></tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </section>

        <section class="section">
          <div class="section__head">
            <h2 class="section__title">Query recipes</h2>
            <span class="section__note">Copy and run</span>
          </div>

          <div class="code">
            <div class="code__bar"><span>Which countries score worst on security?</span><span>pandas</span></div>
            <pre>live = cwo.load(reachable=<span class="k">True</span>)
live.groupby(<span class="s">"probe_country"</span>)[<span class="s">"sub_security_headers_score"</span>] \\
    .agg([<span class="s">"count"</span>, <span class="s">"mean"</span>]) \\
    .query(<span class="s">"count >= 10"</span>) \\
    .sort_values(<span class="s">"mean"</span>) \\
    .head(<span class="s">10</span>)</pre>
          </div>

          <div class="code" style="margin-top:var(--s3)">
            <div class="code__bar"><span>How much does distance cost?</span><span>pandas</span></div>
            <pre>live = cwo.load(reachable=<span class="k">True</span>)
live.groupby(<span class="s">"domestic_probe"</span>)[<span class="s">"sub_response_latency_ms"</span>] \\
    .agg([<span class="s">"count"</span>, <span class="s">"median"</span>, <span class="s">"mean"</span>])</pre>
          </div>

          <div class="code" style="margin-top:var(--s3)">
            <div class="code__bar"><span>Which sectors are worst on accessibility?</span><span>pandas</span></div>
            <pre>cwo.sector_summary().sort_values(<span class="s">"accessibility"</span>)</pre>
          </div>

          <div class="code" style="margin-top:var(--s3)">
            <div class="code__bar"><span>Export a filtered slice</span><span>pandas</span></div>
            <pre>df = cwo.load(reachable=<span class="k">True</span>, countries=[<span class="s">"IN"</span>, <span class="s">"GB"</span>, <span class="s">"JP"</span>])
df.to_parquet(<span class="s">"slice.parquet"</span>, index=<span class="k">False</span>)</pre>
          </div>
        </section>

        <section class="section">
          <div class="section__head">
            <h2 class="section__title">Command line</h2>
            <span class="section__note">No Python required</span>
          </div>
          <div class="code">
            <div class="code__bar"><span>shell</span><span>civicweb</span></div>
            <pre>civicweb info                       <span class="c"># release shape and headline figures</span>
civicweb countries --top 10         <span class="c"># ranked by accessibility</span>
civicweb sectors                    <span class="c"># sector breakdown</span>
civicweb vantage                    <span class="c"># domestic vs nearest</span>
civicweb query --country IN --min-accessibility 90
civicweb export --format csv --out slice.csv --reachable-only</pre>
          </div>
        </section>

        <section class="section">
          <div class="section__head">
            <h2 class="section__title">Reproduce a figure</h2>
            <span class="section__note">Every number on this site</span>
          </div>
          <div class="code">
            <div class="code__bar"><span>Python</span><span>pandas</span></div>
            <pre><span class="k">import</span> pandas <span class="k">as</span> pd

df   = pd.read_parquet(<span class="s">"resources/civicweb_observatory_clean.parquet"</span>)
live = df[df[<span class="s">"is_reachable"</span>]]

<span class="c"># Headline figures</span>
<span class="k">print</span>(<span class="s">"domains   "</span>, <span class="k">len</span>(df))
<span class="k">print</span>(<span class="s">"reachable "</span>, <span class="k">len</span>(live))
<span class="k">print</span>(<span class="s">"countries "</span>, df[<span class="s">"probe_country"</span>].nunique())
<span class="k">print</span>(<span class="s">"acc       "</span>, <span class="k">round</span>(live[<span class="s">"sub_accessibility_score"</span>].mean(), <span class="s">1</span>))
<span class="k">print</span>(<span class="s">"sec       "</span>, <span class="k">round</span>(live[<span class="s">"sub_security_headers_score"</span>].mean(), <span class="s">1</span>))

<span class="c"># The vantage finding</span>
<span class="k">print</span>(live.groupby(<span class="s">"domestic_probe"</span>)[<span class="s">"sub_response_latency_ms"</span>].median())</pre>
          </div>
        </section>

        <section class="section">
          <div class="section__head">
            <h2 class="section__title">What the data cannot tell you</h2>
          </div>
          <ul class="findings">
            <li><span class="findings__idx">01</span><div class="findings__body"><h3>Automated testing is not conformance</h3><p>axe-core catches a subset of WCAG failures. It cannot judge cognitive load, screen-reader audio flow or reading order. A domain scoring well here is free of the machine-detectable defects we tested for; it is not thereby WCAG-conformant.</p></div></li>
            <li><span class="findings__idx">02</span><div class="findings__body"><h3>LCP is estimated, never measured</h3><p>Largest Contentful Paint is derived from time to first byte and payload size. A true LCP needs a browser paint trace, which we did not run at scale.</p></div></li>
            <li><span class="findings__idx">03</span><div class="findings__body"><h3>Nearest probes are not domestic</h3><p>180 countries were measured from a probe in another country. The <code>domestic_probe</code> column says which. Filter on it before making a claim about what a citizen experiences.</p></div></li>
            <li><span class="findings__idx">04</span><div class="findings__body"><h3>Discovery is not verification</h3><p>A domain in the registry was observed in an auditable source. It was not confirmed to be an operational citizen portal, which is why reachability is 30% rather than near 100%.</p></div></li>
            <li><span class="findings__idx">05</span><div class="findings__body"><h3>One snapshot</h3><p>This release is a single observation. The dataset carries no per-domain timestamp series, so no trend claim is supported.</p></div></li>
          </ul>
        </section>

      </div>
    </section>

'''


def main() -> int:
    html = INDEX.read_text(encoding="utf-8")
    start = html.find("    <!-- ========================================================== 05 METHOD -->")
    end = html.find("  </div>\n</main>")
    if start < 0 or end < 0:
        print("could not locate developers boundaries")
        return 1
    html = html[:start] + DEVELOPERS + html[end:]
    INDEX.write_text(html, encoding="utf-8")
    print("developers view rebuilt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
