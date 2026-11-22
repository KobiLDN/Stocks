/* nav.js — navigation config + buildNav()
   Loaded synchronously (no defer) just before </body> on every page.
   Runs before first paint so the nav is correct on first render — no flash.
   Single source of truth: add a group, sector or page here only.

   Rail sections (#88): Markets (index groups + Crypto), Sectors (the 11 standard sectors),
   Themes (the owner's hand-picked groups). Market and sector pages live two folders deep
   (markets/<id>/, sectors/<id>/); themes and All one folder deep. */

const _RAIL_TOP = [
  { key: 'hub',   label: 'Stock Hub',    icon: '⊞',  path: 'index.html' },
  { key: 'rss',   label: 'News Feed',    icon: '📰', path: 'news.html' },
  { key: 'track', label: 'Track Record', icon: '🏁', path: 'track-record.html' },
  { key: 'all',   label: 'All Sectors',  icon: '🌐', path: 'All/index.html' },
];
const _RAIL_SECTIONS = [
  { title: 'Markets', items: [
    { key: 'sp500',     label: 'S&P 500',    icon: '🇺🇸', group: 'markets/sp500' },
    { key: 'nasdaq100', label: 'Nasdaq-100', icon: '📟', group: 'markets/nasdaq100' },
    { key: 'ftse100',   label: 'FTSE 100',   icon: '🇬🇧', group: 'markets/ftse100' },
    { key: 'Crypto',    label: 'Crypto',     icon: '₿',  theme: 'Crypto' },
  ]},
  { title: 'Sectors', items: [
    { key: 'technology',             label: 'Technology',  icon: '💻', group: 'sectors/technology' },
    { key: 'health-care',            label: 'Health Care', icon: '⚕️', group: 'sectors/health-care' },
    { key: 'financials',             label: 'Financials',  icon: '🏦', group: 'sectors/financials' },
    { key: 'consumer-discretionary', label: 'Cons. Disc.', icon: '🛍️', group: 'sectors/consumer-discretionary' },
    { key: 'communication-services', label: 'Comms',       icon: '📡', group: 'sectors/communication-services' },
    { key: 'industrials',            label: 'Industrials', icon: '🏭', group: 'sectors/industrials' },
    { key: 'consumer-staples',       label: 'Staples',     icon: '🛒', group: 'sectors/consumer-staples' },
    { key: 'energy',                 label: 'Energy',      icon: '🛢️', group: 'sectors/energy' },
    { key: 'utilities',              label: 'Utilities',   icon: '💡', group: 'sectors/utilities' },
    { key: 'real-estate',            label: 'Real Estate', icon: '🏢', group: 'sectors/real-estate' },
    { key: 'materials',              label: 'Materials',   icon: '⛏️', group: 'sectors/materials' },
  ]},
  { title: 'Themes', items: [
    { key: 'AI',      label: 'AI',       icon: '🤖', theme: 'AI' },
    { key: 'Biotech', label: 'Biotech',  icon: '🧬', theme: 'Biotech' },
    { key: 'Defence', label: 'Defence',  icon: '🛡️', theme: 'Defence' },
    { key: 'Energy',  label: 'Energy',   icon: '⚡', theme: 'Energy' },
    { key: 'MegaCap', label: 'Mega-Cap', icon: '🌍', theme: 'MegaCap' },
    { key: 'Tech',    label: 'Tech',     icon: '🖥️', theme: 'Tech' },
  ]},
];
const _RAIL_BOTTOM = [
  { key: 'glossary', label: 'Glossary', icon: '📖', path: 'glossary.html' },
];
// Flat list (shared.js looks up a page's label here)
const _RAIL_ITEMS = [..._RAIL_TOP, ..._RAIL_SECTIONS.flatMap(s => s.items), ..._RAIL_BOTTOM]
  .map(p => ({ badge: null, ...p, path: p.path || (p.group ? p.group + '/index.html' : p.theme + '/index.html') }));

