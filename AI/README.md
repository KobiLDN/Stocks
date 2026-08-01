# AI Infrastructure Stock Dashboard

Tracks 48 AI infrastructure stocks in USD with live prices, fundamentals, news sentiment, and AI-generated signals.

**Live: [stocks-4qw.pages.dev/AI/](https://stocks-4qw.pages.dev/AI/)**

## Pages

| Page | Description |
|---|---|
| Dashboard | Live prices, 52-week range, momentum pills (1D/1W/1M/YTD/1Y) for all 48 stocks |
| Metrics | Market cap, P/E, beta, dividend yield, short interest, analyst ratings |
| News | Headlines across all 48 stocks with VADER sentiment scoring |
| Signals | AI top 10 ranked picks with confidence, rationale, and driver chips |
| Heatmap | D3 treemap — tile size = % move, colour = direction |
| Charts | TradingView embeds, single-stock and category grid views |
| What-If | Jan 2026 investment simulator ($100 / $1k / $10k per stock) |

## Stocks — 48 across 12 categories

| Category | Tickers |
|---|---|
| Memory / Storage | SNDK, WDC, 285A, MU, STX, MRVL, PSTG |
| Nuclear Operators | RR., CEG, VST, TLN, BEP |
| SMR Builders | GEV, BWXT, SMR, OKLO, NNE |
| Uranium | CCJ, UEC, LEU |
| Power Infrastructure | VRT, ETN, POWL |
| Data Centres | EQIX, DLR, SMCI |
| Hyperscalers | MSFT, GOOGL, AMZN, META |
| AI Compute | NVDA, AMD, INTC, AVGO, QCOM, ARM |
| Fibre / Optical | COHR, LITE, AAOI, FN |
| DSP / Semi | MTSI, SMTC, CRDO, MXL |
| Test Equipment | KEYS, VIAV |
| Materials | AXTI |

## Automated updates

- **Prices** — GitHub Actions three times daily on weekdays (08:00, 14:30, 20:30 UTC) via `yfinance`. Writes `index.html`, `prices.json`, `prices-data.js`.
- **Signals** — GitHub Actions weekly (Mondays 07:00 UTC) via OpenRouter (`deepseek/deepseek-v4-flash`). Writes `signals-local.json`, `signals-local.js`. Uses `OPENROUTER_API_KEY` repository secret.

## Shared stylesheet

All AI pages load `../shared.css` for shared styles (reset, body, ticker tape, header, nav, footer, sector switcher). Page-specific CSS lives in each page's own `<style>` block. Do not duplicate shared rules in page styles.

## Local development

All work happens in the `STOCKSDev` clone. See [../AGENTS.md](../AGENTS.md) and [../WORKFLOW.md](../WORKFLOW.md).

To run the price updater locally:
```
cd AI
python AI_update_prices.py
```

To run signal generation locally (requires `key.txt` with your OpenRouter key in the `AI/` folder):
```
cd AI
python AI_generate_signals_local.py
```

## Notes

- All prices displayed in USD. GBP/JPY-listed stocks converted via live FX rates (`price_usd = price_gbp * fx_gbp_usd`).
- Tokyo stock 285A (Kioxia) and LSE stock RR. (Rolls-Royce) go through an extra GBP bridge conversion — same formula, no special-case prefix needed.
- `prices-data.js` exposes `window.PRICES_DATA` so all pages work via `file://` without a server.
