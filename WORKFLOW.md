# Workflow

## BRANCH RULES

> **ALL changes go to `dev` only. Never push to `main` without explicit user instruction.**

- Every commit gets pushed to `origin/dev`.
- `main` is the live site — only push `dev → main` when the user explicitly says "go live".
- Always ask before pushing to `main`. Never assume.

---

## How it works

All editing happens in the web Claude container. The user reviews changes on the dev preview site. No local clones needed.

### The 3-step workflow

1. **Make changes** — edit files, commit, `git push origin dev`
2. **Preview** — Cloudflare Pages auto-deploys `dev` in ~30–60s → **https://dev.stocks-4qw.pages.dev**
3. **Go live** — user says "go live" → `git push origin dev:main`

`main` = live production site. Always working, always deployable.
`dev` = preview. Break it freely.

### Pushing to live when main has bot commits

The price/signal/RSS bots push directly to `main` several times a day, so `git push origin dev:main` is often rejected with "fetch first." Always use **merge, not rebase**:

```bash
git fetch origin main
git merge origin/main --no-edit   # absorbs bot commits — no history rewrite
git push origin dev:main          # succeeds
git push origin dev               # fast-forward, no force needed
```

**Never use `git rebase origin/main`** — it rewrites `dev`'s history, makes `origin/dev` incompatible, and requires a force-push to sync (which gets blocked by the auto mode classifier).

## Push to all branches

When the user says **"check branches.md and push to all"** (or just **"push to all"**): read `branches.md` and push the current commit to **every branch listed** — `main`, `dev`, and `claude/magical-davinci-zYLYI`. Worktrees are disabled, so there are no `claude/...` worktree branches.

## Branch hygiene

- All work on `dev`
- `main` only ever receives fast-forward merges from `dev`
- Never commit directly to `main`
- Never force-push `main`
- No feature branches unless user asks
