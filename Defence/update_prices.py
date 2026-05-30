#!/usr/bin/env python3
"""
Update Defence dashboard with live prices from Yahoo Finance.
Run: python update_prices.py
Requires: pip install yfinance beautifulsoup4 vaderSentiment
"""

import yfinance as yf
import re
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

# News sentiment is keyless (VADER, local). It is strictly secondary —
# a missing/broken VADER must never break the price update, so the import
# is guarded and news scoring degrades gracefully.
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _VADER_OK = True
except ImportError:
    _VADER_OK = False

HTML_FILE = "index.html"
JSON_FILE = "prices.json"
JS_FILE   = "prices-data.js"
DASHBOARD_TITLE = "Defence Stock Dashboard"

# ticker → (yahoo_symbol, category, exchange, special)
# special: None | "lse_pence"
STOCKS = {
    # us-primes
    "LMT":   ("LMT",   "us-primes",    "NYSE",   None),
    "RTX":   ("RTX",   "us-primes",    "NYSE",   None),
    "NOC":   ("NOC",   "us-primes",    "NYSE",   None),
    "GD":    ("GD",    "us-primes",    "NYSE",   None),
    "HII":   ("HII",   "us-primes",    "NYSE",   None),
    "LHX":   ("LHX",   "us-primes",    "NYSE",   None),
    "BA":    ("BA",    "us-primes",    "NYSE",   None),
    # uk-european
    "BA.L":  ("BA.L",  "uk-european",  "LSE",    "lse_pence"),
    "RR.L":  ("RR.L",  "uk-european",  "LSE",    "lse_pence"),
    "QQ.L":  ("QQ.L",  "uk-european",  "LSE",    "lse_pence"),
    # cyber-intel
    "PLTR":  ("PLTR",  "cyber-intel",  "NYSE",   None),
    "LDOS":  ("LDOS",  "cyber-intel",  "NYSE",   None),
    "CACI":  ("CACI",  "cyber-intel",  "NYSE",   None),
    "SAIC":  ("SAIC",  "cyber-intel",  "NYSE",   None),
    "BAH":   ("BAH",   "cyber-intel",  "NYSE",   None),
    # drones
    "AVAV":  ("AVAV",  "drones",       "NASDAQ", None),
    "KTOS":  ("KTOS",  "drones",       "NASDAQ", None),
    "RCAT":  ("RCAT",  "drones",       "NASDAQ", None),
    "TXT":   ("TXT",   "drones",       "NYSE",   None),
    # space
    "RKLB":  ("RKLB",  "space",        "NASDAQ", None),
    "PL":    ("PL",    "space",        "NYSE",   None),
    "ASTS":  ("ASTS",  "space",        "NASDAQ", None),
    # weapons
    "TDG":   ("TDG",   "weapons",      "NYSE",   None),
    "HEI":   ("HEI",   "weapons",      "NYSE",   None),
    "AXON":  ("AXON",  "weapons",      "NASDAQ", None),
    "OLN":   ("OLN",   "weapons",      "NYSE",   None),
    "MRCY":  ("MRCY",  "weapons",      "NASDAQ", None),
    "DRS":   ("DRS",   "weapons",      "NYSE",   None),
}


def get_fx_rates():
    """Fetch GBP/USD rate."""
    gbp_usd = yf.Ticker("GBPUSD=X").fast_info["last_price"]
    return gbp_usd


def get_stock_data(yahoo_symbol):
    t = yf.Ticker(yahoo_symbol)
    fi = t.fast_info
    price = fi.last_price
    try:
        low52 = fi.year_low
    except Exception:
        low52 = None
    try:
        high52 = fi.year_high
    except Exception:
        high52 = None
    try:
        prev_close = fi.previous_close
    except Exception:
        prev_close = None
    price_1w = None
    price_1m = None
    price_ytd = None
    vol_1d = None
    vol_1w = None
    vol_1m = None
    try:
        hist = t.history(period='1mo')
        if len(hist) >= 6:
            price_1w = float(hist['Close'].iloc[-6])
        if len(hist) >= 1:
            price_1m = float(hist['Close'].iloc[0])
        if 'Volume' in hist.columns:
            if len(hist) >= 1:
                vol_1d = int(hist['Volume'].iloc[-1])
            if len(hist) >= 5:
                vol_1w = int(hist['Volume'].iloc[-5:].sum())
            vol_1m = int(hist['Volume'].sum())
    except Exception:
        pass
    try:
        year = datetime.now().year
        ytd_hist = t.history(start=f'{year}-01-01', end=f'{year}-01-08')
        if len(ytd_hist) >= 1:
            price_ytd = float(ytd_hist['Close'].iloc[0])
    except Exception:
        pass
    return price, low52, high52, prev_close, price_1w, price_1m, price_ytd, vol_1d, vol_1w, vol_1m


