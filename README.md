# Stocks Hub

A multi-sector stock research platform. Each sector tracks a curated universe of stocks in GBP with live prices, fundamentals, news sentiment, and AI-generated signals.

**Live: [stocks-4qw.pages.dev](https://stocks-4qw.pages.dev/)** &nbsp;·&nbsp; **Dev preview: [dev.stocks-4qw.pages.dev](https://dev.stocks-4qw.pages.dev/)**

## Sectors

| Sector | Status | URL |
|---|---|---|
| AI Infrastructure | Live | [stocks-4qw.pages.dev/AI/](https://stocks-4qw.pages.dev/AI/) |
| Biotech | Live | [stocks-4qw.pages.dev/Biotech/](https://stocks-4qw.pages.dev/Biotech/) |
| Defence | Live | [stocks-4qw.pages.dev/Defence/](https://stocks-4qw.pages.dev/Defence/) |
| Technology | Live | [stocks-4qw.pages.dev/Tech/](https://stocks-4qw.pages.dev/Tech/) |

## Repo structure

```
├── index.html              ← hub landing page
├── shared.css              ← shared stylesheet loaded by all 28 sector pages
├── AI/                     ← AI Infrastructure sector (48 stocks, 12 categories)
│   ├── index.html          ← CANONICAL reference for typography/UI standards
│   ├── AI_update_prices.py
│   ├── AI_generate_signals_local.py
│   └── ...
├── Biotech/                ← Biotech sector (30 stocks, 9 categories)
│   ├── index.html
│   ├── Biotech_update_prices.py
│   ├── Biotech_generate_signals_local.py
│   └── ...
├── Defence/                ← Defence & Aerospace sector (28 stocks, 6 categories)
│   ├── index.html
│   ├── Defence_update_prices.py
│   ├── Defence_generate_signals_local.py
│   └── ...
├── Tech/                   ← Technology sector (31 stocks, 6 categories)
│   ├── index.html
│   ├── Tech_update_prices.py
│   ├── Tech_generate_signals_local.py
│   └── ...
├── .github/workflows/      ← GitHub Actions (must be at repo root)
│   ├── update-prices.yml
│   └── generate-signals.yml
├── AGENTS.md               ← contributor guide (read first)
├── WORKFLOW.md             ← two-clone dev workflow
├── CHANGELOG.md            ← change history
└── FEATURES.md             ← backlog
```

## Development

See [AGENTS.md](AGENTS.md) and [WORKFLOW.md](WORKFLOW.md).
