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
G:\My Drive\coding\ai\Stocks\        ← plain container (no .git)
                       ├── STOCKSMain\   ← clone on `main` — the safe copy + what goes live
                       └── STOCKSDev\    ← clone on `dev`  ← all work happens here
                             ├── index.html      ← hub landing page
                             └── AI\             ← AI sector dashboard
```

- **`STOCKSDev` = where all work happens.** Edit here. Break things freely.
- **`STOCKSMain` = the safe copy.** Never edit directly. It is the restore point and the only branch GitHub Pages deploys.
- **GitHub `origin` = the bridge** between the two clones.

### The 3-step workflow — always follow this order

1. **Edit files in `STOCKSDev`** — make changes, commit, `git push origin dev`.
2. **Sync with `STOCKSMain`** — in the MAIN clone: `git fetch origin` then `git merge --ff-only origin/dev`.
3. **Save to GitHub** — from `STOCKSMain`: `git push`. This is what updates the live site.

Never edit in `STOCKSMain`. Never push to `main` until the user has approved the change ("go"). Step 3 (the live push) **requires explicit user approval every time.**

### Safety net — if `STOCKSDev` gets trashed

`main` always has a known-good copy, so dev is disposable:

```
cd STOCKSDev
git fetch origin
git reset --hard origin/main     # discard local mess, back to known-good
```

Or just delete the `STOCKSDev` folder and re-clone — nothing is lost because `main` is the source of truth.

### If `git merge --ff-only` is refused in step 2

Means `dev` and `main` diverged (usually the price bot committed to `main` in between). Fix:

```
cd STOCKSDev
git fetch origin
git rebase origin/main
git push --force-with-lease origin dev
```

Then retry step 2 in `STOCKSMain`.

## After every edit

When you make a change, update these in the same commit:

1. **Version + timestamp** in the relevant `index.html`
   - Bump version by `0.1` (example: `v1 → v1.1`)
   - The `last-updated` span in `AI/index.html` is managed automatically by `update_prices.py` — do not manually change it unless updating structure
2. **`CHANGELOG.md`**
   - Prepend one new table row (immediately under the header) with **date and time** (`YYYY-MM-DD HH:MM BST`), AI Name, **Where** (`Desktop`, `Mobile`, or `Web`), and what changed — **newest first**

## Version scheme

- Project starts at `v1`.
- Each meaningful commit increments minor by `0.1` (v1 → v1.1 → v1.2).
- Reserve `v2` for a major redesign or significant structural overhaul.
- After `v1.9` comes `v1.10`, `v1.11`, etc.

## Sector structure

All sector files live in their own subfolder:

```
STOCKSDev\
├── index.html          ← hub landing page (links to all sectors)
├── AI\                 ← AI Infrastructure sector (48 stocks, 12 categories)
│   ├── index.html
│   ├── update_prices.py
│   └── ...
├── Biotech\            ← Biotech sector (30 stocks, 9 categories)
│   ├── index.html
│   ├── update_prices.py
│   └── ...
└── (future sectors: Defence\, Energy\, Crypto\)
```

When adding a new sector, create its subfolder and keep all sector-specific scripts inside it.

## GitHub Actions

Workflow files must live at the **repo root** (`.github/workflows/`) — GitHub Actions will not find them inside a sector subfolder. All workflow steps that run sector scripts must use `working-directory: AI` (or the relevant sector folder). Git add paths in workflows must include the sector prefix (e.g. `git add AI/prices.json AI/prices-data.js`).

## Sensitive data

- Never commit API keys or secrets.
- `AI/key.txt` and `AI/test_openrouter.py` are gitignored — never commit them.
- The price-updater workflow uses no external secrets — Yahoo Finance via `yfinance` requires no API key.
- The signals workflow uses **one** secret: `OPENROUTER_API_KEY` — see exception below.

## Architectural rule: keyless by default (EXCEPTION: OPENROUTER_API_KEY)

**This project is keyless by default.** Any new feature must work with no-auth/free data sources. Adding a new secret requires an explicit user decision — do **not** silently add one.

Current approved exceptions:
- **`OPENROUTER_API_KEY`** (GitHub Actions secret) — used only by `.github/workflows/generate-signals.yml` to call `deepseek/deepseek-v4-flash` via OpenRouter. Cost: ~$0.004/run.

Everything else remains keyless:
- **News sentiment** → yfinance `.news` + local VADER scoring (no LLM, no Finnhub).
- **Price data** → yfinance (no key).

## Style and scope

- Match the dark theme tokens in `:root` in `AI/index.html` for all sector pages and the hub.
- Keep commits focused to one logical change.
- Keep comments minimal — only add when intent is non-obvious.
- Never force-push `main`.