def get_metrics(yahoo_symbol, special, gbp_usd):
    """Fetch fundamental metrics from ticker.info. Returns dict or {} on failure."""
    try:
        info = yf.Ticker(yahoo_symbol).info

        # Market cap — convert to GBP billions
        mc_raw = info.get('marketCap')
        if mc_raw and mc_raw > 0:
            mc_gbp = to_gbp(mc_raw, special, gbp_usd)
            mc_gbp_b = round(mc_gbp / 1e9, 3)
        else:
            mc_gbp_b = None

        beta = info.get('beta')
        if beta is not None:
            beta = round(float(beta), 3)

        pe_raw = info.get('trailingPE')
        pe_ratio = round(float(pe_raw), 2) if pe_raw and float(pe_raw) > 0 else None

        avg_vol = info.get('averageVolume')
        avg_volume_m = round(avg_vol / 1e6, 2) if avg_vol and avg_vol > 0 else None

        dy_raw = info.get('dividendYield')
        div_yield_pct = round(float(dy_raw) * 100, 3) if dy_raw and float(dy_raw) > 0 else None

        sp_raw = info.get('shortPercentOfFloat')
        short_pct = round(float(sp_raw) * 100, 2) if sp_raw and float(sp_raw) > 0 else None

        analyst = info.get('recommendationKey') or None
        if analyst:
            analyst = analyst.lower()

        score_raw = info.get('recommendationMean')
        analyst_score = round(float(score_raw), 2) if score_raw else None

        week52_raw = info.get('52WeekChange')
        week52_pct = round(float(week52_raw) * 100) if week52_raw is not None else None

        return {
            'market_cap_gbp_b': mc_gbp_b,
            'beta':             beta,
            'pe_ratio':         pe_ratio,
            'avg_volume_m':     avg_volume_m,
            'div_yield_pct':    div_yield_pct,
            'short_pct':        short_pct,
            'analyst':          analyst,
            'analyst_score':    analyst_score,
            'week52_pct':       week52_pct,
        }
    except Exception as e:
        print(f"[metrics error: {e}]", end=" ")
        return {}


def get_news(yahoo_symbol, analyzer, max_items=5):
    """Fetch recent headlines via yfinance and score each with VADER.

    Returns (items, agg_sentiment). Defensive about yfinance's two news
    shapes (older flat dict vs newer nested under 'content'). Never raises
    — news is secondary to prices.
    """
    try:
        raw = yf.Ticker(yahoo_symbol).news or []
    except Exception as e:
        print(f"[news error: {e}]", end=" ")
        return [], None

    items = []
    for n in raw[:max_items]:
        if not isinstance(n, dict):
            continue
        content = n.get("content")
        if isinstance(content, dict):
            # Newer yfinance shape
            title = content.get("title")
            pub = (content.get("provider") or {}).get("displayName")
            url = ((content.get("canonicalUrl") or {}).get("url")
                   or (content.get("clickThroughUrl") or {}).get("url"))
            ts = content.get("pubDate") or content.get("displayTime")
            pub_ts = None
            if ts:
                try:
                    pub_ts = int(datetime.fromisoformat(
                        ts.replace("Z", "+00:00")).timestamp())
                except Exception:
                    pub_ts = None
        else:
            # Older flat shape
            title = n.get("title")
            pub = n.get("publisher")
            url = n.get("link")
            pub_ts = n.get("providerPublishTime")

        if not title:
            continue

        score = None
        if analyzer is not None:
            try:
                score = round(analyzer.polarity_scores(title)["compound"], 3)
            except Exception:
                score = None

        items.append({
            "title":     title,
            "publisher": pub,
            "url":       url,
            "published": pub_ts,
            "sentiment": score,
        })

    scored = [i["sentiment"] for i in items if i["sentiment"] is not None]
    agg = round(sum(scored) / len(scored), 3) if scored else None
    return items, agg


def to_gbp(price, special, gbp_usd):
    if special == "lse_pence":
        return price / 100          # GBp → GBP
    else:
        return price / gbp_usd


def fmt_gbp(val):
    if val >= 10:
        return str(round(val))
    elif val >= 1:
        return f"{val:.2f}"
    else:
        return f"{val:.3f}"


def calc_return(current_gbp, low_gbp):
    if low_gbp and low_gbp > 0:
        pct = ((current_gbp - low_gbp) / low_gbp) * 100
        return round(pct)
    return None


def bar_pct(current_gbp, low_gbp, high_gbp):
    if low_gbp and high_gbp and high_gbp > low_gbp:
        pct = (current_gbp - low_gbp) / (high_gbp - low_gbp) * 100
        return min(99, max(1, round(pct)))
    return 50


