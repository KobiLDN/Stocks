# Trader rules backtest: results (14 Nov 2026)

Research only (branch `research/trader-backtest`, never merged). Script: `research/backtest_rules.py`. Data: 5 years of daily total-return prices from Yahoo, 15 Nov 2021 to 13 Nov 2026, for the 213 universe assets plus SPY.

**Method.** Each rule fires on a day. Entry is the next day's open. The exits are 5, 21 and 63 trading days later. Excess = asset return − SPY return over the same dates. "vs universe" = the rule's median minus the median of picking any asset from the list at random; the 95% range comes from resampling whole stocks.

## Stocks only (crypto excluded), 3 months

| Rule | Trader | Median vs S&P | Beat S&P | vs random pick from list |
|---|---|---|---|---|
| 12-1 momentum, top fifth | academic | **+1.1%** | 51.7% | +1.8 [−0.1, +3.4] |
| Up ≥ 50% over 1 year | the site's current momentum screen | **+1.0%** | 51.8% | +1.7 [+0.2, +3.0] |
| Darvas box + 1.5× volume | Darvas / O'Neil | −0.1% | 49.7% | +0.6 [−0.4, +1.5] |
| New 50-day high | Livermore / Seykota | −0.1% | 49.6% | +0.6 [−0.1, +1.1] |
| Trend template | Minervini | −0.3% | 49.2% | +0.4 [−0.5, +1.3] |
| Above 200-day average | Paul Tudor Jones | −0.4% | 49.1% | +0.3 [−0.2, +0.8] |
| Random pick from the list | baseline | −0.7% | 48.4% | — |

## The same rules by year (3-month median, stocks)

| Rule | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| 12-1 momentum | −6.6 | +1.1 | +3.8 | +6.9 | −7.1 |
| Up ≥ 50% / 1y | −4.3 | +4.2 | +0.5 | +5.5 | −5.0 |
| Minervini | −6.3 | +1.2 | −0.3 | +0.1 | −3.6 |
| Random pick | −0.2 | −0.9 | −1.2 | +1.8 | −3.7 |

## Live AI picks vs a random pick from the same list, same months (stocks)

| Horizon | Random pick | AI picks |
|---|---|---|
| 1 month | −1.3% median, beat 46% | −0.4% median, beat 48% |
| 3 months | −3.3% median, beat 43% | −0.2% median, beat 49% |

## Caveats
- **Survivorship bias.** The list was chosen in 2026 and includes stocks known to have done well, which flatters every rule over 5 years.
- **No costs, tax or slippage.**
- **Overlapping signals** mean the effective sample is much smaller than the counts.
- **Price-only rules.** The earnings and value rules need #87.
