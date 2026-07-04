#!/usr/bin/env python3
"""
Fetch macro market indicators (SPY, QQQ, VIX) from Yahoo Finance and write
market-data.js + market.json for the Market overview page.

Run: python update_market.py
Requires: pip install yfinance

Mirrors the conventions in the per-sector *_update_prices.py scripts:
yfinance + fast_info, .iloc index-based lookbacks (-6 for 1-week), and a
London-timezone "updated" timestamp. Percent changes are stored as signed
strings ("+1.23%") to match the rest of the site's data format.
"""

import yfinance as yf
import json
import contextlib
import io
from datetime import datetime
from zoneinfo import ZoneInfo

JSON_FILE = "market.json"
JS_FILE   = "market-data.js"

# key -> yahoo symbol
INDICES = {
    "spy": "SPY",
    "qqq": "QQQ",
    "vix": "^VIX",
}


def fmt_pct(current, ref):
    """Signed percent-change string e.g. '+1.23%', or None when not computable."""
    if current is None or ref is None or ref == 0:
        return None
    val = (current - ref) / ref * 100
    return f"{'+' if val >= 0 else ''}{val:.2f}%"


def pct_val(current, ref):
    """Raw percent change (float) or None — used for regime comparison."""
    if current is None or ref is None or ref == 0:
        return None
    return (current - ref) / ref * 100


def vix_signal(level):
    """Human-readable VIX fear label used by portfolio AI."""
    if level is None:
        return "unknown"
    if level < 15:
        return "calm"
    if level < 25:
        return "normal"
    if level < 30:
        return "high_fear"
    return "extreme_fear"


def get_index(yahoo_symbol, include_long=False):
    """Return dict with price/level + 1d/1w/1m changes (+ ytd/1y when include_long=True)."""
    t = yf.Ticker(yahoo_symbol)
    fi = t.fast_info

    try:
        price = float(fi.last_price)
    except Exception:
        price = None
    try:
        prev_close = float(fi.previous_close)
    except Exception:
        prev_close = None

    price_1w = price_1m = price_ytd = price_1y = None
    try:
        period = "1y" if include_long else "1mo"
        with contextlib.redirect_stderr(io.StringIO()):
            hist = t.history(period=period)
        if len(hist) >= 6:
            price_1w = float(hist["Close"].iloc[-6])    # ~5 trading days back
        if include_long:
            if len(hist) >= 23:
                price_1m = float(hist["Close"].iloc[-23])   # ~22 trading days back
            elif len(hist) >= 1:
                price_1m = float(hist["Close"].iloc[0])
            if len(hist) >= 1:
                price_1y = float(hist["Close"].iloc[0])     # oldest row ≈ 1 year ago
            # YTD: first trading day of current calendar year
            year = datetime.now().year
            ytd_rows = hist[hist.index.year == year]
            if not ytd_rows.empty:
                price_ytd = float(ytd_rows["Close"].iloc[0])
        else:
            if len(hist) >= 1:
                price_1m = float(hist["Close"].iloc[0])
        # Fall back to history if fast_info was unavailable.
        if price is None and len(hist) >= 1:
            price = float(hist["Close"].iloc[-1])
        if prev_close is None and len(hist) >= 2:
            prev_close = float(hist["Close"].iloc[-2])
    except Exception:
        pass

    def rnd(v):
        return round(v, 2) if v is not None else None

    result = {
        "price":     round(price, 2) if price is not None else None,
        "change_1d": rnd(pct_val(price, prev_close)),
        "change_1w": rnd(pct_val(price, price_1w)),
        "change_1m": rnd(pct_val(price, price_1m)),
        "_v1w":      pct_val(price, price_1w),
    }
    if include_long:
        result["change_ytd"] = rnd(pct_val(price, price_ytd))
        result["change_1y"]  = rnd(pct_val(price, price_1y))
    return result


def compute_regime(spy, qqq, vix):
    """correction → high_fear → normal, per issue #19 thresholds."""
    spy_1w = spy.get("_v1w")
    qqq_1w = qqq.get("_v1w")
    vix_level = vix.get("price")
    if spy_1w is not None and qqq_1w is not None and spy_1w < -3 and qqq_1w < -3:
        return "correction"
    if vix_level is not None and vix_level > 25:
        return "high_fear"
    return "normal"


def main():
    print("Fetching macro indicators (SPY, QQQ, VIX)...")
    data = {}
    errors = []
    for key, sym in INDICES.items():
        long = key in ("spy", "qqq")
        try:
            print(f"  {key.upper():<4} ({sym})... ", end="", flush=True)
            data[key] = get_index(sym, include_long=long)
            d = data[key]
            ytd_str = f"  ytd {d.get('change_ytd')}%" if long else ""
            print(f"{d['price']}  1d {d['change_1d']}%  1w {d['change_1w']}%{ytd_str}")
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(key)
            base = {"price": None, "change_1d": None, "change_1w": None,
                    "change_1m": None, "_v1w": None}
            if long:
                base.update({"change_ytd": None, "change_1y": None})
            data[key] = base

    regime = compute_regime(data["spy"], data["qqq"], data["vix"])
    vix = data["vix"]

    out = {
        "updated": datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%d %H:%M"),
        "spy": {k: data["spy"][k] for k in ("price", "change_1d", "change_1w", "change_1m", "change_ytd", "change_1y")},
        "qqq": {k: data["qqq"][k] for k in ("price", "change_1d", "change_1w", "change_1m", "change_ytd", "change_1y")},
        "vix": {
            "level":    vix["price"],
            "change_1d": vix["change_1d"],
            "regime":   regime,
            "signal":   vix_signal(vix["price"]),
        },
        "market_regime": regime,
    }

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    with open(JS_FILE, "w", encoding="utf-8") as f:
        f.write(f"window.MARKET_DATA = {json.dumps(out, indent=2)};\n")

    print(f"\nDone. Regime: {regime.upper()}. {len(errors)} failed."
          + (f" Failed: {errors}" if errors else ""))


if __name__ == "__main__":
    main()