const _SECTOR_PAGES = [
  { key: 'dashboard',  label: 'Dashboard', icon: '📊', file: 'index.html' },
  { key: 'metrics',    label: 'Metrics',   icon: '📋', file: 'metrics.html' },
  { key: 'news',       label: 'News',      icon: '📰', file: 'news.html' },
  { key: 'signals',    label: 'Signals',   icon: '🎯', file: 'signals.html' },
  { key: 'heatmap',    label: 'Heatmap',   icon: '🔥', file: 'heatmap.html' },
  { key: 'charts',     label: 'Charts',    icon: '📈', file: 'charts.html' },
  { key: 'calculator', label: 'What-If',   icon: '🧮', file: 'calculator.html' },
];
// Market and sector groups have no Signals page yet (their signal runs come with #88 step 8)
const _GROUP_NO_PAGES = ['signals.html'];
const _THEMES = ['AI', 'Biotech', 'Defence', 'Tech', 'Crypto', 'Energy', 'MegaCap'];
const _KNOWN_PAGES = ['index', 'metrics', 'news', 'signals', 'heatmap', 'charts', 'calculator'];

/* Where am I? { theme, group, inAll, file, root } — handles Cloudflare's clean URLs
   (/AI/, /AI/metrics, /markets/sp500/heatmap). */
function _navWhere() {
  const parts = location.pathname.replace(/^\//, '').split('/').filter(Boolean);
  const theme = _THEMES.find(s => parts[0] === s) || null;
  const inAll = parts[0] === 'All';
  const group = (parts[0] === 'markets' || parts[0] === 'sectors') && parts[1] ? parts[0] + '/' + parts[1] : null;
  const raw = parts[parts.length - 1] || '';
  const ext = _KNOWN_PAGES.includes(raw) ? raw + '.html' : raw;
  const atFolder = !raw || _THEMES.includes(raw) || raw === 'All' || (group && parts.length === 2);
  const file = atFolder ? 'index.html' : ext;
  const root = group ? '../../' : (theme || inAll) ? '../' : '';
  return { theme, group, inAll, file, root };
}

function buildNav() {
  const { theme, group, inAll, file, root } = _navWhere();
  const inSection = theme || inAll || group;
  const isHub = !inSection && file === 'index.html';
  const isRSS = !inSection && file === 'news.html';
  const isTrack = !inSection && (file === 'track-record.html' || file === 'track-record');
  const isGlossary = !inSection && (file === 'glossary.html' || file === 'glossary');
  const groupItem = group && _RAIL_ITEMS.find(p => p.group === group);
  const activeKey = isHub ? 'hub' : isRSS ? 'rss' : isTrack ? 'track' : isGlossary ? 'glossary'
    : inAll ? 'all' : groupItem ? groupItem.key : theme;
  const onSubPage = inSection && file !== 'index.html';

  // On a sub-page, switching group keeps the page type (metrics -> metrics) where the target has it
  const hrefFor = p => {
    if (onSubPage && p.group) return root + p.group + '/' + (_GROUP_NO_PAGES.includes(file) ? 'index.html' : file);
    if (onSubPage && (p.theme || p.key === 'all')) return root + (p.key === 'all' ? 'All' : p.theme) + '/' + file;
    return root + p.path;
  };
  const pill = p => {
    const active = p.key === activeKey;
    return `<a class="sector-pill${active ? ' active' : ''}" href="${hrefFor(p)}">` +
           `<span class="sector-pill-icon">${p.icon}</span>` +
           `<span class="sector-pill-name">${p.label}</span>` +
           (p.badge ? `<span class="sector-pill-badge">${p.badge}</span>` : '') +
           `</a>`;
  };
  const byKey = k => _RAIL_ITEMS.find(p => p.key === k);
  const railHTML =
    _RAIL_TOP.map(p => pill(byKey(p.key))).join('') +
    _RAIL_SECTIONS.map(sec => `<div class="rail-section">${sec.title}</div>` +
      sec.items.map(p => pill(byKey(p.key))).join('')).join('') +
    _RAIL_BOTTOM.map(p => pill(byKey(p.key))).join('');

  document.querySelectorAll('.left-rail').forEach(el => { el.innerHTML = railHTML; });

  if (inSection) {
    const PAGE_MAP = { 'index.html': 'dashboard', 'metrics.html': 'metrics',
      'news.html': 'news', 'signals.html': 'signals', 'heatmap.html': 'heatmap',
      'charts.html': 'charts', 'calculator.html': 'calculator' };
    const currentPage = PAGE_MAP[file] || 'dashboard';
    const pages = group ? _SECTOR_PAGES.filter(p => !_GROUP_NO_PAGES.includes(p.file)) : _SECTOR_PAGES;
    const navPanelHTML = pages.map(p =>
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
