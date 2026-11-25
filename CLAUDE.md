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

## Manager session (owner decision, #120)

The owner's **manager** session (`stocks/cloud`) plans, keeps the owner's Decision Desk and checks both projects each weekday at 08:20 UK. It doesn't write code. This session is the **Stocks builder**:
- **Open issues labelled `decided` are the owner's decisions.** At every session start, list them and work through them, oldest first.
- **Close each one with the PR that does it** (`Closes #N` in the PR body), following the usual branch → PR → checks routine.
- **If a `decided` issue looks wrong or risky, ask the owner in chat before doing it.** Examples: it contradicts an earlier decision, could break the portfolio export, or would expose account data.
- **Tell the manager (#124).** When you finish a `decided` issue, or need the owner's answer on one, schedule a one-off message into the manager session `session_01J3rTmQA4upC5aXGozbqGyJ` (stocks/cloud): a scheduled task with `persistent_session_id`, about 2 minutes ahead. One line only, e.g. `stocks: #122 done (PR #125)` or `stocks: #122 needs an answer, see the issue`; details stay in the issue. The manager checks the work, puts any question on the owner's Decision Desk and replies through the issue.
- **Planning and owner decisions belong to the manager**, not here. Ideas or open questions found while building go to the manager as issue comments, or to the owner in chat, not into new `decided` issues.
- **These rules still apply:** the portfolio notes channel (technical notes only) and no account data in this public repo.

## Read order at session start

1. `CLAUDE.md` (this file)
1b. `FROM_PORTFOLIO.md` on `main` in `KobiLDN/portfolio-private` (see above), if that repo is attached to the session
1c. Open issues labelled `decided` in this repo (see "Manager session")
2. `AGENTS.md`
3. `WORKFLOW.md`
4. `CHANGELOG.md` (newest entry first)
5. `FEATURES.md` (backlog)
