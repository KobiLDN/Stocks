# Stocks Hub

A multi-sector stock research platform. Each sector tracks a curated universe of stocks in GBP with live prices, fundamentals, news sentiment, and AI-generated signals.

**Live: [stocks-4qw.pages.dev](https://stocks-4qw.pages.dev/)** &nbsp;·&nbsp; **Dev preview: [dev.stocks-4qw.pages.dev](https://dev.stocks-4qw.pages.dev/)**

## Sectors

| Sector | Stocks | Status | URL |
|---|---|---|---|
| AI Infrastructure | 48 (12 categories) | Live | [stocks-4qw.pages.dev/AI/](https://stocks-4qw.pages.dev/AI/) |
| Biotech | 30 (9 categories) | Live | [stocks-4qw.pages.dev/Biotech/](https://stocks-4qw.pages.dev/Biotech/) |
| Defence & Aerospace | 29 (6 categories) | Live | [stocks-4qw.pages.dev/Defence/](https://stocks-4qw.pages.dev/Defence/) |
| Technology | 31 (6 categories) | Live | [stocks-4qw.pages.dev/Tech/](https://stocks-4qw.pages.dev/Tech/) |
| Crypto | 34 (7 categories) | Live | [stocks-4qw.pages.dev/Crypto/](https://stocks-4qw.pages.dev/Crypto/) |
| Energy | 20 (5 categories) | Live | [stocks-4qw.pages.dev/Energy/](https://stocks-4qw.pages.dev/Energy/) |

## Repo structure

```
├── index.html              ← hub landing page (sector cards + top 20 signals panel)
├── shared.css              ← shared stylesheet loaded by all sector pages
├── shared.js               ← shared JS (toggleTheme, buildTape)
├── momentum_screener.py    ← cross-sector momentum screener (1Y + YTD thresholds)
├── generate_export.py      ← builds daily JSON/CSV snapshot across all sectors
├── rss.html                ← cross-sector RSS news feed page
├── rss-data.js             ← generated RSS feed data
├── exports/                ← dated market snapshots (JSON + CSV); served via Pages
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
│   └── generate-news-feed.yml ← RSS feed: 3× daily weekdays
├── AGENTS.md               ← contributor guide (read first)
├── WORKFLOW.md             ← dev → main shipping process
├── CHANGELOG.md            ← change history (newest first)
├── FEATURES.md             ← backlog + done
├── branches.md             ← branch map + "push to all" convention
├── kanban.md               ← task board
└── MIGRATION.md            ← single-folder migration plan + reference prompt
```

## Development

See [AGENTS.md](AGENTS.md) and [WORKFLOW.md](WORKFLOW.md).

Single-folder setup — one local clone (`STOCKSDev/`) on `dev`. `main` is the live site (remote-only). Deploy with `git push origin dev:main` on explicit go.
