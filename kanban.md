# Stocks — Kanban

## Backlog

- [ ] **Global Mega-Cap Leaders sector** — 50 stocks across 6–7 categories; full 7-page suite + hub card + workflows
  - Big Tech (6): MSFT, AAPL, AMZN, GOOGL, META, NVDA
  - Financials (6): BRK-B, JPM, V, MA, BAC, MS
  - Healthcare (6): LLY, JNJ, UNH, ABBV, NVO, TMO
  - Consumer (7): WMT, COST, KO, PEP, HD, MCD, PG
  - Energy & Industrials (6): XOM, CVX, SHEL, TM, NESN (NSRGY), 2222.SR
  - Tech & Semis (12): AVGO, TSM, ASML, QCOM, ORCL, SAP, CRM, ADBE, CSCO, IBM, ACN, AMD
  - Global & Growth (7): BABA, TCEHY, SSNLF, LVMUY, TSLA, NFLX, PLTR
  - Note: Samsung/Tencent/Saudi Aramco kept in — expect some N/A on return fields
- [ ] **Crypto signals generator** — `Crypto_generate_signals_local.py` + `generate-signals.yml` entry; DeepSeek via OpenRouter; coin-specific prompt context (tokenomics, chain activity, macro BTC cycle)
- [ ] **Verify Crypto YTD cache on live** — confirm GitHub Actions run picks up `ytd_cache.json` and YTD column populates correctly on `stocks-4qw.pages.dev/Crypto/`

### GitHub best-practices (from 2026-06-21 review)

- [ ] **Shared concurrency group across push-workflows** (HIGH) — `update-prices`, `generate-export`, `generate-news-feed`, `generate-signals` each use a *separate* concurrency group, so they collide on `main` (root cause of the rebase-race dance). Give all four the same `concurrency: group: push-to-main` to serialize pushes
- [ ] **Add a LICENSE** (HIGH) — repo is PUBLIC with no license = "all rights reserved" + fully visible. Decide intent: add MIT (open) or flip repo to private
- [ ] **Branch protection on `main`** (HIGH) — add a ruleset blocking force-push + deletion (do NOT require PRs — bot needs direct push). Cheap insurance against accidental history rewrite on the live branch
- [ ] **DRY the workflows with a matrix** (MED) — `update-prices.yml` repeats install+run 6× per sector; collapse to `strategy.matrix` over the 6 sectors; same for signals
- [ ] **`exports/` retention** (MED) — dated JSON+CSV grow unbounded (29 files, 8.7 MB; `.git` 23 MB). Add a keep-last-~30 prune step or move snapshots to a `data` branch
- [ ] **Add Dependabot** (MED) — `.github/dependabot.yml` for `pip` (per-sector `requirements.txt`) + `github-actions`
- [ ] **`[skip ci]` on bot commits** (LOW) — 491 commits/30d, mostly bot; stop bot price/news commits from needlessly triggering other workflows
- [ ] **CI lint gate** (LOW) — tiny workflow on push to validate Python syntax + JSON validity before it reaches live (no gate today)
- [ ] **Reduce dev/main drift** (LOW) — bot only pushes `main`, so `dev` constantly drifts; every session starts with a reconcile

## In Progress

_(nothing active right now)_

## Done (recent)

- [x] **Crypto YTD cache** — `ytd_cache.json` stores Jan 1 USD prices; fetched once per year, reused every daily run; eliminates 34 extra CoinGecko calls and rate-limit cascades that were causing YTD nulls
- [x] **Crypto CoinGecko constants** — `COINGECKO_PRO_URL` + `COINGECKO_DEMO_URL` declared (were referenced but never defined)
- [x] **branches.md** — repo branch map + "check branches.md and push to all" convention documented
- [x] **MDs updated** — Crypto 19→34 coins, Defence 28→29 stocks, schedule 2×→3× daily, URL → Cloudflare Pages, portfolio path corrected
- [x] **SpaceX (SPCX) added to Defence** — Space category; IPO'd 2026-06-12, NasdaqGS; 29 stocks total
- [x] **CoinStats API key wired in** — crypto news fallback; `X-API-KEY` header sent when key present; falls back to unauthenticated public endpoint
- [x] **Crypto AI Tokens category** — 15 coins added (TAO, FET, RNDR, OCEAN, GRT, AGIX, NMR, ALT, AIOZ, ARKM, WLD, NEAR, ICP, KAITO, VIRTUAL); 34 coins total across 7 categories
- [x] **CoinGecko rate-limit fix** — 60s post-failure cooldown; inter-coin sleep 5s→8s; 34/34 CMC ✅
- [x] **cron-job.org external trigger** — 3 cronjobs (08:00, 14:30, 20:30 UTC weekdays) bypassing GitHub's unreliable native scheduler
- [x] **Energy sector** — 20 stocks, 5 categories; full 7-page suite
- [x] **Crypto sector** — 34 coins, 7 categories; CMC + CoinGecko + CoinStats pipeline
- [x] **Tech sector** — 31 stocks, 6 categories; full 7-page suite
- [x] **Defence sector** — 29 stocks, 6 categories; full 7-page suite
- [x] **Biotech sector** — 30 stocks, 9 categories; full 7-page suite
- [x] **AI sector** — 48 stocks, 12 categories; full 7-page suite
