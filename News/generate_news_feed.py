"""
Fetch RSS feeds from FT, Reuters, BBC Business and Guardian Business.
Outputs:
  - news-feed.json  (in News/, for programmatic use)
  - ../rss-data.js  (at repo root, window.NEWS_FEED_DATA for rss.html)
"""

import json
import calendar
import re
import sys
import time
from datetime import datetime, timezone

import feedparser
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

FEEDS = [
    {"key": "ft",       "label": "Financial Times",  "url": "https://www.ft.com/rss/home"},
    {"key": "reuters",  "label": "Reuters",           "url": "https://feeds.reuters.com/reuters/businessNews"},
    {"key": "bbc",      "label": "BBC Business",      "url": "https://feeds.bbci.co.uk/news/business/rss.xml"},
    {"key": "guardian", "label": "Guardian Business", "url": "https://www.theguardian.com/uk/business/rss"},
]

MAX_PER_SOURCE = 50
MAX_TOTAL = 200
TIMEOUT = 15

analyzer = SentimentIntensityAnalyzer()


def strip_html(text):
    if not text:
        return ""
    return re.sub(r"<[^>]+>", " ", text).strip()


def sentiment(title, summary):
    combined = (title or "") + " " + (summary or "")
    scores = analyzer.polarity_scores(combined.strip())
    return round(scores["compound"], 4)


def fetch_feed(feed_cfg):
    try:
        resp = requests.get(
            feed_cfg["url"],
            timeout=TIMEOUT,
            headers={"User-Agent": "StocksHub-RSSBot/1.0"},
        )
        resp.raise_for_status()
        parsed = feedparser.parse(resp.text)
    except Exception as e:
        print(f"[{feed_cfg['key']}] fetch failed: {e}", file=sys.stderr)
        return []

    articles = []
    seen_urls = set()
    for entry in parsed.entries[:MAX_PER_SOURCE]:
        url = entry.get("link") or ""
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        title = strip_html(entry.get("title") or "").strip()
        if not title:
            continue

        raw_summary = entry.get("summary") or entry.get("description") or ""
        summary = strip_html(raw_summary)[:300].strip()

        pub = None
        if entry.get("published_parsed"):
            try:
                pub = calendar.timegm(entry.published_parsed)
            except Exception:
                pass

        articles.append({
            "source":    feed_cfg["key"],
            "label":     feed_cfg["label"],
            "title":     title,
            "url":       url,
            "summary":   summary,
            "published": pub,
            "sentiment": sentiment(title, summary),
        })

    print(f"[{feed_cfg['key']}] fetched {len(articles)} articles")
    return articles


def main():
    all_articles = []
    seen_global = set()

    for feed_cfg in FEEDS:
        for article in fetch_feed(feed_cfg):
            if article["url"] not in seen_global:
                seen_global.add(article["url"])
                all_articles.append(article)

    all_articles.sort(key=lambda a: a["published"] or 0, reverse=True)
    all_articles = all_articles[:MAX_TOTAL]

    generated = int(time.time())
    payload = {
        "generated": generated,
        "generated_utc": datetime.fromtimestamp(generated, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "articles": all_articles,
    }

    with open("news-feed.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f"Wrote news-feed.json ({len(all_articles)} articles)")

    js_content = "window.NEWS_FEED_DATA = " + json.dumps(payload, ensure_ascii=False) + ";\n"
    with open("../rss-data.js", "w", encoding="utf-8") as f:
        f.write(js_content)
    print("Wrote ../rss-data.js")


if __name__ == "__main__":
    main()
