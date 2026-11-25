(function () {
  'use strict';

  /* ------------------------------------------------------------- helpers */

  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  const esc = (v) =>
    String(v == null ? '' : v).replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));

  const int = (v) => (v == null || Number.isNaN(Number(v)) ? '—' : Number(v).toLocaleString('en-US'));
  const dec = (v, d) => (v == null || Number.isNaN(Number(v)) ? '—' : Number(v).toFixed(d == null ? 1 : d));

  const mean = (xs) => {
    const v = xs.filter((x) => x != null && !Number.isNaN(x));
    return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null;
  };

  const median = (xs) => {
    const v = xs.filter((x) => x != null && !Number.isNaN(x)).sort((a, b) => a - b);
    if (!v.length) return null;
    const m = Math.floor(v.length / 2);
    return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2;
  };

  /* --------------------------------------------------------------- state */

  const state = {
    rows: [],
    live: [],
    global: null,
    world: null,
    selectedCountry: null,
    registry: { page: 0, size: 40, query: '', tier: 'all', status: 'all', sort: 'domain' },
    theme: 'light',
  };

  const VIEWS = ['overview', 'world', 'registry', 'standard', 'developers'];

  /* ------------------------------------------------------------ findings */

  function renderBinds() {
    const g = state.global;
    const rows = state.rows;
    const live = state.live;

    const set = (name, value) => {
      $$(`[data-bind="${name}"]`).forEach((el) => {
        el.textContent = value;
      });
    };

    set('countries', g ? int(g.countries_measured) : '—');
    set('total', g ? int(g.total_rows) : int(rows.length));
    const totalRows = g ? g.total_rows : rows.length;
    // Count the rows; never derive a count by rounding a percentage.
    const reachRows = g ? int(g.reachable_rows) : live.length;
    set('reachable', int(reachRows));
    set('reachablePct', g ? `${dec(g.overall_reach_pct)}%` : '—');
    set('unreachable', int(totalRows - reachRows));
    set('acc', dec(mean(live.map((r) => r.acc_score))));
    set('sec', dec(mean(live.map((r) => r.sec_score))));
    set('maturity', dec(mean(live.map((r) => r.maturity_score))));

    const note = $('#world-note');
    if (note && state.world) {
      note.textContent =
        `${int(state.world.total_countries)} countries classified · ` +
        `${int(g ? g.countries_measured : 0)} measured`;
    }
  }

  function renderFindings() {
    const host = $('#findings');
    if (!host) return;
    const g = state.global;
    const live = state.live;
    if (!g || !live.length) {
      host.innerHTML = '';
      return;
    }

    const dom = g.vantage_comparison.find((v) => v.vantage === 'domestic');
    const near = g.vantage_comparison.find((v) => v.vantage === 'nearest');
    const worstSec = (g.sectors || [])
      .filter((s) => s.security != null && s.domains >= 20)
      .sort((a, b) => a.security - b.security)[0];
    const bestAcc = (g.sectors || [])
      .filter((s) => s.accessibility != null && s.domains >= 20)
      .sort((a, b) => b.accessibility - a.accessibility)[0];

    const items = [];

    if (dom && near) {
      items.push({
        h: 'Distance costs more than the portal does',
        p: `The same kind of portal measured from inside its country answers in ${int(dom.median_ttfb_ms)} ms; from the nearest foreign region, ${int(near.median_ttfb_ms)} ms. That ${int(near.median_ttfb_ms - dom.median_ttfb_ms)} ms gap is the path, not the portal.`,
      });
    }

    items.push({
      h: 'Reachability is a discovery artefact, not a failure rate',
      p: `${int(state.rows.length - live.length)} of ${int(state.rows.length)} domains did not answer. Most were found in Certificate Transparency, which logs certificates for hosts that were never public portals.`,
    });

    if (worstSec) {
      items.push({
        h: `${worstSec.sector} is the weakest sector on security`,
        p: `Across ${int(worstSec.domains)} domains, mean header hardening is ${dec(worstSec.security)} of 100. That is a template-level defect, not individual neglect.`,
      });
    }

    if (bestAcc) {
      items.push({
        h: `${bestAcc.sector} leads on accessibility`,
        p: `Mean accessibility is ${dec(bestAcc.accessibility)} of 100 across ${int(bestAcc.domains)} domains, above the ${dec(mean(live.map((r) => r.acc_score)))} national mean.`,
      });
    }

    items.push({
      h: 'Security lags accessibility everywhere',
      p: `Mean accessibility is ${dec(mean(live.map((r) => r.acc_score)))}; mean header hardening is ${dec(mean(live.map((r) => r.sec_score)))}. Templates ship accessible markup; they cannot ship a content security policy.`,
    });

    host.innerHTML = items
      .map(
        (it, i) =>
          `<li><span class="findings__idx">${String(i + 1).padStart(2, '0')}</span>` +
          `<div class="findings__body"><h3>${esc(it.h)}</h3><p>${esc(it.p)}</p></div></li>`
      )
      .join('');
  }

  /* ------------------------------------------------------------- tables */

  function renderVantageTable(sel, data) {
    const body = $(`${sel} tbody`);
    if (!body || !data) return;
    body.innerHTML = data
      .map(
        (v) =>
          '<tr>' +
          `<td><b>${esc(v.vantage)}</b></td>` +
          `<td class="num">${int(v.domains)}</td>` +
          `<td class="num">${int(v.reachable)} <span class="muted">${dec(v.reach_pct)}%</span></td>` +
          `<td class="num">${dec(v.accessibility)}</td>` +
          `<td class="num">${dec(v.security)}</td>` +
          `<td class="num">${v.median_ttfb_ms == null ? '—' : int(v.median_ttfb_ms) + ' ms'}</td>` +
          '</tr>'
      )
      .join('');
  }

  function renderCoverageTable() {
    const body = $('#overview-coverage tbody');
    const w = state.world;
    if (!body || !w) return;
    const vc = w.vantage_counts || {};
    const rows = [
      ['domestic', vc.domestic || 0, 'Probe inside the country. Describes what a citizen sees.'],
      ['nearest', vc.nearest || 0, 'Probe in the closest region, in another country. Describes a foreign client.'],
      ['unmeasurable', vc.unmeasurable || 0, 'Nearest region over 6,000 km away. A latency figure would describe the path.'],
    ];
    body.innerHTML = rows
      .map(
        ([k, n, meaning]) =>
          `<tr><td><b>${esc(k)}</b></td><td class="num">${int(n)}</td>` +
          `<td class="muted">${esc(meaning)}</td></tr>`
      )
      .join('');
  }

  function renderSectorTable(sel, sectors) {
    const body = $(`${sel} tbody`);
    if (!body || !sectors) return;
    body.innerHTML = sectors
      .map(
        (s) =>
          '<tr>' +
          `<td><b>${esc(s.sector)}</b></td>` +
          `<td class="num">${int(s.domains)}</td>` +
          `<td class="num">${int(s.reachable)} <span class="muted">${dec(s.reach_pct)}%</span></td>` +
          `<td class="num">${dec(s.accessibility)}</td>` +
          `<td class="num">${dec(s.security)}</td>` +
          `<td class="num">${s.median_ttfb_ms == null ? '—' : int(s.median_ttfb_ms) + ' ms'}</td>` +
          '</tr>'
      )
      .join('');
  }

  function renderSchemaTable() {
    const body = $('#schema-table tbody');
    if (!body) return;
    const cols = [
      ['domain_name', 'string', 'Registered domain identifier'],
      ['probe_country', 'string', 'ISO-3166 alpha-2 of the country measured'],
      ['probe_region', 'string', 'Cloud region that performed the measurement'],
      ['probe_region_country', 'string', 'Country the probe physically sits in'],
      ['domestic_probe', 'boolean', 'True when the probe is inside the target country'],
      ['distance_km', 'integer', 'Great-circle distance from country centroid to probe'],
      ['is_reachable', 'boolean', 'True when the domain answered with HTTP < 400'],
      ['measurement_reason', 'string', 'Why a domain was unreachable, or the status code'],
      ['sub_accessibility_score', 'float', 'axe-core severity-weighted index, 0–100'],
      ['sub_security_headers_score', 'float', 'OWASP directive score, 0–100'],
      ['sub_response_latency_ms', 'float', 'Time to first byte, milliseconds'],
      ['sub_lcp_est_sec', 'float', 'Estimated Largest Contentful Paint, seconds'],
      ['sub_https_enforced', 'boolean', 'Final URL served over TLS'],
      ['sub_is_multilingual', 'boolean', 'Non-English lang, hreflang, or Indic script present'],
      ['sub_mobile_responsive', 'boolean', 'Viewport declared and no overflow at 375 px'],
      ['sub_cms_architecture', 'string', 'Fingerprinted platform'],
      ['sub_has_citizen_services', 'boolean', 'Search or grievance affordance present'],
      ['observatory_maturity_score', 'float', 'Composite index, 0–100'],
      ['blocked_by_waf', 'boolean', 'A bot filter refused the request'],
      ['robots_disallowed', 'boolean', 'robots.txt forbade the path'],
    ];
    body.innerHTML = cols
      .map(
        ([name, type, meaning]) =>
          `<tr><td><code>${esc(name)}</code></td><td class="muted">${esc(type)}</td>` +
          `<td>${esc(meaning)}</td></tr>`
      )
      .join('');
  }

  /* ------------------------------------------------------------ tooltip */

  function showTip(event, html) {
    const tip = $('#tip');
    if (!tip) return;
    tip.innerHTML = html;
    tip.setAttribute('aria-hidden', 'false');
    tip.classList.add('is-visible');
    moveTip(event);
  }

  function moveTip(event) {
    const tip = $('#tip');
    if (!tip) return;
    const pad = 14;
    const w = tip.offsetWidth || 180;
    const h = tip.offsetHeight || 60;
    let x = event.clientX + pad;
    let y = event.clientY + pad;
    if (x + w > window.innerWidth - 8) x = event.clientX - w - pad;
    if (y + h > window.innerHeight - 8) y = event.clientY - h - pad;
    tip.style.left = `${Math.max(8, x)}px`;
    tip.style.top = `${Math.max(8, y)}px`;
  }

  function hideTip() {
    const tip = $('#tip');
    if (!tip) return;
    tip.classList.remove('is-visible');
    tip.setAttribute('aria-hidden', 'true');
  }

  /* ---------------------------------------------------------- world map */

  const STATUS_LABEL = {
    operational: 'Domestic, measured',
    domestic_ready: 'Domestic, ready',
    nearest_measured: 'Nearest, measured',
    nearest_available: 'Nearest, ready',
    unmeasurable: 'Unmeasurable',
  };

  const STATUS_ORDER = [
    'operational',
    'domestic_ready',
    'nearest_measured',
    'nearest_available',
    'unmeasurable',
  ];

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

  function countryName(code) {
    const c = countryByCode(code);
    return c ? c.name : code;
  }

  function renderWorldMap() {
    const svg = $('#world-map');
    const map = window.WORLD_MAP;
    if (!svg || !map) return;

    // Build the paths once. Re-rendering on every filter click would destroy
    // focus and re-add listeners; instead the paths persist and only their
    // classes change.
    if (!svg.dataset.built) {
      const markers = (map.markers || [])
        .map(
          (m) =>
            `<circle class="world-marker world-marker--${esc(statusOf(m.code))}" ` +
            `cx="${m.x}" cy="${m.y}" r="3.4" data-code="${esc(m.code)}" ` +
            `tabindex="0" role="button" ` +
            `aria-label="${esc(countryName(m.code))}: ${esc(STATUS_LABEL[statusOf(m.code)] || statusOf(m.code))}"></circle>`
        )
        .join('');

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
        markers +
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
    $$('.world-country, .world-marker', svg).forEach((el) => {
      const status = statusOf(el.dataset.code);
      const dim = worldFilter !== 'all' && status !== worldFilter;
      el.classList.toggle('is-dimmed', dim);
      el.setAttribute('aria-pressed', el.dataset.code === state.selectedCountry ? 'true' : 'false');
    });
  }

  function renderLegend() {
    const legend = $('#world-legend');
    if (!legend || !state.world) return;
    const counts = state.world.status_counts || {};
    legend.innerHTML = STATUS_ORDER
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
      ...STATUS_ORDER.map((s) => [s, STATUS_LABEL[s], counts[s] || 0]),
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

    const target = (event) => event.target.closest('.world-country, .world-marker');

    // One delegated listener for the life of the page.
    svg.addEventListener('click', (event) => {
      const el = target(event);
      if (el && el.dataset.code) selectCountry(el.dataset.code);
    });

    svg.addEventListener('keydown', (event) => {
      const el = target(event);
      if (!el || !el.dataset.code) return;
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        selectCountry(el.dataset.code);
      }
    });

    svg.addEventListener('mouseover', (event) => {
      const el = target(event);
      if (!el) return;
      const c = countryByCode(el.dataset.code);
      if (!c) return;
      showTip(
        event,
        `<b>${esc(c.name)}</b><br>${esc(STATUS_LABEL[c.status] || c.status)}` +
          (c.probe_city ? `<br>${esc(c.probe_city)}` : '')
      );
    });
    svg.addEventListener('mousemove', (event) => {
      if (target(event)) moveTip(event);
    });
    svg.addEventListener('mouseout', (event) => {
      if (target(event)) hideTip();
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
    $$('.world-country, .world-marker', svg).forEach((el) => {
      el.setAttribute('aria-pressed', el.dataset.code === state.selectedCountry ? 'true' : 'false');
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

  function renderWorldVantages() {
    const body = $('#world-vantages tbody');
    const w = state.world;
    if (!body || !w) return;
    const vc = w.vantage_counts || {};
    const rows = [
      ['domestic', vc.domestic || 0, 'Probe inside the country. Describes what a citizen sees.'],
      ['nearest', vc.nearest || 0, 'Probe in the closest region, in another country. Describes a foreign client.'],
      ['unmeasurable', vc.unmeasurable || 0, 'Nearest region over 6,000 km away. A latency figure would describe the path.'],
    ];
    body.innerHTML = rows
      .map(
        ([k, n, meaning]) =>
          `<tr><td><b>${esc(k)}</b></td><td class="num">${int(n)}</td>` +
          `<td class="muted">${esc(meaning)}</td></tr>`
      )
      .join('');
  }

  function renderCountryRank() {
    const body = $('#country-rank-body');
    const g = state.global;
    if (!body || !g) return;
    const rows = (g.countries || []).slice().sort((a, b) => (b.accessibility || 0) - (a.accessibility || 0));
    body.innerHTML = rows
      .map(
        (c, i) =>
          '<tr>' +
          `<td class="muted">${i + 1}</td>` +
          `<td><b>${esc(c.name)}</b> <span class="muted">${esc(c.code)}</span></td>` +
          `<td class="muted">${c.domestic_probe ? 'domestic' : 'nearest'}</td>` +
          `<td class="num">${int(c.domains)}</td>` +
          `<td class="num">${int(c.reachable)} <span class="muted">${dec(c.reach_pct)}%</span></td>` +
          `<td class="num">${dec(c.accessibility)}</td>` +
          `<td class="num">${dec(c.security)}</td>` +
          `<td class="num">${c.median_ttfb_ms == null ? '—' : int(c.median_ttfb_ms) + ' ms'}</td>` +
          '</tr>'
      )
      .join('');
  }

  /* ------------------------------------------------------------- charts */

  function barChart(host, rows, label) {
    if (!host) return;
    const max = Math.max.apply(null, rows.map((r) => r.value)) || 1;
    host.innerHTML =
      `<svg viewBox="0 0 400 ${rows.length * 26 + 10}" width="400" height="${rows.length * 26 + 10}" ` +
      `role="img" aria-label="${esc(label)}" style="width:100%;height:auto">` +
      rows
        .map((r, i) => {
          const w = Math.max(2, (r.value / max) * 250);
          const y = i * 26 + 6;
          return (
            `<text x="0" y="${y + 12}" font-size="11" fill="currentColor">${esc(r.label)}</text>` +
            `<rect x="120" y="${y}" width="${w}" height="16" fill="var(--data-4)"></rect>` +
            `<text x="${124 + w}" y="${y + 12}" font-size="11" fill="currentColor">${dec(r.value)}</text>`
          );
        })
        .join('') +
      '</svg>';
  }

  function renderCharts() {
    const g = state.global;
    if (!g) return;
    const ranked = (g.countries || []).filter((c) => c.accessibility != null);
    const top = ranked.slice(0, 8).map((c) => ({ label: c.name, value: c.accessibility }));
    const bottom = ranked
      .slice(-8)
      .reverse()
      .map((c) => ({ label: c.name, value: c.accessibility }));
    barChart($('#chart-top-countries'), top, 'Highest mean accessibility by country');
    barChart($('#chart-bottom-countries'), bottom, 'Lowest mean accessibility by country');
  }

  /* ----------------------------------------------------------- registry */

  function filteredRows() {
    const r = state.registry;
    let rows = state.rows;
    if (r.query) {
      const q = r.query.toLowerCase();
      rows = rows.filter(
        (x) =>
          (x.domain || '').toLowerCase().includes(q) ||
          (x.entity || '').toLowerCase().includes(q) ||
          (x.state || '').toLowerCase().includes(q) ||
          (x.country || '').toLowerCase().includes(q)
      );
    }
    if (r.tier !== 'all') rows = rows.filter((x) => x.level === r.tier);
    if (r.status === 'reachable') rows = rows.filter((x) => x.reachable);
    if (r.status === 'unreachable') rows = rows.filter((x) => !x.reachable);

    const key = r.sort;
    rows = rows.slice().sort((a, b) => {
      if (key === 'domain') return (a.domain || '').localeCompare(b.domain || '');
      if (key === 'acc') return (b.acc_score || -1) - (a.acc_score || -1);
      if (key === 'sec') return (b.sec_score || -1) - (a.sec_score || -1);
      if (key === 'lat') return (a.latency_ms || 1e9) - (b.latency_ms || 1e9);
      return 0;
    });
    return rows;
  }

  function renderRegistry() {
    const body = $('#registry-body');
    if (!body) return;
    const rows = filteredRows();
    const r = state.registry;
    const start = r.page * r.size;
    const page = rows.slice(start, start + r.size);

    body.innerHTML = page
      .map(
        (x) =>
          '<tr>' +
          `<td><code>${esc(x.domain)}</code></td>` +
          `<td>${esc(x.entity || '')}</td>` +
          `<td class="muted">${esc(x.level || '')}</td>` +
          `<td class="muted">${esc(x.state || '')}</td>` +
          `<td class="num">${x.reachable ? 'yes' : 'no'}</td>` +
          `<td class="num">${dec(x.acc_score)}</td>` +
          `<td class="num">${dec(x.sec_score)}</td>` +
          `<td class="num">${x.latency_ms == null ? '—' : int(x.latency_ms) + ' ms'}</td>` +
          '</tr>'
      )
      .join('');

    const count = $('#registry-count');
    if (count) count.textContent = `${int(rows.length)} domains`;

    const pager = $('#registry-page');
    if (pager) {
      const pages = Math.max(1, Math.ceil(rows.length / r.size));
      pager.textContent = `Page ${r.page + 1} of ${pages}`;
    }
  }

  function wireRegistry() {
    const search = $('#registry-search');
    if (search) {
      search.addEventListener('input', () => {
        state.registry.query = search.value;
        state.registry.page = 0;
        // A search should not be silently narrowed by the status filter.
        if (search.value) {
          state.registry.status = 'all';
          const sel = $('#registry-status');
          if (sel) sel.value = 'all';
        }
        renderRegistry();
      });
    }
    const tier = $('#registry-tier');
    if (tier) {
      tier.addEventListener('change', () => {
        state.registry.tier = tier.value;
        state.registry.page = 0;
        renderRegistry();
      });
    }
    const status = $('#registry-status');
    if (status) {
      status.addEventListener('change', () => {
        state.registry.status = status.value;
        state.registry.page = 0;
        renderRegistry();
      });
    }
    const sort = $('#registry-sort');
    if (sort) {
      sort.addEventListener('change', () => {
        state.registry.sort = sort.value;
        renderRegistry();
      });
    }
    const prev = $('#registry-prev');
    if (prev) {
      prev.addEventListener('click', () => {
        state.registry.page = Math.max(0, state.registry.page - 1);
        renderRegistry();
      });
    }
    const next = $('#registry-next');
    if (next) {
      next.addEventListener('click', () => {
        state.registry.page += 1;
        renderRegistry();
      });
    }
    const exp = $('#registry-export');
    if (exp) {
      exp.addEventListener('click', () => {
        const rows = filteredRows();
        const head = ['domain', 'entity', 'level', 'state', 'reachable', 'acc', 'sec', 'latency_ms'];
        const csv = [head.join(',')]
          .concat(
            rows.map((x) =>
              [x.domain, x.entity, x.level, x.state, x.reachable, x.acc_score, x.sec_score, x.latency_ms]
                .map((v) => `"${String(v == null ? '' : v).replace(/"/g, '""')}"`)
                .join(',')
            )
          )
          .join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'civicweb-registry.csv';
        a.click();
      });
    }
  }

  /* --------------------------------------------------------------- tabs */

  function activateView(name, focus) {
    if (VIEWS.indexOf(name) === -1) return;
    VIEWS.forEach((v) => {
      const panel = document.getElementById(`view-${v}`);
      const tab = document.getElementById(`tab-${v}`);
      const active = v === name;
      if (panel) panel.hidden = !active;
      if (tab) {
        tab.setAttribute('aria-selected', active ? 'true' : 'false');
        tab.tabIndex = active ? 0 : -1;
        if (active && focus) tab.focus();
      }
    });
    if (name === 'world') {
      renderWorldMap();
      renderWorldVantages();
    }
    if (history.replaceState) history.replaceState(null, '', `#${name}`);
  }

  function wireTabs() {
    const tabs = $$('.rail__btn');
    tabs.forEach((tab) => {
      tab.addEventListener('click', () => activateView(tab.dataset.view));
      tab.addEventListener('keydown', (event) => {
        const i = tabs.indexOf(tab);
        let next = null;
        if (event.key === 'ArrowRight') next = (i + 1) % tabs.length;
        if (event.key === 'ArrowLeft') next = (i - 1 + tabs.length) % tabs.length;
        if (event.key === 'Home') next = 0;
        if (event.key === 'End') next = tabs.length - 1;
        if (next == null) return;
        event.preventDefault();
        activateView(tabs[next].dataset.view, true);
      });
    });
    const initial = (location.hash || '').replace('#', '');
    if (VIEWS.indexOf(initial) !== -1) activateView(initial);
  }

  /* -------------------------------------------------------------- theme */

  function applyTheme(theme) {
    state.theme = theme;
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem('civicweb-theme', theme);
    } catch (e) {}
    $$('[data-theme-set]').forEach((b) => {
      b.setAttribute('aria-pressed', b.dataset.themeSet === theme ? 'true' : 'false');
    });
  }

  function wireTheme() {
    let saved = null;
    try {
      saved = localStorage.getItem('civicweb-theme');
    } catch (e) {}
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyTheme(saved || (prefersDark ? 'dark' : 'light'));
    $$('[data-theme-set]').forEach((b) => {
      b.addEventListener('click', () => applyTheme(b.dataset.themeSet));
    });
  }

  /* ---------------------------------------------------------- shortcuts */

  function wireShortcuts() {
    document.addEventListener('keydown', (event) => {
      const tag = (event.target.tagName || '').toLowerCase();
      if (tag === 'input' || tag === 'textarea' || tag === 'select') return;
      if (event.key === 't') applyTheme(state.theme === 'dark' ? 'light' : 'dark');
      const n = parseInt(event.key, 10);
      if (n >= 1 && n <= VIEWS.length) activateView(VIEWS[n - 1]);
    });
  }

  /* --------------------------------------------------------------- boot */

  function boot() {
    const rows = window.RAW_DATASET;
    if (!Array.isArray(rows) || !rows.length) {
      const host = $('#findings');
      if (host) {
        host.innerHTML =
          '<li><span class="findings__idx">!</span><div class="findings__body">' +
          '<h3>Dataset unavailable</h3><p>The bundle did not load. Open this page from the ' +
          '<code>dashboard</code> directory so that <code>static/dataset.js</code> resolves.</p></div></li>';
      }
      return;
    }

    state.rows = rows;
    state.live = rows.filter((r) => r.reachable);
    state.global = window.GLOBAL_DATA || null;
    state.world = window.WORLD_DATA || null;

    renderBinds();
    renderFindings();
    if (state.global) {
      renderVantageTable('#overview-vantage', state.global.vantage_comparison);
      renderSectorTable('#overview-sectors', state.global.sectors);
      renderCountryRank();
      renderCharts();
    }
    renderCoverageTable();
    renderSchemaTable();
    renderWorldMap();
    renderRegistry();

    wireTabs();
    wireTheme();
    wireShortcuts();
    wireRegistry();

    if (state.world) {
      const first = (state.world.countries || []).find((c) => c.measured);
      if (first) selectCountry(first.code);
    }

    document.body.setAttribute('data-ready', 'true');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