def return_class(pct):
    if pct >= 200:
        return "return-mega"
    elif pct >= 50:
        return "return-positive"
    else:
        return "return-modest"


def update_html(results, gbp_usd, today_str):
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id="stock-table")
    if not table:
        print("  [update_html] WARNING: #stock-table not found — skipping HTML update")
        return
    rows = table.find("tbody").find_all("tr")

    for row in rows:
        ticker = row.get("data-ticker")
        if ticker not in results:
            continue

        r = results[ticker]
        ret_str = f"+{r['return_pct']}%"

        # Update data attributes
        row["data-price-usd"]  = f"{r['price_usd']:.2f}"
        row["data-price-gbp"]  = fmt_gbp(r["price_gbp"])
        row["data-return"]     = ret_str
        row["data-low-gbp"]    = fmt_gbp(r["low_gbp"])
        row["data-high-gbp"]   = fmt_gbp(r["high_gbp"])
        row["data-bar-pct"]    = str(r["bar_pct"])
        row["data-change-1d"]  = f"{r['change_1d']:+.2f}%"
        row["data-change-1w"]  = f"{r['change_1w']:+.2f}%"
        row["data-change-1m"]  = f"{r['change_1m']:+.2f}%"
        row["data-change-ytd"] = f"{r['change_ytd']:+.2f}%"

        # Price cell — rebuild with change pills
        price_span = row.find("span", class_="price")
        if price_span:
            price_td = price_span.parent
            price_td.clear()
            new_price = soup.new_tag("span", attrs={"class": "price"})
            new_price.string = f"£{fmt_gbp(r['price_gbp'])}"
            price_td.append(new_price)
            pills_div = soup.new_tag("div", attrs={"class": "change-pills"})
            for label, val in [("1D", r["change_1d"]), ("1W", r["change_1w"]), ("1M", r["change_1m"])]:
                cls = "flat" if val == 0 else ("pos" if val > 0 else "neg")
                pill = soup.new_tag("span", attrs={"class": ["cpill", cls]})
                pill.string = f"{val:+.2f}% {label}"
                pills_div.append(pill)
            price_td.append(pills_div)

        # YTD cell
        ytd_span = row.find("span", class_="ytd-return")
        if ytd_span:
            ytd_val = r["change_ytd"]
            ytd_cls = "ytd-flat" if ytd_val == 0 else ("ytd-pos" if ytd_val > 0 else "ytd-neg")
            ytd_span["class"] = ["ytd-return", ytd_cls]
            ytd_span.string = f"{ytd_val:+.2f}%"

        # Return cell
        ret_span = row.find("span", class_=re.compile(r"return-"))
        if ret_span:
            ret_span["class"] = [return_class(r["return_pct"])]
            ret_span.string = ret_str

        # Range bar
        range_fill = row.find("div", class_="range-fill")
        range_dot  = row.find("div", class_="range-dot")
        if range_fill:
            range_fill["style"] = f"width:{r['bar_pct']}%"
        if range_dot:
            range_dot["style"] = f"left:{r['bar_pct']}%"

        # 52wk labels
        labels = row.find_all("span", class_="range-label")
        if len(labels) >= 2:
            labels[0].string = f"£{fmt_gbp(r['low_gbp'])}"
            labels[1].string = f"£{fmt_gbp(r['high_gbp'])}"

    # Update FX rate display
    fx_span = soup.find("span", id="fx-rate")
    if fx_span:
        fx_span.string = f"£1 = ${gbp_usd:.4f}"

    # Update last updated date
    date_span = soup.find("span", id="last-updated")
    if date_span:
        date_span.string = f"Last updated: {today_str}"

    updated_html = str(soup)
    updated_html = re.sub(
        r"FX Rate used: £1 = \$[\d.]+",
        f"FX Rate used: £1 = ${gbp_usd:.4f}",
        updated_html
    )

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(updated_html)


