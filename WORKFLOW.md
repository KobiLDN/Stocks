# Workflow

## BRANCH RULES

> **There is one branch: `main`. It is the live site.**

- Bots (price updates, news, signals, exports) push directly to `main`.
- Code changes go via a short-lived feature branch + PR — never directly to `main`.
- `main` is always deployable. Do not commit broken code.

---

## How it works

All editing happens in the web Claude container. Changes are reviewed via Cloudflare Pages PR preview before merging.

### The 3-step workflow for code changes

1. **Branch** — create a short-lived branch from `main`: `git checkout -b fix/description`
2. **Make changes** — commit and push the branch: `git push -u origin fix/description`
3. **PR** — open a pull request → Cloudflare builds a preview URL automatically → user reviews → merges → live

Feature branches are deleted after the PR merges. Never re-use them.

### Bots

Price updates, news feed, signals, and exports push directly to `main` via GitHub Actions. No PR needed — these are automated data refreshes, not code changes.

### Naming branches

Use a short `type/description` slug:

| Type | Example |
|---|---|
| Fix | `fix/coingecko-links` |
| Feature | `feat/crypto-signals` |
| Docs | `docs/workflow-update` |
| Refactor | `refactor/nav-cleanup` |

## After every code change

Update these in the same commit (or a final commit before opening the PR):

1. **`CHANGELOG.md`** — prepend one row (newest first): date (BST), AI Name, Where, what changed
2. **`FEATURES.md`** — move completed item from Backlog → Done, or add new Done entry

## Going live

Merging the PR is going live. Cloudflare Pages deploys `main` automatically in ~30–60s after merge.

Never force-push `main`.
