"""Prices for the market and sector groups (#88 phase 1, PR 4).

    python update_group_prices.py                 # prices + due fundamentals, write groups/
    python update_group_prices.py --no-fundamentals

Groups (one data file each, next to the group's pages, holding only its own stocks), from
groups_config.py:
  markets  sp500, nasdaq100, ftse100  -> markets/<id>/prices-data.js
  sectors  the 11 standard sectors    -> sectors/<slug>/prices-data.js (Unclassified stocks left out)
Coins keep their own Crypto/ price script; the theme groups (AI, Defence, ...) keep theirs for now.

How it stays light on Yahoo (#88 "Revised plan", point 5):
  - prices: one batched daily-history download per BATCH symbols (1 year; adjusted close, raw
    close where Yahoo leaves the adjusted one empty), 3x a day with
    the other price bots;
  - fundamentals (market cap, P/E, beta, analyst view, ...): Ticker.info at most once a day per
    stock, cached in groups/fundamentals.json; a run spends at most --fundamentals-minutes on them
    and the rest wait for the next run;
  - jittered backoff on errors (429s); a stock that fails keeps its last good row (price_as_of
    says how old it is) instead of dropping off the page.

  - news headlines (#88 follow-up): Ticker.news for the stocks people look at, in this order: every
    live signal run's picks, each group's biggest movers of the day, then the theme stocks; at most
    every NEWS_MAX_AGE per stock, cached in groups/news.json; a run spends at most --news-minutes on
    them. Headlines older than NEWS_KEEP are dropped from the pages.

Writes <group path>/prices-data.js (window.PRICES_DATA = {...}, the format the sector pages read,
plus fx, and per stock: markets, sector, industry, themes, t212, currency, price_as_of) and
groups/status.json (updated time and counts; read by /health).
"""
import argparse
import json
import os
import random
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import groups_config
import universe

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "groups")
FUND_PATH = os.path.join(OUT, "fundamentals.json")
BATCH = 100
FUND_MAX_AGE = timedelta(hours=20)
NEWS_PATH = os.path.join(OUT, "news.json")
NEWS_MAX_AGE = timedelta(hours=6)
NEWS_KEEP = timedelta(days=7)            # a cached headline list older than this is not shown
NEWS_ITEMS = 5
MOVERS_PER_GROUP = 5                     # biggest risers and fallers per group get headlines
STALE_AFTER = timedelta(days=7)          # newest bar older than this = no usable price this run
LONDON = ZoneInfo("Europe/London")


def groups(assets):
    """{group id: group} from groups_config (shared with the page builder)."""
    return {g["id"]: g for g in groups_config.all_groups(assets)}


# ── FX ─────────────────────────────────────────────────────────────────────────
SAR_PER_USD = 3.75     # the riyal is pegged


def to_gbp_factor(currency, fx):
    """Multiply a price in `currency` by this to get GBP. fx: GBP -> USD/EUR/JPY/... rates."""
    if currency == "GBp":
        return 0.01
    if currency == "GBP":
        return 1.0
    if currency == "SAR":
        return 1.0 / (fx["USD"] * SAR_PER_USD)
    rate = fx.get(currency)
    return 1.0 / rate if rate else None


def get_fx():
    """{currency: units per GBP} for USD, EUR, JPY, CHF, CAD, AUD, HKD (Yahoo, then frankfurter)."""
    import yfinance as yf
    want = ["USD", "EUR", "JPY", "CHF", "CAD", "AUD", "HKD"]
    fx = {}
    try:
        df = yf.download([f"GBP{c}=X" for c in want], period="10d", progress=False, auto_adjust=False)["Close"]
        for c in want:
            col = df.get(f"GBP{c}=X")
            if col is not None and col.dropna().size:
                fx[c] = float(col.dropna().iloc[-1])
    except Exception as e:
        print(f"  FX from Yahoo failed: {e}")
    missing = [c for c in want if c not in fx]
    if missing:
        import requests
        r = requests.get("https://api.frankfurter.app/latest", params={"from": "GBP", "to": ",".join(missing)}, timeout=20)
        fx.update({k: float(v) for k, v in r.json()["rates"].items()})
    return fx