def write_json(results, gbp_usd, today_str):
    stocks = []
    for ticker, (yahoo_sym, cat, exchange, special) in STOCKS.items():
        if ticker not in results:
            continue
        r = results[ticker]
        stocks.append({
            "ticker":           ticker,
            "category":         cat,
            "exchange":         exchange,
            "price_gbp":        fmt_gbp(r["price_gbp"]),
            "price_usd":        round(r["price_usd"], 2),
            "change_1d":        f"{r['change_1d']:+.2f}%",
            "change_1w":        f"{r['change_1w']:+.2f}%",
            "change_1m":        f"{r['change_1m']:+.2f}%",
            "change_ytd":       f"{r['change_ytd']:+.2f}%",
            "return_1yr":       f"+{r['return_pct']}%",
            "low_gbp":          fmt_gbp(r["low_gbp"]),
            "high_gbp":         fmt_gbp(r["high_gbp"]),
            "bar_pct":          r["bar_pct"],
            # Fundamental metrics (None if unavailable)
            "market_cap_gbp_b": r.get("market_cap_gbp_b"),
            "beta":             r.get("beta"),
            "pe_ratio":         r.get("pe_ratio"),
            "avg_volume_m":     r.get("avg_volume_m"),
            "div_yield_pct":    r.get("div_yield_pct"),
            "short_pct":        r.get("short_pct"),
            "analyst":          r.get("analyst"),
            "analyst_score":    r.get("analyst_score"),
            "vol_1d":           r.get("vol_1d"),
            "vol_1w":           r.get("vol_1w"),
            "vol_1m":           r.get("vol_1m"),
            # News (keyless: yfinance .news + local VADER)
            "news":             r.get("news", []),
            "news_sentiment":   r.get("news_sentiment"),
        })

    data = {
        "updated":    today_str,
        "fx_gbp_usd": round(gbp_usd, 4),
        "stocks":     stocks,
    }

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    with open(JS_FILE, "w", encoding="utf-8") as f:
        f.write(f"window.PRICES_DATA = {json.dumps(data, indent=2)};\n")


def main():
    print("Fetching FX rates...")
    gbp_usd = get_fx_rates()
    print(f"  £1 = ${gbp_usd:.4f}")

    analyzer = SentimentIntensityAnalyzer() if _VADER_OK else None
    if analyzer is None:
        print("  [vaderSentiment not installed — news headlines kept, sentiment skipped]")

    results = {}
    errors  = []

    for ticker, (yahoo_sym, cat, exchange, special) in STOCKS.items():
        try:
            print(f"  {ticker:<6} ({yahoo_sym})... ", end="", flush=True)
            price_raw, low_raw, high_raw, prev_close_raw, price_1w_raw, price_1m_raw, price_ytd_raw, vol_1d_raw, vol_1w_raw, vol_1m_raw = get_stock_data(yahoo_sym)

            price_gbp = to_gbp(price_raw, special, gbp_usd)
            low_gbp   = to_gbp(low_raw,   special, gbp_usd) if low_raw       else None
            high_gbp  = to_gbp(high_raw,  special, gbp_usd) if high_raw      else None

            bp  = bar_pct(price_gbp, low_gbp, high_gbp)

            change_1d = round((price_raw - prev_close_raw) / prev_close_raw * 100, 2) \
                        if prev_close_raw and prev_close_raw > 0 else 0.0
            change_1w = round((price_raw - price_1w_raw) / price_1w_raw * 100, 2) \
                        if price_1w_raw and price_1w_raw > 0 else 0.0
            change_1m = round((price_raw - price_1m_raw) / price_1m_raw * 100, 2) \
                        if price_1m_raw and price_1m_raw > 0 else 0.0
            change_ytd = round((price_raw - price_ytd_raw) / price_ytd_raw * 100, 2) \
                         if price_ytd_raw and price_ytd_raw > 0 else 0.0

            metrics = get_metrics(yahoo_sym, special, gbp_usd)
            w52 = metrics.get('week52_pct')
            ret = w52 if w52 is not None else (calc_return(price_gbp, low_gbp) or 0)
            news_items, news_agg = get_news(yahoo_sym, analyzer)

            results[ticker] = {
                "price_usd":  price_raw,
                "price_gbp":  price_gbp,
                "low_gbp":    low_gbp or price_gbp * 0.7,
                "high_gbp":   high_gbp or price_gbp * 1.1,
                "return_pct": ret,
                "bar_pct":    bp,
                "change_1d":  change_1d,
                "change_1w":  change_1w,
                "change_1m":  change_1m,
                "change_ytd": change_ytd,
                "vol_1d":     vol_1d_raw,
                "vol_1w":     vol_1w_raw,
                "vol_1m":     vol_1m_raw,
                "news":          news_items,
                "news_sentiment": news_agg,
                **metrics,
            }
            news_note = f"  (news: {len(news_items)}" + (f", sent {news_agg:+.2f})" if news_agg is not None else ")")
            print(f"£{fmt_gbp(price_gbp)}  (1yr: +{ret}%)  (1d: {change_1d:+.2f}%)  (1w: {change_1w:+.2f}%)  (1m: {change_1m:+.2f}%)  (ytd: {change_ytd:+.2f}%){news_note}")
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(ticker)

    today_str = datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%d %H:%M")
    print(f"\nUpdating {HTML_FILE}, {JSON_FILE} and {JS_FILE}...")
    update_html(results, gbp_usd, today_str)
    write_json(results, gbp_usd, today_str)

    print(f"\nDone. {len(results)} stocks updated, {len(errors)} failed.")
    if errors:
        print(f"Failed tickers: {', '.join(errors)}")


if __name__ == "__main__":
    main()
