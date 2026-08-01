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

## Agora mode (see WORKFLOW.md for full protocol)

When the user says "agora" / "discuss only": deliberation mode. No implementation, no offers to implement. The user relays other AIs' responses (DeepSeek, Cerebras); treat them as proposals to stress-test — trace concrete inputs through their logic. Resolution = spec frozen in a GitHub issue. Implementation starts only when the user explicitly calls the vote; Claude is the sole implementer.

## Bot-code PRs

When a PR touches bot-side Python, run the script on the branch and commit its output so the Cloudflare preview shows real behaviour — see WORKFLOW.md "Bot-code changes".

## Read order at session start

1. `CLAUDE.md` (this file)
2. `AGENTS.md`
3. `WORKFLOW.md`
4. `CHANGELOG.md` (newest entry first)
5. `FEATURES.md` (backlog)