# ── prices (pure part tested in test_group_prices.py) ──────────────────────────
def stats(bars, today):
    """bars: [(date, high, low, close, volume)] oldest first, one stock, no gaps filled.
    Returns the price fields in the stock's own currency, or None if there is no recent bar."""
    bars = [b for b in bars if b[3] is not None and b[3] == b[3]]     # drop empty (NaN) days
    if len(bars) < 2 or today - bars[-1][0] > STALE_AFTER:
        return None
    dates = [b[0] for b in bars]
    close = [b[3] for b in bars]
    last, last_date = close[-1], dates[-1]

    def pct(old):
        return round((last - old) / old * 100, 2) if old else 0.0

    month_ago = last_date - timedelta(days=30)
    in_month = [i for i, d in enumerate(dates) if d >= month_ago]
    in_year = [i for i, d in enumerate(dates) if d.year == last_date.year]
    vols = [b[4] or 0 for b in bars]
    highs = [b[1] for b in bars if b[1] == b[1] and b[1] is not None]
    lows = [b[2] for b in bars if b[2] == b[2] and b[2] is not None]
    return {
        "price": last,
        "price_as_of": last_date.isoformat(),
        "change_1d": pct(close[-2]),
        "change_1w": pct(close[-6]) if len(close) >= 6 else 0.0,
        "change_1m": pct(close[in_month[0]]) if in_month else 0.0,
        "change_ytd": pct(close[in_year[0]]) if in_year else 0.0,
        "return_1yr": round((last - close[0]) / close[0] * 100) if close[0] else 0,
        "high": max(highs) if highs else last,
        "low": min(lows) if lows else last,
        "vol_1d": int(vols[-1]),
        "vol_1w": int(sum(vols[-5:])),
        "vol_1m": int(sum(vols[i] for i in in_month)),
    }


def laggards(stats_by_symbol, exchange_of):
    """Symbols whose newest bar is behind the newest bar of their own exchange (a batched download
    sometimes leaves out a stock's latest day: SanDisk, 22 Nov 2026)."""
    newest = {}
    for y, s in stats_by_symbol.items():
        e = exchange_of[y]
        newest[e] = max(newest.get(e, ""), s["price_as_of"])
    return sorted(y for y, s in stats_by_symbol.items() if s["price_as_of"] < newest[exchange_of[y]])


def _bars(df):
    """Rows -> bars. Close = the dividend/split-adjusted close, or the raw close where Yahoo left
    the adjusted one empty (SanDisk's 20 Nov 2026 bar). For recent days the two are the same:
    adjustment only rewrites older prices."""
    out = []
    for ts, r in df.iterrows():
        adj = r.get("Adj Close")
        close = adj if adj is not None and adj == adj else r["Close"]
        out.append((ts.date(), r["High"], r["Low"], close, r["Volume"]))
    return out


def fill_last_close(bars, last_price):
    """Yahoo sometimes publishes a day's bar with open/high/low/volume but no close (SanDisk,
    20 Nov 2026). If the newest bar is like that, its close is the live quote's last price."""
    if bars and last_price and bars[-1][3] != bars[-1][3] and bars[-1][1] == bars[-1][1]:
        d, hi, lo, _, v = bars[-1]
        if lo <= last_price <= hi:                  # only if it fits that day's range
            bars = bars[:-1] + [(d, hi, lo, float(last_price), v)]
    return bars


