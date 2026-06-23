#!/usr/bin/env python3
"""Consolidate all heatmap page CSS into shared.css.

- Adds one canonical heatmap section to shared.css (based on the clean All/ +
  AI/ rules: integrated toolbar, treemap sections, tooltip, legend).
- Removes the divergent inline <style> block from all 7 heatmap pages.
- Fixes the stray </div> that prematurely closed .container on 5 sector pages.
- Normalises every heatmap .container open tag to <div class="container">.
"""
import re, os

root = os.path.dirname(os.path.abspath(__file__))

HEATMAP_CSS = """\
/* ---- Heatmap pages (toolbar, treemap sections, tooltip) ---- */
.toolbar {
  display: flex; align-items: center; gap: 16px; flex-wrap: nowrap;
  padding: 6px 16px;
  border-top: 1px solid var(--border);
}
.toolbar-label { font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: 2px; color: var(--muted); text-transform: uppercase; white-space: nowrap; }
.metric-group { display: flex; gap: 2px; }
.metric-btn {
  font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase;
  padding: 6px 14px; background: transparent; color: var(--muted); border: 1px solid var(--border); cursor: pointer; transition: all 0.2s;
}
.metric-btn:hover  { color: var(--accent); border-color: var(--accent); }
.metric-btn.active { background: var(--accent); color: var(--bg); border-color: var(--accent); font-weight: 700; }

.size-note { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--muted); white-space: nowrap; }
.size-note em { color: var(--text); font-style: normal; }
.toolbar-ts { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--muted); white-space: nowrap; }
.toolbar-ts span { color: var(--accent); }

.legend { display: flex; align-items: center; gap: 8px; }
.leg-label { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--muted); white-space: nowrap; min-width: 28px; }
.leg-label.r { text-align: right; }
.leg-bar { width: 90px; height: 8px; background: linear-gradient(90deg, var(--red), var(--surface2), var(--green)); border: 1px solid var(--border); flex-shrink: 0; }

.section-hdr { display: flex; align-items: center; gap: 16px; margin: 32px 0 10px; }
.container > .section-hdr:first-child { margin-top: 0; }
.section-hdr-label { font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 3px; color: var(--accent); text-transform: uppercase; white-space: nowrap; }
.section-hdr-line { flex: 1; height: 1px; background: var(--border); }
.section-hdr-count { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--muted); white-space: nowrap; }

.map-wrap { width: 100%; border: 1px solid var(--border); background: var(--surface); overflow: hidden; margin-bottom: 4px; }
.map-wrap svg { display: block; }

#sectors-container { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 700px) { #sectors-container { grid-template-columns: 1fr; } }
.sector-block { margin-bottom: 0; }
.sector-name {
  font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 2px; font-weight: 700;
  color: var(--muted); text-transform: uppercase; padding: 8px 12px;
  background: var(--surface2); border: 1px solid var(--border); border-bottom: none;
  display: flex; align-items: center; gap: 10px;
}
.sector-name .sc { color: var(--muted); font-weight: 400; font-size: 10px; }
.cat-label-text { font-family: 'IBM Plex Mono', monospace; font-size: 10px; font-weight: 700; fill: var(--muted); letter-spacing: 1.5px; pointer-events: none; }

.tooltip { position: fixed; z-index: 500; background: var(--surface2); border: 1px solid var(--accent); padding: 14px 18px; pointer-events: none; min-width: 200px; max-width: 260px; }
.tooltip.hidden { display: none; }
.tt-ticker { font-family: 'IBM Plex Mono', monospace; font-size: 16px; font-weight: 700; color: var(--text); margin-bottom: 2px; }
.tt-company { font-size: 12px; color: var(--muted); margin-bottom: 12px; }
.tt-grid { display: grid; grid-template-columns: 1fr auto; gap: 5px 20px; }
.tt-key { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--muted); letter-spacing: 0.5px; align-self: center; }
.tt-val { font-family: 'IBM Plex Mono', monospace; font-size: 12px; font-weight: 700; text-align: right; }
.tt-val.pos { color: var(--green); }
.tt-val.neg { color: var(--red); }
.tt-val.neu { color: var(--muted); }
.tt-divider { grid-column: 1/-1; height: 1px; background: var(--border); margin: 4px 0; }
.tt-price { font-family: 'IBM Plex Mono', monospace; font-size: 14px; font-weight: 700; color: var(--accent); margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border); }

.empty-state { text-align: center; padding: 60px 24px; color: var(--muted); font-family: 'IBM Plex Mono', monospace; font-size: 13px; line-height: 1.7; border: 1px solid var(--border); }

@media (max-width: 900px) { .legend { display: none; } }
@media (max-width: 600px) { .metric-btn { padding: 5px 10px; font-size: 10px; } .size-note { display: none; } }

"""

# ── 1. Insert into shared.css before the Footer section ───────────────────────
shared_path = os.path.join(root, 'shared.css')
with open(shared_path) as f:
    css = f.read()

if '/* ---- Heatmap pages' in css:
    print('shared.css: heatmap section already present — skipping insert')
else:
    marker = '/* ---- Footer ---- */'
    assert marker in css, 'Footer marker not found in shared.css'
    css = css.replace(marker, HEATMAP_CSS + marker, 1)
    with open(shared_path, 'w') as f:
        f.write(css)
    print('shared.css: heatmap section inserted')

# ── 2-4. Process each heatmap page ────────────────────────────────────────────
ALL_PAGES = [('All', False)] + [(s, True) for s in
             ['AI', 'Biotech', 'Defence', 'Tech', 'Crypto', 'Energy']]

for sector, is_sector in ALL_PAGES:
    path = os.path.join(root, sector, 'heatmap.html')
    with open(path) as f:
        c = f.read()
    orig = c

    # Remove inline <style>...</style> heatmap block (first one in head)
    c, n = re.subn(r'[ \t]*<style>.*?</style>\n', '', c, count=1, flags=re.DOTALL)
    style_removed = n

    # Normalise container open tag (strip inline padding-top etc.)
    c = re.sub(r'<div class="container"[^>]*>', '<div class="container">', c, count=1)

    # Remove stray </div> that prematurely closed .container (sector pages)
    c = c.replace('<div class="container">\n  </div>\n', '<div class="container">\n', 1)

    if c != orig:
        with open(path, 'w') as f:
            f.write(c)
        print(f'{sector}/heatmap.html: updated (style removed={bool(style_removed)})')
    else:
        print(f'{sector}/heatmap.html: NO CHANGE')

print('Done.')
