/* shared.js — common functions loaded on every page
   Loaded with <script src="../shared.js" defer></script> (or src="shared.js" on root)
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
    const price    = parseFloat(s.price_gbp) || 0;
    const priceStr = price <= 0  ? '—' :
                     price >= 10 ? '£' + Math.round(price) :
                     price >= 1  ? '£' + price.toFixed(2) :
                                   '£' + price.toFixed(3);
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
    for (const s of ['AI', 'Defence', 'Biotech', 'Tech', 'Crypto', 'Energy']) {
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

// ── Shared nav: left rail + bottom tabs ───────────────────────────────────────
const _RAIL_ITEMS = [
  { key: 'hub',     label: 'Stock Hub',   icon: '⊞',  path: 'index.html',         badge: null },
  { key: 'all',     label: 'All Sectors', icon: '🌐', path: 'All/index.html',      badge: 'Live' },
  { key: 'AI',      label: 'AI Infra',    icon: '🤖', path: 'AI/index.html',       badge: 'Live' },
  { key: 'Biotech', label: 'Biotech',     icon: '🧬', path: 'Biotech/index.html',  badge: 'Live' },
  { key: 'Defence', label: 'Defence',     icon: '🛡️', path: 'Defence/index.html',  badge: 'Live' },
  { key: 'Tech',    label: 'Technology',  icon: '💻', path: 'Tech/index.html',     badge: 'Live' },
  { key: 'Crypto',  label: 'Crypto',      icon: '₿',  path: 'Crypto/index.html',   badge: 'Live' },
  { key: 'Energy',  label: 'Energy',      icon: '⚡', path: 'Energy/index.html',   badge: 'Live' },
  { key: 'market',  label: 'Market',      icon: '💹', path: 'index.html#market-section', badge: 'Live' },
  { key: 'rss',     label: 'RSS Feed',    icon: '📰', path: 'rss.html',            badge: 'Live' },
];

const _SECTOR_PAGES = [
  { key: 'dashboard',  label: 'Dashboard', icon: '📊', file: 'index.html' },
  { key: 'metrics',    label: 'Metrics',   icon: '📋', file: 'metrics.html' },
  { key: 'news',       label: 'News',      icon: '📰', file: 'news.html' },
  { key: 'signals',    label: 'Signals',   icon: '🎯', file: 'signals.html' },
  { key: 'heatmap',    label: 'Heatmap',   icon: '🔥', file: 'heatmap.html' },
  { key: 'charts',     label: 'Charts',    icon: '📈', file: 'charts.html' },
  { key: 'calculator', label: 'What-If',   icon: '🧮', file: 'calculator.html' },
];

function buildNav() {
  // Detect context from URL path
  const parts = location.pathname.replace(/^\//, '').split('/').filter(Boolean);
  const SECTORS = ['AI', 'Biotech', 'Defence', 'Tech', 'Crypto', 'Energy'];
  const sector  = SECTORS.find(s => parts[0] === s) || null;
  const inAll   = parts[0] === 'All';
  const file    = parts[parts.length - 1] || 'index.html';
  const isHub   = !sector && !inAll && (parts.length === 0 || file === 'index.html');
  const isRSS   = !sector && !inAll && file === 'rss.html';
  const root    = (sector || inAll) ? '../' : '';  // prefix to reach repo root

  // Active rail key
  const activeKey = isHub ? 'hub' : isRSS ? 'rss' : inAll ? 'all' : sector;

  // Build left rail HTML (identical for all pages, only active pill differs)
  const railHTML = _RAIL_ITEMS.map(p => {
    const href    = root + p.path;
    const active  = p.key === activeKey;
    return `<a class="sector-pill${active ? ' active' : ''}" href="${href}">` +
           `<span class="sector-pill-icon">${p.icon}</span>` +
           `<span class="sector-pill-name">${p.label}</span>` +
           (p.badge ? `<span class="sector-pill-badge">${p.badge}</span>` : '') +
           `</a>`;
  }).join('');

  // Inject into all .left-rail elements (main rail + drawer)
  document.querySelectorAll('.left-rail').forEach(el => { el.innerHTML = railHTML; });

  // Build bottom tabs HTML
  const PAGE_MAP = { 'index.html': 'dashboard', 'metrics.html': 'metrics',
    'news.html': 'news', 'signals.html': 'signals', 'heatmap.html': 'heatmap',
    'charts.html': 'charts', 'calculator.html': 'calculator' };
  const currentPage = PAGE_MAP[file] || 'dashboard';

  let tabsHTML = '';
  if (isHub) {
    // Hub: 8 cross-sector tabs
    const HUB_TABS = [
      { label: 'Hub',     icon: '⊞', action: `window.location='index.html'`,                                               active: true },
      { label: 'Market',  icon: '💹', action: `document.getElementById('market-section').scrollIntoView({behavior:'smooth'})` },
      { label: 'All',     icon: '🌐', action: `window.location='All/index.html'` },
      { label: 'AI',      icon: '🤖', action: `window.location='AI/index.html'` },
      { label: 'Biotech', icon: '🧬', action: `window.location='Biotech/index.html'` },
      { label: 'Defence', icon: '🛡️', action: `window.location='Defence/index.html'` },
      { label: 'Tech',    icon: '💻', action: `window.location='Tech/index.html'` },
      { label: 'Crypto',  icon: '₿',  action: `window.location='Crypto/index.html'` },
    ];
    tabsHTML = HUB_TABS.map(t =>
      `<button class="tab-btn${t.active ? ' active' : ''}" onclick="${t.action}">` +
      `<span class="tab-icon">${t.icon}</span>${t.label}</button>`
    ).join('');
  } else if (sector || inAll) {
    // Sector / All Sectors: Hub + 7 within-sector page tabs
    const hubBtn = `<button class="tab-btn" onclick="window.location='${root}index.html'">` +
                   `<span class="tab-icon">⊞</span>Hub</button>`;
    const pageBtns = _SECTOR_PAGES.map(p =>
      `<button class="tab-btn${p.key === currentPage ? ' active' : ''}" onclick="window.location='${p.file}'">` +
      `<span class="tab-icon">${p.icon}</span>${p.label}</button>`
    ).join('');
    tabsHTML = hubBtn + pageBtns;
  }

  const tabsInner = document.querySelector('.bottom-tabs-inner');
  if (tabsInner && tabsHTML) tabsInner.innerHTML = tabsHTML;
}

// ── Initialise on DOMContentLoaded ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Set correct theme icon
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = document.documentElement.getAttribute('data-theme') === 'dark' ? '☀' : '☾';

  // Wrap header+nav in sticky shell (non-rail pages)
  buildStickyTop();

  // Inject shared left rail + bottom tabs
  buildNav();

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
          price_gbp: row.dataset.priceGbp || '0',
          change_1d: row.dataset['change-1d'] || '+0.00%',
        })));
      });
  }
});