def fetch_prices(symbols, today, exchange_of):
    """{yahoo symbol: stats} via batched downloads; failed batches retried with backoff; stocks
    missing from a batch or a day behind their exchange are fetched again on their own."""
    import yfinance as yf
    out = {}
    for start in range(0, len(symbols), BATCH):
        chunk = symbols[start:start + BATCH]
        for attempt in range(4):
            try:
                df = yf.download(chunk, period="1y", interval="1d", group_by="ticker",
                                 auto_adjust=False, progress=False, threads=True)
                break
            except Exception as e:
                print(f"  batch {start // BATCH + 1}: {str(e)[:80]} — retrying")
                time.sleep(2 ** attempt + random.random())
        else:
            continue
        for y in chunk:
            try:
                d = df[y] if len(chunk) > 1 else df
                bars = _bars(d)
            except KeyError:
                continue
            s = stats(bars, today)
            if s:
                out[y] = s
        print(f"  prices {min(start + BATCH, len(symbols))}/{len(symbols)}: {len(out)} ok so far")
        time.sleep(1 + random.random())
    again = sorted(set(symbols) - set(out)) + laggards(out, exchange_of)
    for y in again:
        try:
            tk = yf.Ticker(y)
            bars = fill_last_close(_bars(tk.history(period="1y", auto_adjust=False)), tk.fast_info.last_price)
            s = stats(bars, today)
        except Exception:
            s = None
        if s and (y not in out or s["price_as_of"] > out[y]["price_as_of"]):
            out[y] = s
        time.sleep(0.3 + random.random() * 0.3)
    behind = laggards(out, exchange_of)
    print(f"  re-fetched {len(again)} on their own; still a day or more behind: {behind or 'none'}")
    return out


# ── fundamentals (cached, once a day) ──────────────────────────────────────────
def fundamentals_from_info(info, currency):
    """The fields the pages show, from Ticker.info. Market cap stays in the listing's money
    (Yahoo gives LSE caps in GBP even though the price is in pence)."""
    def num(k, scale=1.0, digits=3, positive=True):
        v = info.get(k)
        try:
            v = float(v)
        except (TypeError, ValueError):
            return None
        if v != v or (positive and v <= 0):
            return None
        return round(v * scale, digits)
    analyst = info.get("recommendationKey")
    return {
        "market_cap": num("marketCap", digits=0),
        "market_cap_currency": "GBP" if currency == "GBp" else currency,
        "beta": num("beta", positive=False),
        "pe_ratio": num("trailingPE", digits=2),
        "avg_volume_m": num("averageVolume", 1e-6, 2),
        "div_yield_pct": num("dividendYield"),          # already a percentage (0.31 = 0.31%)
        "short_pct": num("shortPercentOfFloat", 100, 2),
        "analyst": analyst.lower() if isinstance(analyst, str) and analyst != "none" else None,
        "analyst_score": num("recommendationMean", digits=2),
    }


def due(cache, symbols, now):
    """Symbols whose fundamentals are missing or older than FUND_MAX_AGE, oldest first."""
    def age(y):
        f = (cache.get(y) or {}).get("fetched")
        return datetime.fromisoformat(f) if f else datetime.min.replace(tzinfo=timezone.utc)
    return sorted((y for y in symbols if now - age(y) > FUND_MAX_AGE), key=age)


def refresh_fundamentals(cache, symbols, currencies, now, minutes):
    import yfinance as yf
    todo = due(cache, symbols, now)
    stop = time.monotonic() + minutes * 60
    done = failed = 0
    for y in todo:
        if time.monotonic() > stop:
            break
        for attempt in range(3):
            try:
                info = yf.Ticker(y).info or {}
                if info:
                    cache[y] = {"fetched": now.isoformat(timespec="seconds"),
                                **fundamentals_from_info(info, currencies[y])}
                    done += 1
                break
            except Exception:
                time.sleep(2 ** attempt * 2 + random.random())      # 429s: back off, then move on
        else:
            failed += 1                                            # keep the last good values
        time.sleep(0.2 + random.random() * 0.3)
    print(f"  fundamentals: {len(todo)} due, {done} fetched, {failed} failed, "
          f"{max(0, len(todo) - done - failed)} left for the next run")


