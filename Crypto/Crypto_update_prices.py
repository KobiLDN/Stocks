#!/usr/bin/env python3
"""
Update prices for the Crypto sector — uses CoinMarketCap API for price data.
Run: python Crypto_update_prices.py
Requires: pip install yfinance requests tzdata vaderSentiment
CMC key: set CMC_API_KEY environment variable (GitHub Secret or local env)
"""

import os
import json
import time
import datetime as dt
import requests
import yfinance as yf
from datetime import datetime
from zoneinfo import ZoneInfo

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _VADER_OK = True
except ImportError:
    _VADER_OK = False

JSON_FILE      = "prices.json"
JS_FILE        = "prices-data.js"
YTD_CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ytd_cache.json")

DASHBOARD_TITLE = "Crypto"

# ── CoinMarketCap API ─────────────────────────────────────────────────────────
CMC_API_KEY = os.environ.get("CMC_API_KEY", "")
CMC_URL     = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

COINGECKO_API_KEY  = os.environ.get("COINGECKO_API_KEY", "")
COINSTATS_API_KEY  = os.environ.get("COINSTATS_API_KEY", "")

# CoinGecko IDs — used for true YTD (Jan 1 → today) via /coins/{id}/history
COINGECKO_IDS = {
    "BTC":  "bitcoin",                  "ETH":  "ethereum",
    "SOL":  "solana",                   "BNB":  "binancecoin",
    "ADA":  "cardano",                  "AVAX": "avalanche-2",
    "XRP":  "ripple",                   "XLM":  "stellar",
    "TRX":  "tron",                     "SUI":  "sui",
    "HBAR": "hedera-hashgraph",         "TON":  "the-open-network",
    "ALGO": "algorand",                 "MINA": "mina-protocol",
    "POL":  "polygon-ecosystem-token",  "DOT":  "polkadot",
    "LINK": "chainlink",                "DOGE": "dogecoin",
    "PEPE": "pepe",
    # ── AI Tokens ─────────────────────────────────────────────────────────────
    "TAO":     "bittensor",             "FET":     "fetch-ai",
    "RNDR":    "render-token",          "OCEAN":   "ocean-protocol",
    "GRT":     "the-graph",            "AGIX":    "singularitynet",
    "NMR":     "numeraire",            "ALT":     "altlayer",
    "AIOZ":    "aioz-network",         "ARKM":    "arkham",
    "WLD":     "worldcoin-wld",        "NEAR":    "near",
    "ICP":     "internet-computer",    "KAITO":   "kaito",
    "VIRTUAL": "virtual-protocol",
}

