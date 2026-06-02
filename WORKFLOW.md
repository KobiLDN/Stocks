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

### If dev and main diverge

Usually caused by GitHub Actions (price bot) committing directly to `main`. Fix:

```
git fetch origin
git rebase origin/main
git push origin dev
```

## Branch hygiene

- All work on `dev`
- `main` only ever receives fast-forward merges from `dev`
- Never commit directly to `main`
- Never force-push `main`
- No feature branches unless user asks