# ── news headlines (cached; picks and movers first) ─────────────────────────────
def parse_news(raw, analyzer, max_items=NEWS_ITEMS):
    """yfinance Ticker.news (old or new shape) -> ([{title, publisher, url, published, sentiment}], average)."""
    items = []
    for n in (raw or [])[:max_items]:
        if not isinstance(n, dict):
            continue
        c = n.get("content")
        if isinstance(c, dict):
            title, pub = c.get("title"), (c.get("provider") or {}).get("displayName")
            url = (c.get("canonicalUrl") or {}).get("url") or (c.get("clickThroughUrl") or {}).get("url")
            ts = c.get("pubDate") or c.get("displayTime")
            try:
                pub_ts = int(datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()) if ts else None
            except ValueError:
                pub_ts = None
        else:
            title, pub, url, pub_ts = n.get("title"), n.get("publisher"), n.get("link"), n.get("providerPublishTime")
        if not title:
            continue
        score = None
        if analyzer is not None:
            try:
                score = round(analyzer.polarity_scores(title)["compound"], 3)
            except Exception:
                score = None
        items.append({"title": title, "publisher": pub, "url": url, "published": pub_ts, "sentiment": score})
    scored = [i["sentiment"] for i in items if i["sentiment"] is not None]
    return items, (round(sum(scored) / len(scored), 3) if scored else None)


def live_picks(root=ROOT):
    """Tickers picked by any live signal run: the theme runs that remain + every group run's file."""
    import glob
    out = set()
    paths = [os.path.join(root, t, "signals-local.json") for t in ("AI", "Defence")]
    paths += glob.glob(os.path.join(root, "sectors", "*", "signals-local.json"))
    paths += glob.glob(os.path.join(root, "markets", "*", "signals-local.json"))
    for path in paths:
        try:
            data = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        out.update(p["ticker"] for p in data.get("picks") or [] if p.get("ticker"))
    return out


def news_wanted(gs, assets, prices, picks, themed):
    """Yahoo symbols in priority order: picks, then each group's biggest movers, then theme stocks."""
    order = []
    def add(t):
        a = assets.get(t)
        if a and a["yahoo"] in prices and a["yahoo"] not in order:
            order.append(a["yahoo"])
    for t in sorted(picks):
        add(t)
    for g in gs.values():
        moves = sorted((prices[assets[t]["yahoo"]]["change_1d"], t) for t in g["tickers"] if assets[t]["yahoo"] in prices)
        for _m, t in moves[:MOVERS_PER_GROUP] + moves[-MOVERS_PER_GROUP:]:
            add(t)
    for t in sorted(themed):
        add(t)
    return order


def refresh_news(cache, wanted, now, minutes, fetch=None, analyzer=None):
    """Fetch headlines for `wanted` symbols whose cache is missing or older than NEWS_MAX_AGE, in order,
    until the time budget runs out. A failed fetch keeps the old headlines."""
    if fetch is None:
        import yfinance as yf
        fetch = lambda y: yf.Ticker(y).news
    if analyzer is None:
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            analyzer = SentimentIntensityAnalyzer()
        except ImportError:
            print("  [vaderSentiment not installed: headlines kept, sentiment skipped]")
    def age(y):
        f = (cache.get(y) or {}).get("fetched")
        return now - datetime.fromisoformat(f) if f else timedelta.max
    todo = [y for y in wanted if age(y) > NEWS_MAX_AGE]
    stop = time.monotonic() + minutes * 60
    done = failed = 0
    for y in todo:
        if time.monotonic() > stop:
            break
        try:
            items, agg = parse_news(fetch(y), analyzer)
            cache[y] = {"fetched": now.isoformat(timespec="seconds"), "news": items, "sentiment": agg}
            done += 1
        except Exception:
            failed += 1
            time.sleep(2 + random.random())
        time.sleep(0.2 + random.random() * 0.3)
    print(f"  news: {len(wanted)} wanted, {len(todo)} due, {done} fetched, {failed} failed, "
          f"{max(0, len(todo) - done - failed)} left for the next run")