# CMC numeric IDs — used for OHLCV historical YTD fetch (avoids symbol ambiguity)
CMC_IDS = {
    "BTC": 1,     "ETH": 1027,  "SOL": 5426,  "BNB": 1839,  "ADA": 2010,
    "AVAX": 5805, "XRP": 52,    "XLM": 512,   "TRX": 1958,  "SUI": 20947,
    "HBAR": 4642, "TON": 11419, "ALGO": 4031, "MINA": 20804,"POL": 28321,
    "DOT": 6636,  "LINK": 1975, "DOGE": 74,   "PEPE": 24478,
    # AI Tokens
    "TAO": 22974, "FET": 3773,  "RNDR": 5690,  "OCEAN": 3911,
    "GRT": 6719,  "AGIX": 6945, "NMR": 1732,   "ALT": 28067,
    "AIOZ": 9444, "ARKM": 25691,"WLD": 13502,  "NEAR": 6535,
    "ICP": 8916,  "KAITO": 30999, "VIRTUAL": 29420,
}

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
    "POL":  ("POL",  "POL-USD",       "infra",    "Crypto", "Polygon (MATIC)"),
    "DOT":  ("DOT",  "DOT-USD",       "infra",    "Crypto", "Polkadot"),
    "LINK": ("LINK", "LINK-USD",      "infra",    "Crypto", "Chainlink"),
    # ── Meme ──────────────────────────────────────────────────────────────────
    "DOGE": ("DOGE", "DOGE-USD",      "meme",     "Crypto", "Dogecoin"),
    "PEPE": ("PEPE", "PEPE24478-USD", "meme",     "Crypto", "Pepe"),
    # ── AI Tokens ─────────────────────────────────────────────────────────────
    "TAO":     ("TAO",     "TAO-USD",     "ai", "Crypto", "Bittensor"),
    "FET":     ("FET",     "FET-USD",     "ai", "Crypto", "ASI Alliance"),
    "RNDR":    ("RENDER",  "RNDR-USD",    "ai", "Crypto", "Render"),  # CMC symbol is RENDER post-rebrand
    "OCEAN":   ("OCEAN",   "OCEAN-USD",   "ai", "Crypto", "Ocean Protocol"),
    "GRT":     ("GRT",     "GRT-USD",     "ai", "Crypto", "The Graph"),
    "AGIX":    ("AGIX",    "AGIX-USD",    "ai", "Crypto", "SingularityNET"),
    "NMR":     ("NMR",     "NMR-USD",     "ai", "Crypto", "Numeraire"),
    "ALT":     ("ALT",     "ALT-USD",     "ai", "Crypto", "AltLayer"),
    "AIOZ":    ("AIOZ",    "AIOZ-USD",    "ai", "Crypto", "AIOZ Network"),
    "ARKM":    ("ARKM",    "ARKM-USD",    "ai", "Crypto", "Arkham"),
    "WLD":     ("WLD",     "WLD-USD",     "ai", "Crypto", "Worldcoin"),
    "NEAR":    ("NEAR",    "NEAR-USD",    "ai", "Crypto", "NEAR Protocol"),
    "ICP":     ("ICP",     "ICP-USD",     "ai", "Crypto", "Internet Computer"),
    "KAITO":   ("KAITO",   "KAITO-USD",   "ai", "Crypto", "Kaito"),
    "VIRTUAL": ("VIRTUAL", "VIRTUAL-USD", "ai", "Crypto", "Virtuals Protocol"),
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
            # note: percent_change_90d NOT stored — it's not YTD, CoinGecko provides true YTD
            "market_cap": q.get("market_cap"),
            "volume_24h": q.get("volume_24h"),
            "cmc_rank":   entry.get("cmc_rank"),
        }
    return quotes


def _cg_get(path, params):
    """
    CoinGecko request with automatic Pro → Demo → public fallback.
    Returns parsed JSON or raises on final failure.
    """
    candidates = []
    if COINGECKO_API_KEY:
        candidates += [
            (COINGECKO_PRO_URL,  {"x-cg-pro-api-key":  COINGECKO_API_KEY}),
            (COINGECKO_DEMO_URL, {"x-cg-demo-api-key": COINGECKO_API_KEY}),
        ]
    candidates.append((COINGECKO_DEMO_URL, {}))  # public fallback

    last_err = None
    for base, headers in candidates:
        for attempt in range(3):
            try:
                resp = requests.get(f"{base}{path}", headers=headers,
                                    params=params, timeout=15)
                if resp.status_code == 429:
                    wait = 10 * (attempt + 1)
                    print(f"    [CoinGecko 429 — waiting {wait}s]", end=" ")
                    time.sleep(wait)
                    continue
                if resp.status_code in (401, 403):
                    break  # wrong key type — try next candidate
                resp.raise_for_status()
                return resp.json()
            except requests.HTTPError as e:
                last_err = e
                break
            except Exception as e:
                last_err = e
                if attempt == 2:
                    break
    raise RuntimeError(f"CoinGecko request failed: {last_err}")


def load_ytd_cache():
    """Return cached Jan 1 USD prices for the current year, or None if missing/stale."""
    try:
        with open(YTD_CACHE_PATH) as f:
            cache = json.load(f)
        if cache.get("year") == dt.datetime.utcnow().year:
            return cache["jan1_prices_usd"]
    except Exception:
        pass
    return None

