# Claude Code — Project Memory

Rules that apply to every session in this repo. Read before acting.

## Site URLs — always use clickable markdown links

| Environment | URL |
|---|---|
| Dev preview | [dev.stocks-4qw.pages.dev](https://dev.stocks-4qw.pages.dev) |
| Live / production | [stocks-4qw.pages.dev](https://stocks-4qw.pages.dev) |

**After every push to `dev`:** include a clickable link to the relevant page on the dev preview so the user can jump straight to it. Example: "Preview at [dev.stocks-4qw.pages.dev/MegaCap/](https://dev.stocks-4qw.pages.dev/MegaCap/)". Never paste a bare URL — always wrap it in `[text](url)` markdown.

## Branch rules (summary — see AGENTS.md for full detail)

- All changes → `dev` only
- Never push `main` without explicit "go live" / "push to live" from the user
- Always ask before pushing to `main`

## Read order at session start

1. `CLAUDE.md` (this file)
2. `AGENTS.md`
3. `WORKFLOW.md`
4. `CHANGELOG.md` (newest entry first)
5. `FEATURES.md` (backlog)
