#!/usr/bin/env python3
"""Rebuild rss.html body into the rail layout (header rows + left rail + page-main)."""

path = 'rss.html'
with open(path) as f:
    c = f.read()

start = c.index('<body>')
end   = c.index('</footer>') + len('</footer>')

NEW = '''<body data-layout="rail">

<div id="ticker-tape"><div class="tape-track" id="tape-track"></div></div>
<header>
  <div class="header-inner">
  <div class="header-left">
    <div class="header-label">// Market Intelligence</div>
    <h1>Business <span>RSS</span></h1>
    <div class="header-sub">FT · Reuters · BBC · Guardian — aggregated and sentiment scored, refreshed 3× daily</div>
  </div>
  <div class="header-blocks">
  <div class="header-block">
  <div class="header-block-label">Prices Last Updated</div>
  <div class="header-block-value" id="data-bar-ts">—</div>
  </div>
  </div>
  <button aria-label="Toggle theme" class="theme-toggle" id="theme-toggle" onclick="toggleTheme()">☾</button>
  </div>

  <div class="filter-bar" id="filter-bar"></div>

  <div class="rss-controls">
    <input type="text" id="news-search" placeholder="Search headline or source..." oninput="filterNews(this.value)">
    <span class="sort-label">Sort</span>
    <div class="sort-group" id="sort-group">
      <button class="sort-btn active" data-sort="newest" onclick="setSort('newest', this)">Newest</button>
      <button class="sort-btn" data-sort="oldest" onclick="setSort('oldest', this)">Oldest</button>
      <button class="sort-btn" data-sort="positive" onclick="setSort('positive', this)">Most Positive</button>
      <button class="sort-btn" data-sort="negative" onclick="setSort('negative', this)">Most Negative</button>
    </div>
    <span class="sort-label">Period</span>
    <div class="sort-group" id="window-group">
      <button class="sort-btn active" data-window="all" onclick="setWindow('all', this)">All Time</button>
      <button class="sort-btn" data-window="day" onclick="setWindow('day', this)">Last 24h</button>
      <button class="sort-btn" data-window="week" onclick="setWindow('week', this)">Last Week</button>
    </div>
    <span class="row-count">Showing <span id="news-count">—</span> articles</span>
  </div>
</header>

<div class="page-body">
<div class="left-rail">
<a class="sector-pill" href="index.html"><span class="sector-pill-icon">⊞</span><span class="sector-pill-name">Stock Hub</span></a>
<a class="sector-pill" href="All/index.html"><span class="sector-pill-icon">🌐</span><span class="sector-pill-name">All Sectors</span><span class="sector-pill-badge">Live</span></a>
<a class="sector-pill" href="AI/index.html"><span class="sector-pill-icon">🤖</span><span class="sector-pill-name">AI Infra</span><span class="sector-pill-badge">Live</span></a>
<a class="sector-pill" href="Biotech/index.html"><span class="sector-pill-icon">🧬</span><span class="sector-pill-name">Biotech</span><span class="sector-pill-badge">Live</span></a>
<a class="sector-pill" href="Defence/index.html"><span class="sector-pill-icon">🛡️</span><span class="sector-pill-name">Defence</span><span class="sector-pill-badge">Live</span></a>
<a class="sector-pill" href="Tech/index.html"><span class="sector-pill-icon">💻</span><span class="sector-pill-name">Technology</span><span class="sector-pill-badge">Live</span></a>
<a class="sector-pill" href="Crypto/index.html"><span class="sector-pill-icon">₿</span><span class="sector-pill-name">Crypto</span><span class="sector-pill-badge">Live</span></a>
<a class="sector-pill" href="Energy/index.html"><span class="sector-pill-icon">⚡</span><span class="sector-pill-name">Energy</span><span class="sector-pill-badge">Live</span></a>
<a class="sector-pill active" href="rss.html"><span class="sector-pill-icon">📰</span><span class="sector-pill-name">RSS Feed</span></a>
</div>
<div class="page-main">
<div class="container">

  <div class="news-feed" id="news-feed"></div>

</div><!-- /.container -->

<footer>
  Business RSS · FT · Reuters · BBC · Guardian · Sentiment: VADER · Updated <span id="feed-updated">—</span>
</footer>
</div><!-- /.page-main -->
</div><!-- /.page-body -->'''

c = c[:start] + NEW + c[end:]
with open(path, 'w') as f:
    f.write(c)
print('rss.html body rebuilt into rail layout')