def save_ytd_cache(jan1_prices_usd):
    with open(YTD_CACHE_PATH, "w") as f:
        json.dump({"year": dt.datetime.utcnow().year, "jan1_prices_usd": jan1_prices_usd}, f, indent=2)

def fetch_jan1_prices():
    """Fetch the Jan 1 USD price for each coin via CoinGecko /coins/{id}/history.
    One call per coin — runs once per year, result saved to ytd_cache.json."""
    year  = dt.datetime.utcnow().year
    date  = f"01-01-{year}"   # CoinGecko DD-MM-YYYY format
    jan1  = {}
    for i, (ticker, cg_id) in enumerate(COINGECKO_IDS.items()):
        if i > 0:
            time.sleep(8)
        try:
            data  = _cg_get(f"/coins/{cg_id}/history", {"date": date, "localization": "false"})
            price = data.get("market_data", {}).get("current_price", {}).get("usd")
            jan1[ticker] = price
            print(f"    {ticker}: ${price:,.2f}" if price else f"    {ticker}: N/A")
        except Exception as e:
            print(f"    {ticker}: error — {e}")
            jan1[ticker] = None
    return jan1

def compute_ytd(jan1_prices_usd, current_prices_usd):
    """Calculate YTD % from cached Jan 1 prices and today's CMC prices."""
    ytd_map = {}
    for ticker in COINGECKO_IDS:
        jan1    = jan1_prices_usd.get(ticker)
        current = current_prices_usd.get(ticker)
        if jan1 and jan1 > 0 and current:
            ytd_map[ticker] = round((current - jan1) / jan1 * 100, 2)
        else:
            ytd_map[ticker] = None
    return ytd_map


def fetch_coingecko_data():
    """
    Single CoinGecko market_chart/range call per coin (365-day window).
    Returns: (low_map, high_map, vol_1d_map, vol_1w_map, vol_1m_map, avg_vol_map)
    All dicts keyed by display ticker.
    - Low/High: min/max over the full 365-day price range (true 52-week range)
    - vol_1d:   most recent day's trading volume (USD)
    - vol_1w:   7-day cumulative volume (USD)
    - vol_1m:   30-day cumulative volume (USD)
    - avg_vol:  7-day average daily volume (USD) — used as 'Avg Vol' on metrics page
    YTD is now handled separately via ytd_cache.json (see compute_ytd).
    """
    today   = dt.datetime.utcnow()
    from_ts = int((today - dt.timedelta(days=365)).timestamp())
    to_ts   = int(today.timestamp())

    low_map     = {}
    high_map    = {}
    vol_1d_map  = {}
    vol_1w_map  = {}
    vol_1m_map  = {}
    avg_vol_map = {}

    for i, (ticker, cg_id) in enumerate(COINGECKO_IDS.items()):
        if i > 0:
            time.sleep(8)  # CoinGecko Demo rate limit — 8s buffer for 34 coins (≈ 272s); 5s caused 429s
        try:
            data    = _cg_get(f"/coins/{cg_id}/market_chart/range",
                              {"vs_currency": "usd", "from": from_ts, "to": to_ts})
            prices  = data.get("prices", [])       # [[timestamp_ms, price], ...]
            volumes = data.get("total_volumes", []) # [[timestamp_ms, volume_usd], ...]

            if len(prices) >= 2:
                vals             = [p[1] for p in prices]
                low_map[ticker]  = min(vals)
                high_map[ticker] = max(vals)
            else:
                low_map[ticker] = high_map[ticker] = None

            if len(volumes) >= 7:
                vol_1d_map[ticker]  = volumes[-1][1]
                last_7              = [v[1] for v in volumes[-7:]]
                vol_1w_map[ticker]  = sum(last_7)
                avg_vol_map[ticker] = sum(last_7) / len(last_7)
                last_30             = [v[1] for v in volumes[-30:]] if len(volumes) >= 30 else [v[1] for v in volumes]
                vol_1m_map[ticker]  = sum(last_30)
            else:
                vol_1d_map[ticker] = vol_1w_map[ticker] = vol_1m_map[ticker] = avg_vol_map[ticker] = None

        except Exception as e:
            print(f"    [CoinGecko {ticker}: {e}]", end=" ")
            low_map[ticker] = high_map[ticker] = None
            vol_1d_map[ticker] = vol_1w_map[ticker] = vol_1m_map[ticker] = avg_vol_map[ticker] = None
            print(f"    [CoinGecko rate-limit cooldown 60s]", end=" ")
            time.sleep(60)

    return low_map, high_map, vol_1d_map, vol_1w_map, vol_1m_map, avg_vol_map



