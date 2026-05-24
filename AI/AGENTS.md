# Agent Guide (Read First)

This file is for any AI or human contributor working in this repo.

## Read order before editing

1. `AGENTS.md` (this file)
2. `WORKFLOW.md` (repo structure + DEV→MAIN→GitHub shipping process)
3. `CHANGELOG.md` (newest entry is first row under the header)
4. `FEATURES.md` (backlog of planned work)

## Repo structure & workflow (READ THIS)

The project lives in a container folder with **two independent clones** (not git worktrees):

```
G:\My Drive\coding\ai\aiStocks\        ← plain container (no .git)
                          ├── aiStocksMAIN\   ← clone on `main` — the safe copy + what goes live
                          └── aiStocksDEV\    ← clone on `dev`  — the workbench
```

- **`aiStocksDEV` = where all work happens.** Edit here. Break things freely.
- **`aiStocksMAIN` = the safe copy.** Never edit directly. It is the restore point and the only branch GitHub Pages deploys.
- **GitHub `origin` = the bridge** between the two clones.

### The 3-step workflow — always follow this order

1. **Edit files in `aiStocksDEV`** — make changes, commit, `git push origin dev`.
2. **Sync with `aiStocksMAIN`** — in the MAIN clone: `git fetch origin` then `git merge --ff-only origin/dev`.
3. **Save to GitHub** — from `aiStocksMAIN`: `git push`. This is what updates the live site.

Never edit in `aiStocksMAIN`. Never push to `main` until the user has approved the change ("go"). Step 3 (the live push) **requires explicit user approval every time.**

### Safety net — if `aiStocksDEV` gets trashed

`main` always has a known-good copy, so dev is disposable:

```
cd aiStocksDEV
git fetch origin
git reset --hard origin/main     # discard local mess, back to known-good
```

Or just delete the `aiStocksDEV` folder and re-clone — nothing is lost because `main` is the source of truth.

### If `git merge --ff-only` is refused in step 2

Means `dev` and `main` diverged (usually the price bot committed to `main` in between). Fix:

```
cd aiStocksDEV
git fetch origin
git rebase origin/main
git push --force-with-lease origin dev
```

Then retry step 2 in `aiStocksMAIN`.

## After every edit

When you make a change, update these in the same commit:

1. **`index.html` version + timestamp**
   - Bump version by `0.1` (example: `v1 → v1.1`)
   - The `last-updated` span is managed automatically by `update_prices.py` — do not manually change it unless updating structure
2. **`CHANGELOG.md`**
   - Prepend one new table row (immediately under the header) with **date and time** (`YYYY-MM-DD HH:MM BST`), AI Name, **Where** (`Desktop` or `Mobile` — which Claude client the change was made from), and what changed — **newest first**
   - The `Where` column was added 2026-05-23. Past entries default to `Desktop`. If you're editing from a mobile Claude client, use `Mobile`.

## Version scheme

- Project starts at `v1`.
- Each meaningful commit increments minor by `0.1` (v1 → v1.1 → v1.2).
- Reserve `v2` for a major redesign or significant structural overhaul.
- After `v1.9` comes `v1.10`, `v1.11`, etc.

## Price updater bot

