# Stocks — Design System

**Reference page:** Stock Hub (`/index.html`)  
All pages must conform to these rules. When in doubt, match the hub exactly.

---

## Spacing Reference

Exact pixel values for every zone. Do not deviate.

```
┌─────────────────────────────────────────────────────────┐
│  TICKER TAPE  h=36px  │ item pad: 0 20px │ gap: 7px     │
├─────────────────────────────────────────────────────────┤
│  HEADER ROW 1   brand + toggle   pad: 12px 20px         │
├─────────────────────────────────────────────────────────┤
│  HEADER ROW 2   nav tabs         pad: 0 16px            │
├─────────────────────────────────────────────────────────┤
│  HEADER ROW 3   filter bar       pad: 8px 16px          │
│                 (only on pages that have filters)        │
├────────┬────────────────────────────────────────────────┤
│  RAIL  │  CONTENT   pad: 20px 24px                      │
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
| Ticker tape | item gap (ticker · price · change) | `7px` |
| Ticker tape | font size | `11px` IBM Plex Mono |
| Body | padding-top (clears tape) | `36px` |
| Header row 1 | padding | `12px 20px` |
| Header row 2 (nav) | padding | `0 16px` |
| Header row 3 (filters) | padding | `8px 16px` |
| Nav tab | padding | `10px 16px` |
| Nav tab | active underline | `border-bottom: 2px solid var(--accent)` |
| Filter button | padding | `6px 10px` (via `.filter-btn`) |
| Left rail | width | `92px` |
| Left rail | padding | `8px 6px` |
| Left rail | gap between pills | `4px` |
| Sector pill | padding | `8px 6px` |
| Sector pill | internal gap (icon · name · badge) | `3px` |
| Sector pill icon | font-size | `18px` |
| Sector pill name | font-size | `8px` |
| Sector pill badge | font-size | `7px`, padding `1px 4px` |
| Content area | padding | `20px 24px` |
| Info block (each) | padding | `6px 24px` |
| Info block (each) | internal gap (label → value) | `4px` |
| Info blocks group | margin-right (before toggle) | `16px` |
| Info block label | font-size | `9px` |
| Info block value | font-size | `13px` |
| Theme toggle | size | `44×44px` |

---

## Layout: Layer Stack (top → bottom)

```
┌──────────────────────────────────────────┐
│  TICKER TAPE   position: fixed  h=36px   │  z-index: 200
├──────────────────────────────────────────┤
│  HEADER ROW 1  brand + toggle  sticky    │  z-index: 100
│  HEADER ROW 2  nav tabs                  │
│  HEADER ROW 3  filter bar (if present)   │
├─────────┬────────────────────────────────┤
│         │                                │
│  LEFT   │  CONTENT  overflow-y: auto     │
│  RAIL   │  padding: 20px 24px            │
│  w=92px │                                │
└─────────┴────────────────────────────────┘
```

- `html, body { height: 100%; }` — full viewport height, no scroll on the page itself
- `body { overflow: hidden; padding-top: 36px; }` — clears the fixed ticker tape
- `body[data-layout="rail"] { display: flex; flex-direction: column; }` — stacks header → page-body
- Only the content area (`.page-main`) scrolls internally
- The entire `<header>` (all 3 rows) is sticky — no separate sticky-top wrapper needed on rail pages

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
  background: var(--bg);
  border-bottom: 1px solid var(--accent);
  overflow: hidden;
}
```

- Always the **topmost element** in `<body>`
- Populated by `buildTape()` from `shared.js`
- Pauses on hover
- On the hub: aggregates stocks across all 6 sector `__pd_*` globals (deduplicated by ticker)

---

## 2 · Header

The header contains **all three sticky rows** for rail pages. It is a flex column:

```css
body[data-layout="rail"] header {
  padding: 0;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  border-bottom: 1px solid var(--accent);
  background: var(--bg);
}
```

### Row 1 — Brand + Toggle

```css
body[data-layout="rail"] .header-inner {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  max-width: none;
  margin: 0;
  gap: 20px;
}
body[data-layout="rail"] .header-left { margin-right: auto; }
```

```html
<div class="header-inner">
  <div class="header-left">
    <div class="header-label">// Market Intelligence</div>
    <h1>Page <span>Title</span></h1>
    <div class="header-sub">— · — · —</div>
  </div>
  <button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()">☾</button>
</div>
```

- `header-label`: always `// Market Intelligence`, `color: var(--accent)`
- `h1`: page name — second word/phrase in `<span>` to get accent colour
- `header-sub`: page-specific descriptor — include dynamic `<span id="...">` for live values
- **Info blocks** (hub only): go between `.header-left` and the toggle. See hub inline CSS.

### Row 2 — Nav Tabs

```css
body[data-layout="rail"] header nav {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 0 16px;
  border-top: 1px solid var(--border);
  background: var(--bg);
  overflow-x: auto;
  scrollbar-width: none;
}
.nav-link {
  font-family: 'IBM Plex Mono'; font-size: 11px; letter-spacing: 1.5px;
  text-transform: uppercase; padding: 10px 16px;
  color: var(--dim); border-bottom: 2px solid transparent;
  text-decoration: none; white-space: nowrap;
}
.nav-link.active { color: var(--accent); border-bottom-color: var(--accent); }
```

