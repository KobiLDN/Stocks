#!/usr/bin/env python3
"""Insert static .header-blocks PLU block into all sector HTML files."""
import re, os, glob

BLOCK_TMPL = (
    '{i}<div class="header-blocks">\n'
    '{i}<div class="header-block">\n'
    '{i}<div class="header-block-label">Prices Last Updated</div>\n'
    '{i}<div class="header-block-value" id="data-bar-ts">—</div>\n'
    '{i}</div>\n'
    '{i}</div>\n'
)

SECTORS = ['AI', 'Biotech', 'Defence', 'Tech', 'Crypto', 'Energy']
PAGES   = ['index.html', 'metrics.html', 'signals.html', 'heatmap.html',
           'news.html', 'screener.html', 'sector.html']

root = os.path.dirname(os.path.abspath(__file__))
results = {'updated': [], 'already_done': [], 'no_match': []}

for sector in SECTORS:
    for page in PAGES:
        path = os.path.join(root, sector, page)
        if not os.path.exists(path):
            continue

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'id="data-bar-ts"' in content:
            results['already_done'].append(f'{sector}/{page}')
            continue

        # Find theme-toggle button, capture leading whitespace for indentation
        m = re.search(r'^([ \t]*)<button[^>]*class="theme-toggle"[^>]*>☾</button>',
                      content, re.MULTILINE)
        if not m:
            results['no_match'].append(f'{sector}/{page}')
            continue

        indent = m.group(1)
        block  = BLOCK_TMPL.format(i=indent)
        new    = content[:m.start()] + block + content[m.start():]

        with open(path, 'w', encoding='utf-8') as f:
            f.write(new)
        results['updated'].append(f'{sector}/{page}')

print(f"Updated ({len(results['updated'])}):")
for f in results['updated']:    print(f'  {f}')
print(f"\nAlready done ({len(results['already_done'])}):")
for f in results['already_done']: print(f'  {f}')
print(f"\nNo match ({len(results['no_match'])}):")
for f in results['no_match']:   print(f'  {f}')
