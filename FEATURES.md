# Features

## Backlog

- **Global Mega-Cap Leaders sector** — 50 stocks across 6–7 categories; full 7-page suite + hub card + workflows
  - Big Tech (6): MSFT, AAPL, AMZN, GOOGL, META, NVDA
  - Financials (6): BRK-B, JPM, V, MA, BAC, MS
  - Healthcare (6): LLY, JNJ, UNH, ABBV, NVO, TMO
  - Consumer (7): WMT, COST, KO, PEP, HD, MCD, PG
  - Energy & Industrials (6): XOM, CVX, SHEL, TM, NESN (NSRGY), 2222.SR
  - Tech & Semis (12): AVGO, TSM, ASML, QCOM, ORCL, SAP, CRM, ADBE, CSCO, IBM, ACN, AMD
  - Global & Growth (7): BABA, TCEHY, SSNLF, LVMUY, TSLA, NFLX, PLTR
  - Notes: Samsung (SSNLF) + Tencent (TCEHY) + Saudi Aramco (2222.SR) kept in — expect some N/A on return fields; #50 Netflix duplicate replaced with Thermo Fisher (TMO)

## Done

- **Heatmap gainers/losers split + flat colours** — all 6 heatmap pages: "All Stocks" and every By Sector/Category block groups green (gainers) tiles on the left and red (losers) tiles on the right, sized proportionally by count; solid `var(--green)` / `var(--red)` colours, no gradient shading; `header-note` banner aligned to match the blue accent bar and nav content (`shared.css`, all 6 `heatmap.html` files)

- **Price updates 3× daily** — `update-prices.yml` runs at 09:00 BST (1h after UK open), 15:30 BST (1h after US open), 21:30 BST (after US close); weekdays only; $0 cost (yfinance + public repo Actions free tier)

- **Hub Top 20 Signals panel + 1920px layout** — full-width panel above sector cards shows top 20 unique picks across all 6 sectors ranked by confidence (deduplicated by ticker); all 9 columns sortable; last-updated date in page header; sector grid 3-col (3+3); header/main/footer 1920px; responsive 2-col ≤ 1100px; BST timestamps on exports page (`index.html`, `exports/index.html`, `generate_export.py`)

- **T212 MCP server + local portfolio dashboard** — `t212_mcp/server.py` (FastMCP); 4 tools: `get_positions`, `get_account_summary`, `get_orders`, `get_portfolio_vs_signals`; `.claude/settings.json` wires it into Claude Code automatically; `generate_export.py` merges T212 positions into `exports/YYYY-MM-DD-portfolio.json` (gitignored, local only). Container-level `G:\My Drive\coding\ai\Stocks\t212_mcp\portfolio.py` + `run.bat` — fetches live T212 positions, merges with latest STOCKSMain export, writes `snapshot.html` (1920px browser dashboard) + `snapshot.json` + `snapshot.txt`; appends to `portfolio_history.json` each run. Dashboard sections: account cards (incl. T212 P&L + Real GBP P&L with FX explanation); sector allocation bar blocks (equal-width, variable-height, 1D weighted avg above each block in green/red); portfolio value line chart; holdings treemap heatmap (sized by 1D% magnitude, coloured by direction); holdings table (Bought+Current+P&L, sortable); picks table (filterable by sector/signal, pinnable). `TICKER_ALIASES` maps T212 non-standard tickers (e.g. HUTMF→HUT). Key: `KEY_ID:SECRET_KEY` in `.key` outside any git repo

- **Daily export pipeline** — `generate_export.py` builds `exports/YYYY-MM-DD.json+csv` (176 stocks; metrics, what-if £100/£1k/£10k × 5 timeframes, top-3 news + sentiment, AI signals); `exports/manifest.json` tracks all snapshots; `generate-export.yml` runs at 22:00 UTC weekdays; `exports/index.html` shows date dropdown, loads selected snapshot, one-click Copy JSON/CSV; served at `stocks-4qw.pages.dev/exports/`

- **Site max-width 1920px** — `.header-inner`, `.nav-inner`, `.container` in `shared.css` widened from 1600px to 1920px; no layout changes, just allows the content to spread wider on large monitors (`shared.css`)

- **Heatmap text stroke removed** — SVG `stroke`/`stroke-width`/`stroke-linejoin`/`paint-order` attributes removed from ticker and value text on all 5 sector heatmaps; tile border stroke (0.5px) retained (`AI/heatmap.html`, `Biotech/heatmap.html`, `Defence/heatmap.html`, `Tech/heatmap.html`, `Crypto/heatmap.html`)

- **1D / 1W / 1M return columns on metrics** — three sortable columns added between YTD and Beta on all 4 equity metrics pages; data sourced from `change_1d`/`change_1w`/`change_1m` fields in `prices-data.js`; colour-coded like YTD (`AI/metrics.html`, `Biotech/metrics.html`, `Defence/metrics.html`, `Tech/metrics.html`)

- **Energy sector** — 20 stocks across 5 categories (Oil Majors: XOM/CVX/SHEL/BP/TTE/EQNR; E&P/Refining: COP/OXY/EOG/MPC/VLO; Oilfield Services: SLB/HAL/BKR; Utilities: NEE/SSE.L; Clean Energy: ENPH/FSLR/BEPC/DNNGY); full 7-page suite; Energy card added to all 35 existing sector pages; hub card + SECTORS array entry; both GitHub Actions workflows updated (`Energy/`, `index.html`, `.github/workflows/update-prices.yml`, `.github/workflows/generate-signals.yml`)

- **Crypto sector** — 19 coins across 6 categories (Bitcoin; Layer 1: ETH/SOL/BNB/ADA/AVAX; Payments: XRP/XLM/TRX; Emerging: SUI/HBAR/TON/ALGO/MINA; Infra: MATIC/DOT/LINK; Meme: DOGE/PEPE); metrics, news, signals, heatmap, charts, calculator; prices updated twice daily via GitHub Actions
- **AI sector** — 48 stocks across 12 categories; metrics, news, signals, heatmap, charts, calculator; prices updated twice daily via GitHub Actions
- **Biotech sector** — 30 stocks across 9 categories (large-cap, UK listed, gene editing, genomics, oncology, mRNA, rare disease, metabolic, neuroscience); metrics, news, signals, heatmap, charts, calculator; prices updated twice daily via GitHub Actions
- **Technology sector** — 31 stocks across 6 categories (mega-cap, semiconductors, enterprise software, cybersecurity, consumer platforms, hardware/infra); full 7-page suite; prices and signals via GitHub Actions
- **Defence & Aerospace sector** — 28 stocks across 6 categories (US Primes, UK/European, Cyber/Intel, Drones, Space, Weapons/Systems); full 7-page suite; prices and signals via GitHub Actions
- **Hub signals picks** — each sector card on the hub shows the top 5 AI signal picks fetched live from `signals-local.json` + `prices-data.js`; metrics-style full-bleed table (ticker, signal badge, 1D/1W/YTD, confidence); clicking the table navigates to that sector's signals page
- **Sector selector on both workflows** — `workflow_dispatch` dropdown (all / AI / Biotech / Defence / Tech / Crypto) on both `update-prices.yml` and `generate-signals.yml`; lets you refresh a single sector's prices or signals on demand; scheduled runs always run all sectors
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
