/* nav.js — navigation config + buildNav()
   Loaded synchronously (no defer) just before </body> on every page.
   Runs before first paint so the nav is correct on first render — no flash.
   Single source of truth: add a sector or rename a page here only. */

const _RAIL_ITEMS = [
  { key: 'hub',     label: 'Stock Hub',   icon: '⊞',  path: 'index.html',        badge: null },
  { key: 'rss',     label: 'News Feed',   icon: '📰', path: 'news.html',          badge: null },
  { key: 'all',     label: 'All Sectors', icon: '🌐', path: 'All/index.html',     badge: null },
  { key: 'AI',      label: 'AI',          icon: '🤖', path: 'AI/index.html',      badge: null },
  { key: 'Biotech', label: 'Biotech',     icon: '🧬', path: 'Biotech/index.html', badge: null },
  { key: 'Crypto',  label: 'Crypto',      icon: '₿',  path: 'Crypto/index.html',  badge: null },
  { key: 'Defence', label: 'Defence',     icon: '🛡️', path: 'Defence/index.html', badge: null },
  { key: 'Energy',  label: 'Energy',      icon: '⚡', path: 'Energy/index.html',  badge: null },
  { key: 'MegaCap', label: 'Mega-Cap',   icon: '🌍', path: 'MegaCap/index.html', badge: null },
  { key: 'Tech',    label: 'Technology',  icon: '💻', path: 'Tech/index.html',    badge: null },
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
  const parts = location.pathname.replace(/^\//, '').split('/').filter(Boolean);
  const SECTORS = ['AI', 'Biotech', 'Defence', 'Tech', 'Crypto', 'Energy', 'MegaCap'];
  const sector  = SECTORS.find(s => parts[0] === s) || null;
  const inAll   = parts[0] === 'All';

  const _KNOWN_PAGES = ['index', 'metrics', 'news', 'signals', 'heatmap', 'charts', 'calculator'];
  const _rawFile = parts[parts.length - 1] || '';
  const _extFile = _KNOWN_PAGES.includes(_rawFile) ? _rawFile + '.html' : _rawFile;
  const file = (!_rawFile || SECTORS.includes(_rawFile) || _rawFile === 'All') ? 'index.html' : _extFile;

  const isHub = !sector && !inAll && (parts.length === 0 || file === 'index.html');
  const isRSS = !sector && !inAll && file === 'news.html';
  const root  = (sector || inAll) ? '../' : '';

  const activeKey = isHub ? 'hub' : isRSS ? 'rss' : inAll ? 'all' : sector;

  const onSubPage = (sector || inAll) && file !== 'index.html';
  const railHTML = _RAIL_ITEMS.map(p => {
    const href = onSubPage && (SECTORS.includes(p.key) || p.key === 'all')
      ? root + (p.key === 'all' ? 'All' : p.key) + '/' + file
      : root + p.path;
    const active = p.key === activeKey;
    return `<a class="sector-pill${active ? ' active' : ''}" href="${href}">` +
           `<span class="sector-pill-icon">${p.icon}</span>` +
           `<span class="sector-pill-name">${p.label}</span>` +
           (p.badge ? `<span class="sector-pill-badge">${p.badge}</span>` : '') +
           `</a>`;
  }).join('');

  document.querySelectorAll('.left-rail').forEach(el => { el.innerHTML = railHTML; });

  if (sector || inAll) {
    const PAGE_MAP = { 'index.html': 'dashboard', 'metrics.html': 'metrics',
      'news.html': 'news', 'signals.html': 'signals', 'heatmap.html': 'heatmap',
      'charts.html': 'charts', 'calculator.html': 'calculator' };
    const currentPage = PAGE_MAP[file] || 'dashboard';
    const navPanelHTML = _SECTOR_PAGES.map(p =>
      `<a class="nav-link${p.key === currentPage ? ' active' : ''}" href="${p.file}">` +
      `<span class="nav-icon">${p.icon}</span><span class="nav-label">${p.label}</span></a>`
    ).join('');
    document.querySelectorAll('.nav-panel').forEach(el => { el.innerHTML = navPanelHTML; });
  }
}

buildNav();

/* ── Date formatter: YYYY-MM-DD HH:MM → DD/MM/YYYY HH:MM ───────────────────
   Defined here (synchronous) so it's available to all inline scripts and to
   deferred shared.js. nav.js also runs after each page's synchronous init(),
   so the post-process loop below catches timestamps already written to the DOM. */
function fmtDate(s) {
  if (!s || s === '—') return s || '—';
  var m = String(s).match(/^(\d{4})-(\d{2})-(\d{2})[\sT](\d{2}:\d{2})/);
  return m ? m[3] + '/' + m[2] + '/' + m[1] + ' ' + m[4] : s;
}

['heatmap-ts', 'data-bar-ts', 'signals-ts', 'feed-updated', 'hub-updated-ts'].forEach(function(id) {
  var el = document.getElementById(id);
  if (el && /^\d{4}-\d{2}-\d{2}/.test(el.textContent)) el.textContent = fmtDate(el.textContent);
});
