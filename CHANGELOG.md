# Changelog

Columns: `Date · time (BST)`, `AI Name (Tool)`, `Where` (Desktop / Mobile / Web — which Claude client the change was made from), `Changed` (short description with primary file(s) in backticks).

All notable changes to this repository are documented here — **newest first**. Use **BST** for the changelog.

| Date · time (BST) | AI Name | Where | Changed |
|---|---|---|---|
| 2026-05-26 01:55 | Claude Sonnet 4.6 (Claude Code) | Web | **All dashboard columns sortable** — 52-Week Range and Key Angle columns now sortable on both AI and Biotech dashboards (`AI/index.html`, `Biotech/index.html`). |
| 2026-05-26 01:54 | Claude Sonnet 4.6 (Claude Code) | Web | Fix: **Company column sortable** on Biotech and AI metrics tables (`AI/metrics.html`, `Biotech/metrics.html`). |
| 2026-05-26 01:52 | Claude Sonnet 4.6 (Claude Code) | Web | Fix: stale tooltip in Biotech nav — replaced 'AI top 10 picks' with 'Top 10 biotech picks' (`Biotech/signals.html`, `Biotech/news.html`, `Biotech/heatmap.html`, `Biotech/charts.html`, `Biotech/calculator.html`, `Biotech/metrics.html`). |
| 2026-05-26 00:42 | Claude Sonnet 4.6 (Claude Code) | Web | Fix: Biotech signals page h1 read 'AI Signals' → corrected to 'Biotech Signals' (`Biotech/signals.html`). |
| 2026-05-25 13:45 | Claude Sonnet 4.6 (Claude Code) | Web | Added **COAG** (Hemab Therapeutics) to Biotech sector — 30 stocks total (`Biotech/update_prices.py`, `Biotech/index.html`, `Biotech/news.html`). |
| 2026-05-24 21:36 | Claude Sonnet 4.6 (Claude Code) | Web | Built **Biotech sector dashboard** — 29 stocks across 9 categories (large-cap, UK listed, gene editing, genomics, oncology, mRNA, rare disease, metabolic, neuroscience); full suite: metrics, news, signals, heatmap, charts, calculator; prices via GitHub Actions; `Biotech/` subfolder + workflow updated (`Biotech/`, `.github/workflows/update-prices.yml`, `.github/workflows/generate-signals.yml`, `index.html`, `FEATURES.md`). |
| 2026-05-24 16:41 | Claude Sonnet 4.6 (Claude Code) | Web | Heatmap: added prices **last-updated timestamp** to toolbar (`AI/heatmap.html`). |
| 2026-05-24 | Claude Sonnet 4.6 (Claude Code) | Web | **Full migration from KobiLDN/aiSTOCKS** — copied all AI sector files into `AI/`; moved `.github/workflows/` to repo root with `working-directory: AI` on all steps; built hub landing page (`index.html`) with sector cards; added `← All Sectors` back link to all 7 AI pages; added root `.gitignore`; repo docs created (`AGENTS.md`, `WORKFLOW.md`, `CHANGELOG.md`, `FEATURES.md`). v1. |