def news_for(cache, yahoo, now):
    """(headlines, average sentiment) to show, or ([], None) if none or too old."""
    c = cache.get(yahoo) or {}
    if not c.get("fetched") or now - datetime.fromisoformat(c["fetched"]) > NEWS_KEEP:
        return [], None
    return c.get("news") or [], c.get("sentiment")


# ── rows ───────────────────────────────────────────────────────────────────────
def fmt_gbp(v):
    return str(round(v)) if v >= 10 else (f"{v:.2f}" if v >= 1 else f"{v:.3f}")


def bar_pct(price, low, high):
    if low is not None and high is not None and high > low:
        return min(99, max(1, round((price - low) / (high - low) * 100)))
    return 50


def make_row(t, a, s, f, fx, themes, category):
    """One stock in the sector pages' format. s: stats (own currency), f: fundamentals or {}."""
    k = to_gbp_factor(a["currency"], fx)
    usd = fx["USD"]
    p, lo, hi = s["price"] * k, s["low"] * k, s["high"] * k
    mc = f.get("market_cap")
    mk = to_gbp_factor(f.get("market_cap_currency"), fx) if mc else None
    mc_gbp_b = round(mc * mk / 1e9, 3) if mc and mk else None
    return {
        "ticker": t, "company_name": a["name"], "category": category, "exchange": a["exchange"],
        "price_gbp": fmt_gbp(p), "price_usd": round(p * usd, 2),
        "change_1d": f"{s['change_1d']:+.2f}%", "change_1w": f"{s['change_1w']:+.2f}%",
        "change_1m": f"{s['change_1m']:+.2f}%", "change_ytd": f"{s['change_ytd']:+.2f}%",
        "return_1yr": f"{s['return_1yr']:+}%",
        "low_gbp": fmt_gbp(lo), "low_usd": round(lo * usd, 2),
        "high_gbp": fmt_gbp(hi), "high_usd": round(hi * usd, 2),
        "bar_pct": bar_pct(p, lo, hi),
        "market_cap_gbp_b": mc_gbp_b, "market_cap_usd_b": round(mc_gbp_b * usd, 3) if mc_gbp_b else None,
        "beta": f.get("beta"), "pe_ratio": f.get("pe_ratio"), "avg_volume_m": f.get("avg_volume_m"),
        "div_yield_pct": f.get("div_yield_pct"), "short_pct": f.get("short_pct"),
        "analyst": f.get("analyst"), "analyst_score": f.get("analyst_score"),
        "vol_1d": s["vol_1d"], "vol_1w": s["vol_1w"], "vol_1m": s["vol_1m"],
        "news": [], "news_sentiment": None,
        "markets": a.get("markets") or [], "sector": a.get("sector"), "industry": a.get("industry"),
        "themes": themes.get(t, []), "t212": a.get("t212"), "currency": a["currency"],
        "price_as_of": s["price_as_of"],
    }


def previous_stats(group):
    """Last good rows per ticker from the group's current file (kept when Yahoo fails)."""
    path = os.path.join(ROOT, group["path"], "prices-data.js")
    try:
        raw = open(path, encoding="utf-8").read()
        data = json.loads(re.sub(r"^\s*window\.PRICES_DATA\s*=\s*", "", raw).rstrip().rstrip(";"))
        return {r["ticker"]: r for r in data.get("stocks", [])}
    except (OSError, ValueError):
        return {}


# ── All pages: every stock in one file (#88 PR 7) ────────────────────────────────
ALL_PATH = "All/all-data.js"
NEWS_ALL_PATH = "All/news-data.js"      # only the stocks with headlines, for All News
# universe.yaml theme names -> the keys the All pages use (and sector-data.js's notes)
THEME_KEYS = {"AI": "ai", "Biotech": "biotech", "Crypto": "crypto", "Defence": "defence",
              "Energy": "energy", "MegaCap": "megacap", "Tech": "tech"}
ALL_DROP = ("news", "news_sentiment", "low_gbp", "high_gbp", "price_gbp")   # unused there; keeps the file small