def get_news_coinstats(ticker, analyzer, max_items=5):
    """
    CoinStats API — crypto-specific news fallback when yfinance returns 0 headlines.
    Uses authenticated endpoint if COINSTATS_API_KEY is set, else public endpoint.
    """
    try:
        headers = {"X-API-KEY": COINSTATS_API_KEY} if COINSTATS_API_KEY else {}
        resp = requests.get(
            "https://api.coinstats.app/public/v1/news",
            params={"coin": ticker, "limit": max_items},
            headers=headers,
            timeout=10,
        )
        if resp.status_code != 200:
            return [], None
        articles = resp.json().get("news", [])
        items = []
        for a in articles[:max_items]:
            title = a.get("title")
            if not title:
                continue
            score = None
            if analyzer:
                try:
                    score = round(analyzer.polarity_scores(title)["compound"], 3)
                except Exception:
                    pass
            items.append({
                "title":     title,
                "publisher": a.get("source"),
                "url":       a.get("link") or a.get("url"),
                "published": a.get("date"),
                "sentiment": score,
            })
        scored = [i["sentiment"] for i in items if i["sentiment"] is not None]
        agg    = round(sum(scored) / len(scored), 3) if scored else None
        return items, agg
    except Exception:
        return [], None


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
        # Volume: prefer CoinGecko (daily from 365-day chart), fall back to CMC for 1d only
        vol_1d_cg  = r.get("vol_1d_cg")
        vol_1w_cg  = r.get("vol_1w_cg")
        vol_1m_cg  = r.get("vol_1m_cg")
        avg_vol_cg = r.get("avg_vol_cg")
        vol_1d_raw = vol_1d_cg if vol_1d_cg is not None else r.get("volume_24h_cmc")
        avg_vol_m  = round(avg_vol_cg / 1e6, 2) if avg_vol_cg else (
                     round(vol_1d_raw / 1e6, 2) if vol_1d_raw else None)

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
            "change_ytd":       f"{r['change_ytd']:+.2f}%" if r['change_ytd'] is not None else None,
            "return_1yr":       f"{r['change_ytd']:+.0f}%" if r['change_ytd'] is not None else None,
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
            # volume from CoinGecko (USD); 1d falls back to CMC if CG unavailable
            "vol_1d":           round(vol_1d_raw)  if vol_1d_raw  is not None else None,
            "vol_1w":           round(vol_1w_cg)   if vol_1w_cg   is not None else None,
            "vol_1m":           round(vol_1m_cg)   if vol_1m_cg   is not None else None,
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

    # Build current USD price map
    current_prices_usd = {
        ticker: cmc_quotes[v[0]]["price_usd"]
        for ticker, v in STOCKS.items()
        if v[0] in cmc_quotes
    }

    # ── YTD: load from cache, fetch Jan 1 prices once if missing/stale ──────────
    jan1_prices = load_ytd_cache()
    if jan1_prices is None:
        print(f"Fetching Jan 1 {dt.datetime.utcnow().year} prices from CoinGecko (YTD cache)...")
        jan1_prices = fetch_jan1_prices()
        save_ytd_cache(jan1_prices)
        print(f"  Cached {sum(1 for v in jan1_prices.values() if v is not None)}/{len(jan1_prices)} prices")
    else:
        print(f"  YTD cache hit ({dt.datetime.utcnow().year}) — skipping Jan 1 fetch")
    ytd_map = compute_ytd(jan1_prices, current_prices_usd)
    print(f"  YTD computed for {sum(1 for v in ytd_map.values() if v is not None)}/{len(ytd_map)} coins")

    # ── 52-week range + volume from CoinGecko (365-day chart) ───────────────────
    print("Fetching 52-week range + volume from CoinGecko (365-day window)...")
    try:
        low_map, high_map, vol_1d_cg, vol_1w_cg, vol_1m_cg, avg_vol_cg = fetch_coingecko_data()
        print(f"  Fetched range/volume for {sum(1 for v in low_map.values() if v is not None)}/{len(low_map)} coins")
    except Exception as e:
        print(f"  CoinGecko unavailable ({e}) — no 52w range / CG volume")
        low_map, high_map = {}, {}
        vol_1d_cg, vol_1w_cg, vol_1m_cg, avg_vol_cg = {}, {}, {}, {}

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

            # 52-week range from CoinGecko (min/max of 365-day price series)
            low_raw  = low_map.get(ticker)
            high_raw = high_map.get(ticker)
            low_gbp  = to_gbp(low_raw,  gbp_usd) if low_raw  else price_gbp * 0.5
            high_gbp = to_gbp(high_raw, gbp_usd) if high_raw else price_gbp * 1.5
            bp = bar_pct(price_gbp, low_gbp, high_gbp)

            # YTD: true Jan 1 → today via CoinGecko. No CMC fallback — CMC's
            # percent_change_90d is a 90-day return, not YTD, and would mislead.
            change_ytd = ytd_map.get(ticker)  # None if CoinGecko failed for this coin

            news_items, news_agg = get_news(yf_sym, analyzer)
            if not news_items:  # yfinance missed — try CoinStats (no key, VADER sentiment)
                news_items, news_agg = get_news_coinstats(ticker, analyzer)

            # Drop articles older than 7 days — yfinance often returns years-old stale data
            MAX_NEWS_AGE = 7 * 86400
            now_ts = time.time()
            news_items = [n for n in news_items if n.get("published") and (now_ts - n["published"]) <= MAX_NEWS_AGE]
            if news_items:
                scored = [n["sentiment"] for n in news_items if n.get("sentiment") is not None]
                news_agg = round(sum(scored) / len(scored), 3) if scored else None
            else:
                news_agg = None

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
                # Volume: CoinGecko (daily from 365-day chart) preferred; CMC fallback for vol_1d only
                "vol_1d_cg":      vol_1d_cg.get(ticker),    # CoinGecko latest day USD volume
                "vol_1w_cg":      vol_1w_cg.get(ticker),    # CoinGecko 7-day cumulative USD
                "vol_1m_cg":      vol_1m_cg.get(ticker),    # CoinGecko 30-day cumulative USD
                "avg_vol_cg":     avg_vol_cg.get(ticker),   # CoinGecko 7-day average daily USD
                "volume_24h_cmc": q.get("volume_24h"),      # CMC 24h rolling — fallback only
                "cmc_rank":       q.get("cmc_rank"),
                "news":           news_items,
                "news_sentiment": news_agg,
            }

            news_note = f"  (news: {len(news_items)}" + (
                f", sent {news_agg:+.2f})" if news_agg is not None else ")")
            ytd_str = f"(ytd: {change_ytd:+.2f}%)" if change_ytd is not None else "(ytd: N/A)"
            print(
                f"£{fmt_gbp(price_gbp)}  "
                f"(1d: {q['change_1d']:+.2f}%)  "
                f"(1w: {q['change_1w']:+.2f}%)  "
                f"(1m: {q['change_1m']:+.2f}%)  "
                + ytd_str + news_note
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
