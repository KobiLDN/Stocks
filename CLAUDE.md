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

## Portfolio notes channel

The private portfolio project (`KobiLDN/portfolio-private`) reads this site's daily export. The two Claude sessions talk through two files on that repo's `main`:
- **`FROM_PORTFOLIO.md`**: notes from the portfolio session to this one. It covers which export fields the portfolio depends on, its decisions and its format requests. Read it at every session start, before changing anything in `generate_export.py` or the signal format.
- **`FROM_STOCKS.md`**: notes from this session to the portfolio. Add the newest note at the top whenever a change affects the export or the meaning of a signal, before it ships.

This repo is **public**. Never copy holdings, balances or other account data from the portfolio repo into anything here, including issues, commits and docs.

## Read order at session start

1. `CLAUDE.md` (this file)
1b. `FROM_PORTFOLIO.md` on `main` in `KobiLDN/portfolio-private` (see above), if that repo is attached to the session
2. `AGENTS.md`
3. `WORKFLOW.md`
4. `CHANGELOG.md` (newest entry first)
5. `FEATURES.md` (backlog)
