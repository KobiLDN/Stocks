#!/usr/bin/env python3
"""Move signals refresh info into the rail layout:

1. Header block: relabel "Prices Last Updated"/#data-bar-ts → "Last Refreshed"/#signals-ts
   so renderSignals() populates the timestamp in the Row-1 header block.
2. Remove the in-body .refresh-banner div (and its now-dead CSS).
3. Move the "Auto-refreshed Mon/Wed/Fri …" line to the bottom of the
   "// How signals are generated" section as a .how-refresh-note.
"""
import re, os

root = os.path.dirname(os.path.abspath(__file__))
SECTORS = ['AI', 'Biotech', 'Defence', 'Tech', 'Crypto', 'Energy']

for sector in SECTORS:
    path = os.path.join(root, sector, 'signals.html')
    with open(path, encoding='utf-8') as f:
        c = f.read()
    orig = c

    # 1. Header block → Last Refreshed / #signals-ts
    c = c.replace(
        '<div class="header-block-label">Prices Last Updated</div>\n'
        '  <div class="header-block-value" id="data-bar-ts">—</div>',
        '<div class="header-block-label">Last Refreshed</div>\n'
        '  <div class="header-block-value" id="signals-ts">—</div>',
        1)

    # 2a. Capture the "Auto-refreshed …" inner content, then drop the banner div.
    m = re.search(
        r'  <div class="refresh-banner" id="refresh-banner">\n'
        r'    <span>Last refreshed: <span class="ts" id="signals-ts">—</span></span>\n'
        r'    <span>(?P<auto>.*?)</span>\n'
        r'  </div>\n\n',
        c, flags=re.DOTALL)
    assert m, f'{sector}: refresh-banner not found'
    auto = m.group('auto')
    c = c[:m.start()] + c[m.end():]

    # 2b. Remove the now-dead .refresh-banner CSS block.
    c = re.sub(r'  /\* Refresh banner \*/\n.*?\.refresh-banner code \{.*?\n  \}\n',
               '', c, count=1, flags=re.DOTALL)

    # 3. Add .how-refresh-note CSS (after .how-footer-note span rule).
    c = c.replace(
        '  .how-footer-note span { color: var(--accent2); }\n',
        '  .how-footer-note span { color: var(--accent2); }\n'
        '  .how-refresh-note {\n'
        '    grid-column: 1 / -1;\n'
        '    font-family: \'IBM Plex Mono\', monospace;\n'
        '    font-size: 11px;\n'
        '    color: var(--muted);\n'
        '    line-height: 1.7;\n'
        '    letter-spacing: 0.3px;\n'
        '  }\n'
        '  .how-refresh-note code {\n'
        '    background: var(--bg);\n'
        '    color: var(--text);\n'
        '    padding: 2px 6px;\n'
        '    border: 1px solid var(--border);\n'
        '    font-size: 10px;\n'
        '  }\n',
        1)

    # 3b. Insert the refresh note after the how-footer-note div.
    c, n = re.subn(
        r'(<div class="how-footer-note">.*?</div>)',
        r'\1\n\n      <div class="how-refresh-note">' + auto.replace('\\', '\\\\') + '</div>',
        c, count=1, flags=re.DOTALL)
    assert n == 1, f'{sector}: how-footer-note not found'

    if c != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'{sector}/signals.html: updated')
    else:
        print(f'{sector}/signals.html: NO CHANGE')

print('Done.')
