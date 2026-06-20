# Migration plan — collapse to a single local folder

**Status:** ✅ DONE 2026-06-21 — migrated to **Model (A) LIGHT**. Single folder `STOCKSDev/` on `dev`; `main` is remote-only; `STOCKSMain/` clone removed. Cross-device branch `claude/magical-davinci-zYLYI` kept. The plan/prompt below is retained for reference (and for the football-analyser migration).

## Why

Currently two local folders on Google Drive — `STOCKSDev/` (tracks `dev`) and
`STOCKSMain/` (tracks `main`). The local `main` mirror earns its keep less than it
looks (live can be read via the Cloudflare URL, `git show origin/main:path`, or
`git diff origin/main`), and the bot's constant pushes to `main` mean every session
opens with a reconcile. Goal: one clean local folder, less drift.

## Three Stocks-specific gotchas (why this isn't a generic migration)

1. **`dev` is a deployment, not just a branch** — it auto-deploys the preview at
   `dev.stocks-4qw.pages.dev`. Deleting `dev` loses the preview unless replaced by
   Cloudflare per-branch/PR preview deployments.
2. **The price bot commits to `main` directly 3×/day** — any working branch drifts
   behind it; a rebase-on-`main` step is unavoidable.
3. **`claude/magical-davinci-zYLYI`** (cross-device branch) also exists — decide
   keep / sync / delete; don't leave it stale.

Plus: this repo lives on `G:\My Drive` (Google Drive) — **branch-switching in one
folder causes sync churn and file-lock errors**, so avoid checkout-switching flows.

## Two target models

- **(A) LIGHT** — one folder on `dev`, `main` stays remote-only, no feature branches,
  no PRs, ship via `git push origin dev:main`. Drive-friendly, keeps the preview.
  *Recommended for this repo.*
- **(B) GITHUB FLOW** — one folder on `main`, short-lived feature branches + PRs,
  Cloudflare preview deployments on PRs to replace the dev preview. More standard,
  adds CI/review gates, but more branch-switching (Drive churn) and PR ceremony.

## Test first

Run the migration on **football-analyser** first (lower stakes — no bot on main,
simpler deploy) before touching Stocks.

## Paste-ready prompt for the migration session

```
This is the Stocks repo (https://github.com/KobiLDN/Stocks). I want to simplify
my local setup to a single folder. Read AGENTS.md and branches.md first, then help
me migrate safely.

CURRENT SETUP:
- Two local folders on Google Drive: STOCKSDev/ (tracks `dev`) and STOCKSMain/ (tracks `main`)
- `dev` auto-deploys a PREVIEW site to dev.stocks-4qw.pages.dev (Cloudflare Pages)
- `main` is the LIVE site (Cloudflare Pages) — a price bot (github-actions[bot])
  commits to `main` directly 3x/day on weekdays
- A cross-device branch `claude/magical-davinci-zYLYI` also exists
- This repo lives on G:\My Drive (Google Drive) — branch-switching in one folder
  causes sync churn and file-lock errors, so AVOID checkout-switching workflows

THREE THINGS YOU MUST ACCOUNT FOR (the reason this isn't a generic migration):
1. If we drop `dev`, we LOSE the preview deployment. Before deleting `dev`, tell me
   how to preserve a staging/preview look — either keep `dev` as the working branch
   (main stays remote-only), or set up Cloudflare Pages preview deployments per
   branch/PR to replace it. Do not delete `dev` until I've decided.
2. The bot pushes to `main`, so any branch I work on will drift behind it — factor
   the rebase-on-main step into whatever flow you propose.
3. Don't forget `claude/magical-davinci-zYLYI` — tell me whether to keep, sync, or
   delete it; don't silently leave it stale.

WHAT I WANT YOU TO DO:
1. Check the current state of all branches (dev, main, cross-device) and any
   uncommitted work in both folders. Confirm nothing will be lost.
2. Ask me to choose between two target models before changing anything:
     (A) LIGHT: one folder on `dev`, `main` stays remote-only, no feature branches,
         no PRs, ship via `git push origin dev:main`. (Drive-friendly, keeps preview.)
     (B) GITHUB FLOW: one folder on `main`, short-lived feature branches + PRs,
         Cloudflare preview deployments on PRs to replace the dev preview.
3. Once I pick, make sure the surviving branch(es) are fully up to date and nothing
   is lost, then do the cleanup (remove the redundant folder / branch).
4. Update AGENTS.md, branches.md, and .claude/settings.json to match the new model.
5. HARD RULE: never push to `main`/live unless I say "go" or "push to all". Stop at
   `dev` otherwise.
```
