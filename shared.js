/* shared.js — common functions loaded on every page (deferred, non-critical)
   nav.js handles buildNav() and runs synchronously before first paint.
   Heatmap pages set window._onThemeChange to trigger re-render after theme switch. */

// ── Theme toggle ──────────────────────────────────────────────────────────────
function toggleTheme() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  if (isDark) {
    document.documentElement.removeAttribute('data-theme');
    localStorage.setItem('theme', 'light');
    document.getElementById('theme-toggle').textContent = '☾';
  } else {
    document.documentElement.setAttribute('data-theme', 'dark');
    localStorage.setItem('theme', 'dark');
    document.getElementById('theme-toggle').textContent = '☀';
  }
  if (typeof window._onThemeChange === 'function') window._onThemeChange();
}

// ── Price formatting ─────────────────────────────────────────────────────────
// Variable precision to match the site's compact numeric style: whole
// numbers ≥ $10, 2dp ≥ $1, 3dp below (e.g. sub-$1 meme coins).
function fmtUsd(v) {
  const n = parseFloat(v);
  if (isNaN(n)) return '—';
  if (n >= 10) return String(Math.round(n));
  if (n >= 1)  return n.toFixed(2);
  return n.toFixed(3);
}

// ── Ticker tape ───────────────────────────────────────────────────────────────
function buildTape(stocks) {
  const track = document.getElementById('tape-track');
  if (!track || !stocks || !stocks.length) return;
  const items = stocks.map(s => {
    const change   = s.change_1d || '+0.00%';
    const val      = parseFloat(change);
    const isNeg    = change.startsWith('-');
    const isFlat   = val === 0;
    const cls      = isFlat ? 'flat' : isNeg ? 'neg' : 'pos';
    const arrow    = isFlat ? '—'   : isNeg ? '▼'   : '▲';
    const price    = parseFloat(s.price_usd) || 0;
    const priceStr = price <= 0 ? '—' : '$' + fmtUsd(price);
    return `<span class="tape-item"><span class="tape-t">${s.ticker}</span><span class="tape-p">${priceStr}</span><span class="tape-r ${cls}">${arrow} ${change}</span></span>`;
  }).join('');
  track.innerHTML = items + items;
  track.style.animationDuration = Math.max(30, stocks.length * 1.6) + 's';
  track.classList.add('running');
}

// ── Data bar — "Prices Last Updated" info block ────────────────────────────────
function buildDataBar() {
  if (document.querySelector('.data-bar') || document.querySelector('.refresh-banner')) return;
  let ts = null;
  if (window.SIGNALS_DATA && window.SIGNALS_DATA.generated) {
    ts = window.SIGNALS_DATA.generated;
  } else if (window.PRICES_DATA && window.PRICES_DATA.updated) {
    ts = window.PRICES_DATA.updated;
  } else {
    for (const s of ['AI', 'Defence', 'Biotech', 'Tech', 'Crypto', 'Energy', 'MegaCap']) {
      const pd = window['__pd_' + s];
      if (pd && pd.updated) { ts = pd.updated; break; }
    }
  }
  if (!ts) return;
  const el = document.getElementById('data-bar-ts');
  if (el) el.textContent = ts;
}

// ── Sticky header+nav wrapper ─────────────────────────────────────────────────
function buildStickyTop() {
  if (document.body.dataset.layout === 'rail') return;
  const header = document.querySelector('header');
  const nav    = document.querySelector('nav');
  if (!header || header.closest('.sticky-top')) return;
  const wrapper = document.createElement('div');
  wrapper.className = 'sticky-top';
  header.parentNode.insertBefore(wrapper, header);
  wrapper.appendChild(header);
  if (nav) wrapper.appendChild(nav);
}

// ── Dashboard content header ──────────────────────────────────────────────
function buildDashboardHeader() {
  const parts = location.pathname.replace(/^\//, '').split('/').filter(Boolean);
  const SECTORS = ['AI', 'Biotech', 'Defence', 'Tech', 'Crypto', 'Energy', 'MegaCap'];
  const sector = SECTORS.find(s => parts[0] === s) || null;
  const inAll  = parts[0] === 'All';
  const rawFile = parts[parts.length - 1] || '';
  // Treat sector-name-as-last-segment (trailing-slash URLs) as index.html
  const SECTORS2 = ['AI', 'Biotech', 'Defence', 'Tech', 'Crypto', 'Energy', 'MegaCap'];
  // Normalise extensionless "clean" URLs (Cloudflare Pages): /AI/index → 'index.html'
  const _KNOWN_PAGES2 = ['index', 'metrics', 'news', 'signals', 'heatmap', 'charts', 'calculator'];
  const _extRawFile = _KNOWN_PAGES2.includes(rawFile) ? rawFile + '.html' : rawFile;
  const file = (rawFile === '' || SECTORS2.includes(rawFile) || rawFile === 'All') ? 'index.html' : _extRawFile;
  if (file !== 'index.html' || (!sector && !inAll)) return;

  const railItem = _RAIL_ITEMS.find(r => r.key === (sector || 'all'));
  const name     = railItem ? railItem.label : (sector || 'All');
  const words    = name.split(' ');
  const titleHTML = words.length > 1
    ? words[0] + ' <span>' + words.slice(1).join(' ') + '</span>'
    : '<span>' + name + '</span>';

  const pd      = window.PRICES_DATA || window['__pd_' + sector] || {};
  const count   = (pd.stocks || []).length || null;
  const updated = pd.updated || null;

  const headerLeft = document.querySelector('.header-left');
  if (headerLeft && headerLeft.children.length > 0) {
    // Content already hardcoded — just refresh the dynamic spans
    const sc = document.getElementById('sector-count');
    if (sc && count) sc.textContent = count;
    const ts = document.getElementById('data-bar-ts');
    if (ts && updated) ts.textContent = updated;
  } else if (headerLeft) {
    headerLeft.innerHTML =
      '<div class="header-label">// Market Intelligence</div>' +
      '<h1>' + titleHTML + '</h1>' +
      '<div class="header-sub">' + (count || '—') + ' stocks · Last updated ' + (updated || '—') + '</div>';
  }

  const headerBlocks = document.querySelector('.header-blocks');
  if (headerBlocks) headerBlocks.remove();
}

// ── Initialise on DOMContentLoaded ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Set correct theme icon
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = document.documentElement.getAttribute('data-theme') === 'dark' ? '☀' : '☾';

  // Wrap header+nav in sticky shell (non-rail pages)
  buildStickyTop();

  // Inject dashboard content header (sector/All dashboard pages only)
  buildDashboardHeader();

  // Inject data bar below nav
  buildDataBar();

  // Populate ticker tape
  if (window.PRICES_DATA) {
    buildTape(window.PRICES_DATA.stocks);
  } else {
    fetch('prices.json')
      .then(r => r.json())
      .then(data => buildTape(data.stocks))
      .catch(() => {
        const rows = Array.from(document.querySelectorAll('tbody tr[data-ticker]'));
        if (rows.length) buildTape(rows.map(row => ({
          ticker:    row.dataset.ticker,
          price_usd: row.dataset.priceUsd || '0',
          change_1d: row.dataset['change-1d'] || '+0.00%',
        })));
      });
  }
});

