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
  // Skip if already present or page has its own refresh-banner (signals pages)
  if (document.querySelector('.data-bar') || document.querySelector('.refresh-banner')) return;

  let ts = null;

  // Signals pages — read from SIGNALS_DATA global
  if (window.SIGNALS_DATA && window.SIGNALS_DATA.generated) {
    ts = window.SIGNALS_DATA.generated;
  }
  // Sector pages — read from PRICES_DATA (prices-data.js)
  else if (window.PRICES_DATA && window.PRICES_DATA.updated) {
    ts = window.PRICES_DATA.updated;
  }
  // Hub page — find first available sector snapshot
  else {
    for (const s of ['AI', 'Defence', 'Biotech', 'Tech', 'Crypto', 'Energy']) {
      const pd = window['__pd_' + s];
      if (pd && pd.updated) { ts = pd.updated; break; }
    }
  }

  if (!ts) return;

  const isRail    = document.body.getAttribute('data-layout') === 'rail';
  const hdrInner  = document.querySelector('.header-inner');

  // Populate the static #data-bar-ts element (present in every sector page's HTML)
  const el = document.getElementById('data-bar-ts');
  if (el) el.textContent = ts;
}

// ── Sticky header+nav wrapper ─────────────────────────────────────────────────
function buildStickyTop() {
  if (document.body.dataset.layout === 'rail') return; // rail pages handle their own layout
  const header = document.querySelector('header');
  const nav    = document.querySelector('nav');
  if (!header || header.closest('.sticky-top')) return; // already wrapped or no header
  const wrapper = document.createElement('div');
  wrapper.className = 'sticky-top';
  header.parentNode.insertBefore(wrapper, header);
  wrapper.appendChild(header);
  if (nav) wrapper.appendChild(nav);
}

// ── Initialise on DOMContentLoaded ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Set correct theme icon
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = document.documentElement.getAttribute('data-theme') === 'dark' ? '☀' : '☾';

  // Wrap header+nav in sticky shell
  buildStickyTop();

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
