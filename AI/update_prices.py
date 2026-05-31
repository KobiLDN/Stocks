#!/usr/bin/env python3
"""
Update index.html with live prices from Yahoo Finance.
Run: python update_prices.py
Requires: pip install yfinance beautifulsoup4 vaderSentiment
"""

import yfinance as yf
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# News sentiment is keyless (VADER, local). It is strictly secondary —
# a missing/broken VADER must never break the price update, so the import
# is guarded and news scoring degrades gracefully.
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _VADER_OK = True
except ImportError:
    _VADER_OK = False

JSON_FILE = "prices.json"
JS_FILE   = "prices-data.js"

# ticker → (yahoo_symbol, category, exchange, special, company_name)
# special: None | "lse_pence" | "jpy"
STOCKS = {
    "SNDK":  ("SNDK",   "memory",        "NASDAQ", None,        "SanDisk Corporation"),
    "WDC":   ("WDC",    "memory",        "NASDAQ", None,        "Western Digital"),
    "285A":  ("285A.T", "memory",        "TSE",    "jpy",       "Kioxia Holdings"),
    "MU":    ("MU",     "memory",        "NASDAQ", None,        "Micron Technology"),
    "STX":   ("STX",    "memory",        "NASDAQ", None,        "Seagate Technology"),
    "MRVL":  ("MRVL",   "memory",        "NASDAQ", None,        "Marvell Technology"),
    "P":     ("P",      "memory",        "NYSE",   None,        "Everpure"),
    "RR.":   ("RR.L",   "nuclear-ops",   "LSE",    "lse_pence", "Rolls-Royce Holdings"),
    "CEG":   ("CEG",    "nuclear-ops",   "NASDAQ", None,        "Constellation Energy"),
    "VST":   ("VST",    "nuclear-ops",   "NYSE",   None,        "Vistra Corp"),
    "TLN":   ("TLN",    "nuclear-ops",   "NYSE",   None,        "Talen Energy"),
    "BEP":   ("BEP",    "nuclear-ops",   "NYSE",   None,        "Brookfield Renewable"),
    "BEPC":  ("BEPC",   "nuclear-ops",   "NYSE",   None,        "Brookfield Renewable Corp"),
    "GEV":   ("GEV",    "smr",           "NYSE",   None,        "GE Vernova"),
    "BWXT":  ("BWXT",   "smr",           "NYSE",   None,        "BWX Technologies"),
    "SMR":   ("SMR",    "smr",           "NYSE",   None,        "NuScale Power"),
    "OKLO":  ("OKLO",   "smr",           "NYSE",   None,        "Oklo Inc"),
    "NNE":   ("NNE",    "smr",           "NASDAQ", None,        "NANO Nuclear Energy"),
    "CCJ":   ("CCJ",    "uranium",       "NYSE",   None,        "Cameco Corporation"),
    "UEC":   ("UEC",    "uranium",       "NYSE",   None,        "Uranium Energy Corp"),
    "LEU":   ("LEU",    "uranium",       "NYSE",   None,        "Centrus Energy"),
    "VRT":   ("VRT",    "power-infra",   "NYSE",   None,        "Vertiv Holdings"),
    "ETN":   ("ETN",    "power-infra",   "NYSE",   None,        "Eaton Corporation"),
    "POWL":  ("POWL",   "power-infra",   "NASDAQ", None,        "Powell Industries"),
    "EQIX":  ("EQIX",   "dc-operators",  "NASDAQ", None,        "Equinix"),
    "DLR":   ("DLR",    "dc-operators",  "NYSE",   None,        "Digital Realty"),
    "AMT":   ("AMT",    "dc-operators",  "NYSE",   None,        "American Tower"),
    "GOOGL": ("GOOGL",  "hyperscalers",  "NASDAQ", None,        "Alphabet (Google)"),
    "MSFT":  ("MSFT",   "hyperscalers",  "NASDAQ", None,        "Microsoft"),
    "AMZN":  ("AMZN",   "hyperscalers",  "NASDAQ", None,        "Amazon"),
    "META":  ("META",   "hyperscalers",  "NASDAQ", None,        "Meta Platforms"),
    "IREN":  ("IREN",   "ai-compute",    "NASDAQ", None,        "Iris Energy"),
    "CORZ":  ("CORZ",   "ai-compute",    "NASDAQ", None,        "Core Scientific"),
    "WULF":  ("WULF",   "ai-compute",    "NASDAQ", None,        "TeraWulf"),
    "HUT":   ("HUT",    "ai-compute",    "NASDAQ", None,        "Hut 8 Mining"),
    "SMCI":  ("SMCI",   "ai-compute",    "NASDAQ", None,        "Super Micro Computer"),
    "DELL":  ("DELL",   "ai-compute",    "NYSE",   None,        "Dell Technologies"),
    "COHR":  ("COHR",   "fibre-optical", "NYSE",   None,        "Coherent Corp"),
    "LITE":  ("LITE",   "fibre-optical", "NASDAQ", None,        "Lumentum Holdings"),
    "AAOI":  ("AAOI",   "fibre-optical", "NASDAQ", None,        "Applied Optoelectronics"),
    "FN":    ("FN",     "fibre-optical", "NYSE",   None,        "Fabrinet"),
    "MTSI":  ("MTSI",   "dsp-semi",      "NASDAQ", None,        "MACOM Technology"),
    "SMTC":  ("SMTC",   "dsp-semi",      "NASDAQ", None,        "Semtech"),
    "CRDO":  ("CRDO",   "dsp-semi",      "NASDAQ", None,        "Credo Technology"),
    "MXL":   ("MXL",    "dsp-semi",      "NASDAQ", None,        "MaxLinear"),
    "KEYS":  ("KEYS",   "test-equip",    "NYSE",   None,        "Keysight Technologies"),
    "VIAV":  ("VIAV",   "test-equip",    "NASDAQ", None,        "Viavi Solutions"),
    "AXTI":  ("AXTI",   "materials",     "NASDAQ", None,        "AXT Inc"),
}

