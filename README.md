# Stocks Hub

A stock research site: about 840 stocks and coins across the US, UK and Europe, with live prices,
fundamentals, headlines, AI picks that are scored against the S&P 500 and against picking at random,
and a Situations page for unresolved events that could move a stock a lot.

**Live: [stocks-4qw.pages.dev](https://stocks-4qw.pages.dev/)**

## What's on the site

**Markets** (each with Dashboard, Metrics, News, Signals, Heatmap, Charts and What-If pages)

| Market | Stocks | URL |
|---|---|---|
| S&P 500 | 503 | [markets/sp500/](https://stocks-4qw.pages.dev/markets/sp500/) |
| Nasdaq-100 | 101 | [markets/nasdaq100/](https://stocks-4qw.pages.dev/markets/nasdaq100/) |
| FTSE 100 | 100 | [markets/ftse100/](https://stocks-4qw.pages.dev/markets/ftse100/) |
| Europe (Euro Stoxx 50, DAX, CAC 40, SMI; index filter) | 117 | [markets/europe/](https://stocks-4qw.pages.dev/markets/europe/) |
| Crypto | 32 coins | [Crypto/](https://stocks-4qw.pages.dev/Crypto/) |

**Sectors:** the 11 standard sectors (Technology, Health Care, Financials, …) at `sectors/<slug>/`,
same 7 page types. **Themes:** AI and Defence have their own folders; Biotech, Energy, Mega-Cap and Tech
are filters on the All pages (their old URLs redirect there).

**All Stocks** ([All/](https://stocks-4qw.pages.dev/All/)): every stock in one place, with market, sector,
theme and "on Trading 212" filters kept in the URL.

**Other pages**

| Page | What | URL |
|---|---|---|
| Stock Hub | Market overview, group heatmap, top picks | [stocks-4qw.pages.dev](https://stocks-4qw.pages.dev/) |
| Situations | Unresolved events with the AI's odds of each outcome; scored after 30 days | [situations.html](https://stocks-4qw.pages.dev/situations.html) |
| Track Record | Every pick scored at 1 week / 1 month / 3 months vs the S&P 500, in £, vs local indexes, and each AI run vs random | [track-record.html](https://stocks-4qw.pages.dev/track-record.html) |
| News Feed | Business news (FT, Reuters, BBC, Guardian), sentiment scored | [news.html](https://stocks-4qw.pages.dev/news.html) |
| Exports | Daily JSON/CSV snapshot (one row per stock), read by the private portfolio project | [exports/](https://stocks-4qw.pages.dev/exports/) |
| Health | Freshness of every data stream (200 ok / 503 stale) | [/health](https://stocks-4qw.pages.dev/health) |

## How it works

- **`universe.yaml`** is the master list: every stock with its index memberships, ISIN, currency, official
  sector, industry and "on T212" flag. `index_refresh.py` updates the index lists from Wikipedia each quarter.
- **Bots** on GitHub Actions, started by cron-job.org (London time):
  - prices 07:30 / 15:30 / 20:30 weekdays (`update-prices.yml`: the theme folders + `update_group_prices.py`
    for every market and sector group, with headlines);
  - Situations after each price run (`generate-situations.yml`);
  - AI picks Mon / Wed / Fri 08:00 (`generate-signals.yml`: 15 runs — 11 sectors, FTSE 100, AI, Defence,
    Crypto; S&P 500, Nasdaq-100 and Europe pages show the sector runs' picks);
  - news feed, daily export 21:30, history + track record after the export.
- **History** (Cloudflare D1, `history/`): prices, every pick and the list each run chose from, so the track
  record is point-in-time.
- **Pages** are static files on Cloudflare Pages. Repeated pages are generated from templates by
  `site/build.py` (CI fails if a generated page is out of date); a page check loads every page at desktop and
  phone size and enforces a 2-second phone speed limit.

## Development

Read [CLAUDE.md](CLAUDE.md), [AGENTS.md](AGENTS.md) (how each part works), [WORKFLOW.md](WORKFLOW.md)
(branch → PR → main), [CHANGELOG.md](CHANGELOG.md) and [FEATURES.md](FEATURES.md) (what's next).

Everything runs in the cloud: code changes go on a short-lived branch + PR; merging to `main` is going live.

## License

All rights reserved — see [LICENSE](LICENSE). This is a proprietary project, not open source.
