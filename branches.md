# Stocks repo — branches & local folders

Same GitHub remote for all: `https://github.com/KobiLDN/Stocks.git`

## Local folders

Single-folder setup since **2026-06-21** — one local clone only.

| Folder | Branch | Purpose |
|---|---|---|
| `STOCKSDev/` | `dev` | The only local folder. All work happens here. |

`main` is **remote-only** — never checked out locally. Read live via the Cloudflare URL, `git show origin/main:<path>`, or `git diff origin/main`. Deploy with `git push origin dev:main`. (The old `STOCKSMain/` clone was removed in the single-folder migration — see `MIGRATION.md`.)

## Branches

| Branch | Last updated | Purpose |
|---|---|---|
| `main` | Auto (cron, 3×/day on weekdays) | Live site — GitHub Actions pushes prices here, Cloudflare Pages deploys from it |
| `dev` | Manual (local work) | Development branch — merge to main when ready to go live |
| `claude/magical-davinci-zYLYI` | On demand | Cross-device branch — used from work PC or mobile |

## Workflow

```
dev  →  (test locally)  →  merge to main  →  Cloudflare Pages auto-deploys
```

- When the user says **"check branches.md and push to all"** — push to ALL BRANCHES listed above: `main`, `dev`, and `claude/magical-davinci-zYLYI`
- Worktrees are disabled, so no new `claude/...` worktree branches are created
