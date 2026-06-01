# Features

## Backlog

- **Energy sector** — dedicated `Energy\` subfolder and sector card on hub

## Done

- **Crypto sector** — 16 stocks across 5 categories (Bitcoin ETFs, Ethereum ETFs, exchanges, corporate treasury, miners); metrics, news, signals, heatmap, charts, calculator; prices updated twice daily via GitHub Actions
- **AI sector** — 48 stocks across 12 categories; metrics, news, signals, heatmap, charts, calculator; prices updated twice daily via GitHub Actions
- **Biotech sector** — 30 stocks across 9 categories (large-cap, UK listed, gene editing, genomics, oncology, mRNA, rare disease, metabolic, neuroscience); metrics, news, signals, heatmap, charts, calculator; prices updated twice daily via GitHub Actions
- **Technology sector** — 31 stocks across 6 categories (mega-cap, semiconductors, enterprise software, cybersecurity, consumer platforms, hardware/infra); full 7-page suite; prices and signals via GitHub Actions
- **Defence & Aerospace sector** — 28 stocks across 6 categories (US Primes, UK/European, Cyber/Intel, Drones, Space, Weapons/Systems); full 7-page suite; prices and signals via GitHub Actions
- **Hub signals picks** — each sector card on the hub shows the top 5 AI signal picks fetched live from `signals-local.json` + `prices-data.js`; metrics-style full-bleed table (ticker, signal badge, 1D/1W/YTD, confidence); clicking the table navigates to that sector's signals page
- **Crypto coming soon card** — placeholder card on the hub with `Coming Soon` badge; no link, dimmed styling
- **Sector selector on generate-signals workflow** — `workflow_dispatch` dropdown (all / AI / Biotech / Defence / Tech) lets you refresh a single sector's signals on demand; scheduled runs always run all sectors (`.github/workflows/generate-signals.yml`)
- **Sector-prefixed script names** — `update_prices.py` → `[Sector]_update_prices.py`; `generate_signals_local.py` → `[Sector]_generate_signals_local.py`; workflows, bat files, and all docs updated
- **Bot push-rejection fix** — `git pull --rebase` before `git push` in both workflows prevents push failures when new commits land while the bot job is running
- **Bot commit messages** — both workflows now commit as "Update prices — all sectors" / "Update signals — all sectors (or sector name)" for clarity
- **`generate_all_signals.bat`** — single root-level script runs all 4 sector signal generators; output streams live and saves to `generate_all_signals_log.txt` (overwritten each run)
- **`update_all_prices.bat`** — single root-level script runs all 4 sector price updates; output streams live and saves to `update_all_prices_log.txt` (overwritten each run)
- **Consistent page headers** — all 18 sub-pages use `// Stock Universe` label + sector-prefixed h1 (e.g. "AI Metrics", "Biotech News", "Defence Charts") matching the index.html pattern; eliminates generic "Stock Metrics", "Market Heatmap", "Price Charts" etc
- **Charts toolbar layout** — category filter row sits above view/period controls; category buttons styled to match metrics filter-btn spec (10px / 2px letter-spacing / 5px 12px); row only appears in grid view
- **Filter button standard** — all `.filter-btn` and `.cat-btn` across index, news, metrics and charts pages (all 3 sectors) use identical spec: 10px / letter-spacing 2px / padding 5px 12px / hover = accent colour only / active = full fill + bold / tooltip bg `var(--surface2)`; no emoji icons on any filter button
- **Category filter tooltips everywhere** — all filter/category buttons across dashboard, metrics, news, and charts pages (all 3 sectors) have hover tooltip popups; tooltip CSS in each page, data in `CAT_TOOLTIPS` / `CHART_CATS` dicts
- **Financial advice header-note** — `.header-note` bordered strip below the sector switcher on all 28 sector pages; defined once in `shared.css`; all page-specific `.disclaimer` divs consolidated into the header-note with page-tailored caveats (signals: AI-generated warning; metrics: data delay; news: VADER scoring; calculator: YTD methodology)
- **Dynamic dashboard + charts** — `index.html` and `charts.html` across all 3 sectors build content from `prices-data.js` at runtime; adding a stock requires only one entry in `update_prices.py` + one note in `index.html` NOTES dict
- **Heatmap metric persists across sectors** — selected timeframe (1D/1W/1M/YTD/1Y) saved to `localStorage`; switching sectors via the sector switcher keeps the active metric
- **Charts default: Category Grid / 1W / first category** — charts pages open directly on grid view, 1-week timeframe, first category pre-selected per sector
- **Dashboard header hierarchy** — sector name is the large h1; "Stock Universe" is the small monospace label; Biotech h1 split Bio (dark) / tech (blue)
- **shared.js** — `toggleTheme()` and `buildTape()` extracted from 22 inline copies into one shared file; heatmaps use `window._onThemeChange` hook
- **Light/dark mode toggle** — ☾/☀ button in every page's header; light mode default; dark via `html[data-theme="dark"]`; `localStorage` persistence; flash-prevention in `<head>`; all 22 pages (root hub + 3 sectors × 7); heatmap D3 colours CSS-var-driven with re-render on toggle
- **shared.css** — all shared CSS (reset, body, ticker tape, header, nav, footer, container, sector switcher) extracted into a single file loaded by all 21 sector pages; eliminates duplication across sectors
- **Sector switcher** — replaces the fragile back-link; mini sector cards in the header right side; context-aware links (stays on same page type when switching); Stock Hub card; active sector is bright/cyan, others dimmed
