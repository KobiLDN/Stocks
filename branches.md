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
| `claude/agitated-elgamal-9e6c49` | 2026-06-14 | Last Claude worktree session (worktrees now disabled) |

## Workflow

```
dev  →  (test locally)  →  merge to main  →  Cloudflare Pages auto-deploys
```

- When the user says **"check branches.md and push to all"** — push to ALL BRANCHES listed above: `main`, `dev`, `claude/magical-davinci-zYLYI`, and any active Claude worktree branch
- Claude worktree branches (`claude/...`) are session-scoped — cherry-pick commits to `dev` when done
