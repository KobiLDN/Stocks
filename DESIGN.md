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
│  HEADER       pad: 12px 20px (top/btm: 12  left/right: 20)
│  ├─ header-label  mb: 4px                               │
│  ├─ h1         font: 26px                               │
│  ├─ header-sub  mt: 4px  font: 11px                     │
│  ├─ info blocks  pad: 6px 24px  gap: 4px  mr: 16px      │
│  └─ theme toggle  44×44px                               │
├────────┬────────────────────────────────────────────────┤
│  RAIL  │  NAV   pad: 0 16px │ tab pad: 10px 16px        │
│ w=92px ├────────────────────────────────────────────────┤
│pad:    │                                                 │
│8px 6px │  CONTENT   pad: 20px 24px                      │
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
| Header sticky | top | `36px` |
| Header | padding | `12px 20px` |
| Header label | margin-bottom | `4px` |
| Header h1 | font-size | `26px` |
| Header sub | margin-top | `4px` |
| Header sub | font-size | `11px` |
| Info block (each) | padding | `6px 24px` |
| Info block (each) | internal gap (label → value) | `4px` |
| Info blocks group | margin-right (before toggle) | `16px` |
| Info block label | font-size | `9px` |
| Info block value | font-size | `13px` |
| Theme toggle | size | `44×44px` |
| Left rail | width | `92px` |
| Left rail | padding | `8px 6px` |
| Left rail | gap between pills | `4px` |
| Sector pill | padding | `8px 6px` |
| Sector pill | internal gap (icon · name · badge) | `3px` |
| Sector pill icon | font-size | `18px` |
| Sector pill name | font-size | `8px` |
| Sector pill badge | font-size | `7px`, padding `1px 4px` |
| Nav bar | padding | `0 16px` |
| Nav tab | padding | `10px 16px` |
| Nav tab | active underline | `border-bottom: 2px solid var(--accent)` |
| Content area | padding | `20px 24px` |

---

## Layout: Layer Stack (top → bottom)

```
┌──────────────────────────────────────────┐
│  TICKER TAPE   position: fixed  h=36px   │  z-index: 200
├──────────────────────────────────────────┤
│  HEADER        position: sticky top=36px │  z-index: 100
├─────────┬────────────────────────────────┤
│         │  NAV BAR (All/ pages only)     │
│  LEFT   ├────────────────────────────────┤
│  RAIL   │                                │
│  w=92px │  CONTENT  overflow-y: auto     │
│         │                                │
└─────────┴────────────────────────────────┘
```

- `html, body { height: 100%; }` — full viewport height, no scroll on the page itself
- `body { overflow: hidden; padding-top: 36px; }` — clears the fixed ticker tape
- Only the content area scrolls internally

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

```css
header {
  padding: 12px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--accent);
}
```

Wrapped in `.header-sticky { position: sticky; top: 36px; z-index: 100; background: var(--bg); }`.

### Header structure — three blocks left → right

```
[ BRAND BLOCK ]  [ INFO BLOCKS (optional) ]  [ THEME TOGGLE ]
```

**Brand block** (always present, always left):
```html
<div class="header-brand">
  <div class="header-label">// Market Intelligence</div>
  <h1>Page <span>Title</span></h1>
  <div class="header-sub">— · — · —</div>
</div>
```

- `header-label`: always `// Market Intelligence`, `color: var(--accent)`
- `h1`: page name — second word/phrase in `<span>` to get accent colour
- `header-sub`: page-specific descriptor in mono — include dynamic `<span id="...">` for live values (stock count, timestamp)

**Info blocks** (hub only — fills the middle):
```html
<div class="header-blocks">
  <div class="header-block">
    <div class="header-block-label">Universe</div>
    <div class="header-block-value" id="hb-universe">— stocks · — sectors</div>
  </div>
  <!-- repeat for Prices, Last Updated, etc. -->
</div>
```
```css
.header-blocks { display: flex; align-items: stretch; margin-left: auto; margin-right: 16px; }
.header-block  { padding: 6px 24px; border-left: 1px solid var(--border);
                 display: flex; flex-direction: column; justify-content: center; gap: 4px; }
.header-block-label { font-family: 'IBM Plex Mono'; font-size: 9px; letter-spacing: 1.5px;
                      text-transform: uppercase; color: var(--muted); }
.header-block-value { font-family: 'IBM Plex Mono'; font-size: 13px; font-weight: 700;
                      color: var(--text); white-space: nowrap; }
```

