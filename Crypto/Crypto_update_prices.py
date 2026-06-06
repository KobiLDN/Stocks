#!/usr/bin/env python3
"""
Update prices for the Crypto sector — uses CoinMarketCap API for price data.
Run: python Crypto_update_prices.py
Requires: pip install yfinance requests tzdata vaderSentiment
CMC key: set CMC_API_KEY environment variable (GitHub Secret or local env)
"""

import os
import json
import requests
import yfinance as yf
from datetime import datetime
from zoneinfo import ZoneInfo

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _VADER_OK = True
except ImportError:
    _VADER_OK = False

JSON_FILE = "prices.json"
JS_FILE   = "prices-data.js"

DASHBOARD_TITLE = "Crypto"

# ── CoinMarketCap API ─────────────────────────────────────────────────────────
CMC_API_KEY = os.environ.get("CMC_API_KEY", "")
CMC_URL     = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

# display ticker → (cmc_symbol, yf_symbol, category, exchange, company_name)
# cmc_symbol: what CMC knows it as (MATIC rebranded to POL on CMC)
STOCKS = {
    # ── Bitcoin ───────────────────────────────────────────────────────────────
    "BTC":  ("BTC",  "BTC-USD",       "bitcoin",  "Crypto", "Bitcoin"),
    # ── Layer 1 ───────────────────────────────────────────────────────────────
    "ETH":  ("ETH",  "ETH-USD",       "layer1",   "Crypto", "Ethereum"),
    "SOL":  ("SOL",  "SOL-USD",       "layer1",   "Crypto", "Solana"),
    "BNB":  ("BNB",  "BNB-USD",       "layer1",   "Crypto", "BNB"),
    "ADA":  ("ADA",  "ADA-USD",       "layer1",   "Crypto", "Cardano"),
    "AVAX": ("AVAX", "AVAX-USD",      "layer1",   "Crypto", "Avalanche"),
    # ── Payments ──────────────────────────────────────────────────────────────
    "XRP":  ("XRP",  "XRP-USD",       "payments", "Crypto", "XRP"),
    "XLM":  ("XLM",  "XLM-USD",       "payments", "Crypto", "Stellar"),
    "TRX":  ("TRX",  "TRX-USD",       "payments", "Crypto", "TRON"),
    # ── Emerging ──────────────────────────────────────────────────────────────
    "SUI":  ("SUI",  "SUI20947-USD",  "emerging", "Crypto", "Sui"),
    "HBAR": ("HBAR", "HBAR-USD",      "emerging", "Crypto", "Hedera"),
    "TON":  ("TON",  "TON11419-USD",  "emerging", "Crypto", "Toncoin"),
    "ALGO": ("ALGO", "ALGO-USD",      "emerging", "Crypto", "Algorand"),
    "MINA": ("MINA", "MINA-USD",      "emerging", "Crypto", "Mina"),
    # ── Infrastructure ────────────────────────────────────────────────────────
    "MATIC":("POL",  "MATIC-USD",     "infra",    "Crypto", "Polygon"),
    "DOT":  ("DOT",  "DOT-USD",       "infra",    "Crypto", "Polkadot"),
    "LINK": ("LINK", "LINK-USD",      "infra",    "Crypto", "Chainlink"),
    # ── Meme ──────────────────────────────────────────────────────────────────
    "DOGE": ("DOGE", "DOGE-USD",      "meme",     "Crypto", "Dogecoin"),
    "PEPE": ("PEPE", "PEPE24478-USD", "meme",     "Crypto", "Pepe"),
}


def get_fx_rates():
    """Fetch GBP/USD rate via yfinance."""
    gbp_usd = yf.Ticker("GBPUSD=X").fast_info["last_price"]
    return gbp_usd


