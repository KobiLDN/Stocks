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


def get_index(yahoo_symbol):
    """Return dict with price/level + 1d/1w/1m changes (formatted + raw 1w)."""
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

    price_1w = price_1m = None
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            hist = t.history(period="1mo")
        if len(hist) >= 6:
            price_1w = float(hist["Close"].iloc[-6])   # 6 trading days back
        if len(hist) >= 1:
            price_1m = float(hist["Close"].iloc[0])     # oldest row in window
        # Fall back to history if fast_info was unavailable.
        if price is None and len(hist) >= 1:
            price = float(hist["Close"].iloc[-1])
        if prev_close is None and len(hist) >= 2:
            prev_close = float(hist["Close"].iloc[-2])
    except Exception:
        pass

    def rnd(v):
        return round(v, 2) if v is not None else None

    return {
        "price":     round(price, 2) if price is not None else None,
        "change_1d": rnd(pct_val(price, prev_close)),
        "change_1w": rnd(pct_val(price, price_1w)),
        "change_1m": rnd(pct_val(price, price_1m)),
        "_v1w":      pct_val(price, price_1w),
    }


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
        try:
            print(f"  {key.upper():<4} ({sym})... ", end="", flush=True)
            data[key] = get_index(sym)
            d = data[key]
            print(f"{d['price']}  1d {d['change_1d']}%  1w {d['change_1w']}%")
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(key)
            data[key] = {"price": None, "change_1d": None, "change_1w": None,
                         "change_1m": None, "_v1w": None}

    regime = compute_regime(data["spy"], data["qqq"], data["vix"])
    vix = data["vix"]

    out = {
        "updated": datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%d %H:%M"),
        "spy": {k: data["spy"][k] for k in ("price", "change_1d", "change_1w", "change_1m")},
        "qqq": {k: data["qqq"][k] for k in ("price", "change_1d", "change_1w", "change_1m")},
        "vix": {"level": vix["price"], "change_1d": vix["change_1d"], "regime": regime},
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
