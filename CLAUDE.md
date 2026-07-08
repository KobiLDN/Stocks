# Claude Code — Project Memory

Rules that apply to every session in this repo. Read before acting.

## Site URL

| Environment | URL |
|---|---|
| Live / production | [stocks-4qw.pages.dev](https://stocks-4qw.pages.dev) |

**After every PR merge:** include a clickable link to the relevant live page. Example: "Live at [stocks-4qw.pages.dev/MegaCap/](https://stocks-4qw.pages.dev/MegaCap/)". Never paste a bare URL — always wrap it in `[text](url)` markdown.

## Branch rules (summary — see AGENTS.md for full detail)

- One branch: `main` — it is the live site
- Code changes go via a feature branch + PR (`fix/description`, `feat/description`)
- Bots push data updates directly to `main` — no PR needed
- Never commit code directly to `main`
- PR merge = goes live (Cloudflare deploys automatically)

## Read order at session start

1. `CLAUDE.md` (this file)
2. `AGENTS.md`
3. `WORKFLOW.md`
4. `CHANGELOG.md` (newest entry first)
5. `FEATURES.md` (backlog)
