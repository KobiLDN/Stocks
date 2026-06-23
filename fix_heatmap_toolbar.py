#!/usr/bin/env python3
"""Fix .toolbar placement in sector heatmap pages.
Target state (matching AI/heatmap.html): toolbar inside <header>, right after </nav>.

Two broken states exist:
  A) Biotech/Tech/Crypto: complete toolbar is inside .page-main>.container
  B) Defence/Energy:      toolbar split — first half unclosed in header,
                          size-note/toolbar-ts/legend orphaned in container
"""
import re, os

TOOLBAR = """\
  <div class="toolbar">
    <span class="toolbar-label">Colour by</span>
    <div class="metric-group" id="metric-group">
      <button class="metric-btn active" data-metric="1d">1D</button>
      <button class="metric-btn" data-metric="1w">1W</button>
      <button class="metric-btn" data-metric="1m">1M</button>
      <button class="metric-btn" data-metric="ytd">YTD</button>
      <button class="metric-btn" data-metric="1y">1Y</button>
    </div>
    <span class="size-note">Size = <em id="size-label">|1D %|</em></span>
    <span class="toolbar-ts">Prices: <span id="heatmap-ts">—</span></span>
    <div class="legend">
      <span class="leg-label r" id="leg-neg">−5%</span>
      <div class="leg-bar"></div>
      <span class="leg-label" id="leg-pos">+5%</span>
    </div>
  </div>
"""

root = os.path.dirname(os.path.abspath(__file__))

def fix_type_a(path):
    """Toolbar complete but in container — move it into header after </nav>."""
    with open(path) as f: c = f.read()

    # Remove toolbar (with optional comment) from container
    c = re.sub(
        r'(?:  <!-- Sticky toolbar -->\n)?  <div class="toolbar">.*?  </div>\n',
        '', c, count=1, flags=re.DOTALL
    )
    # Insert after </nav>\n</header>
    c = c.replace('  </nav>\n</header>', '  </nav>\n' + TOOLBAR + '</header>', 1)

    with open(path, 'w') as f: f.write(c)
    print(f'  Fixed (type A): {os.path.relpath(path, root)}')

def fix_type_b(path):
    """Toolbar split: partial in header (unclosed), rest orphaned in container."""
    with open(path) as f: c = f.read()

    # Remove partial toolbar (opened but unclosed) from header
    c = re.sub(
        r'\n\n  <div class="toolbar">\n    <span class="toolbar-label">Colour by</span>\n'
        r'    <div class="metric-group" id="metric-group">.*?    </div>\n</header>',
        '\n' + TOOLBAR + '</header>',
        c, count=1, flags=re.DOTALL
    )
    # Remove orphaned size-note/toolbar-ts/legend + stray </div> from container start
    c = re.sub(
        r'(<div class="container">)\n\n    <span class="size-note">.*?  </div>\n',
        r'\1\n',
        c, count=1, flags=re.DOTALL
    )

    with open(path, 'w') as f: f.write(c)
    print(f'  Fixed (type B): {os.path.relpath(path, root)}')

# Type A: toolbar fully inside container
for sector in ['Biotech', 'Tech', 'Crypto']:
    fix_type_a(os.path.join(root, sector, 'heatmap.html'))

# Type B: toolbar split across header/container
for sector in ['Defence', 'Energy']:
    fix_type_b(os.path.join(root, sector, 'heatmap.html'))

print('Done.')
