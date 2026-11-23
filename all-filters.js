/* all-filters.js — filters for the All pages (#88): every stock on the site, ~720 rows.
   Data: All/all-data.js (window.ALL_DATA), written by update_group_prices.py.
   Filters: market, sector, theme, "hide not on T212", search. They are kept in the URL
   (?market=sp500&sector=technology&theme=ai&t212=1&q=nvid), so a filtered view can be shared
   and an old theme page can send its visitors to All with its theme already chosen. */

const AF_MARKETS = [
  ['sp500', 'S&P 500'], ['nasdaq100', 'Nasdaq-100'], ['ftse100', 'FTSE 100'],
  ['eurostoxx50', 'Euro Stoxx 50'], ['dax', 'DAX'], ['cac40', 'CAC 40'], ['smi', 'SMI'], ['crypto', 'Crypto'],
];
const AF_SECTORS = [
  'Communication Services', 'Consumer Discretionary', 'Consumer Staples', 'Energy', 'Financials',
  'Health Care', 'Industrials', 'Materials', 'Real Estate', 'Technology', 'Utilities',
];
const AF_THEMES = [
  ['ai', 'AI'], ['biotech', 'Biotech'], ['crypto', 'Crypto'], ['defence', 'Defence'],
  ['energy', 'Energy'], ['megacap', 'Mega-Cap'], ['tech', 'Tech'],
];
const AF_THEME_LABEL = Object.fromEntries(AF_THEMES);
const AF_MARKET_LABEL = Object.fromEntries(AF_MARKETS);

const afSlug = s => String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

const AF = { market: '', sector: '', theme: '', t212: false, q: '' };

function afReadUrl() {
  const p = new URLSearchParams(location.search);
  AF.market = AF_MARKET_LABEL[p.get('market')] ? p.get('market') : '';
  AF.sector = AF_SECTORS.some(s => afSlug(s) === p.get('sector')) ? p.get('sector') : '';
  AF.theme = AF_THEME_LABEL[p.get('theme')] ? p.get('theme') : '';
  AF.t212 = p.get('t212') === '1';
  AF.q = (p.get('q') || '').slice(0, 60);
}

function afWriteUrl() {
  const p = new URLSearchParams();
  if (AF.market) p.set('market', AF.market);
  if (AF.sector) p.set('sector', AF.sector);
  if (AF.theme) p.set('theme', AF.theme);
  if (AF.t212) p.set('t212', '1');
  if (AF.q) p.set('q', AF.q);
  const qs = p.toString();
  history.replaceState(null, '', location.pathname + (qs ? '?' + qs : ''));
}

/* Does one stock pass the current filters? */
function afMatch(s) {
  if (AF.market && !(s.markets || []).includes(AF.market)) return false;
  if (AF.sector && afSlug(s.sector) !== AF.sector) return false;
  if (AF.theme && !(s.themes || []).includes(AF.theme)) return false;
  if (AF.t212 && s.t212 === 'no') return false;
  if (AF.q) {
    const q = AF.q.toLowerCase();
    if (!String(s.ticker).toLowerCase().includes(q) && !String(s.company_name || '').toLowerCase().includes(q)) return false;
  }
  return true;
}

/* Draw the filter controls into `el`; call onChange() whenever a filter changes. */
function afBuildBar(el, onChange) {
  const opt = (v, label, sel) => `<option value="${v}"${sel ? ' selected' : ''}>${label}</option>`;
  el.innerHTML =
    `<label class="af-field"><span>Market</span><select id="af-market">${opt('', 'All markets', !AF.market)}` +
      AF_MARKETS.map(([k, l]) => opt(k, l, AF.market === k)).join('') + `</select></label>` +
    `<label class="af-field"><span>Sector</span><select id="af-sector">${opt('', 'All sectors', !AF.sector)}` +
      AF_SECTORS.map(s => opt(afSlug(s), s, AF.sector === afSlug(s))).join('') + `</select></label>` +
    `<label class="af-field"><span>Theme</span><select id="af-theme">${opt('', 'All themes', !AF.theme)}` +
      AF_THEMES.map(([k, l]) => opt(k, l, AF.theme === k)).join('') + `</select></label>` +
    `<label class="af-check" title="Trading 212 offers most ordinary shares on major exchanges; this hides the ones it doesn't list">` +
      `<input type="checkbox" id="af-t212"${AF.t212 ? ' checked' : ''}> Hide stocks not on T212</label>` +
    `<button class="af-reset" id="af-reset" type="button">Clear filters</button>`;
  const changed = () => { afWriteUrl(); onChange(); };
  el.querySelector('#af-market').onchange = e => { AF.market = e.target.value; changed(); };
  el.querySelector('#af-sector').onchange = e => { AF.sector = e.target.value; changed(); };
  el.querySelector('#af-theme').onchange = e => { AF.theme = e.target.value; changed(); };
  el.querySelector('#af-t212').onchange = e => { AF.t212 = e.target.checked; changed(); };
  el.querySelector('#af-reset').onclick = () => {
    Object.assign(AF, { market: '', sector: '', theme: '', t212: false, q: '' });
    const search = document.getElementById('stock-search');
    if (search) search.value = '';
    afBuildBar(el, onChange);
    changed();
  };
}

/* Hook a search box to the filters (debounced: ~720 rows). */
function afHookSearch(input, onChange) {
  input.value = AF.q;
  let t = null;
  input.addEventListener('input', () => {
    clearTimeout(t);
    t = setTimeout(() => { AF.q = input.value.trim(); afWriteUrl(); onChange(); }, 120);
  });
}

afReadUrl();
