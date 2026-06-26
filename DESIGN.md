# Stocks — Design System

**Reference page:** Stock Hub (`/index.html`)  
All pages must conform to these rules. When in doubt, match the hub exactly.

**Site URLs:**
- Dev: [dev.stocks-4qw.pages.dev](https://dev.stocks-4qw.pages.dev)
- Live: [stocks-4qw.pages.dev](https://stocks-4qw.pages.dev)

> When sharing these URLs in chat, always make them clickable markdown links.

---

## Spacing Reference

```
┌─────────────────────────────────────────────────────────┐
│  TICKER TAPE  h=36px  │ item pad: 0 20px │ gap: 7px     │
├─────────────────────────────────────────────────────────┤
│  HEADER ROW 1   brand + toggle   pad: 12px 20px         │
├─────────────────────────────────────────────────────────┤
│  HEADER ROW 2   nav tabs         pad: 0 16px            │
├─────────────────────────────────────────────────────────┤
│  HEADER ROW 3+  page controls    pad: 6–8px 16px        │
│  (filters / toolbar / chart-controls — page-specific)   │
├────────┬────────────────────────────────────────────────┤
│  RAIL  │  CONTENT   pad: 20px 24px  (overflow-y: auto)  │
│ w=92px │                                                 │
│pad:    │                                                 │
│8px 6px │                                                 │
│gap:4px │                                                 │
└────────┴────────────────────────────────────────────────┘
```

| Zone | Property | Value |
|---|---|---|
| Ticker tape | height | `36px` |
| Ticker tape | item padding | `0 20px` |
| Ticker tape | font size | `11px` IBM Plex Mono |
| Body | padding-top (clears tape) | `36px` |
| Header row 1 | padding | `12px 20px` |
| Header row 2 (nav) | padding | `0 16px` |
| Header row 3+ (controls) | padding | `6–8px 16px` |
| Nav tab | padding | `10px 16px` |
| Nav tab active | style | `border-bottom: 2px solid var(--accent)` |
| Left rail | width | `92px` |
| Left rail | padding | `8px 6px` |
| Left rail | gap between pills | `4px` |
| Sector pill | padding | `8px 6px` |
| Content area | padding | `20px 24px` |
| Theme toggle | size | `44×44px` |

---

## Layout: Layer Stack

```
┌──────────────────────────────────────────┐
│  TICKER TAPE   position: fixed  h=36px   │  z-index: 200
├──────────────────────────────────────────┤
│  HEADER ROW 1  brand + toggle  sticky    │
│  HEADER ROW 2  nav tabs                  │
│  HEADER ROW 3+ page controls             │
├─────────┬────────────────────────────────┤
│         │                                │
│  LEFT   │  CONTENT  overflow-y: auto     │
│  RAIL   │                                │
│  w=92px │                                │
└─────────┴────────────────────────────────┘
```

- `html:has(body[data-layout="rail"]) { height: 100%; }` — required for scroll to work
- `body[data-layout="rail"] { height: 100%; overflow: hidden; display: flex; flex-direction: column; }`
- `body { padding-top: 36px; }` — clears the fixed ticker tape
- The entire `<header>` is sticky — contains all rows above the content
- Only `.page-main` scrolls internally

---

## Colour Tokens

| Token | Light | Dark |
|---|---|---|
| `--bg` | `#f8fafc` | `#000000` |
| `--surface` | `#ffffff` | `#0e1419` |
| `--surface2` | `#f1f5f9` | `#141b22` |
| `--border` | `#cbd5e1` | `#1e2d3d` |
| `--accent` | `#0284c7` | `#00d4ff` |
| `--accent2` | `#ea580c` | `#ff6b35` |
| `--green` | `#16a34a` | `#00e676` |
| `--gold` | `#b45309` | `#ffd700` |
| `--text` | `#0f172a` | `#e0eaf5` |
| `--dim` | `#1e293b` | `#6b8299` |

Theme toggled via `html[data-theme="dark"]`. Persisted in `localStorage('theme')`.

---

## Typography

| Use | Family | Size | Weight | Other |
|---|---|---|---|---|
| Body copy | IBM Plex Sans | 13–14px | 400 | — |
| Page title `h1` | IBM Plex Sans | 26px | 700 | `letter-spacing: -0.01em` |
| Labels / mono data | IBM Plex Mono | 9–13px | 400/700 | `letter-spacing: 1–3px; text-transform: uppercase` |
| Header label | IBM Plex Mono | 11px | 400 | `letter-spacing: 0.15em; uppercase; color: var(--accent)` |
| Header sub | IBM Plex Mono | 11px | 400 | `color: var(--dim)` |

---

## 1 · Ticker Tape

```css
#ticker-tape {
  position: fixed; top: 0; left: 0; right: 0;
  height: 36px; z-index: 200;
  background: var(--bg); border-bottom: 1px solid var(--accent);
  overflow: hidden;
}
```

- Always the **topmost element** in `<body>`
- Populated by `buildTape()` from `shared.js`

---

## 2 · Header

The `<header>` contains **all sticky rows** for a page. It is a flex column:

```css
body[data-layout="rail"] header {
  padding: 0; display: flex; flex-direction: column; flex-shrink: 0;
  border-bottom: 1px solid var(--accent); background: var(--bg);
}
```

Every row after the first uses `border-top: 1px solid var(--border)` to separate.

### Row 1 — Brand + Toggle (every page)

```css
body[data-layout="rail"] .header-inner {
  display: flex; align-items: center; padding: 12px 20px; gap: 20px; max-width: none; margin: 0;
}
body[data-layout="rail"] .header-left { margin-right: auto; }
```

```html
<div class="header-inner">
  <div class="header-left">
    <div class="header-label">// Market Intelligence</div>
    <h1>Page <span>Title</span></h1>
    <div class="header-sub"><span id="stock-count">—</span> stocks · v1</div>
  </div>
  <button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()">☾</button>
</div>
```

#### Timestamp in header-sub (every rail page)

The "Last updated" timestamp lives **inline in `.header-sub`** as a `<span id="data-bar-ts">—</span>`, not in a separate top-right block. `buildDataBar()` in `shared.js` fills it on DOMContentLoaded — it reads `window.SIGNALS_DATA.generated`, `window.PRICES_DATA.updated`, or `window['__pd_*'].updated` (first non-null wins). All/ pages that load data asynchronously must fill it manually in their `.then()` callback.

**Signals pages** use `<span id="signals-ts">—</span>` in the subtitle instead, wired to `SIGNALS_DATA.updated` in page-specific JS.

**Hub** keeps its own Universe + Prices Last Updated blocks inside `.header-blocks` (managed by `index.html` inline JS — not shared.js).

### Row 2 — Nav Tabs (every page)

```css
body[data-layout="rail"] header nav {
  display: flex; align-items: center; gap: 2px; padding: 0 16px;
  border-top: 1px solid var(--border); background: var(--bg); overflow-x: auto;
}
.nav-link { font-family: 'IBM Plex Mono'; font-size: 11px; letter-spacing: 1.5px;
  text-transform: uppercase; padding: 10px 16px; color: var(--dim);
  border-bottom: 2px solid transparent; text-decoration: none; white-space: nowrap; }
.nav-link.active { color: var(--accent); border-bottom-color: var(--accent); }
```

### Row 3+ — Page Controls (page-specific)

Each control row shares this pattern:
```css
border-top: 1px solid var(--border);
padding: 6–8px 16px;
display: flex; align-items: center; gap: …;
```

| Page | Row 3 class | Contents |
|---|---|---|
| Dashboard | `.filter-bar` | Sector filter buttons (All · AI Infra · Biotech · Defence · Tech · Crypto · Energy) |
| Metrics | `.filter-bar` | Same sector filters |
| News | `.news-controls` | Sector group · separator · Sort group · separator · Period group + count |
| Signals | `.filter-bar` | Sector filters |
| Heatmap | `.toolbar` | Colour By · timeframe buttons · Prices timestamp · gradient legend |
| Charts | `.chart-controls` | Toolbar inner with category row + period/view controls |
| Calculator | `.filter-bar` | Sector filters |
| Calculator | `.search-count-bar` | Search input + visible/total count — sits as Row 4 inside `<header>` |

**Calculator search row** (Row 4 on calculator pages only):
```html
<div class="search-count-bar">
  <input id="stock-search" type="text" placeholder="Search ticker or company..." oninput="applyFilters()"/>
  <span class="row-count">Showing <span id="visible-count">—</span> of <span id="total-count">—</span> stocks</span>
</div>
```
```css
.search-count-bar { display: flex; align-items: center; gap: 16px;
  padding: 6px 16px; border-top: 1px solid var(--border); }
```

**Filter buttons** (shared, in `shared.css`):
```css
.filter-btn { font-family: 'IBM Plex Mono'; font-size: 10px; letter-spacing: 2px;
  text-transform: uppercase; padding: 5px 12px; border: 1px solid var(--border);
  background: transparent; color: var(--muted); cursor: pointer; }
.filter-btn:hover { color: var(--accent); border-color: var(--accent); }
.filter-btn.active { background: var(--accent); color: var(--bg); border-color: var(--accent); font-weight: 700; }
```

Sector-colour active states (in each page's inline `<style>`):
```css
.filter-btn[data-filter="biotech"].active { background: var(--green); ... }
.filter-btn[data-filter="defence"].active { background: var(--rose);  ... }
/* etc. */
```

**News controls** (single row, three groups with separators):
```html
<div class="news-controls">
  <div class="news-sector"><!-- filter-btn × 7 --></div>
  <span class="controls-sep"></span>
  <div class="news-sort"><!-- sort-btn × 4 --></div>
  <span class="controls-sep"></span>
  <div class="news-period"><!-- period-btn × 3 + #news-count --></div>
</div>
```

---

## 3 · Left Rail

```css
.left-rail {
  width: 92px; flex-shrink: 0; border-right: 1px solid var(--border);
  background: var(--bg); display: flex; flex-direction: column;
  padding: 8px 6px; gap: 4px; overflow-y: auto; scrollbar-width: none;
}
```

Always **9 pills** in order: Stock Hub · News Feed · All Sectors · AI Infra · Biotech · Crypto · Defence · Energy · Technology

Active pill: `border-color: var(--accent); color: var(--accent); background: var(--surface2)`

Each pill links to the **same page type** across sectors (e.g. on metrics → each sector's `metrics.html`).

**Pill HTML:**
```html
<a class="sector-pill [active]" href="...">
  <span class="sector-pill-icon">🌐</span>
  <span class="sector-pill-name">All Sectors</span>
  <span class="sector-pill-badge">Live</span>  <!-- omit if not live -->
</a>
```

| Pill | Icon | href (from root) | Badge |
|---|---|---|---|
| Stock Hub | ⊞ | `/index.html` | — |
| All Sectors | 🌐 | `/All/index.html` | Live |
| AI Infra | 🤖 | `/AI/index.html` | Live |
| Biotech | 🧬 | `/Biotech/index.html` | Live |
| Defence | 🛡️ | `/Defence/index.html` | Live |
| Technology | 💻 | `/Tech/index.html` | Live |
| Crypto | ₿ | `/Crypto/index.html` | Live |
| Energy | ⚡ | `/Energy/index.html` | Live |
| News Feed | 📰 | `/news.html` | — |

---

## 4 · Content Area

```css
body[data-layout="rail"] .page-main { flex: 1; overflow-y: auto; min-width: 0; }
body[data-layout="rail"] .container { padding: 20px 24px; margin: 0; max-width: none; }
```

- `.page-main` is the scroll container — same pattern as hub's `<main>`
- Only this element scrolls — everything in `<header>` and `.left-rail` is fixed
- **Last updated timestamp** lives in `.header-sub` as `<span id="data-bar-ts">—</span>`. `buildDataBar()` in `shared.js` fills it from `window.PRICES_DATA.updated` (sector pages) or `window.SIGNALS_DATA.generated`. All/ pages (async data) fill it manually in their `.then()` callback.
- **Signals pages** use `<span id="signals-ts">—</span>` in the subtitle instead — sector signals JS populates it from `SIGNALS_DATA.updated`; `All/signals.html` populates it in its async callback. The "Auto-refreshed Mon/Wed/Fri …" line lives at the bottom of the `// How signals are generated` panel as `.how-refresh-note`.

**Container overrides by page:**
| Page | Override |
|---|---|
| Heatmap | none — uses standard 20px container padding; first `.section-hdr` margin-top is zeroed in `shared.css` via `.container > .section-hdr:first-child` |
| Charts | `style="padding-left:0; padding-right:0; max-width:100%;"` (full-width charts layout) |

---

## 5 · Rail Page HTML Skeleton

```html
<body data-layout="rail">
  <div id="ticker-tape"><div class="tape-track" id="tape-track"></div></div>

  <header>
    <!-- Row 1: brand + toggle -->
    <div class="header-inner">
      <div class="header-left">
        <div class="header-label">// Market Intelligence</div>
        <h1>Page <span>Title</span></h1>
        <div class="header-sub"><span id="stock-count">—</span> stocks · Last updated <span id="data-bar-ts">—</span></div>
      </div>
      <button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()">☾</button>
    </div>
    <!-- Row 2: nav tabs -->
    <nav>
      <a class="nav-link active" href="index.html">📊 Dashboard</a>
      <a class="nav-link" href="metrics.html">📋 Metrics</a>
      <a class="nav-link" href="news.html">📰 News</a>
      <a class="nav-link" href="signals.html">🎯 Signals</a>
      <a class="nav-link" href="heatmap.html">🔥 Heatmap</a>
      <a class="nav-link" href="charts.html">📈 Charts</a>
      <a class="nav-link" href="calculator.html">🧮 What-If</a>
    </nav>
    <!-- Row 3: page controls (use appropriate class per page — see table above) -->
    <div class="filter-bar">
      <button class="filter-btn active" data-filter="all">All</button>
      <!-- sector buttons… -->
    </div>
  </header>

  <div class="page-body">
    <div class="left-rail"><!-- 9 pills --></div>
    <div class="page-main">
      <div class="container"><!-- page content --></div>
    </div>
  </div>
</body>
```

---

## 6 · Dynamic Values

| Element | Source |
|---|---|
| Stock count in header-sub (`#stock-count` / `#sector-count`) | `stocks.length` from loaded price data; set in page JS or `buildDashboardHeader()` |
| Stock count static placeholder | Hardcode the current real count so the page looks right before JS runs |
| Last updated (`#data-bar-ts`) | `buildDataBar()` in shared.js fills it; All/ pages fill it in their async `.then()` |
| Signals timestamp (`#signals-ts`) | Set in page-specific signals JS from `SIGNALS_DATA.updated` |
| Model name (`#model-name`) | Set in page-specific signals JS from `SIGNALS_DATA.model` |
| Ticker tape | `buildTape(stocks)` via shared.js |
| Hub info blocks | Aggregated from `window.__pd_*` globals (hub inline JS) |

Never hardcode timestamps. Static count placeholders are acceptable — they get overwritten by JS at runtime.

---

## 7 · Shared Files

| File | Purpose |
|---|---|
| `shared.css` | Rail layout, ticker tape, nav, filter-btn, sector-pill |
| `shared.js` | `toggleTheme()`, `buildTape()`, `buildStickyTop()` (skipped on rail), `buildNav()` (left rail + nav-panel + bottom tabs), `buildDashboardHeader()` (sector/All dashboard index pages only), `buildDataBar()` (fills `#data-bar-ts` in header-sub) |

- Hub (`index.html`) uses inline `<style>` only — does **not** load `shared.css`
- All other pages: `<link href="../shared.css">` + `<script src="../shared.js" defer>`
- `news.html` is a **root-level rail page** — loads `shared.css` / `shared.js` with no `../`, and its left-rail pills use root-relative hrefs (`AI/index.html`, not `../AI/index.html`). Sector pills point to each sector's dashboard (`index.html`); the News Feed pill is active.
- `buildNav()` in `shared.js` generates all left-rail pills AND the nav-panel 7-link sub-nav from URL detection — no hardcoded nav HTML needed in individual pages.
- `buildStickyTop()` is skipped on rail pages — `<header>` handles stickiness directly

---

## 8 · Sector Colour Mapping

Each sector has a canonical CSS variable used consistently for badges, filter-btn active states, and chart colours:

| Sector | CSS var | Usage |
|---|---|---|
| AI Infra | `var(--accent)` | filter-btn active, sector badge, rail highlight |
| Biotech | `var(--green)` | filter-btn active, sector badge |
| Defence | `var(--rose)` | filter-btn active, sector badge |
| Technology | `var(--indigo)` | filter-btn active, sector badge (text `#fff`) |
| Crypto | `var(--gold)` | filter-btn active, sector badge |
| Energy | `var(--amber)` | filter-btn active, sector badge |

**Filter-btn active states** (inline `<style>` per page — sector-specific colours not in shared.css):
```css
.filter-btn[data-filter="ai"].active      { background: var(--accent);  border-color: var(--accent); }
.filter-btn[data-filter="biotech"].active { background: var(--green);   border-color: var(--green);  color: var(--bg); }
.filter-btn[data-filter="defence"].active { background: var(--rose);    border-color: var(--rose);   color: var(--bg); }
.filter-btn[data-filter="tech"].active    { background: var(--indigo);  border-color: var(--indigo); color: #fff; }
.filter-btn[data-filter="crypto"].active  { background: var(--gold);    border-color: var(--gold);   color: var(--bg); }
.filter-btn[data-filter="energy"].active  { background: var(--amber);   border-color: var(--amber);  color: var(--bg); }
```

**Sector badge classes** (inline `<style>` per page):
```css
.sector-badge { display: inline-block; font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: 1px; padding: 3px 8px; border-radius: 2px; text-transform: uppercase; font-weight: 700; }
.sector-ai      { background: rgba(0,212,255,0.1);   color: var(--accent); border: 1px solid rgba(0,212,255,0.25); }
.sector-biotech { background: rgba(0,230,118,0.1);   color: var(--green);  border: 1px solid rgba(0,230,118,0.25); }
.sector-defence { background: rgba(251,113,133,0.1); color: var(--rose);   border: 1px solid rgba(251,113,133,0.25); }
.sector-tech    { background: rgba(167,139,250,0.1); color: var(--indigo); border: 1px solid rgba(167,139,250,0.25); }
.sector-crypto  { background: rgba(255,215,0,0.1);   color: var(--gold);   border: 1px solid rgba(255,215,0,0.25); }
.sector-energy  { background: rgba(245,158,11,0.1);  color: var(--amber);  border: 1px solid rgba(245,158,11,0.25); }
```

---

## 9 · Category Badges

Used in dashboard and metrics tables. Inline `<style>` per page — not in shared.css.

```css
.cat-badge { display: inline-block; font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: 1px; padding: 3px 8px; border-radius: 2px; text-transform: uppercase; font-weight: 700; }
.cat-memory        { background: rgba(192,132,252,0.15); color: var(--purple);  border: 1px solid rgba(192,132,252,0.3); }
.cat-nuclear-ops   { background: rgba(255,107,53,0.15);  color: var(--accent2); border: 1px solid rgba(255,107,53,0.3); }
.cat-smr           { background: rgba(57,255,20,0.1);    color: var(--green);   border: 1px solid rgba(57,255,20,0.25); }
.cat-uranium       { background: rgba(255,215,0,0.1);    color: var(--gold);    border: 1px solid rgba(255,215,0,0.3); }
.cat-power-infra   { background: rgba(0,212,255,0.1);    color: var(--accent);  border: 1px solid rgba(0,212,255,0.25); }
.cat-dc-operators  { background: rgba(68,136,255,0.1);   color: var(--blue);    border: 1px solid rgba(68,136,255,0.25); }
.cat-hyperscalers  { background: rgba(167,139,250,0.1);  color: var(--indigo);  border: 1px solid rgba(167,139,250,0.25); }
.cat-ai-compute    { background: rgba(251,113,133,0.1);  color: var(--rose);    border: 1px solid rgba(251,113,133,0.25); }
.cat-fibre-optical { background: rgba(45,212,191,0.1);   color: var(--teal);    border: 1px solid rgba(45,212,191,0.25); }
.cat-dsp-semi      { background: rgba(245,158,11,0.1);   color: var(--amber);   border: 1px solid rgba(245,158,11,0.25); }
.cat-test-equip    { background: rgba(148,163,184,0.1);  color: var(--slate);   border: 1px solid rgba(148,163,184,0.25); }
.cat-materials     { background: rgba(163,230,53,0.1);   color: var(--lime);    border: 1px solid rgba(163,230,53,0.25); }
```

---

## 10 · Charts Page Layout

All charts pages use the standard rail layout. All shared CSS lives in `shared.css` under `/* ---- Charts pages ---- */`. Only sector-specific `.cat-btn.active-*` and `.cat-label.*` colour rules stay inline per page.

Charts pages include `<span id="data-bar-ts">—</span>` in `.header-sub` — filled by `buildDataBar()` from `shared.js`, same as other pages.

### Header structure

```html
<header>
  <div class="header-inner">
    <div class="header-left">…brand…</div>
    <!-- NO header-blocks / data-bar-ts -->
    <button class="theme-toggle" …>☾</button>
  </div>
  <nav>…</nav>
  <div class="chart-controls">
    <div class="toolbar-inner">
      <!-- Category row — shown only in grid mode -->
      <div class="toolbar-row" id="cat-row" style="display:none">
        <span class="toolbar-label">Category</span>
        <div id="cat-toolbar-btns" style="display:flex;gap:6px;flex-wrap:wrap;"></div>
      </div>
      <!-- Controls row -->
      <div class="toolbar-row">
        <div class="toolbar-group">
          <span class="toolbar-label">View</span>
          <button class="tool-btn active" id="btn-single" onclick="setView('single')">Single</button>
          <button class="tool-btn" id="btn-grid" onclick="setView('grid')">Category Grid</button>
        </div>
        <div class="divider"></div>
        <div class="toolbar-group">
          <span class="toolbar-label">Period</span>
          <button class="tool-btn active" onclick="setTimeframe('1W',this)">1W</button>
          <button class="tool-btn" onclick="setTimeframe('1M',this)">1M</button>
          <button class="tool-btn" onclick="setTimeframe('12M',this)">1Y</button>
          <button class="tool-btn" onclick="setTimeframe('60M',this)">5Y</button>
        </div>
      </div>
    </div>
  </div>
</header>
```

### Page body structure

```html
<div class="page-body">
  <div class="left-rail">…sector pills…</div>
  <div class="page-main">
    <div class="container" style="padding-left:0;padding-right:0;max-width:100%;">

      <!-- SINGLE VIEW -->
      <div id="single-view">
        <button class="sidebar-toggle" …>☰ Select Stock ▾</button>
        <aside class="sidebar" id="sidebar">
          <div class="sidebar-title">Select Stock</div>
          <div id="sidebar-stocks"></div>
        </aside>
        <main class="chart-area">
          <div class="chart-header">…ticker + name…</div>
          <div class="chart-widget" id="single-widget"></div>
          <div class="chart-note">Charts powered by TradingView…</div>
        </main>
      </div>

      <!-- GRID VIEW -->
      <div id="grid-view">
        <div class="grid-heading" id="grid-heading">Select a category above</div>
        <div class="chart-grid" id="chart-grid"></div>
        <div class="chart-note" style="margin-top:16px;">…</div>
      </div>

    </div>
  </div>
</div>
```

### Key CSS rules (all in shared.css)

| Selector | Purpose |
|---|---|
| `.chart-controls` | Toolbar wrapper inside `<header>` — `border-top`, sticky z-index 25 |
| `.toolbar-inner` | Flex column, `padding: 8px 16px` — no max-width/centering |
| `.toolbar-row` | Flex row for one row of controls |
| `.toolbar-group` | Groups label + buttons horizontally |
| `.tool-btn` | View / Period buttons; `.active` uses `var(--accent)` fill |
| `.cat-btn` | Category filter buttons with tooltip support; active class is `.active-{catKey}` (sector-specific colours inline) |
| `.divider` | 1px vertical separator between toolbar groups |
| `#single-view` | CSS Grid `260px 1fr`, `padding: 24px` — no max-width/centering |
| `.sidebar` | Sticky `top: 24px`, scrollable stock list |
| `.cat-label` | Category group label in sidebar; colour from inline `.cat-label.{cls}` rules |
| `.stock-btn` | Sidebar stock button; `.active` highlights with left accent border |
| `#grid-view` | `padding: 12px 24px 24px` — top 12px keeps it tight under toolbar |
| `.grid-heading` | Category + stock count heading; `span` uses `var(--accent)` |
| `.chart-grid` | `auto-fill minmax(480px, 1fr)` responsive grid |
| `.grid-card` | Individual chart card with border |

### TradingView widgets
- Single view: fixed `height: 580`, `width: '100%'`
- Grid cards: fixed `height: 320` per card, staggered with `setTimeout(fn, i * 150)`

### Sector-specific colours (inline per page)
```css
/* Keep INLINE — not in shared.css */
.cat-btn.active-{catKey} { background: var(--COLOR); border-color: var(--COLOR); color: var(--bg); }
.cat-label.{clsSuffix}   { color: var(--COLOR); }
```

### All/charts — Sector Grid variant

`All/charts.html` uses a **different pattern** from sector charts pages — no Single/Grid view toggle, no category buttons. Instead:

```html
<div class="chart-controls">
  <div class="toolbar-inner">
    <div class="toolbar-row">
      <span class="toolbar-label">Sector</span>
      <button class="tool-btn active-all" data-sector="all" onclick="setSector('all',this)">All</button>
      <button class="tool-btn" data-sector="ai" onclick="setSector('ai',this)">AI Infra</button>
      <!-- …one button per sector… -->
    </div>
    <div class="toolbar-row">
      <span class="toolbar-label">Period</span>
      <button class="tool-btn" data-period="1W">1W</button>
      <button class="tool-btn active" data-period="1Y">1Y</button>
      <button class="tool-btn" data-period="5Y">5Y</button>
    </div>
  </div>
</div>
```

**"All" mode** renders a `display:grid; grid-template-columns: repeat(6,1fr)` with a header row of sector labels followed by 3 stock rows (top 3 per sector by `market_cap_gbp_b`). Chart height 200px.

**Single-sector mode** renders a `chart-grid` with `repeat(auto-fill, minmax(320px, 1fr))`. Chart height 220px.

Sector active-state colours use `.active-{sectorKey}` classes (inline `<style>` per page), mirroring the sector colour mapping from §8.

---

## 11 · Section Header (divider with label + count)

Used in heatmap and any page with multiple named sections:

```html
<div class="section-hdr">
  <span class="section-hdr-label">All Stocks</span>
  <div class="section-hdr-line"></div>
  <span class="section-hdr-count">192 stocks</span>
</div>
```
```css
.section-hdr { display: flex; align-items: center; gap: 16px; margin: 32px 0 10px; }
.container > .section-hdr:first-child { margin-top: 0; }   /* first header sits tight under the toolbar */
.section-hdr-label { font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 3px; color: var(--accent); text-transform: uppercase; white-space: nowrap; }
.section-hdr-line { flex: 1; height: 1px; background: var(--border); }
.section-hdr-count { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--muted); white-space: nowrap; }
```

> **Subsequent** section headers (e.g. "By Sector" / "By Category") keep an inline `style="margin-top:48px;"` to separate them from the block above.

### Heatmap CSS lives in `shared.css`

As of the rail redesign, **all heatmap-page styles are consolidated in `shared.css`** (section `/* ---- Heatmap pages ---- */`) — no per-page inline `<style>` blocks. This covers `.toolbar` + controls, `.metric-btn`, `.size-note`, `.toolbar-ts`, `.legend`/`.leg-*`, `.section-hdr*`, `.map-wrap`, `#sectors-container` (2-col grid), `.sector-block`/`.sector-name`, `.cat-label-text`, `.tooltip`/`.tt-*`, and `.empty-state`. All 7 heatmap pages (`All/` + 6 sectors) render identically from this single source.

The `.toolbar` sits **inside `<header>`** (Row 3, after `<nav>`) on every heatmap page — a clean `border-top` bar, not a free-floating boxed/sticky element.

---

## 12 · Button Variants

All buttons share the same base shape (IBM Plex Mono, uppercase, 1px border). Active states differ by button type:

| Variant | Class | Active state |
|---|---|---|
| Filter | `.filter-btn` | Filled accent background, white text |
| Sort | `.sort-btn` | Accent text + border only (no fill) |
| Period | `.period-btn` | Surface2 background + accent border |
| Timeframe | `.tf-btn` | Accent text + border only (no fill) |
| View toggle | `.view-btn` | Filled accent background |

**Sort button** (news page):
```css
.sort-btn.active { color: var(--accent); border-color: var(--accent); font-weight: 700; }
```

**Period button** (news page):
```css
.period-btn.active { background: var(--surface2); color: var(--text); border-color: var(--accent); font-weight: 700; }
```

**Controls separator** (news page, between button groups):
```css
.controls-sep { width: 1px; height: 20px; background: var(--border); margin: 0 10px; flex-shrink: 0; }
```

---

## 13 · Analyst Rating Badges

Used in metrics table. Inline `<style>` per page.

```css
.analyst-badge { font-family: 'IBM Plex Mono', monospace; font-size: 10px; padding: 2px 7px; letter-spacing: 0.5px; font-weight: 600; white-space: nowrap; border: 1px solid; }
.analyst-strong-buy   { background: rgba(0,230,118,0.15);  color: var(--green);   border-color: rgba(0,230,118,0.3); }
.analyst-buy          { background: rgba(163,230,53,0.12); color: var(--lime);    border-color: rgba(163,230,53,0.3); }
.analyst-hold         { background: rgba(245,158,11,0.12); color: var(--amber);   border-color: rgba(245,158,11,0.3); }
.analyst-underperform { background: rgba(255,107,53,0.12); color: var(--accent2); border-color: rgba(255,107,53,0.3); }
.analyst-sell         { background: rgba(255,68,68,0.12);  color: var(--red);     border-color: rgba(255,68,68,0.3); }
```

---

## 14 · Return & YTD Colouring

**1-year return classes** (dashboard table):
```css
.return-mega     { color: #0284c7; font-family: 'IBM Plex Mono', monospace; font-weight: 700; } /* ≥200% */
html[data-theme="dark"] .return-mega { color: #ffd700; }
.return-positive { color: #16a34a; font-family: 'IBM Plex Mono', monospace; font-weight: 700; } /* ≥50% */
.return-modest   { color: #0284c7; font-family: 'IBM Plex Mono', monospace; font-weight: 700; } /* positive but <50% */
.return-negative { color: #dc2626; font-family: 'IBM Plex Mono', monospace; font-weight: 700; }
```

**YTD classes:**
```css
.ytd-return { font-family: 'IBM Plex Mono', monospace; font-weight: 700; }
.ytd-pos  { color: var(--green); }
.ytd-neg  { color: var(--red); }
.ytd-flat { color: var(--muted); }
```

---

## 15 · Rules Summary

1. **Ticker tape** is always first in `<body>`, always fixed at top
2. **Header** contains all sticky chrome: brand row → nav row → page control row(s)
3. **Brand row**: `header-left` (with `margin-right: auto`) + theme toggle — brand always left
4. **Nav and all controls live inside `<header>`** — they are sticky chrome, not page content
5. **Left rail** always has all 9 pills; active pill matches the current page's sector
6. **Stock counts are always dynamic** — never hardcode numbers in HTML
7. **Only `.page-main` scrolls** — header and rail are fixed
8. **Colours from CSS tokens only** — never hardcode hex in HTML or JS
