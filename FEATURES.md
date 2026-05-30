# Features

## Backlog

- **Energy sector** — dedicated `Energy\` subfolder and sector card on hub
- **Crypto sector** — dedicated `Crypto\` subfolder and sector card on hub

## Done

- **AI sector** — 48 stocks across 12 categories; metrics, news, signals, heatmap, charts, calculator; prices updated twice daily via GitHub Actions
- **Biotech sector** — 30 stocks across 9 categories (large-cap, UK listed, gene editing, genomics, oncology, mRNA, rare disease, metabolic, neuroscience); metrics, news, signals, heatmap, charts, calculator; prices updated twice daily via GitHub Actions
- **Defence & Aerospace sector** — 28 stocks across 6 categories (US Primes, UK/European, Cyber/Intel, Drones, Space, Weapons/Systems); full 7-page suite; prices and signals via GitHub Actions
- **`generate_all_signals.bat`** — single root-level script runs all 3 sector signal generators; output streams live and saves to `signals_log.txt` (overwritten each run)
- **`update_all_prices.bat`** — single root-level script runs all 3 sector price updates; output streams live and saves to `update_log.txt` (overwritten each run)
- **Charts default: Category Grid / 1W / first category** — charts pages open directly on grid view, 1-week timeframe, first category pre-selected per sector
- **Dashboard header hierarchy** — sector name is the large h1; "Stock Universe" is the small monospace label; Biotech h1 split Bio (dark) / tech (blue)
- **shared.js** — `toggleTheme()` and `buildTape()` extracted from 22 inline copies into one shared file; heatmaps use `window._onThemeChange` hook
- **Light/dark mode toggle** — ☾/☀ button in every page's header; light mode default; dark via `html[data-theme="dark"]`; `localStorage` persistence; flash-prevention in `<head>`; all 22 pages (root hub + 3 sectors × 7); heatmap D3 colours CSS-var-driven with re-render on toggle
- **shared.css** — all shared CSS (reset, body, ticker tape, header, nav, footer, container, sector switcher) extracted into a single file loaded by all 21 sector pages; eliminates duplication across sectors
- **Sector switcher** — replaces the fragile back-link; mini sector cards in the header right side; context-aware links (stays on same page type when switching); Stock Hub card; active sector is bright/cyan, others dimmed
