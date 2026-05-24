# Stocks Hub

A multi-sector stock research platform. Each sector tracks a curated universe of stocks in GBP with live prices, fundamentals, news sentiment, and AI-generated signals.

**Live site: [kobildn.github.io/Stocks](https://kobildn.github.io/Stocks/)**

## Sectors

| Sector | Status | URL |
|---|---|---|
| AI Infrastructure | Live | [/Stocks/AI/](https://kobildn.github.io/Stocks/AI/) |
| Defence | Coming Soon | — |
| Biotech | Coming Soon | — |

## Repo structure

```
├── index.html              ← hub landing page
├── AI/                     ← AI sector (48 stocks)
│   ├── index.html
│   ├── update_prices.py
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
