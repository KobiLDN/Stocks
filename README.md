# Stocks Hub

A multi-sector stock research platform. Each sector tracks a curated universe of stocks in GBP with live prices, fundamentals, news sentiment, and AI-generated signals.

**Live site: [kobildn.github.io/Stocks](https://kobildn.github.io/Stocks/)**

## Sectors

| Sector | Status | URL |
|---|---|---|
| AI Infrastructure | Live | [/Stocks/AI/](https://kobildn.github.io/Stocks/AI/) |
| Biotech | Live | [/Stocks/Biotech/](https://kobildn.github.io/Stocks/Biotech/) |
| Defence | Live | [/Stocks/Defence/](https://kobildn.github.io/Stocks/Defence/) |
| Technology | Live | [/Stocks/Tech/](https://kobildn.github.io/Stocks/Tech/) |

## Repo structure

```
├── index.html              ← hub landing page
├── shared.css              ← shared stylesheet loaded by all 21 sector pages
├── AI/                     ← AI Infrastructure sector (48 stocks, 12 categories)
│   ├── index.html          ← CANONICAL reference for typography/UI standards
│   ├── AI_update_prices.py
│   ├── generate_signals_local.py
│   └── ...
├── Biotech/                ← Biotech sector (30 stocks, 9 categories)
│   ├── index.html
│   ├── Biotech_update_prices.py
│   ├── generate_signals_local.py
│   └── ...
├── Defence/                ← Defence & Aerospace sector (28 stocks, 6 categories)
│   ├── index.html
│   ├── Defence_update_prices.py
│   ├── generate_signals_local.py
│   └── ...
├── Tech/                   ← Technology sector (31 stocks, 6 categories)
│   ├── index.html
│   ├── Tech_update_prices.py
│   ├── generate_signals_local.py
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
