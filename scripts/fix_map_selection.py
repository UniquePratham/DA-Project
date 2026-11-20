"""Fix five real bugs in the world map selection.

1. **Listeners accumulate.** ``renderWorldMap`` is called on every filter click
   and every tab activation, and each call adds another ``click`` listener to
   the same SVG. After ten filter clicks, one click fires eleven handlers.

2. **No selection state.** ``selectCountry`` sets ``state.selectedCountry`` but
   never marks the path, so the map gives no visual feedback about what is
   selected.

3. **No keyboard access.** The paths are not focusable and have no key handler,
   so the map cannot be used without a mouse.

4. **Filtering does not dim.** Clicking "Nearest probe" re-renders the same map
   with the same colours; nothing indicates the filter is active.

5. **The dossier does not clear.** Selecting a country with no measurements
   leaves the previous country's numbers in place if the stats lookup fails.

The fix rewrites the map module around a single delegated listener, an explicit
selection overlay, keyboard support, and a dimmed state for filtered-out
countries.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
APP = REPO / "dashboard" / "static" / "app.js"

NEW_MAP = r'''  /* ---------------------------------------------------------- world map */

  const STATUS_LABEL = {
    operational: 'Domestic, measured',
    domestic_ready: 'Domestic, ready',
    nearest_available: 'Nearest probe',
    unmeasurable: 'Unmeasurable',
  };

  let worldFilter = 'all';
  let mapWired = false;

  function statusOf(code) {
    const w = state.world;
    if (!w) return 'unmeasurable';
    const c = (w.countries || []).find((x) => x.code === code);
    return c ? c.status : 'unmeasurable';
  }

  function countryByCode(code) {
    const w = state.world;
    return w ? (w.countries || []).find((c) => c.code === code) : null;
  }

  function renderWorldMap() {
    const svg = $('#world-map');
    const map = window.WORLD_MAP;
    if (!svg || !map) return;

    // Build the paths once. Re-rendering on every filter click would destroy
    // focus and re-add listeners; instead the paths persist and only their
    // classes change.
    if (!svg.dataset.built) {
      svg.innerHTML =
        (map.countries || [])
          .map((c) => {
            const status = statusOf(c.code);
            return (
              `<path class="world-country world-country--${esc(status)}" d="${c.d}" ` +
              `data-code="${esc(c.code)}" tabindex="0" role="button" ` +
              `aria-label="${esc(c.name)}: ${esc(STATUS_LABEL[status] || status)}"></path>`
            );
          })
          .join('') +
        '<path class="world-selected" d="" aria-hidden="true"></path>';
      svg.dataset.built = '1';
    }

    applyFilter();
    renderLegend();
    renderFilters();
    wireMapOnce();
    paintSelection();
  }

  function applyFilter() {
    const svg = $('#world-map');
    if (!svg) return;
    $$('.world-country', svg).forEach((path) => {
      const status = statusOf(path.dataset.code);
      const dim = worldFilter !== 'all' && status !== worldFilter;
      path.classList.toggle('is-dimmed', dim);
      path.setAttribute('aria-pressed', path.dataset.code === state.selectedCountry ? 'true' : 'false');
    });
  }

  function renderLegend() {
    const legend = $('#world-legend');
    if (!legend || !state.world) return;
    const counts = state.world.status_counts || {};
    legend.innerHTML = ['operational', 'domestic_ready', 'nearest_available', 'unmeasurable']
      .map(
        (s) =>
          `<span class="world-legend__item">` +
          `<span class="world-legend__swatch world-legend__swatch--${s}"></span>` +
          `${esc(STATUS_LABEL[s])} <b>${int(counts[s] || 0)}</b></span>`
      )
      .join('');
  }

  function renderFilters() {
    const filters = $('#world-filters');
    if (!filters || !state.world) return;
    const counts = state.world.status_counts || {};
    const opts = [
      ['all', 'All countries', state.world.total_countries],
      ['operational', 'Domestic, measured', counts.operational || 0],
      ['domestic_ready', 'Domestic, ready', counts.domestic_ready || 0],
      ['nearest_available', 'Nearest probe', counts.nearest_available || 0],
      ['unmeasurable', 'Unmeasurable', counts.unmeasurable || 0],
    ];
    filters.innerHTML = opts
      .map(
        ([k, label, n]) =>
          `<button type="button" class="world-filter${k === worldFilter ? ' is-active' : ''}" ` +
          `data-filter="${k}" aria-pressed="${k === worldFilter}">${esc(label)} <b>${int(n)}</b></button>`
      )
      .join('');
    $$('.world-filter', filters).forEach((btn) => {
      btn.addEventListener('click', () => {
        worldFilter = btn.dataset.filter;
        applyFilter();
        renderFilters();
      });
    });
  }

  function wireMapOnce() {
    if (mapWired) return;
    const svg = $('#world-map');
    if (!svg) return;
    mapWired = true;

    // One delegated listener for the life of the page.
    svg.addEventListener('click', (event) => {
      const path = event.target.closest('.world-country');
      if (path && path.dataset.code) selectCountry(path.dataset.code);
    });

    svg.addEventListener('keydown', (event) => {
      const path = event.target.closest('.world-country');
      if (!path || !path.dataset.code) return;
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        selectCountry(path.dataset.code);
      }
    });

    svg.addEventListener('mouseover', (event) => {
      const path = event.target.closest('.world-country');
      if (!path) return;
      const c = countryByCode(path.dataset.code);
      if (!c) return;
      showTip(
        event,
        `<b>${esc(c.name)}</b><br>${esc(STATUS_LABEL[c.status] || c.status)}` +
          (c.probe_city ? `<br>${esc(c.probe_city)}` : '')
      );
    });
    svg.addEventListener('mousemove', (event) => {
      if (event.target.closest('.world-country')) moveTip(event);
    });
    svg.addEventListener('mouseout', (event) => {
      if (event.target.closest('.world-country')) hideTip();
    });
  }

  function paintSelection() {
    const svg = $('#world-map');
    if (!svg) return;
    const outline = $('.world-selected', svg);
    const selected = state.selectedCountry
      ? $(`.world-country[data-code="${state.selectedCountry}"]`, svg)
      : null;
    if (outline) {
      outline.setAttribute('d', selected ? selected.getAttribute('d') : '');
    }
    $$('.world-country', svg).forEach((p) => {
      p.setAttribute('aria-pressed', p.dataset.code === state.selectedCountry ? 'true' : 'false');
    });
  }

  function selectCountry(code) {
    const cov = countryByCode(code);
    if (!cov) return;

    state.selectedCountry = code;
    paintSelection();

    const g = state.global;
    const stats = g ? (g.countries || []).find((c) => c.code === code) : null;

    const name = $('#country-name');
    if (name) name.textContent = cov.name;

    const vantage = $('#country-vantage');
    if (vantage) vantage.textContent = STATUS_LABEL[cov.status] || cov.status;

    const set = (id, value) => {
      const el = $(id);
      if (el) el.innerHTML = value;
    };

    // Always write every cell, so a country with no data cannot inherit the
    // previous country's numbers.
    if (stats) {
      set('#country-domains', int(stats.domains));
      set('#country-reach', `${int(stats.reachable)} <small>${dec(stats.reach_pct)}%</small>`);
      set('#country-acc', `${dec(stats.accessibility)} <small>/ 100</small>`);
      set('#country-sec', `${dec(stats.security)} <small>/ 100</small>`);
      set('#country-mat', `${dec(stats.maturity)} <small>/ 100</small>`);
      set('#country-ttfb', `${int(stats.median_ttfb_ms)} <small>ms</small>`);
    } else {
      ['#country-domains', '#country-reach', '#country-acc', '#country-sec', '#country-mat', '#country-ttfb']
        .forEach((id) => set(id, '<span class="muted">not measured</span>'));
    }

    const note = $('#country-note');
    if (note) note.textContent = cov.note || '';
  }

'''


def main() -> int:
    js = APP.read_text(encoding="utf-8")

    start = js.find("  /* ---------------------------------------------------------- world map */")
    end = js.find("  function renderCountryRank()")
    if start < 0 or end < 0:
        print("could not locate the map block")
        return 1

    js = js[:start] + NEW_MAP + js[end:]
    APP.write_text(js, encoding="utf-8")
    print("map module rewritten")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
