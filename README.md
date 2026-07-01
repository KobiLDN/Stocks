# Stocks Hub

A multi-sector stock research platform. Each sector tracks a curated universe of stocks in USD with live prices, fundamentals, news sentiment, and AI-generated signals.

**Live: [stocks-4qw.pages.dev](https://stocks-4qw.pages.dev/)** &nbsp;·&nbsp; **Dev preview: [dev.stocks-4qw.pages.dev](https://dev.stocks-4qw.pages.dev/)**

## Sectors & Pages

| Sector | Stocks | Status | URL |
|---|---|---|---|
| AI Infrastructure | 48 (12 categories) | Live | [stocks-4qw.pages.dev/AI/](https://stocks-4qw.pages.dev/AI/) |
| Biotech | 30 (9 categories) | Live | [stocks-4qw.pages.dev/Biotech/](https://stocks-4qw.pages.dev/Biotech/) |
| Defence & Aerospace | 29 (6 categories) | Live | [stocks-4qw.pages.dev/Defence/](https://stocks-4qw.pages.dev/Defence/) |
| Technology | 31 (6 categories) | Live | [stocks-4qw.pages.dev/Tech/](https://stocks-4qw.pages.dev/Tech/) |
| Crypto | 33 (7 categories) | Live | [stocks-4qw.pages.dev/Crypto/](https://stocks-4qw.pages.dev/Crypto/) |
| Energy | 20 (5 categories) | Live | [stocks-4qw.pages.dev/Energy/](https://stocks-4qw.pages.dev/Energy/) |
| All Sectors | 192 stocks combined | Live | [stocks-4qw.pages.dev/All/](https://stocks-4qw.pages.dev/All/) |

## Top-level pages

| Page | Description | URL |
|---|---|---|
| Hub | Sector cards + Top 20 signals panel | [stocks-4qw.pages.dev](https://stocks-4qw.pages.dev/) |
| Market | Regime banner, SPY/QQQ/VIX cards + charts, sector heatmap, Leaders/Fallers | [stocks-4qw.pages.dev/market](https://stocks-4qw.pages.dev/market) |
| News Feed | Cross-sector news feed | [stocks-4qw.pages.dev/news](https://stocks-4qw.pages.dev/news) |
| Exports | Daily JSON/CSV snapshots | [stocks-4qw.pages.dev/exports/](https://stocks-4qw.pages.dev/exports/) |

## Repo structure

```
├── index.html              ← hub landing page (sector cards + top 20 signals panel)
├── market.html             ← Market overview page (regime banner, SPY/QQQ/VIX, heatmap)
├── news.html               ← cross-sector news feed page (FT · Reuters · BBC · Guardian · sentiment scored)
├── shared.css              ← shared stylesheet loaded by all sector pages
├── shared.js               ← shared JS (toggleTheme, buildTape, buildNav, buildDashboardHeader, buildDataBar)
├── momentum_screener.py    ← cross-sector momentum screener (1Y + YTD thresholds)
├── update_market.py        ← fetches SPY/QQQ/VIX via yfinance → market-data.js + market.json
├── generate_export.py      ← builds daily JSON/CSV snapshot across all sectors
├── market-data.js          ← generated market data (SPY/QQQ/VIX, regime, timestamps)
├── market.json             ← same data as JSON (consumed by generate_export.py macro block)
├── rss-data.js             ← generated RSS feed data
├── exports/                ← dated market snapshots (JSON + CSV); served via Pages
├── All/                    ← All Sectors suite (192 stocks; aggregates all 6 sectors)
│   ├── index.html          ← combined dashboard with sector filter + search
│   ├── metrics.html        ← combined fundamentals table
│   ├── news.html           ← combined news feed
│   ├── signals.html        ← cross-sector AI signals + combined momentum screener
│   ├── heatmap.html        ← combined heatmap (drawSplit gainers/losers)
│   ├── charts.html         ← 6×3 sector grid (top 3 by market cap, 1W/1Y/5Y)
│   └── calculator.html     ← combined What-If calculator
├── AI/                     ← AI Infrastructure sector (48 stocks, 12 categories)
│   ├── index.html          ← CANONICAL reference for typography/UI standards
│   ├── AI_update_prices.py
│   ├── AI_generate_signals_local.py
│   └── ...
├── Biotech/                ← Biotech sector (30 stocks, 9 categories)
├── Defence/                ← Defence & Aerospace sector (29 stocks, 6 categories)
├── Tech/                   ← Technology sector (31 stocks, 6 categories)
├── Crypto/                 ← Crypto sector (34 coins, 7 categories)
├── Energy/                 ← Energy sector (20 stocks, 5 categories)
├── .github/workflows/
│   ├── update-prices.yml      ← prices: 3× daily weekdays (08:00/14:30/20:30 UTC)
│   ├── generate-signals.yml   ← signals: Mon/Wed/Fri 07:00 UTC via OpenRouter
│   ├── generate-export.yml    ← export: 22:00 UTC weekdays
│   └── generate-news-feed.yml ← News feed: 3× daily weekdays
├── AGENTS.md               ← contributor guide (read first)
├── WORKFLOW.md             ← dev → main shipping process
├── CHANGELOG.md            ← change history (newest first)
├── FEATURES.md             ← backlog + done
├── branches.md             ← branch map + "push to all" convention
└── MIGRATION.md            ← single-folder migration plan + reference prompt
```

## Development

See [AGENTS.md](AGENTS.md) and [WORKFLOW.md](WORKFLOW.md).

Single-folder setup — one local clone (`STOCKSDev/`) on `dev`. `main` is the live site (remote-only). Deploy with `git push origin dev:main` on explicit go.
