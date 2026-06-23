#!/usr/bin/env python3
"""
Transform sector HTML pages from old layout (sector-switcher cards) to new rail layout.
Uses AI sector pages as reference - they're already transformed.
"""

import re
import os
import sys

SECTORS_TO_PROCESS = ['Biotech', 'Defence', 'Tech', 'Crypto', 'Energy']
PAGES = ['index', 'metrics', 'news', 'signals', 'heatmap', 'charts', 'calculator']

# Pill definitions: (sector_key, icon, pill_name, badge)
# sector_key=None means fixed href
PILL_ORDER = [
    (None,      '⊞', 'Stock Hub',   None,   '../index.html'),
    ('All',     '🌐', 'All Sectors', 'Live', None),
    ('AI',      '🤖', 'AI Infra',    'Live', None),
    ('Biotech', '🧬', 'Biotech',     'Live', None),
    ('Defence', '🛡️', 'Defence',     'Live', None),
    ('Tech',    '💻', 'Technology',  'Live', None),
    ('Crypto',  '₿',  'Crypto',      'Live', None),
    ('Energy',  '⚡', 'Energy',      'Live', None),
    (None,      '📰', 'RSS Feed',    None,   '../rss.html'),
]

SECTOR_DIR = {
    'All': 'All', 'AI': 'AI', 'Biotech': 'Biotech',
    'Defence': 'Defence', 'Tech': 'Tech', 'Crypto': 'Crypto', 'Energy': 'Energy',
}


def build_left_rail(sector, page):
    lines = ['<div class="left-rail">']
    for key, icon, name, badge, fixed_href in PILL_ORDER:
        if fixed_href:
            href = fixed_href
        elif key == sector:
            href = f'{page}.html'
        else:
            href = f'../{SECTOR_DIR[key]}/{page}.html'
        is_active = (key == sector)
        cls = 'sector-pill active' if is_active else 'sector-pill'
        badge_html = f'<span class="sector-pill-badge">{badge}</span>' if badge else ''
        lines.append(f'<a class="{cls}" href="{href}">'
                     f'<span class="sector-pill-icon">{icon}</span>'
                     f'<span class="sector-pill-name">{name}</span>'
                     f'{badge_html}</a>')
    lines.append('</div>')
    return '\n'.join(lines)


def extract_h1(html):
    m = re.search(r'(<h1[^>]*>.*?</h1>)', html, re.DOTALL)
    return m.group(1) if m else '<h1>Unknown</h1>'


def extract_header_sub(html):
    """Return the current header-sub content."""
    m = re.search(r'<div class="header-sub">(.*?)</div>', html, re.DOTALL)
    return m.group(1).strip() if m else ''


def extract_nav_links(html):
    """Extract nav-link elements, stripping the nav-inner wrapper."""
    # Find content between <nav> and </nav>
    m = re.search(r'<nav>(.*?)</nav>', html, re.DOTALL)
    if not m:
        return ''
    nav_content = m.group(1)
    # Strip nav-inner wrapper
    inner = re.search(r'<div class="nav-inner">(.*?)</div>', nav_content, re.DOTALL)
    if inner:
        return inner.group(1)
    return nav_content


def extract_theme_toggle(html):
    """Extract theme toggle button from sector-switcher."""
    m = re.search(r'(<button[^>]*class="theme-toggle"[^>]*>.*?</button>)', html, re.DOTALL)
    return m.group(1) if m else '<button aria-label="Toggle theme" class="theme-toggle" id="theme-toggle" onclick="toggleTheme()">☾</button>'


def find_controls_between_nav_and_container(html):
    """Find controls (filter-bar, toolbar) between </nav> and <div class="container">."""
    # Pattern: after </nav> (and optional whitespace), a div before <div class="container">
    m = re.search(
        r'</nav>\s*\n(.*?)(?=<div class="container")',
        html,
        re.DOTALL
    )
    if not m:
        return ''
    block = m.group(1).strip()
    if not block:
        return ''
    # Only return if it looks like a controls element
    if 'filter-bar' in block or 'toolbar' in block or 'chart-controls' in block:
        return block
    return ''