- `update_prices.py` runs automatically via GitHub Actions **twice daily on weekdays** (13:00 UTC and 21:30 UTC).
- It fetches live prices from Yahoo Finance, converts to GBP, and writes three files: `index.html` (data-* attributes), `prices.json` (JSON snapshot), and `prices-data.js` (`window.PRICES_DATA` global for file:// compatibility).
- It commits and pushes all three files to `main` if prices changed.
- **Do not manually edit price data in `index.html`** — the bot will overwrite it on the next run.
- To add a new stock: add it to the `STOCKS` dict in `update_prices.py` and add the corresponding `<tr>` row in `index.html`. Placeholder prices (`£0`) are fine — the bot fills them on next run.
- The bot relies on `data-ticker` attributes to match rows. Never remove or rename these.
- **Ticker tape** on all pages loads `prices-data.js` via a `<script>` tag and reads `window.PRICES_DATA` directly — works with file:// and HTTP. Falls back to `fetch('prices.json')` if the global isn't set, then to DOM rows on `index.html`. New pages only need the tape HTML, CSS, `<script src="prices-data.js">`, and the shared `buildTape()` JS block.

## ⚠️ prices-data.js deployment gap (READ THIS)

**The committed `prices-data.js` / `prices.json` are only as fresh as the last GitHub Actions run.** Pages like `metrics.html` render entirely from `window.PRICES_DATA` at runtime — they do not embed their own data.

This means: **if you add a new field to the bot output (`update_prices.py` → `write_json()`), the live site will show blank/dashes for that field until the workflow runs on GitHub and regenerates `prices-data.js`.** Running the bot locally only fixes *your* local copy — the committed file on `main` still has the old shape.

**Rule when adding/changing bot output fields:**

1. Add the field to `update_prices.py` (`get_*` + `write_json`).
2. Update the consuming page(s) to read the new field.
3. **Either** run `python update_prices.py` locally and commit the regenerated `prices-data.js` + `prices.json` alongside the code change, **or** explicitly trigger the GitHub workflow (`workflow_dispatch`) immediately after pushing so live data matches the new code.
4. Never push new-field code expecting the live page to "just work" — it won't until the data file is regenerated *on GitHub*.

Symptom of forgetting this: page works locally, all columns blank on `kobildn.github.io`. The fix is always "run the workflow", not a code change.

## Stock row structure

Each `<tr>` row in `index.html` must have these `data-*` attributes for the price updater to work:

```
data-ticker       — Yahoo Finance symbol used as the key
data-cat          — category slug (e.g. "memory", "fibre-optical")
data-exchange     — exchange label shown in UI
data-price-usd    — raw price in native currency (bot updates)
data-price-gbp    — price converted to GBP (bot updates)
data-return       — 1yr return string e.g. "+45%" (bot updates)
data-low-gbp      — 52wk low in GBP (bot updates)
data-high-gbp     — 52wk high in GBP (bot updates)
data-bar-pct      — range bar position 1–99 (bot updates)
data-change-1d    — daily % change e.g. "+1.23%" (bot updates)
data-change-1w    — 1-week % change (bot updates)
data-change-1m    — 1-month % change (bot updates)
data-change-ytd   — year-to-date % change from first trading day of year (bot updates)
```

The bot also rebuilds the price `<td>` on each run, inserting three coloured `.cpill` spans (1D / 1W / 1M) below the price. Do not manually edit the price cell structure — it will be overwritten.

## Adding a new category

1. Add a CSS variable for the colour in `:root` in `index.html`
2. Add a `.filter-btn[data-filter="slug"].active` style
3. Add a `.cat-slug` badge style
4. Add a filter button in the `.filters` div
5. Add the tickers to `STOCKS` in `update_prices.py`
6. Add `<tr>` rows to `index.html` with correct `data-cat` slug
7. The row-count display (`visible-count` span) is updated dynamically by JS — no manual change needed
8. Update the ticker list in the HTML header comment block

## Sensitive data

- Never commit API keys or secrets.
- The price-updater workflow (`update-prices.yml`) uses no external secrets — Yahoo Finance via `yfinance` requires no API key.
- The signals workflow (`generate-signals.yml`) uses **one** secret: `OPENROUTER_API_KEY` — see exception below.

## Architectural rule: keyless by default (DECIDED 2026-05-19 · EXCEPTION 2026-05-23)

**This project is keyless by default.** Any new feature must work with no-auth/free data sources (yfinance, public RSS) and local or CI-native processing. Adding a new secret requires an explicit user decision — do **not** silently add one.

Current approved exceptions:
- **`OPENROUTER_API_KEY`** (GitHub Actions secret) — used only by `generate-signals.yml` to call `deepseek/deepseek-v4-flash` via OpenRouter. Cost: ~$0.004/run. Decision: 2026-05-23 by user.

Everything else remains keyless:
- **News sentiment** → yfinance `.news` + local VADER scoring (no LLM, no Finnhub).
- **Price data** → yfinance (no key).

If a future request seems to need a new cloud API key, do **not** silently add a secret — surface the trade-off and get an explicit approval first.

## Generator scripts (local vs. CI)

The repo has two classes of generator scripts. Filename suffix and workflow indicate which:

| Pattern              | Runs where              | Refreshed how                                | Example                       |
|----------------------|-------------------------|----------------------------------------------|-------------------------------|
| `update_*.py`        | GitHub Actions (CI)     | Cron schedule (e.g. twice daily on weekdays) | `update_prices.py`            |
| `generate_*_local.py`| GitHub Actions **and** user's PC | Cron or `workflow_dispatch`; or run manually | `generate_signals_local.py`   |

`generate_signals_local.py` runs in CI via `generate-signals.yml` (weekly, Mondays 07:00 UTC) using the `OPENROUTER_API_KEY` secret. It can also be run locally using `key.txt` for on-demand refreshes. Output files (`signals-local.json`, `signals-local.js`) are committed to the repo so the live site always has data.

When designing a new feature that needs LLM-quality output: prefer CI-compatible pipelines where possible. If it truly needs local-only infra, document that clearly in the script docstring and this section.

## Style and scope

- Match the dark theme tokens in `:root` in `index.html`.
- Keep commits focused to one logical change.
- Keep comments minimal — only add when intent is non-obvious.
- Never force-push `main`.
