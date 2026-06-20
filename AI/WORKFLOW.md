# Workflow

> **Superseded.** This repo migrated to a **single-folder** setup on 2026-06-21.
> The old two-clone (`STOCKSMain` + `STOCKSDev`) model described here is retired.

See the canonical docs at the repo root:

- **`../WORKFLOW.md`** — current shipping process (single folder on `dev`, `main` remote-only)
- **`../AGENTS.md`** — repo rules and branch rules
- **`../branches.md`** — branch map and the "push to all" convention
- **`../MIGRATION.md`** — why and how the single-folder migration was done

## TL;DR

```
Stocks/
└── STOCKSDev/    ← the only local folder, works on `dev`
```

1. **Edit** in `STOCKSDev` → commit → `git push origin dev`
2. **Preview** — Cloudflare Pages auto-deploys `dev` → https://dev.stocks-4qw.pages.dev
3. **Go live** — only on explicit "go" / "push to all": `git push origin dev:main`

`main` is remote-only (the live site) — never checked out locally.