def all_row(r, sector_slug=None):
    out = {k: v for k, v in r.items() if k not in ALL_DROP}
    out["themes"] = [THEME_KEYS.get(x, x.lower()) for x in r.get("themes") or []]
    out["category"] = sector_slug or groups_config.slug(r.get("sector") or "")
    return out


def crypto_rows(keep_news=False):
    """The Crypto page's own rows (CoinMarketCap/CoinGecko prices), as All rows."""
    try:
        raw = open(os.path.join(ROOT, "Crypto", "prices-data.js"), encoding="utf-8").read()
        data = json.loads(re.sub(r"^\s*window\.PRICES_DATA\s*=\s*", "", raw).rstrip().rstrip(";"))
    except (OSError, ValueError):
        return []
    out = []
    for r in data.get("stocks", []):
        row = all_row({**r, "themes": ["Crypto"], "markets": ["crypto"], "sector": None, "t212": "no",
                       "currency": "USD"}, "crypto")
        if keep_news:
            row["news"] = r.get("news") or []
        out.append(row)
    return out


def write_all(gs, all_rows, updated, fx):
    rows = [all_row(r) for _, r in sorted(all_rows.items())] + crypto_rows()
    data = {"updated": updated, "fx_gbp_usd": round(fx["USD"], 4), "count": len(rows), "stocks": rows}
    os.makedirs(os.path.join(ROOT, "All"), exist_ok=True)
    with open(os.path.join(ROOT, ALL_PATH), "w", encoding="utf-8") as f:
        f.write(f"window.ALL_DATA = {json.dumps(data, separators=(',', ':'))};\n")
    write_all_news(all_rows, updated)


NEWS_KEEP_FIELDS = ("ticker", "company_name", "sector", "markets", "themes", "t212")