def fetch_cmc_quotes():
    """
    Single bulk call to CMC for all coins.
    Returns dict: cmc_symbol → quote dict (price, changes, market_cap, volume).
    """
    cmc_symbols = list({v[0] for v in STOCKS.values()})
    resp = requests.get(
        CMC_URL,
        headers={"X-CMC_PRO_API_KEY": CMC_API_KEY, "Accept": "application/json"},
        params={"symbol": ",".join(cmc_symbols), "convert": "USD"},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("status", {}).get("error_code", 0) != 0:
        raise RuntimeError(f"CMC API error: {data['status']}")

    quotes = {}
    for sym, entries in data["data"].items():
        # CMC returns a list when a symbol is ambiguous; take first entry
        entry = entries[0] if isinstance(entries, list) else entries
        q = entry["quote"]["USD"]
        quotes[sym] = {
            "price_usd":  q["price"],
            "change_1d":  q.get("percent_change_24h") or 0.0,
            "change_1w":  q.get("percent_change_7d")  or 0.0,
            "change_1m":  q.get("percent_change_30d") or 0.0,
            "change_ytd": q.get("percent_change_1y")  or 0.0,
            "market_cap": q.get("market_cap"),
            "volume_24h": q.get("volume_24h"),
            "cmc_rank":   entry.get("cmc_rank"),
        }
    return quotes


def get_yf_supplemental(yf_symbol):
    """Fetch 52-week high/low and YTD start price from yfinance (single Ticker object)."""
    year_low = year_high = price_ytd = None
    try:
        t  = yf.Ticker(yf_symbol)
        fi = t.fast_info
        year_low  = fi.get("year_low")
        year_high = fi.get("year_high")
        import contextlib, io as _io
        with contextlib.redirect_stderr(_io.StringIO()):
            ytd_hist = t.history(period="ytd", raise_errors=False)
        if len(ytd_hist) >= 1:
            price_ytd = float(ytd_hist["Close"].iloc[0])
    except Exception:
        pass
    return year_low, year_high, price_ytd


def get_news(yf_symbol, analyzer, max_items=5):
    """Fetch recent headlines via yfinance and score with VADER."""
    try:
        raw = yf.Ticker(yf_symbol).news or []
    except Exception as e:
        print(f"[news error: {e}]", end=" ")
        return [], None

    items = []
    for n in raw[:max_items]:
        if not isinstance(n, dict):
            continue
        content = n.get("content")
        if isinstance(content, dict):
            title  = content.get("title")
            pub    = (content.get("provider") or {}).get("displayName")
            url    = ((content.get("canonicalUrl") or {}).get("url")
                      or (content.get("clickThroughUrl") or {}).get("url"))
            ts     = content.get("pubDate") or content.get("displayTime")
            pub_ts = None
            if ts:
                try:
                    pub_ts = int(datetime.fromisoformat(
                        ts.replace("Z", "+00:00")).timestamp())
                except Exception:
                    pub_ts = None
        else:
            title  = n.get("title")
            pub    = n.get("publisher")
            url    = n.get("link")
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


def to_gbp(price_usd, gbp_usd):
    return price_usd / gbp_usd


def fmt_gbp(val):
    if val >= 10:
        return str(round(val))
    elif val >= 1:
        return f"{val:.2f}"
    elif val >= 0.01:
        return f"{val:.4f}"
    elif val >= 0.000001:
        return f"{val:.8f}"
    else:
        return f"{val:.10f}"


def bar_pct(current, low, high):
    if low and high and high > low:
        pct = (current - low) / (high - low) * 100
        return min(99, max(1, round(pct)))
    return 50


def write_json(results, gbp_usd, today_str):
    stocks = []
    for ticker, (cmc_sym, yf_sym, cat, exchange, company_name) in STOCKS.items():
        if ticker not in results:
            continue
        r = results[ticker]
        mc_usd     = r.get("market_cap")
        mc_gbp_b   = round(mc_usd / gbp_usd / 1e9, 3) if mc_usd else None
        vol_24h    = r.get("volume_24h")
        avg_vol_m  = round(vol_24h / 1e6, 2) if vol_24h else None

        stocks.append({
            "ticker":           ticker,
            "yf_ticker":        yf_sym,
            "company_name":     company_name,
            "category":         cat,
            "exchange":         exchange,
            "price_gbp":        fmt_gbp(r["price_gbp"]),
            "price_usd":        round(r["price_usd"], 6),
            "change_1d":        f"{r['change_1d']:+.2f}%",
            "change_1w":        f"{r['change_1w']:+.2f}%",
            "change_1m":        f"{r['change_1m']:+.2f}%",
            "change_ytd":       f"{r['change_ytd']:+.2f}%",
            "return_1yr":       f"{r['change_ytd']:+.0f}%",
            "low_gbp":          fmt_gbp(r["low_gbp"]),
            "high_gbp":         fmt_gbp(r["high_gbp"]),
            "bar_pct":          r["bar_pct"],
            "market_cap_gbp_b": mc_gbp_b,
            "avg_volume_m":     avg_vol_m,
            "cmc_rank":         r.get("cmc_rank"),
            # not applicable for crypto — kept for schema compatibility
            "beta":             None,
            "pe_ratio":         None,
            "div_yield_pct":    None,
            "short_pct":        None,
            "analyst":          None,
            "analyst_score":    None,
            "vol_1d":           round(vol_24h) if vol_24h else None,
            "vol_1w":           None,
            "vol_1m":           None,
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
    if not CMC_API_KEY:
        print("ERROR: CMC_API_KEY environment variable not set.")
        print("  Windows: set CMC_API_KEY=your_key")
        print("  Linux:   export CMC_API_KEY=your_key")
        raise SystemExit(1)

    print("Fetching FX rates...")
    gbp_usd = get_fx_rates()
    print(f"  £1 = ${gbp_usd:.4f}")

    print("Fetching all crypto prices from CoinMarketCap (1 bulk call)...")
    cmc_quotes = fetch_cmc_quotes()
    print(f"  Got {len(cmc_quotes)} quotes from CMC")

    analyzer = SentimentIntensityAnalyzer() if _VADER_OK else None
    if analyzer is None:
        print("  [vaderSentiment not installed — news skipped]")

    results = {}
    errors  = []

    for ticker, (cmc_sym, yf_sym, cat, exchange, company_name) in STOCKS.items():
        try:
            print(f"  {ticker:<6} ({cmc_sym})... ", end="", flush=True)

            q = cmc_quotes.get(cmc_sym)
            if not q:
                raise ValueError(f"No CMC data for symbol '{cmc_sym}'")

            price_usd = q["price_usd"]
            price_gbp = to_gbp(price_usd, gbp_usd)

            # 52-week range + YTD start price from yfinance (single Ticker object)
            low_raw, high_raw, price_ytd = get_yf_supplemental(yf_sym)
            low_gbp  = to_gbp(low_raw,  gbp_usd) if low_raw  else price_gbp * 0.5
            high_gbp = to_gbp(high_raw, gbp_usd) if high_raw else price_gbp * 1.5
            bp = bar_pct(price_gbp, low_gbp, high_gbp)

            # YTD: compute from yfinance Jan-1 close; fall back to CMC 1y (may be 0 on free plan)
            if price_ytd and price_ytd > 0:
                change_ytd = round((price_usd - price_ytd) / price_ytd * 100, 2)
            else:
                change_ytd = round(q["change_ytd"], 2)

            news_items, news_agg = get_news(yf_sym, analyzer)

            results[ticker] = {
                "price_usd":      price_usd,
                "price_gbp":      price_gbp,
                "change_1d":      round(q["change_1d"], 2),
                "change_1w":      round(q["change_1w"], 2),
                "change_1m":      round(q["change_1m"], 2),
                "change_ytd":     change_ytd,
                "low_gbp":        low_gbp,
                "high_gbp":       high_gbp,
                "bar_pct":        bp,
                "market_cap":     q.get("market_cap"),
                "volume_24h":     q.get("volume_24h"),
                "cmc_rank":       q.get("cmc_rank"),
                "news":           news_items,
                "news_sentiment": news_agg,
            }

            news_note = f"  (news: {len(news_items)}" + (
                f", sent {news_agg:+.2f})" if news_agg is not None else ")")
            print(
                f"£{fmt_gbp(price_gbp)}  "
                f"(1d: {q['change_1d']:+.2f}%)  "
                f"(1w: {q['change_1w']:+.2f}%)  "
                f"(1m: {q['change_1m']:+.2f}%)  "
                f"(ytd: {change_ytd:+.2f}%)"
                f"{news_note}"
            )

        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(ticker)

    today_str = datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%d %H:%M")
    print(f"\nUpdating {JSON_FILE} and {JS_FILE}...")
    write_json(results, gbp_usd, today_str)

    print(f"\nDone. {len(results)} coins updated, {len(errors)} failed.")
    if errors:
        print(f"Failed tickers: {', '.join(errors)}")


if __name__ == "__main__":
    main()
