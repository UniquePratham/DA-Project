/* Hallmark · component: data engine + SVG chart renderers
 * genre: editorial / institutional · theme: custom "Survey Paper"
 * states: default · hover · focus · active · disabled · loading · error · empty
 *
 * Every figure on the page is computed from the released dataset at load time.
 * No number in this file is a literal placeholder for a statistic.
 */

(function () {
  'use strict';

  /* ------------------------------------------------------------- constants */

  const TIER_ORDER = [
    'central',
    'state_ut',
    'district',
    'academic_research',
    'judiciary',
    'public_sector',
    'urban_local_body',
  ];

  const TIER_LABEL = {
    central: 'Central ministries',
    state_ut: 'State departments',
    district: 'District administrations',
    academic_research: 'Higher education',
    judiciary: 'Judiciary',
    public_sector: 'Public sector & banks',
    urban_local_body: 'Urban local bodies',
  };

  const TIER_SHORT = {
    central: 'Central',
    state_ut: 'State',
    district: 'District',
    academic_research: 'Higher ed',
    judiciary: 'Judiciary',
    public_sector: 'PSU',
    urban_local_body: 'Municipal',
  };

  const ARCH_LABEL = {
    s3waas_drupal: 'S3WaaS (Drupal)',
    custom_dynamic_cms: 'Custom dynamic CMS',
    modern_spa: 'Modern SPA',
    legacy_asp_net: 'Legacy ASP.NET',
    wordpress: 'WordPress',
    indeterminate_unreachable: 'Not fingerprinted',
  };

  const PAGE_SIZE = 40;

  const SCHEMA = [
    ['domain_name', 'string', 'Metadata', 'Registered domain identifier, e.g. meity.gov.in'],
    ['entity_name', 'string', 'Metadata', 'Administrative owner of the domain'],
    ['government_level', 'categorical', 'Metadata', 'One of seven non-overlapping governance tiers'],
    ['state_or_ut', 'string', 'Metadata', 'State or Union Territory, or National for central bodies'],
    ['district', 'string', 'Metadata', 'Revenue district, where the tier has one'],
    ['final_url', 'string', 'Metadata', 'Canonical URL after redirect resolution'],
    ['http_status_code', 'integer', 'Reachability', 'Final HTTP status observed from domestic transit'],
    ['is_reachable', 'boolean', 'Reachability', 'True when the host answered 2xx or 3xx in-country'],
    ['measurement_reason', 'string', 'Diagnostic', 'Explicit reason, so an offline host is never scored zero'],
    ['sub_accessibility_score', 'float 0–100', 'Pillar 1', 'WCAG 2.1 AA structural checks: alt text, labels, lang, skip links'],
    ['sub_has_gigw_toolbar', 'boolean', 'Pillar 1', 'GIGW 3.0 widget: font resizer, contrast toggle, skip-to-content'],
    ['sub_response_latency_ms', 'float ms', 'Pillar 2', 'Time to first byte over domestic peering'],
    ['sub_lcp_est_sec', 'float s', 'Pillar 2', 'Estimated Largest Contentful Paint from TTFB and payload'],
    ['sub_https_enforced', 'boolean', 'Pillar 3', 'Whether canonical traffic is forced onto TLS'],
    ['sub_security_headers_score', 'float 0–100', 'Pillar 3', 'HSTS, CSP, X-Frame-Options and X-Content-Type-Options'],
    ['sub_is_multilingual', 'boolean', 'Pillar 4', 'Content available in an Eighth Schedule language'],
    ['sub_mobile_responsive', 'boolean', 'Pillar 4', 'Declares width=device-width, initial-scale=1.0'],
    ['sub_cms_architecture', 'categorical', 'Pillar 5', 'Platform fingerprinted from headers and markup'],
    ['sub_has_citizen_services', 'boolean', 'Pillar 5', 'Native search and grievance redressal integration'],
    ['observatory_maturity_score', 'float 0–100', 'Composite', 'Weighted synthesis of all five pillars'],
  ];

  /* ----------------------------------------------------------------- utils */

  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  const esc = (value) =>
    String(value == null ? '' : value).replace(/[&<>"']/g, (ch) => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
    }[ch]));

  const int = (n) => (n == null || Number.isNaN(n) ? '—' : Math.round(n).toLocaleString('en-IN'));
  const dec = (n, places) =>
    n == null || Number.isNaN(n) ? '—' : Number(n).toFixed(places == null ? 1 : places);
  const pct = (part, whole) => (whole ? (part / whole) * 100 : 0);

  const mean = (values) => {
    const clean = values.filter((v) => typeof v === 'number' && !Number.isNaN(v));
    return clean.length ? clean.reduce((a, b) => a + b, 0) / clean.length : null;
  };

  const median = (values) => {
    const clean = values.filter((v) => typeof v === 'number' && !Number.isNaN(v)).sort((a, b) => a - b);
    if (!clean.length) return null;
    const mid = Math.floor(clean.length / 2);
    return clean.length % 2 ? clean[mid] : (clean[mid - 1] + clean[mid]) / 2;
  };

  const countWhere = (rows, predicate) => rows.reduce((n, row) => n + (predicate(row) ? 1 : 0), 0);

  const debounceFrame = (fn) => {
    let queued = false;
    return function () {
      if (queued) return;
      queued = true;
      requestAnimationFrame(() => {
        queued = false;
        fn();
      });
    };
  };

  /* ----------------------------------------------------------------- state */

  const state = {
    rows: [],
    live: [],
    stats: null,
    tiers: [],
    states: [],
    selectedState: null,
    ledger: { page: 1, rows: [], sort: 'maturity' },
    charts: [],
    paletteIndex: 0,
    paletteResults: [],
  };

  /* --------------------------------------------------------------- compute */

  function computeStats(rows) {
    const live = rows.filter((r) => r.reachable);

    const tiers = TIER_ORDER.map((key) => {
      const all = rows.filter((r) => r.level === key);
      const up = all.filter((r) => r.reachable);
      return {
        key,
        label: TIER_LABEL[key],
        short: TIER_SHORT[key],
        total: all.length,
        live: up.length,
        reachRate: pct(up.length, all.length),
        acc: mean(up.map((r) => r.acc_score)),
        sec: mean(up.map((r) => r.sec_score)),
        lat: median(up.map((r) => r.latency_ms)),
        lcp: median(up.map((r) => r.lcp_sec)),
        maturity: mean(up.map((r) => r.maturity_score)),
        gigw: pct(countWhere(up, (r) => r.has_gigw_toolbar), up.length),
        multi: pct(countWhere(up, (r) => r.multilingual), up.length),
        mobile: pct(countWhere(up, (r) => r.mobile_responsive), up.length),
        services: pct(countWhere(up, (r) => r.has_citizen_services), up.length),
        https: pct(countWhere(up, (r) => r.has_https), up.length),
      };
    });

    const mapNames = new Set((window.INDIA_MAP ? window.INDIA_MAP.states : []).map((s) => s.name));

    const states = Array.from(new Set(rows.map((r) => r.state)))
      .filter((name) => mapNames.has(name))
      .map((name) => {
        const all = rows.filter((r) => r.state === name);
        const up = all.filter((r) => r.reachable);
        return {
          name,
          total: all.length,
          live: up.length,
          reachRate: pct(up.length, all.length),
          maturity: mean(up.map((r) => r.maturity_score)),
          acc: mean(up.map((r) => r.acc_score)),
          sec: mean(up.map((r) => r.sec_score)),
          lat: median(up.map((r) => r.latency_ms)),
          lcp: median(up.map((r) => r.lcp_sec)),
          gigw: pct(countWhere(up, (r) => r.has_gigw_toolbar), up.length),
          multi: pct(countWhere(up, (r) => r.multilingual), up.length),
          mobile: pct(countWhere(up, (r) => r.mobile_responsive), up.length),
          services: pct(countWhere(up, (r) => r.has_citizen_services), up.length),
        };
      })
      .filter((s) => s.live > 0)
      .sort((a, b) => b.maturity - a.maturity);

    states.forEach((s, i) => {
      s.rank = i + 1;
    });

    const archCounts = {};
    live.forEach((r) => {
      archCounts[r.arch] = (archCounts[r.arch] || 0) + 1;
    });
    const arch = Object.keys(archCounts)
      .map((key) => ({ key, label: ARCH_LABEL[key] || key, count: archCounts[key] }))
      .sort((a, b) => b.count - a.count);

    const lcpBuckets = [
      { label: '≤ 2.5 s', note: 'good', count: countWhere(live, (r) => r.lcp_sec != null && r.lcp_sec <= 2.5) },
      { label: '2.5–4 s', note: 'needs work', count: countWhere(live, (r) => r.lcp_sec > 2.5 && r.lcp_sec <= 4) },
      { label: '> 4 s', note: 'poor', count: countWhere(live, (r) => r.lcp_sec > 4) },
    ];

    const latBuckets = [
      { label: '≤ 500 ms', count: countWhere(live, (r) => r.latency_ms != null && r.latency_ms <= 500) },
      { label: '0.5–1 s', count: countWhere(live, (r) => r.latency_ms > 500 && r.latency_ms <= 1000) },
      { label: '1–2 s', count: countWhere(live, (r) => r.latency_ms > 1000 && r.latency_ms <= 2000) },
      { label: '> 2 s', count: countWhere(live, (r) => r.latency_ms > 2000) },
    ];

    const secBuckets = [
      { label: '0–25', count: countWhere(live, (r) => r.sec_score != null && r.sec_score < 25) },
      { label: '25–50', count: countWhere(live, (r) => r.sec_score >= 25 && r.sec_score < 50) },
      { label: '50–75', count: countWhere(live, (r) => r.sec_score >= 50 && r.sec_score < 75) },
      { label: '75–99', count: countWhere(live, (r) => r.sec_score >= 75 && r.sec_score < 100) },
      { label: '100', count: countWhere(live, (r) => r.sec_score === 100) },
    ];

    const offlineReasons = {};
    rows
      .filter((r) => !r.reachable)
      .forEach((r) => {
        const reason = (r.meas_reason || 'Unspecified').split('—')[0].trim();
        offlineReasons[reason] = (offlineReasons[reason] || 0) + 1;
      });
    const topOfflineReason = Object.keys(offlineReasons).sort(
      (a, b) => offlineReasons[b] - offlineReasons[a]
    )[0];

    return {
      total: rows.length,
      live: live.length,
      offline: rows.length - live.length,
      reachRate: pct(live.length, rows.length),
      acc: mean(live.map((r) => r.acc_score)),
      sec: mean(live.map((r) => r.sec_score)),
      maturity: mean(live.map((r) => r.maturity_score)),
      medianLat: median(live.map((r) => r.latency_ms)),
      medianLcp: median(live.map((r) => r.lcp_sec)),
      gigw: pct(countWhere(live, (r) => r.has_gigw_toolbar), live.length),
      multi: pct(countWhere(live, (r) => r.multilingual), live.length),
      mobile: pct(countWhere(live, (r) => r.mobile_responsive), live.length),
      services: pct(countWhere(live, (r) => r.has_citizen_services), live.length),
      https: pct(countWhere(live, (r) => r.has_https), live.length),
      perfectSec: countWhere(live, (r) => r.sec_score === 100),
      slowTtfb: countWhere(live, (r) => r.latency_ms > 2000),
      districtShare: pct(countWhere(rows, (r) => r.level === 'district'), rows.length),
      tiers,
      states,
      arch,
      lcpBuckets,
      latBuckets,
      secBuckets,
      topOfflineReason,
      offlineReasons,
    };
  }

  /* ------------------------------------------------------------ svg charts */

  function svgWrap(width, height, inner, label) {
    return (
      `<svg viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" ` +
      `preserveAspectRatio="xMidYMid meet" role="img" aria-label="${esc(label)}" ` +
      `style="width:100%;height:auto;overflow:visible">${inner}</svg>`
    );
  }

  function hbar(width, rows, opts) {
    const options = opts || {};
    const rowH = options.rowH || 30;
    const labelW = Math.min(options.labelW || 168, Math.max(84, width * 0.36));
    const valueW = 58;
    const barX = labelW + 10;
    const barW = Math.max(24, width - barX - valueW);
    const height = rows.length * rowH + 6;
    const max = options.max || Math.max.apply(null, rows.map((r) => r.value)) || 1;

    let out = '';

    if (options.ref != null) {
      const refX = barX + (options.ref / max) * barW;
      out +=
        `<line x1="${refX.toFixed(1)}" y1="0" x2="${refX.toFixed(1)}" y2="${height}" ` +
        `stroke="var(--oxide)" stroke-width="1" stroke-dasharray="3 3" opacity="0.75"/>`;
    }

    rows.forEach((row, i) => {
      const y = i * rowH + 3;
      const mid = y + rowH / 2 - 4;
      const w = Math.max(1.5, (row.value / max) * barW);
      const fill = options.color ? options.color(row, i) : 'var(--data-4)';

      out +=
        `<text class="cat-label${row.strong ? ' cat-label--strong' : ''}" x="0" y="${mid + 4}">${esc(row.label)}</text>`;
      out +=
        `<rect x="${barX}" y="${mid - 5}" width="${barW}" height="10" style="fill:var(--paper-3)"/>`;
      out +=
        `<rect class="bar" x="${barX}" y="${mid - 5}" width="${w.toFixed(1)}" height="10" style="fill:${fill}">` +
        `<title>${esc(row.label)}: ${esc(row.tip || row.valueText)}</title></rect>`;
      out +=
        `<text class="value-label" x="${width}" y="${mid + 4}" text-anchor="end">${esc(row.valueText)}</text>`;
    });

    return svgWrap(width, height, out, options.label || 'Bar chart');
  }

  function vbar(width, rows, opts) {
    const options = opts || {};
    const height = options.height || 168;
    const padTop = 20;
    const axisH = 24;
    const plotH = height - padTop - axisH;
    const colW = width / rows.length;
    const barW = Math.min(colW * 0.56, 54);
    const max = options.max || Math.max.apply(null, rows.map((r) => r.value)) || 1;

    let out = `<line class="axis-line" x1="0" y1="${padTop + plotH}" x2="${width}" y2="${padTop + plotH}"/>`;

    rows.forEach((row, i) => {
      const cx = colW * i + colW / 2;
      const h = Math.max(1.5, (row.value / max) * plotH);
      const y = padTop + plotH - h;
      const fill = options.color ? options.color(row, i) : 'var(--data-4)';

      out +=
        `<rect class="bar" x="${(cx - barW / 2).toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" ` +
        `height="${h.toFixed(1)}" style="fill:${fill}">` +
        `<title>${esc(row.label)}: ${esc(row.tip || row.valueText)}</title></rect>`;
      out +=
        `<text class="value-label" x="${cx.toFixed(1)}" y="${(y - 6).toFixed(1)}" text-anchor="middle">${esc(row.valueText)}</text>`;
      out +=
        `<text class="tick-label" x="${cx.toFixed(1)}" y="${padTop + plotH + 15}" text-anchor="middle">${esc(row.label)}</text>`;
      if (row.note) {
        out +=
          `<text class="tick-label" x="${cx.toFixed(1)}" y="${padTop + plotH + 26}" text-anchor="middle" opacity="0.7">${esc(row.note)}</text>`;
      }
    });

    return svgWrap(width, height, out, options.label || 'Column chart');
  }

  function stacked(width, segments, opts) {
    const options = opts || {};
    const barH = 30;
    const legendH = 46;
    const height = barH + legendH;
    const total = segments.reduce((n, s) => n + s.value, 0) || 1;

    let out = '';
    let x = 0;

    segments.forEach((seg) => {
      const w = (seg.value / total) * width;
      out +=
        `<rect class="bar" x="${x.toFixed(1)}" y="0" width="${Math.max(0, w - 1).toFixed(1)}" height="${barH}" ` +
        `style="fill:${seg.color}"><title>${esc(seg.label)}: ${esc(seg.tip || seg.valueText)}</title></rect>`;
      if (w > 46) {
        out +=
          `<text class="value-label value-label--inverse" x="${(x + w / 2).toFixed(1)}" y="${barH / 2 + 4}" ` +
          `text-anchor="middle">${esc(seg.shareText)}</text>`;
      }
      x += w;
    });

    // Legend entries are laid out on an even grid rather than at each segment's
    // left edge, so short segments do not collide with their neighbours.
    const colW = width / segments.length;
    segments.forEach((seg, i) => {
      const lx = i * colW;
      out +=
        `<rect x="${lx.toFixed(1)}" y="${barH + 14}" width="9" height="9" style="fill:${seg.color}"/>`;
      out +=
        `<text class="tick-label" x="${(lx + 14).toFixed(1)}" y="${barH + 22}">${esc(seg.label)}</text>`;
      out +=
        `<text class="tick-label" x="${(lx + 14).toFixed(1)}" y="${barH + 34}" opacity="0.75">${esc(seg.valueText)}</text>`;
    });

    return svgWrap(width, height, out, options.label || 'Proportion chart');
  }

  /* --------------------------------------------------------- chart mounting */

  function mountChart(id, draw) {
    const el = document.getElementById(id);
    if (!el) return;
    state.charts.push({ el, draw });
    const render = () => {
      const width = Math.floor(el.clientWidth);
      if (width < 40) return;
      el.innerHTML = draw(width);
    };
    el._render = render;
    render();
    if (typeof ResizeObserver !== 'undefined') {
      const observer = new ResizeObserver(debounceFrame(render));
      observer.observe(el);
    }
  }

  function renderChartsIn(root) {
    state.charts.forEach((chart) => {
      if (root.contains(chart.el) && chart.el._render) chart.el._render();
    });
  }

  /* ------------------------------------------------------------- rendering */

  function renderBinds() {
    const s = state.stats;
    const values = {
      total: int(s.total),
      reachable: int(s.live),
      unreachable: int(s.offline),
      reachablePct: `· ${dec(s.reachRate)}%`,
      acc: dec(s.acc),
      sec: dec(s.sec),
      maturity: dec(s.maturity),
      medianLat: `${int(s.medianLat)} ms`,
      medianLcp: `${dec(s.medianLcp, 2)} s`,
      districtShare: `${dec(s.districtShare)}%`,
      mapMin: dec(Math.min.apply(null, s.states.map((x) => x.maturity))),
      mapMax: dec(Math.max.apply(null, s.states.map((x) => x.maturity))),
    };

    $$('[data-bind]').forEach((el) => {
      const key = el.getAttribute('data-bind');
      if (key in values) el.textContent = values[key];
    });
  }

  function renderFindings() {
    const s = state.stats;
    const topTier = s.tiers.slice().sort((a, b) => b.acc - a.acc)[0];
    const worstTier = s.tiers.slice().sort((a, b) => a.sec - b.sec)[0];
    const perfectShare = pct(s.perfectSec, s.live);
    const slowShare = pct(s.slowTtfb, s.live);
    const offlineShare = pct(s.offline, s.total);

    const items = [
      {
        title: 'Security headers lag accessibility by a wide margin',
        body:
          `Mean accessibility reaches <span class="num">${dec(s.acc)}</span> of 100, but mean security ` +
          `hardening sits at <span class="num">${dec(s.sec)}</span>. Only ` +
          `<span class="num">${int(s.perfectSec)}</span> portals ` +
          `(<span class="num">${dec(perfectShare)}%</span>) set all four headers. ` +
          `The gap is not capability &mdash; it is that a missing header breaks nothing visible.`,
      },
      {
        title: 'Standardised distribution beats bespoke development',
        body:
          `${topTier.label} record the highest mean accessibility at ` +
          `<span class="num">${dec(topTier.acc)}</span>, ahead of central ministries at ` +
          `<span class="num">${dec(s.tiers[0].acc)}</span>. The cause is distribution, not budget: ` +
          `the S3WaaS Drupal template ships accessible markup by default, so every site built on it ` +
          `inherits the fix.`,
      },
      {
        title: 'Speed is bimodal, not uniformly slow',
        body:
          `Median time to first byte is <span class="num">${int(s.medianLat)} ms</span>, which is ` +
          `respectable. But <span class="num">${int(s.slowTtfb)}</span> portals ` +
          `(<span class="num">${dec(slowShare)}%</span>) exceed two seconds, and those are the ones ` +
          `citizens on mobile networks actually feel. The median hides the tail.`,
      },
      {
        title: 'Language coverage outruns the accessibility toolbar',
        body:
          `<span class="num">${dec(s.multi)}%</span> of reachable portals publish content in a scheduled ` +
          `language, yet only <span class="num">${dec(s.gigw)}%</span> ship the GIGW toolbar that lets a ` +
          `low-vision citizen enlarge the text. Translation was prioritised; the assistive controls were not.`,
      },
      {
        title: 'Offline is mostly deprecation, not outage',
        body:
          `<span class="num">${int(s.offline)}</span> domains ` +
          `(<span class="num">${dec(offlineShare)}%</span>) did not answer. The dominant reason is ` +
          `<em>${esc(s.topOfflineReason)}</em>, which describes a retired host rather than a failed one. ` +
          `The weakest tier on security is ${worstTier.label.toLowerCase()} at ` +
          `<span class="num">${dec(worstTier.sec)}</span>.`,
      },
    ];

    $('#findings').innerHTML = items
      .map(
        (item, i) =>
          `<li><span class="findings__idx">${String(i + 1).padStart(2, '0')}</span>` +
          `<div class="findings__body"><h3>${item.title}</h3><p>${item.body}</p></div></li>`
      )
      .join('');
  }

  function renderTierMatrix() {
    const body = $('#tier-matrix-body');
    const s = state.stats;

    body.innerHTML = s.tiers
      .map(
        (t) =>
          `<tr>` +
          `<td><span class="cat-label--strong">${esc(t.label)}</span></td>` +
          `<td class="ledger__num">${int(t.total)}</td>` +
          `<td class="ledger__num">${int(t.live)} <span class="ledger__num--muted">${dec(t.reachRate)}%</span></td>` +
          `<td class="ledger__num">${dec(t.acc)}</td>` +
          `<td class="ledger__num">${dec(t.sec)}</td>` +
          `<td class="ledger__num">${dec(t.gigw)}%</td>` +
          `<td class="ledger__num">${dec(t.multi)}%</td>` +
          `<td class="ledger__num">${dec(t.mobile)}%</td>` +
          `</tr>`
      )
      .join('') +
      `<tr>` +
      `<td><span class="cat-label--strong">National</span></td>` +
      `<td class="ledger__num">${int(s.total)}</td>` +
      `<td class="ledger__num">${int(s.live)} <span class="ledger__num--muted">${dec(s.reachRate)}%</span></td>` +
      `<td class="ledger__num">${dec(s.acc)}</td>` +
      `<td class="ledger__num">${dec(s.sec)}</td>` +
      `<td class="ledger__num">${dec(s.gigw)}%</td>` +
      `<td class="ledger__num">${dec(s.multi)}%</td>` +
      `<td class="ledger__num">${dec(s.mobile)}%</td>` +
      `</tr>`;
  }

  function renderPillars() {
    const s = state.stats;
    const topArch = s.arch[0];

    const pillars = [
      {
        no: 'Pillar 1',
        title: 'Accessibility and usability',
        std: 'WCAG 2.1 AA · GIGW 3.0',
        desc:
          'Structural barriers for disabled citizens: alternative text on images, programmatic labels on ' +
          'form controls, a declared document language, and a skip link past repeated navigation.',
        fields: [
          ['sub_accessibility_score', `${dec(s.acc)} / 100`],
          ['sub_has_gigw_toolbar', `${dec(s.gigw)}%`],
        ],
      },
      {
        no: 'Pillar 2',
        title: 'Performance and latency',
        std: 'Core Web Vitals',
        desc:
          'Time to first byte over domestic peering, and an estimated Largest Contentful Paint derived ' +
          'from that latency and the document payload. Both are measured in-country.',
        fields: [
          ['sub_response_latency_ms', `${int(s.medianLat)} ms`],
          ['sub_lcp_est_sec', `${dec(s.medianLcp, 2)} s`],
        ],
      },
      {
        no: 'Pillar 3',
        title: 'Security and cryptography',
        std: 'CERT-In hardening',
        desc:
          'Whether canonical traffic is forced onto TLS, and whether the response sets HSTS, a content ' +
          'security policy, frame options and MIME sniffing protection.',
        fields: [
          ['sub_https_enforced', `${dec(s.https)}%`],
          ['sub_security_headers_score', `${dec(s.sec)} / 100`],
        ],
      },
      {
        no: 'Pillar 4',
        title: 'Linguistic and mobile reach',
        std: 'Eighth Schedule · Digital India',
        desc:
          'Whether content exists in one of the 22 scheduled languages, and whether the document declares ' +
          'a mobile viewport rather than assuming a desktop screen.',
        fields: [
          ['sub_is_multilingual', `${dec(s.multi)}%`],
          ['sub_mobile_responsive', `${dec(s.mobile)}%`],
        ],
      },
      {
        no: 'Pillar 5',
        title: 'Architecture and services',
        std: 'Platform fingerprint',
        desc:
          'The content management platform behind the portal, and whether it exposes native search and a ' +
          'grievance route rather than only publishing static notices.',
        fields: [
          ['sub_cms_architecture', topArch ? `${dec(pct(topArch.count, s.live))}% ${topArch.label}` : '—'],
          ['sub_has_citizen_services', `${dec(s.services)}%`],
        ],
      },
    ];

    $('#pillars').innerHTML = pillars
      .map(
        (p) =>
          `<article class="pillar">` +
          `<div class="pillar__no">${esc(p.no)}</div>` +
          `<h3 class="pillar__title">${esc(p.title)}</h3>` +
          `<div class="pillar__std">${esc(p.std)}</div>` +
          `<p class="pillar__desc">${esc(p.desc)}</p>` +
          `<div class="pillar__fields">` +
          p.fields
            .map(
              (f) =>
                `<div class="pillar__field"><code>${esc(f[0])}</code><b>${esc(f[1])}</b></div>`
            )
            .join('') +
          `</div></article>`
      )
      .join('');
  }

  function renderSchema() {
    $('#schema-body').innerHTML = SCHEMA.map(
      (row) =>
        `<tr>` +
        `<td><code style="font-family:var(--font-mono);font-size:var(--fs-xs);color:var(--oxide)">${esc(row[0])}</code></td>` +
        `<td style="color:var(--ink-3);font-size:var(--fs-xs);white-space:nowrap">${esc(row[1])}</td>` +
        `<td style="color:var(--ink-2);font-size:var(--fs-xs);white-space:nowrap">${esc(row[2])}</td>` +
        `<td style="color:var(--ink-2);font-size:var(--fs-xs)">${esc(row[3])}</td>` +
        `</tr>`
    ).join('');
  }

  /* ------------------------------------------------------------------ map */

  function maturityColor(value, min, max) {
    if (value == null) return 'var(--paper-3)';
    const span = max - min || 1;
    const t = Math.max(0, Math.min(1, (value - min) / span));
    const step = Math.min(4, Math.floor(t * 5));
    return `var(--data-${step + 1})`;
  }

  function renderMap() {
    const svg = $('#india-map');
    const map = window.INDIA_MAP;
    if (!svg || !map) return;

    const byName = {};
    state.stats.states.forEach((s) => {
      byName[s.name] = s;
    });

    const values = state.stats.states.map((s) => s.maturity);
    const min = Math.min.apply(null, values);
    const max = Math.max.apply(null, values);

    svg.setAttribute('viewBox', `0 0 ${map.width} ${map.height}`);

    const paths = map.states
      .map((geo) => {
        const stat = byName[geo.name];
        if (!stat) {
          return (
            `<path class="map-state map-state--empty" d="${geo.d}" ` +
            `aria-label="${esc(geo.name)}: no registered portal"></path>`
          );
        }
        const fill = maturityColor(stat.maturity, min, max);
        return (
          `<path class="map-state" d="${geo.d}" tabindex="0" role="button" ` +
          `data-state="${esc(geo.name)}" style="fill:${fill}" ` +
          `aria-label="${esc(geo.name)}: maturity ${dec(stat.maturity)} of 100, ${int(stat.live)} reachable portals"></path>`
        );
      })
      .join('');

    svg.innerHTML = paths;

    const ramp = $('#map-legend-ramp');
    if (ramp) {
      ramp.innerHTML = [1, 2, 3, 4, 5]
        .map((n) => `<span class="legend__swatch" style="background:var(--data-${n})"></span>`)
        .join('');
    }

    svg.addEventListener('mouseover', (event) => {
      const path = event.target.closest('.map-state');
      if (!path || !path.dataset.state) return;
      const stat = byName[path.dataset.state];
      showTip(
        event,
        `<b>${esc(stat.name)}</b><br>Maturity ${dec(stat.maturity)} · ${int(stat.live)} of ${int(stat.total)} reachable`
      );
    });

    svg.addEventListener('mousemove', (event) => {
      if (event.target.closest('.map-state')) moveTip(event);
    });

    svg.addEventListener('mouseout', (event) => {
      if (event.target.closest('.map-state')) hideTip();
    });

    svg.addEventListener('click', (event) => {
      const path = event.target.closest('.map-state');
      if (path && path.dataset.state) selectState(path.dataset.state);
    });

    svg.addEventListener('keydown', (event) => {
      const path = event.target.closest('.map-state');
      if (!path || !path.dataset.state) return;
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        selectState(path.dataset.state);
      }
    });

    selectState(state.stats.states[0].name);
  }

  function selectState(name) {
    const stat = state.stats.states.find((s) => s.name === name);
    if (!stat) return;
    state.selectedState = name;

    $$('.map-state').forEach((path) => {
      path.setAttribute('aria-pressed', path.dataset.state === name ? 'true' : 'false');
    });

    $('#dossier-name').textContent = stat.name;
    $('#dossier-rank').innerHTML = `Rank <b>${stat.rank}</b> of ${state.stats.states.length}`;
    $('#dossier-portals').textContent = int(stat.total);
    $('#dossier-reach').innerHTML = `${int(stat.live)} <small>${dec(stat.reachRate)}%</small>`;
    $('#dossier-maturity').innerHTML = `${dec(stat.maturity)} <small>/ 100</small>`;
    $('#dossier-acc').innerHTML = `${dec(stat.acc)} <small>/ 100</small>`;
    $('#dossier-sec').innerHTML = `${dec(stat.sec)} <small>/ 100</small>`;
    $('#dossier-lat').innerHTML = `${int(stat.lat)} <small>ms</small>`;

    const meters = [
      ['GIGW accessibility toolbar', stat.gigw],
      ['Scheduled language content', stat.multi],
      ['Mobile viewport declared', stat.mobile],
      ['Citizen services present', stat.services],
    ];

    $('#dossier-meters').innerHTML = meters
      .map(
        (m) =>
          `<div class="meter">` +
          `<span class="meter__label">${esc(m[0])}</span>` +
          `<span class="meter__value">${dec(m[1])}%</span>` +
          `<div class="meter__track"><div class="meter__fill" style="width:${Math.max(0, Math.min(100, m[1])).toFixed(1)}%"></div></div>` +
          `</div>`
      )
      .join('');
  }

  function renderStateRank() {
    $('#state-rank-body').innerHTML = state.stats.states
      .map(
        (s) =>
          `<tr data-state="${esc(s.name)}" style="cursor:pointer">` +
          `<td class="ledger__num ledger__num--muted">${s.rank}</td>` +
          `<td><span class="ledger__name">${esc(s.name)}</span></td>` +
          `<td class="ledger__num">${int(s.total)}</td>` +
          `<td class="ledger__num">${dec(s.maturity)}</td>` +
          `<td class="ledger__num">${dec(s.acc)}</td>` +
          `<td class="ledger__num">${dec(s.sec)}</td>` +
          `<td class="ledger__num">${int(s.lat)} ms</td>` +
          `</tr>`
      )
      .join('');

    $('#state-rank-body').addEventListener('click', (event) => {
      const row = event.target.closest('tr[data-state]');
      if (row) selectState(row.dataset.state);
    });
  }

  /* --------------------------------------------------------------- ledger */

  function populateTierFilter() {
    const select = $('#ledger-tier');
    const counts = {};
    state.rows.forEach((r) => {
      counts[r.level] = (counts[r.level] || 0) + 1;
    });
    select.innerHTML =
      `<option value="all">All tiers (${int(state.rows.length)})</option>` +
      TIER_ORDER.map(
        (key) => `<option value="${key}">${esc(TIER_LABEL[key])} (${int(counts[key] || 0)})</option>`
      ).join('');
  }

  function applyLedgerFilters() {
    const term = $('#ledger-search').value.trim().toLowerCase();
    const tier = $('#ledger-tier').value;
    const status = $('#ledger-status').value;
    const sort = $('#ledger-sort').value;

    let rows = state.rows.filter((r) => {
      if (tier !== 'all' && r.level !== tier) return false;
      if (status === 'reachable' && !r.reachable) return false;
      if (status === 'unreachable' && r.reachable) return false;
      if (!term) return true;
      return (
        (r.domain || '').toLowerCase().includes(term) ||
        (r.entity || '').toLowerCase().includes(term) ||
        (r.district || '').toLowerCase().includes(term) ||
        (r.state || '').toLowerCase().includes(term) ||
        (r.arch || '').toLowerCase().includes(term)
      );
    });

    const numeric = (key, dir) => (a, b) => {
      const av = a[key];
      const bv = b[key];
      if (av == null && bv == null) return 0;
      if (av == null) return 1;
      if (bv == null) return -1;
      return dir * (av - bv);
    };

    // Ties break on domain so the ledger order is deterministic across runs and
    // reproducible against the CSV.
    const byDomain = (a, b) => (a.domain || '').localeCompare(b.domain || '');
    const tie = (primary) => (a, b) => primary(a, b) || byDomain(a, b);

    const sorters = {
      maturity: tie(numeric('maturity_score', -1)),
      'maturity-asc': tie(numeric('maturity_score', 1)),
      acc: tie(numeric('acc_score', -1)),
      sec: tie(numeric('sec_score', -1)),
      latency: tie(numeric('latency_ms', 1)),
      domain: byDomain,
    };

    rows.sort(sorters[sort] || sorters.maturity);

    state.ledger.rows = rows;
    state.ledger.page = 1;
    state.ledger.sort = sort;
    renderLedger();
  }

  function renderLedger() {
    const rows = state.ledger.rows;
    const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
    const page = Math.min(state.ledger.page, totalPages);
    state.ledger.page = page;

    const start = (page - 1) * PAGE_SIZE;
    const slice = rows.slice(start, start + PAGE_SIZE);

    $('#ledger-body').innerHTML = slice
      .map((r) => {
        const accClass =
          r.acc_score == null
            ? 'ledger__num ledger__num--muted'
            : r.acc_score >= 90
            ? 'ledger__num'
            : 'ledger__num';

        const checks = [
          r.multilingual ? '<span class="tag">Lang</span>' : '',
          r.mobile_responsive ? '<span class="tag">Mobile</span>' : '',
          r.has_citizen_services ? '<span class="tag">Services</span>' : '',
          r.has_gigw_toolbar ? '<span class="tag tag--accent">GIGW</span>' : '',
        ]
          .filter(Boolean)
          .join(' ');

        const status = r.reachable
          ? `<span class="status status--ok"><span class="status__dot"></span>${esc(r.status_code || 200)}</span>`
          : `<span class="status status--fail"><span class="status__dot"></span>Offline</span>`;

        return (
          `<tr>` +
          `<td><div class="ledger__domain">${esc(r.domain)}</div>` +
          `<div class="ledger__entity" title="${esc(r.entity)}">${esc(r.entity)}</div></td>` +
          `<td><span class="tag">${esc(TIER_SHORT[r.level] || r.level)}</span>` +
          `<div class="ledger__reason" title="${esc(r.state)}">${esc(r.state)}</div></td>` +
          `<td><span class="ledger__reason" style="max-width:14ch" title="${esc(ARCH_LABEL[r.arch] || r.arch)}">${esc(ARCH_LABEL[r.arch] || r.arch)}</span></td>` +
          `<td class="${accClass}">${r.acc_score == null ? '—' : dec(r.acc_score)}</td>` +
          `<td class="ledger__num">${r.sec_score == null ? '—' : dec(r.sec_score)}</td>` +
          `<td class="ledger__num">${r.latency_ms == null ? '—' : int(r.latency_ms)}</td>` +
          `<td class="ledger__num">${r.lcp_sec == null ? '—' : dec(r.lcp_sec, 2)}</td>` +
          `<td>${checks || '<span class="ledger__num--muted">—</span>'}</td>` +
          `<td>${status}<div class="ledger__reason" title="${esc(r.meas_reason)}">${esc(r.meas_reason)}</div></td>` +
          `</tr>`
        );
      })
      .join('');

    $('#ledger-count').innerHTML =
      rows.length === 0
        ? 'No domains match these filters'
        : `Showing <b>${int(start + 1)}</b>–<b>${int(Math.min(start + PAGE_SIZE, rows.length))}</b> of <b>${int(rows.length)}</b> domains`;

    $('#ledger-pos').textContent = `Page ${page} of ${totalPages}`;
    $('#ledger-prev').disabled = page <= 1;
    $('#ledger-next').disabled = page >= totalPages;
  }

  function exportCsv() {
    const rows = state.ledger.rows;
    if (!rows.length) return;

    const columns = [
      'domain',
      'entity',
      'level',
      'state',
      'district',
      'final_url',
      'status_code',
      'reachable',
      'meas_reason',
      'acc_score',
      'has_gigw_toolbar',
      'latency_ms',
      'lcp_sec',
      'has_https',
      'sec_score',
      'multilingual',
      'mobile_responsive',
      'arch',
      'has_citizen_services',
      'maturity_score',
    ];

    const cell = (value) => {
      const text = value == null ? '' : String(value);
      return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
    };

    const csv = [columns.join(',')]
      .concat(rows.map((row) => columns.map((key) => cell(row[key])).join(',')))
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `bharatgov_access_${rows.length}_domains.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /* -------------------------------------------------------------- tooltip */

  const tip = { el: null };

  function showTip(event, html) {
    if (!tip.el) tip.el = $('#tip');
    tip.el.innerHTML = html;
    tip.el.setAttribute('data-on', 'true');
    tip.el.setAttribute('aria-hidden', 'false');
    moveTip(event);
  }

  function moveTip(event) {
    if (!tip.el) return;
    const pad = 14;
    const rect = tip.el.getBoundingClientRect();
    let x = event.clientX + pad;
    let y = event.clientY + pad;
    if (x + rect.width > window.innerWidth - 8) x = event.clientX - rect.width - pad;
    if (y + rect.height > window.innerHeight - 8) y = event.clientY - rect.height - pad;
    tip.el.style.left = `${Math.max(8, x)}px`;
    tip.el.style.top = `${Math.max(8, y)}px`;
  }

  function hideTip() {
    if (!tip.el) return;
    tip.el.setAttribute('data-on', 'false');
    tip.el.setAttribute('aria-hidden', 'true');
  }

  /* ---------------------------------------------------------------- tabs */

  const VIEWS = ['overview', 'atlas', 'ledger', 'standard', 'method'];

  function activateView(name, focus) {
    if (VIEWS.indexOf(name) === -1) return;

    VIEWS.forEach((view) => {
      const panel = document.getElementById(`view-${view}`);
      const tab = document.getElementById(`tab-${view}`);
      const active = view === name;
      if (panel) panel.hidden = !active;
      if (tab) {
        tab.setAttribute('aria-selected', active ? 'true' : 'false');
        tab.tabIndex = active ? 0 : -1;
        if (active && focus) tab.focus();
      }
    });

    const panel = document.getElementById(`view-${name}`);
    if (panel) renderChartsIn(panel);

    if (name === 'atlas' && state.selectedState) selectState(state.selectedState);

    if (history.replaceState) {
      history.replaceState(null, '', `#${name}`);
    }
  }

  function wireTabs() {
    const tabs = $$('.rail__btn');

    tabs.forEach((tab) => {
      tab.addEventListener('click', () => activateView(tab.dataset.view));
      tab.addEventListener('keydown', (event) => {
        const index = tabs.indexOf(tab);
        let next = null;
        if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
        if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
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

  /* --------------------------------------------------------------- theme */

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);

    $$('[data-theme-set]').forEach((button) => {
      button.setAttribute('aria-pressed', button.dataset.themeSet === theme ? 'true' : 'false');
    });

    try {
      localStorage.setItem('bga-theme', theme);
    } catch (error) {
      /* storage may be unavailable on file:// — the theme still applies */
    }

    state.charts.forEach((chart) => chart.el._render && chart.el._render());
  }

  function currentTheme() {
    return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  }

  function wireTheme() {
    let stored = null;
    try {
      stored = localStorage.getItem('bga-theme');
    } catch (error) {
      stored = null;
    }

    const prefersDark =
      window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

    applyTheme(stored || (prefersDark ? 'dark' : 'light'));

    $$('[data-theme-set]').forEach((button) => {
      button.addEventListener('click', () => applyTheme(button.dataset.themeSet));
    });

    // Follow the OS only while the reader has not made an explicit choice.
    if (window.matchMedia) {
      const query = window.matchMedia('(prefers-color-scheme: dark)');
      const onChange = (event) => {
        let chosen = null;
        try {
          chosen = localStorage.getItem('bga-theme');
        } catch (error) {
          chosen = null;
        }
        if (!chosen) applyTheme(event.matches ? 'dark' : 'light');
      };
      if (query.addEventListener) query.addEventListener('change', onChange);
    }
  }

  /* ------------------------------------------------------------- palette */

  function openPalette() {
    const palette = $('#palette');
    palette.hidden = false;
    const input = $('#palette-input');
    input.value = '';
    input.focus();
    state.paletteIndex = 0;
    searchPalette('');
  }

  function closePalette() {
    $('#palette').hidden = true;
  }

  function searchPalette(term) {
    const query = term.trim().toLowerCase();
    let results;

    if (!query) {
      results = state.stats.states.slice(0, 8).map((s) => ({
        kind: 'state',
        label: s.name,
        meta: `${int(s.live)} reachable · maturity ${dec(s.maturity)}`,
        value: s.name,
      }));
    } else {
      results = state.rows
        .filter(
          (r) =>
            (r.domain || '').toLowerCase().includes(query) ||
            (r.entity || '').toLowerCase().includes(query) ||
            (r.district || '').toLowerCase().includes(query)
        )
        .slice(0, 12)
        .map((r) => ({
          kind: 'domain',
          label: r.domain,
          meta: `${r.entity} · ${r.state}`,
          value: r.domain,
        }));
    }

    state.paletteResults = results;
    state.paletteIndex = 0;

    const list = $('#palette-list');
    if (!results.length) {
      list.innerHTML = `<li class="palette__empty">No domain matches “${esc(term)}”</li>`;
      return;
    }

    list.innerHTML = results
      .map(
        (item, i) =>
          `<li class="palette__item" role="option" aria-selected="${i === 0}" data-index="${i}">` +
          `<span><b style="font-family:var(--font-mono);font-size:var(--fs-xs)">${esc(item.label)}</b>` +
          `<br><span style="font-size:var(--fs-xs);color:var(--ink-3)">${esc(item.meta)}</span></span>` +
          `<kbd>${item.kind === 'state' ? 'state' : 'domain'}</kbd></li>`
      )
      .join('');
  }

  function movePalette(delta) {
    const items = $$('.palette__item');
    if (!items.length) return;
    state.paletteIndex = (state.paletteIndex + delta + items.length) % items.length;
    items.forEach((item, i) => item.setAttribute('aria-selected', i === state.paletteIndex ? 'true' : 'false'));
    items[state.paletteIndex].scrollIntoView({ block: 'nearest' });
  }

  function commitPalette() {
    const item = state.paletteResults[state.paletteIndex];
    if (!item) return;
    closePalette();

    if (item.kind === 'state') {
      activateView('atlas');
      selectState(item.value);
      return;
    }

    activateView('ledger');
    $('#ledger-search').value = item.value;
    $('#ledger-status').value = 'all';
    $('#ledger-tier').value = 'all';
    applyLedgerFilters();
  }

  function wirePalette() {
    $('#palette-open').addEventListener('click', openPalette);

    $('#palette').addEventListener('click', (event) => {
      if (event.target.id === 'palette') closePalette();
    });

    $('#palette-input').addEventListener('input', (event) => searchPalette(event.target.value));

    $('#palette-input').addEventListener('keydown', (event) => {
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        movePalette(1);
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        movePalette(-1);
      } else if (event.key === 'Enter') {
        event.preventDefault();
        commitPalette();
      } else if (event.key === 'Escape') {
        closePalette();
      }
    });

    $('#palette-list').addEventListener('click', (event) => {
      const item = event.target.closest('.palette__item');
      if (!item) return;
      state.paletteIndex = Number(item.dataset.index);
      commitPalette();
    });
  }

  /* ------------------------------------------------------------ shortcuts */

  function wireShortcuts() {
    document.addEventListener('keydown', (event) => {
      const tag = (event.target.tagName || '').toLowerCase();
      const typing = tag === 'input' || tag === 'select' || tag === 'textarea';

      if (event.key === 'Escape') {
        if (!$('#palette').hidden) closePalette();
        hideTip();
        return;
      }

      if (typing) return;

      if (event.key === '/') {
        event.preventDefault();
        openPalette();
        return;
      }

      if (event.key === 't' || event.key === 'T') {
        applyTheme(currentTheme() === 'dark' ? 'light' : 'dark');
        return;
      }

      const index = Number(event.key);
      if (index >= 1 && index <= VIEWS.length) {
        activateView(VIEWS[index - 1]);
      }
    });
  }

  /* ----------------------------------------------------------------- boot */

  function wireLedger() {
    ['#ledger-search', '#ledger-tier', '#ledger-status', '#ledger-sort'].forEach((sel) => {
      const el = $(sel);
      el.addEventListener(sel === '#ledger-search' ? 'input' : 'change', applyLedgerFilters);
    });

    $('#ledger-prev').addEventListener('click', () => {
      if (state.ledger.page > 1) {
        state.ledger.page -= 1;
        renderLedger();
        $('#ledger-table').scrollIntoView({ block: 'start', behavior: 'smooth' });
      }
    });

    $('#ledger-next').addEventListener('click', () => {
      const totalPages = Math.ceil(state.ledger.rows.length / PAGE_SIZE);
      if (state.ledger.page < totalPages) {
        state.ledger.page += 1;
        renderLedger();
        $('#ledger-table').scrollIntoView({ block: 'start', behavior: 'smooth' });
      }
    });

    $('#ledger-export').addEventListener('click', exportCsv);
  }

  function wireDossier() {
    $('#dossier-open-ledger').addEventListener('click', () => {
      if (!state.selectedState) return;
      activateView('ledger');
      $('#ledger-search').value = state.selectedState;
      $('#ledger-status').value = 'all';
      $('#ledger-tier').value = 'all';
      applyLedgerFilters();
    });

    $('#dossier-copy').addEventListener('click', async () => {
      const stat = state.stats.states.find((s) => s.name === state.selectedState);
      if (!stat) return;
      const text =
        `${stat.name} — BharatGov Access\n` +
        `Portals: ${stat.total} (${stat.live} reachable, ${dec(stat.reachRate)}%)\n` +
        `Composite maturity: ${dec(stat.maturity)} / 100 (rank ${stat.rank} of ${state.stats.states.length})\n` +
        `Accessibility: ${dec(stat.acc)} / 100\n` +
        `Security headers: ${dec(stat.sec)} / 100\n` +
        `Median TTFB: ${int(stat.lat)} ms\n` +
        `GIGW toolbar: ${dec(stat.gigw)}% · Scheduled language: ${dec(stat.multi)}% · Mobile viewport: ${dec(stat.mobile)}%`;

      const button = $('#dossier-copy');
      const original = button.textContent;
      try {
        await navigator.clipboard.writeText(text);
        button.textContent = 'Copied';
      } catch (error) {
        button.textContent = 'Copy unavailable';
      }
      setTimeout(() => {
        button.textContent = original;
      }, 1600);
    });
  }

  function mountCharts() {
    const s = state.stats;

    mountChart('chart-tier', (width) =>
      hbar(
        width,
        s.tiers
          .slice()
          .sort((a, b) => b.maturity - a.maturity)
          .map((t) => ({
            label: t.label,
            value: t.maturity,
            valueText: dec(t.maturity),
            tip: `${dec(t.maturity)} of 100 · ${int(t.live)} reachable portals`,
            strong: t.maturity === Math.max.apply(null, s.tiers.map((x) => x.maturity)),
          })),
        {
          max: 100,
          ref: s.maturity,
          color: (row) => (row.value >= s.maturity ? 'var(--data-5)' : 'var(--data-3)'),
          label: `Mean composite maturity by governance tier. National mean ${dec(s.maturity)}.`,
        }
      )
    );

    mountChart('chart-lcp', (width) =>
      stacked(
        width,
        s.lcpBuckets.map((b, i) => ({
          label: b.label,
          value: b.count,
          valueText: `${int(b.count)} · ${dec(pct(b.count, s.live))}%`,
          tip: `${int(b.count)} portals · ${dec(pct(b.count, s.live))}%`,
          shareText: `${dec(pct(b.count, s.live), 0)}%`,
          color: ['var(--data-2)', 'var(--data-4)', 'var(--data-5)'][i],
        })),
        { label: 'Estimated Largest Contentful Paint distribution' }
      )
    );

    mountChart('chart-latency', (width) =>
      vbar(
        width,
        s.latBuckets.map((b) => ({
          label: b.label,
          value: b.count,
          valueText: int(b.count),
          tip: `${int(b.count)} portals · ${dec(pct(b.count, s.live))}%`,
        })),
        {
          color: (row, i) => ['var(--data-2)', 'var(--data-3)', 'var(--data-4)', 'var(--data-5)'][i],
          label: 'Time to first byte distribution over domestic transit',
        }
      )
    );

    mountChart('chart-sec', (width) =>
      vbar(
        width,
        s.secBuckets.map((b) => ({
          label: b.label,
          value: b.count,
          valueText: int(b.count),
          tip: `${int(b.count)} portals · ${dec(pct(b.count, s.live))}%`,
        })),
        {
          color: (row, i) => ['var(--data-5)', 'var(--data-4)', 'var(--data-3)', 'var(--data-2)', 'var(--data-1)'][i],
          label: 'Security header score distribution',
        }
      )
    );

    mountChart('chart-arch', (width) =>
      hbar(
        width,
        s.arch.map((a) => ({
          label: a.label,
          value: a.count,
          valueText: `${dec(pct(a.count, s.live))}%`,
          tip: `${int(a.count)} portals`,
        })),
        {
          labelW: 150,
          color: (row, i) => `var(--data-${Math.max(1, 5 - i)})`,
          label: 'Content management platform distribution',
        }
      )
    );
  }

  function boot() {
    const rows = window.RAW_DATASET;
    if (!Array.isArray(rows) || !rows.length) {
      document.getElementById('findings').innerHTML =
        '<li><span class="findings__idx">!</span><div class="findings__body">' +
        '<h3>Dataset unavailable</h3><p>The census bundle did not load. Open this page from the ' +
        '<code>dashboard</code> directory so that <code>static/dataset.js</code> resolves.</p></div></li>';
      return;
    }

    state.rows = rows;
    state.live = rows.filter((r) => r.reachable);
    state.stats = computeStats(rows);

    renderBinds();
    renderFindings();
    renderTierMatrix();
    renderPillars();
    renderSchema();
    renderMap();
    renderStateRank();
    populateTierFilter();
    applyLedgerFilters();
    mountCharts();

    wireTabs();
    wireTheme();
    wirePalette();
    wireShortcuts();
    wireLedger();
    wireDossier();

    document.body.setAttribute('data-ready', 'true');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
