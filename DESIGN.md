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
    <div class="header-sub">— stocks · v1 · Last updated —</div>
  </div>
  <button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()">☾</button>
</div>
```

Info blocks (Universe / Prices / Last Updated) go between `.header-left` and the toggle — **hub only**.

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
| Charts | `.chart-controls` | Ticker label · 1W/1Y/5Y buttons · Single/Grid toggle (right) |
| Calculator | `.filter-bar` | Sector filters |

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

Always **9 pills** in order: Stock Hub · All Sectors · AI Infra · Biotech · Defence · Technology · Crypto · Energy · RSS Feed

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
| RSS Feed | 📰 | `/rss.html` | — |

---

## 4 · Content Area

```css
body[data-layout="rail"] .page-main { flex: 1; overflow-y: auto; min-width: 0; }
body[data-layout="rail"] .container { padding: 20px 24px; margin: 0; max-width: none; }
```

- `.page-main` is the scroll container — same pattern as hub's `<main>`
- Only this element scrolls — everything in `<header>` and `.left-rail` is fixed
- `data-bar` (last updated / schedule info) injected at `afterbegin` of `.container` by `shared.js`

**Container overrides by page:**
| Page | Override |
|---|---|
| Heatmap | `style="padding-top: 8px;"` (toolbar is in header, less gap needed) |
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
        <div class="header-sub">— stocks · v1 · Last updated —</div>
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
| Stock count in header-sub | `new Set(stocks.map(s => s.ticker)).size` from loaded price data |
| Last updated | `data.updated` from prices-data.js / signals-local.js |
| Ticker tape | `buildTape(stocks)` via shared.js |
| Hub info blocks | Aggregated from `window.__pd_*` globals |

Never hardcode stock counts or timestamps.

---

## 7 · Shared Files

| File | Purpose |
|---|---|
| `shared.css` | Rail layout, ticker tape, nav, filter-btn, sector-pill |
| `shared.js` | `toggleTheme()`, `buildTape()`, `buildStickyTop()` (skipped on rail), `buildDataBar()` |

- Hub (`index.html`) uses inline `<style>` only — does **not** load `shared.css`
- All other pages: `<link href="../shared.css">` + `<script src="../shared.js" defer>`
- `buildStickyTop()` is skipped on rail pages — `<header>` handles stickiness directly

---

## 8 · Rules Summary

1. **Ticker tape** is always first in `<body>`, always fixed at top
2. **Header** contains all sticky chrome: brand row → nav row → page control row(s)
3. **Brand row**: `header-left` (with `margin-right: auto`) + theme toggle — brand always left
4. **Nav and all controls live inside `<header>`** — they are sticky chrome, not page content
5. **Left rail** always has all 9 pills; active pill matches the current page's sector
6. **Stock counts are always dynamic** — never hardcode numbers in HTML
7. **Only `.page-main` scrolls** — header and rail are fixed
8. **Colours from CSS tokens only** — never hardcode hex in HTML or JS
