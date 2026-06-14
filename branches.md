# Stocks repo — branches & local folders

Same GitHub remote for all: `https://github.com/KobiLDN/Stocks.git`

## Local folders

| Folder | Branch | Purpose |
|---|---|---|
| `STOCKSMain/` | `main` | Live read — tracks what's deployed on Cloudflare Pages |
| `STOCKSDev/` | `dev` | Working branch — where changes are made before going live |

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