### Row 3 — Filter Bar (pages that have filters)

```css
body[data-layout="rail"] header .filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 8px 16px;
  border-top: 1px solid var(--border);
  margin-bottom: 0;
}
```

Pages with filter bar: Dashboard, Metrics, Signals, Calculator  
Pages without: News, Heatmap, Charts

---

## 3 · Left Rail

```css
.left-rail {
  width: 92px; flex-shrink: 0;
  border-right: 1px solid var(--border);
  background: var(--bg);
  display: flex; flex-direction: column;
  padding: 8px 6px; gap: 4px;
  overflow-y: auto; scrollbar-width: none;
}
```

- Always **9 pills** in order: Stock Hub · All Sectors · AI Infra · Biotech · Defence · Technology · Crypto · Energy · RSS Feed
- Active pill gets `class="... active"` — `border-color: var(--accent); color: var(--accent); background: var(--surface2)`
- Each pill links to the **same page type** across sectors (e.g. if on metrics, links go to each sector's `metrics.html`)

**Pill HTML:**
```html
<a class="sector-pill [active]" href="...">
  <span class="sector-pill-icon">🌐</span>
  <span class="sector-pill-name">All Sectors</span>
  <span class="sector-pill-badge">Live</span>  <!-- omit if not live -->
</a>
```

```css
.sector-pill {
  display: flex; flex-direction: column; align-items: center;
  gap: 3px; padding: 8px 6px;
  background: var(--surface); border: 1px solid var(--border); border-radius: 2px;
  font-family: 'IBM Plex Mono'; font-size: 8px; letter-spacing: 1.2px;
  text-transform: uppercase; color: var(--dim); text-decoration: none;
}
.sector-pill-icon  { font-size: 18px; line-height: 1; }
.sector-pill-badge { font-size: 7px; padding: 1px 4px;
                     background: rgba(0,230,118,0.1); color: var(--green);
                     border: 1px solid rgba(0,230,118,0.25); }
```

### Sector pill reference

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
body[data-layout="rail"] .page-main {
  flex: 1;
  overflow-y: auto;
  min-width: 0;
}
body[data-layout="rail"] .container {
  padding: 20px 24px;
  margin: 0;
  max-width: none;
}
```

- `.page-main` is the scroll container — same pattern as hub's `<main>`
- Only this element scrolls — everything above (header with all 3 rows, left rail) is fixed
- `data-bar` (last updated / schedule info) injected here by `shared.js` at `afterbegin`

---

## 5 · Rail Page Setup (`data-layout="rail"`)

All `All/` sub-pages and their sector equivalents use the rail layout.

```css
body[data-layout="rail"] {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
```

**Full HTML skeleton for every rail page:**

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
    <!-- Row 3: filter bar (omit if page has no filters) -->
    <div class="filter-bar">
      <button class="filter-btn active" data-filter="all">All</button>
      <button class="filter-btn" data-filter="ai">AI Infra</button>
      <button class="filter-btn" data-filter="biotech">Biotech</button>
      <button class="filter-btn" data-filter="defence">Defence</button>
      <button class="filter-btn" data-filter="tech">Tech</button>
      <button class="filter-btn" data-filter="crypto">Crypto</button>
      <button class="filter-btn" data-filter="energy">Energy</button>
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

All stock counts and timestamps must be **live from data** — never hardcoded.

| Element | Source |
|---|---|
| Stock count in header-sub | `new Set(stocks.map(s => s.ticker)).size` from loaded price data |
| Last updated | `data.updated` from prices-data.js / signals-local.js |
| Ticker tape | `buildTape(stocks)` via shared.js |
| Hub info blocks | Aggregated from `window.__pd_*` globals |

---

## 7 · Shared Files

| File | Purpose |
|---|---|
| `shared.css` | Ticker tape, sector-card pills, rail layout, sticky-top, data-bar |
| `shared.js` | `toggleTheme()`, `buildTape()`, `buildStickyTop()`, `buildDataBar()` |

- Hub (`index.html`) has its own inline `<style>` — it does **not** load `shared.css`
- All other pages load `shared.css` and `shared.js`
- `shared.js` is always loaded with `defer`
- `buildStickyTop()` is skipped on rail pages — the header handles its own stickiness

---

## Rules Summary

1. **Ticker tape** is always first in `<body>`, always fixed at top
2. **Header** contains all 3 rows (brand · nav · filters) and is always sticky — no separate sticky-top wrapper
3. **Header row 1**: Brand (left, `margin-right: auto`) → Toggle (right). Info blocks in middle on hub only.
4. **Nav and filter bar** live inside `<header>` — they are part of the sticky chrome, not page content
5. **Left rail** always has all 9 pills; active pill matches the current page's sector
6. **Stock counts are always dynamic** — never write a hardcoded number into HTML
7. **Only `.page-main` scrolls** — header and rail are fixed
8. **Colours come from CSS tokens only** — never hardcode hex values in HTML or JS