def find_controls_at_container_start(html):
    """Find filter-bar or toolbar as first element(s) inside container."""
    # Find content right after <div class="container"> (possibly with style attr)
    m = re.search(
        r'<div class="container"[^>]*>\s*\n((?:\s*<div class="(?:filter-bar|toolbar|news-controls)[^"]*"[^>]*>.*?</div>\s*\n)+)',
        html,
        re.DOTALL
    )
    if m:
        return m.group(1).strip()
    return ''


def remove_margin_bottom_from_filter_bar_css(html):
    """Remove margin-bottom: 16px from .filter-bar CSS rule."""
    # Pattern: .filter-bar { ... margin-bottom: 16px; ... }
    html = re.sub(
        r'(\.filter-bar\s*\{[^}]*?)(\s*margin-bottom:\s*16px;)([^}]*\})',
        r'\1\3',
        html
    )
    return html


def transform_file(filepath, sector, page):
    """Transform a single HTML file to rail layout."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Already transformed?
    if 'data-layout="rail"' in content:
        print(f'  SKIP (already done): {os.path.basename(filepath)}')
        return False

    original = content

    # 1. Add data-layout to body tag
    content = re.sub(r'<body>', '<body data-layout="rail">', content, count=1)

    # 2. Remove margin-bottom from filter-bar CSS
    content = remove_margin_bottom_from_filter_bar_css(content)

    # 3. Extract components from old layout
    h1 = extract_h1(content)
    header_sub_old = extract_header_sub(content)
    nav_links = extract_nav_links(content)
    theme_toggle = extract_theme_toggle(content)

    # Determine new header-sub
    if page in ('index', 'metrics'):
        new_header_sub = '<span id="stock-count">—</span> stocks · v1 · <span id="last-updated">—</span>'
    else:
        new_header_sub = header_sub_old

    # 4. Find controls to put in header Row 3
    controls_between = find_controls_between_nav_and_container(content)

    # 5. Build new header
    nav_links_stripped = nav_links.strip()
    if controls_between:
        controls_row = '\n' + controls_between
    else:
        controls_row = ''

    new_header = f'''<header>
  <div class="header-inner">
  <div class="header-left">
    <div class="header-label">// Market Intelligence</div>
    {h1}
    <div class="header-sub">{new_header_sub}</div>
  </div>
  {theme_toggle}
  </div>
  <nav>
{nav_links_stripped}
  </nav>{controls_row}
</header>'''

    # 6. Replace old header + nav + [controls_between] region
    # Find start of <header> and end of either controls or </nav>
    # We replace: <header>...</header>\n<nav>...</nav>\n[controls_between]
    # Use a broad pattern to find the entire old region

    if controls_between:
        # Need to remove: <header>...</header>, <nav>...</nav>, and the controls block
        # Find the end of the controls block
        old_region_pattern = re.compile(
            r'<header>.*?</header>\s*\n<nav>.*?</nav>\s*\n' + re.escape(controls_between.split('\n')[0]),
            re.DOTALL
        )
        # Simpler: find from <header> to the end of the controls block
        # The controls block ends just before <div class="container">
        old_region_pattern = re.compile(
            r'(<header>.*?</header>\s*\n<nav>.*?</nav>\s*\n.*?)(?=<div class="container")',
            re.DOTALL
        )
        m = old_region_pattern.search(content)
        if m:
            content = content[:m.start()] + new_header + '\n\n' + content[m.end():]
        else:
            print(f'  WARNING: Could not find old header+nav+controls region in {filepath}')
            return False
    else:
        # Replace header + nav block (no controls between them)
        old_region_pattern = re.compile(
            r'<header>.*?</header>\s*\n<nav>.*?</nav>',
            re.DOTALL
        )
        content = old_region_pattern.sub(new_header, content, count=1)

    # 7. Build left rail
    left_rail = build_left_rail(sector, page)

    # 8. Find container and its first-child controls (for index/metrics/news/heatmap)
    # and remove them from container if they exist there
    # For pages where controls are NOT between nav and container, they may be inside container
    if not controls_between and page in ('index', 'metrics', 'news', 'heatmap'):
        # Try to find filter-bar as first child of container
        # and move it to header
        container_controls_pattern = re.compile(
            r'(<div class="container"[^>]*>\s*\n)'
            r'((?:\s*<div class="(?:filter-bar|toolbar)[^"]*"[^>]*>.*?</div>\s*\n)+)',
            re.DOTALL
        )
        cm = container_controls_pattern.search(content)
        if cm:
            container_start = cm.group(1)
            container_controls = cm.group(2).strip()
            # Remove from container
            content = content[:cm.start()] + container_start + content[cm.end():]
            # Add to header (before </header>)
            new_header_with_controls = new_header.replace('</header>', f'\n  {container_controls}\n</header>')
            # Replace the header we just added with the updated one
            content = content.replace(new_header, new_header_with_controls, 1)

    # 9. Insert page-body, left-rail, page-main after </header>
    page_body_html = f'''
<div class="page-body">
{left_rail}
<div class="page-main">'''

    content = content.replace('</header>\n\n<div class="container"',
                               '</header>\n' + page_body_html + '\n<div class="container"',
                               1)
    # Also try without double newline
    if page_body_html not in content and '<div class="page-body">' not in content:
        content = content.replace('</header>\n<div class="container"',
                                   '</header>\n' + page_body_html + '\n<div class="container"',
                                   1)
    # Also try with whitespace variations
    if '<div class="page-body">' not in content:
        content = re.sub(
            r'(</header>)\s*\n(\s*<div class="container")',
            r'\1\n' + page_body_html + r'\n\2',
            content,
            count=1
        )

    # 10. Add closing divs before </body>
    if '</div><!-- /.page-main -->' not in content:
        content = content.replace(
            '\n</body>',
            '\n</div><!-- /.page-main -->\n</div><!-- /.page-body -->\n</body>'
        )

    # 11. Add JS stock-count/last-updated for index/metrics pages
    if page in ('index', 'metrics') and 'stock-count' not in content[content.find('<script'):]:
        # Find the main build function (buildTable, buildMetrics, etc.)
        # and add the stock-count update after it processes stocks
        js_injection = '''  // Update header counts from prices-data
  const sc = document.getElementById('stock-count');
  if (sc) sc.textContent = stocks.length;
  if (window.PRICES_DATA) {
    const lu = document.getElementById('last-updated');
    if (lu) lu.textContent = window.PRICES_DATA.updated || '—';
  }'''
        # Find the closing of the main build function
        for fn_name in ('buildTable', 'buildMetrics'):
            fn_end_pattern = re.compile(
                rf'(function {fn_name}\([^)]*\).*?)(^\}})',
                re.DOTALL | re.MULTILINE
            )
            fm = fn_end_pattern.search(content)
            if fm:
                # Add before the last } of the function
                insert_pos = fm.end(2)
                content = content[:fm.start(2)] + js_injection + '\n}\n' + content[fm.end(2)+1:]
                break

    if content == original:
        print(f'  WARNING: No changes made to {filepath}')
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'  OK: {os.path.basename(filepath)}')
    return True


def main():
    repo = os.path.dirname(os.path.abspath(__file__))
    sectors = sys.argv[1:] if len(sys.argv) > 1 else SECTORS_TO_PROCESS

    for sector in sectors:
        sector_dir = os.path.join(repo, sector)
        if not os.path.isdir(sector_dir):
            print(f'SKIP (no dir): {sector}')
            continue
        print(f'\n=== {sector} ===')
        for page in PAGES:
            filepath = os.path.join(sector_dir, f'{page}.html')
            if not os.path.exists(filepath):
                print(f'  MISSING: {page}.html')
                continue
            transform_file(filepath, sector, page)

    print('\nDone.')


if __name__ == '__main__':
    main()