# Speculative tickers — show return from 52wk low with asterisk
SPECULATIVE = {"OKLO", "NNE", "SMR", "IREN", "CORZ", "WULF"}


def get_fx_rates():
    """Fetch GBP/USD and GBP/JPY rates."""
    gbp_usd = yf.Ticker("GBPUSD=X").fast_info["last_price"]
    gbp_jpy = yf.Ticker("GBPJPY=X").fast_info["last_price"]
    return gbp_usd, gbp_jpy


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
        ytd_hist = t.history(start=f'{year}-01-02', end=f'{year}-01-10')
        if len(ytd_hist) >= 1:
            price_ytd = float(ytd_hist['Close'].iloc[0])
    except Exception:
        pass
    return price, low52, high52, prev_close, price_1w, price_1m, price_ytd, vol_1d, vol_1w, vol_1m


def get_metrics(yahoo_symbol, special, gbp_usd, gbp_jpy):
    """Fetch fundamental metrics from ticker.info. Returns dict or {} on failure."""
    try:
        info = yf.Ticker(yahoo_symbol).info

        # Market cap — convert to GBP billions
        mc_raw = info.get('marketCap')
        if mc_raw and mc_raw > 0:
            mc_gbp = to_gbp(mc_raw, special, gbp_usd, gbp_jpy)
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


def to_gbp(price, special, gbp_usd, gbp_jpy):
    if special == "lse_pence":
        return price / 100          # already GBP pence → £
    elif special == "jpy":
        return price / gbp_jpy
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


def return_class(pct, speculative=False):
    # speculative param kept for signature compatibility; no longer caps colour
    if pct >= 200:
        return "return-mega"
    elif pct >= 50:
        return "return-positive"
    elif pct >= 0:
        return "return-modest"
    else:
        return "return-negative"


def write_json(results, gbp_usd, today_str):
    stocks = []
    for ticker, (yahoo_sym, cat, exchange, special, company_name) in STOCKS.items():
        if ticker not in results:
            continue
        r = results[ticker]
        is_spec = ticker in SPECULATIVE
        stocks.append({
            "ticker":           ticker,
            "company_name":     company_name,
            "category":         cat,
            "exchange":         exchange,
            "price_gbp":        fmt_gbp(r["price_gbp"]),
            "price_usd":        round(r["price_usd"], 2),
            "change_1d":        f"{r['change_1d']:+.2f}%",
            "change_1w":        f"{r['change_1w']:+.2f}%",
            "change_1m":        f"{r['change_1m']:+.2f}%",
            "change_ytd":       f"{r['change_ytd']:+.2f}%",
            "return_1yr":       f"{r['return_pct']:+}%{'*' if is_spec else ''}",
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
    gbp_usd, gbp_jpy = get_fx_rates()
    print(f"  £1 = ${gbp_usd:.4f}  |  £1 = ¥{gbp_jpy:.2f}")

    analyzer = SentimentIntensityAnalyzer() if _VADER_OK else None
    if analyzer is None:
        print("  [vaderSentiment not installed — news headlines kept, sentiment skipped]")

    results = {}
    errors  = []

    for ticker, (yahoo_sym, cat, exchange, special, company_name) in STOCKS.items():
        try:
            print(f"  {ticker:<6} ({yahoo_sym})... ", end="", flush=True)
            price_raw, low_raw, high_raw, prev_close_raw, price_1w_raw, price_1m_raw, price_ytd_raw, vol_1d_raw, vol_1w_raw, vol_1m_raw = get_stock_data(yahoo_sym)

            price_gbp = to_gbp(price_raw, special, gbp_usd, gbp_jpy)
            low_gbp   = to_gbp(low_raw,   special, gbp_usd, gbp_jpy) if low_raw       else None
            high_gbp  = to_gbp(high_raw,  special, gbp_usd, gbp_jpy) if high_raw      else None

            bp  = bar_pct(price_gbp, low_gbp, high_gbp)

            change_1d = round((price_raw - prev_close_raw) / prev_close_raw * 100, 2) \
                        if prev_close_raw and prev_close_raw > 0 else 0.0
            change_1w = round((price_raw - price_1w_raw) / price_1w_raw * 100, 2) \
                        if price_1w_raw and price_1w_raw > 0 else 0.0
            change_1m = round((price_raw - price_1m_raw) / price_1m_raw * 100, 2) \
                        if price_1m_raw and price_1m_raw > 0 else 0.0
            change_ytd = round((price_raw - price_ytd_raw) / price_ytd_raw * 100, 2) \
                         if price_ytd_raw and price_ytd_raw > 0 else 0.0

            metrics = get_metrics(yahoo_sym, special, gbp_usd, gbp_jpy)
            # Use Yahoo Finance's own 52-week change; fall back to 52wk-low calc for new stocks
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
            print(f"£{fmt_gbp(price_gbp)}  (1yr: {ret:+}%)  (1d: {change_1d:+.2f}%)  (1w: {change_1w:+.2f}%)  (1m: {change_1m:+.2f}%)  (ytd: {change_ytd:+.2f}%){news_note}")
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(ticker)

    today_str = datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%d %H:%M")
    print(f"\nUpdating {JSON_FILE} and {JS_FILE}...")
    write_json(results, gbp_usd, today_str)

    print(f"\nDone. {len(results)} stocks updated, {len(errors)} failed.")
    if errors:
        print(f"Failed tickers: {', '.join(errors)}")


if __name__ == "__main__":
    main()