- Info blocks fill the empty space between brand and toggle
- Any additional header element (toggle, status, actions) goes **to the right**
- Think in blocks: `[Brand] → [Info...] → [Toggle]`

**Theme toggle** (always present, always right):
```html
<button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()">☾</button>
```
```css
.theme-toggle { width: 44px; height: 44px; font-size: 18px; flex-shrink: 0;
                background: var(--surface); border: 1px solid var(--border);
                border-top: 2px solid var(--border); border-radius: 4px;
                color: var(--dim); opacity: 0.65; }
```

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

## 4 · Nav Bar (All/ and sector pages only)

Sits inside `.page-main`, below the header, above the content.

```css
nav {
  border-bottom: 1px solid var(--border);
  padding: 0 16px;
  display: flex; gap: 2px; flex-shrink: 0;
  background: var(--bg); overflow-x: auto;
}
.nav-link {
  font-family: 'IBM Plex Mono'; font-size: 11px; letter-spacing: 1.5px;
  text-transform: uppercase; padding: 10px 16px;
  color: var(--dim); border-bottom: 2px solid transparent;
  text-decoration: none; white-space: nowrap;
}
.nav-link.active { color: var(--accent); border-bottom-color: var(--accent); }
```

---

## 5 · Content Area

```css
.container { /* or main on hub */
  flex: 1; overflow-y: auto;
  padding: 20px 24px;
}
```

- Only this element scrolls — everything above is fixed/sticky
- `data-bar` (last updated / schedule info) injected here by `shared.js` at `afterbegin`

---

## 6 · Rail Page Setup (`data-layout="rail"`)

All `All/` sub-pages and their sector equivalents use the rail layout. Set on `<body>`:

```html
<body data-layout="rail">
```

`shared.css` applies these overrides automatically:
```css
body[data-layout="rail"] { height: 100%; overflow: hidden; }
body[data-layout="rail"] .page-body { display: flex; flex: 1; min-height: 0; overflow: hidden; }
body[data-layout="rail"] .left-rail { width: 92px; ... }
body[data-layout="rail"] .page-main { flex: 1; display: flex; flex-direction: column; min-width: 0; overflow: hidden; }
body[data-layout="rail"] nav { flex-shrink: 0; position: static; }
body[data-layout="rail"] .container { flex: 1; overflow-y: auto; padding-top: 16px; }
```

HTML skeleton for every rail page:
```html
<body data-layout="rail">
  <div id="ticker-tape"><div class="tape-track" id="tape-track"></div></div>

  <header>
    <div class="header-inner">
      <div class="header-left">
        <div class="header-label">// Market Intelligence</div>
        <h1>Page <span>Title</span></h1>
        <div class="header-sub">...</div>
      </div>
      <button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()">☾</button>
    </div>
  </header>

  <div class="page-body">
    <div class="left-rail"><!-- 9 pills --></div>
    <div class="page-main">
      <nav><!-- page tabs --></nav>
      <div class="container"><!-- content --></div>
    </div>
  </div>
</body>
```

---

## 7 · Dynamic Values

All stock counts and timestamps must be **live from data** — never hardcoded.

| Element | Source |
|---|---|
| Stock count in header-sub | `new Set(stocks.map(s => s.ticker)).size` from loaded price data |
| Last updated | `data.updated` from prices-data.js / signals-local.js |
| Ticker tape | `buildTape(stocks)` via shared.js |
| Hub info blocks | Aggregated from `window.__pd_*` globals |

---

## 8 · Shared Files

| File | Purpose |
|---|---|
| `shared.css` | Ticker tape, sector-card pills, rail layout, sticky-top, data-bar |
| `shared.js` | `toggleTheme()`, `buildTape()`, `buildStickyTop()`, `buildDataBar()` |

- Hub (`index.html`) has its own inline `<style>` — it does **not** load `shared.css`
- All other pages load `shared.css` and `shared.js`
- `shared.js` is always loaded with `defer`

---

## Rules Summary

1. **Ticker tape** is always first in `<body>`, always fixed at top
2. **Header** is always sticky at `top: 36px`, always `// Market Intelligence` label in accent colour
3. **Header structure**: Brand (left) → Info blocks (middle, if needed) → Toggle (right). No dead empty space
4. **Left rail** always has all 9 pills; active pill matches the current page's sector
5. **Stock counts are always dynamic** — never write a hardcoded number into HTML
6. **Only the content area scrolls** — header, rail, and nav are all fixed/sticky
7. **Colours come from CSS tokens only** — never hardcode hex values in HTML or JS