def write_all_news(all_rows, updated):
    """All/news-data.js: every stock (and coin) with headlines, with what the All filters need."""
    rows = []
    for _, r in sorted(all_rows.items()):
        if r.get("news"):
            row = all_row(r)
            rows.append({**{k: row.get(k) for k in NEWS_KEEP_FIELDS}, "news": r["news"]})
    for r in crypto_rows(keep_news=True):
        if r.get("news"):
            rows.append({**{k: r.get(k) for k in NEWS_KEEP_FIELDS}, "news": r["news"]})
    data = {"updated": updated, "count": len(rows), "stocks": rows}
    with open(os.path.join(ROOT, NEWS_ALL_PATH), "w", encoding="utf-8") as f:
        f.write(f"window.NEWS_DATA = {json.dumps(data, separators=(',', ':'))};\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--no-fundamentals", action="store_true")
    ap.add_argument("--fundamentals-minutes", type=float, default=15)
    ap.add_argument("--no-news", action="store_true")
    ap.add_argument("--news-minutes", type=float, default=6)
    args = ap.parse_args(argv)

    u = universe.load()
    assets = {t: a for t, a in u["assets"].items() if a["exchange"] != "Crypto"}
    # themes per listing: RR. (AI) and RR.L (Defence) are one share, so RR.L carries both
    by_yahoo = {}
    for theme, members in u["sectors"].items():
        for t, _ in members:
            y = u["assets"][t]["yahoo"]
            if theme not in by_yahoo.setdefault(y, []):
                by_yahoo[y].append(theme)
    themes = {t: by_yahoo.get(a["yahoo"], []) for t, a in u["assets"].items()}
    gs = groups(assets)
    in_groups = sorted({t for g in gs.values() for t in g["tickers"]})
    symbols = sorted({assets[t]["yahoo"] for t in in_groups})
    now = datetime.now(timezone.utc)
    print(f"{len(gs)} groups, {len(in_groups)} stocks, {len(symbols)} Yahoo symbols")

    fx = get_fx()
    print("  FX per £1:", {k: round(v, 4) for k, v in fx.items()})
    prices = fetch_prices(symbols, now.date(), {a["yahoo"]: a["exchange"] for a in assets.values()})
    if len(prices) < len(symbols) * 0.5:     # Yahoo down: keep every file as it is, fail the run
        print(f"ERROR: only {len(prices)}/{len(symbols)} prices — nothing written")
        sys.exit(1)

    os.makedirs(OUT, exist_ok=True)
    try:
        cache = json.load(open(FUND_PATH, encoding="utf-8"))
    except (OSError, ValueError):
        cache = {}
    if not args.no_fundamentals:
        currencies = {a["yahoo"]: a["currency"] for a in assets.values()}
        refresh_fundamentals(cache, [s for s in symbols if s in prices], currencies, now, args.fundamentals_minutes)
        with open(FUND_PATH, "w", encoding="utf-8") as f:
            json.dump(dict(sorted(cache.items())), f, separators=(",", ":"))
            f.write("\n")

    try:
        news = json.load(open(NEWS_PATH, encoding="utf-8"))
    except (OSError, ValueError):
        news = {}
    if not args.no_news:
        themed = {t for t, a in assets.items() if themes.get(t)}
        refresh_news(news, news_wanted(gs, assets, prices, live_picks(), themed), now, args.news_minutes)
        news = {y: c for y, c in news.items() if now - datetime.fromisoformat(c["fetched"]) <= NEWS_KEEP}
        with open(NEWS_PATH, "w", encoding="utf-8") as f:
            json.dump(dict(sorted(news.items())), f, separators=(",", ":"))
            f.write("\n")

    updated = now.astimezone(LONDON).strftime("%Y-%m-%d %H:%M")
    status = {"updated": updated, "fx": fx, "groups": {}, "missing": []}
    all_rows = {}
    for gid, g in gs.items():
        kept = previous_stats(g)
        cats = groups_config.categories(g, assets)
        rows = []
        for t in g["tickers"]:
            a = assets[t]
            s = prices.get(a["yahoo"])
            if s:
                row = make_row(t, a, s, cache.get(a["yahoo"]) or {}, fx, themes,
                               groups_config.category_of(g, a, cats))
                row["news"], row["news_sentiment"] = news_for(news, a["yahoo"], now)
                rows.append(row)
            elif t in kept:                       # Yahoo failed this run: keep the last good row
                rows.append(kept[t])
                status["missing"].append(t)
        if g["kind"] == "sector":                  # every stock is in exactly one sector group
            all_rows.update({r["ticker"]: r for r in rows})
        data = {"updated": updated, "group": gid, "name": g["name"], "kind": g["kind"],
                "fx_gbp_usd": round(fx["USD"], 4), "fx": {k: round(v, 4) for k, v in fx.items()},
                "stocks": rows}
        os.makedirs(os.path.join(ROOT, g["path"]), exist_ok=True)
        with open(os.path.join(ROOT, g["path"], "prices-data.js"), "w", encoding="utf-8") as f:
            f.write(f"window.PRICES_DATA = {json.dumps(data, separators=(',', ':'))};\n")
        status["groups"][gid] = {"name": g["name"], "kind": g["kind"], "path": g["path"],
                                 "stocks": len(rows), "members": len(g["tickers"])}
    status["missing"] = sorted(set(status["missing"]))
    write_all(gs, all_rows, updated, fx)
    status["all"] = {"path": ALL_PATH, "stocks": len(all_rows)}
    with open(os.path.join(OUT, "status.json"), "w", encoding="utf-8") as f:
        json.dump(status, f, indent=1)
        f.write("\n")

    no_price = [t for t in in_groups if assets[t]["yahoo"] not in prices]
    print(f"priced {len(in_groups) - len(no_price)}/{len(in_groups)}; "
          f"no fresh price: {len(no_price)} ({', '.join(no_price[:15])}{' …' if len(no_price) > 15 else ''})")
    for gid, g in status["groups"].items():
        print(f"  {gid:24} {g['stocks']:4}/{g['members']}")
    if len(no_price) > len(in_groups) * 0.1:
        print("WARNING: over 10% of stocks have no fresh price (their last good rows are kept)")


if __name__ == "__main__":
    main()
