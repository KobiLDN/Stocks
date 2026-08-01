"""
generate_export.py — combines all sector data into a dated snapshot + updates manifest
Run: python generate_export.py  (from repo root)
Also called by .github/workflows/generate-export.yml after each evening price update.
If T212_API_KEY env var is set, portfolio positions are fetched and merged in.
"""
import json, re, csv, os
from datetime import datetime, timezone, timedelta
from pathlib import Path

SECTORS = ["AI", "Biotech", "Crypto", "Defence", "Energy", "MegaCap", "Tech"]
BASE    = os.path.dirname(os.path.abspath(__file__))

# T212 ticker → canonical universe ticker (OTC / ADR aliases)
TICKER_ALIASES = {
    "KXIAY": "285A",   # Kioxia Holdings US OTC = TSE 285A
}

# ── T212 portfolio fetch (optional) ──────────────────────────────────────────
def fetch_t212_portfolio():
    key_file = Path(BASE) / "t212_mcp" / ".key"
    raw_key  = key_file.read_text().strip() if key_file.exists() else os.getenv("T212_API_KEY", "")
    if not raw_key or ":" not in raw_key:
        return None, None
    key_id, secret = raw_key.split(":", 1)
    auth = (key_id, secret)
    try:
        import httpx
        base   = "https://live.trading212.com/api/v0"
        pos_r  = httpx.get(f"{base}/equity/portfolio",    auth=auth, timeout=15)
        cash_r = httpx.get(f"{base}/equity/account/cash", auth=auth, timeout=15)
        pos_r.raise_for_status(); cash_r.raise_for_status()

        def clean(t): return re.split(r'_', t)[0]

        positions = []
        held_set  = set()
        for p in pos_r.json():
            ticker = clean(p.get("ticker", ""))
            ticker = TICKER_ALIASES.get(ticker, ticker)  # resolve OTC/ADR aliases
            held_set.add(ticker)
            positions.append({
                "ticker":      ticker,
                "t212_ticker": p.get("ticker"),
                "quantity":    p.get("quantity"),
                "avg_price":   p.get("averagePrice"),
                "ppl":         p.get("ppl"),
                "total_value": round((p.get("quantity") or 0) * (p.get("currentPrice") or 0), 2),
            })
        positions.sort(key=lambda x: x["total_value"] or 0, reverse=True)

        c = cash_r.json()
        summary = {
            "total_value": c.get("total"),
            "invested":    c.get("invested"),
            "free_cash":   c.get("free"),
            "total_ppl":   c.get("result"),
        }
        print(f"  T212: fetched {len(positions)} positions, total £{summary['total_value']}")
        return {"summary": summary, "positions": positions}, held_set
    except Exception as e:
        print(f"  T212: fetch failed — {e}")
        return None, None

def parse_prices(path):
    raw = open(path, encoding="utf-8").read()
    json_str = re.sub(r'^\s*window\.PRICES_DATA\s*=\s*', '', raw).rstrip().rstrip(';')
    return json.loads(json_str)

def load_signals(sector):
    path = os.path.join(BASE, sector, "signals-local.json")
    try:
        data = json.load(open(path, encoding="utf-8"))
        return {p["ticker"]: p for p in data.get("picks", [])}, data.get("updated", "")
    except Exception:
        return {}, ""

def to_pct(val):
    if val in (None, "", "N/A"):
        return None
    try:
        return float(re.sub(r'[^0-9.\-]', '', str(val)))
    except ValueError:
        return None

def whatsit(pct, amount):
    if pct is None:
        return None, None
    current = round(amount * (1 + pct / 100), 2)
    return current, round(current - amount, 2)

PERIODS = [
    ("1d",  "change_1d"),
    ("1w",  "change_1w"),
    ("1m",  "change_1m"),
    ("ytd", "change_ytd"),
    ("1y",  "return_1yr"),
]
AMOUNTS = [100, 1000, 10000]

PRICE_FIELDS = [
    "ticker", "company_name", "sector", "category", "exchange",
    "price_usd", "change_1d", "change_1w", "change_1m",
    "change_ytd", "return_1yr",
    "market_cap_usd_b", "beta", "pe_ratio",
    "avg_volume_m", "vol_1d", "vol_1w", "vol_1m",
    "div_yield_pct", "short_pct",
    "analyst", "analyst_score",
]

def compute_export_momentum(stocks):
    """Cross-sector momentum picks using both YTD and 1Y thresholds."""
    month  = datetime.now(tz=timezone.utc).month
    sb_ytd = (1.1225 ** month - 1) * 100
    b_ytd  = (1.07   ** month - 1) * 100
    SB_1Y, B_1Y = 500.0, 200.0

    picks = []
    for s in stocks:
        ytd = s.get("pct_ytd") or 0.0
        y1  = s.get("pct_1y")  or 0.0

        is_sb = ytd >= sb_ytd or y1 >= SB_1Y
        is_b  = ytd >= b_ytd  or y1 >= B_1Y
        if not (is_sb or is_b):
            continue

        if is_sb:
            signal = "strong_buy"
            confs  = []
            if ytd >= sb_ytd: confs.append(ytd / sb_ytd / 2)
            if y1  >= SB_1Y:  confs.append(y1  / SB_1Y  / 2)
        else:
            signal = "buy"
            confs  = []
            if ytd >= b_ytd: confs.append(ytd / b_ytd / 2)
            if y1  >= B_1Y:  confs.append(y1  / B_1Y  / 2)

        drivers = []
        if ytd >= sb_ytd:
            drivers.append(f"YTD {s.get('change_ytd', '') or f'+{ytd:.1f}%'} ≥ {round(sb_ytd, 1)}%")
        elif ytd >= b_ytd:
            drivers.append(f"YTD {s.get('change_ytd', '') or f'+{ytd:.1f}%'} ≥ {round(b_ytd, 1)}%")
        if y1 >= SB_1Y:
            drivers.append(f"1Y {s.get('return_1yr', '') or f'+{y1:.1f}%'} ≥ {SB_1Y:.0f}%")
        elif y1 >= B_1Y:
            drivers.append(f"1Y {s.get('return_1yr', '') or f'+{y1:.1f}%'} ≥ {B_1Y:.0f}%")

        picks.append({
            "ticker":     s["ticker"],
            "sector":     s["sector"],
            "signal":     signal,
            "confidence": round(min(max(confs), 1.0), 3),
            "change_ytd": s.get("change_ytd", ""),
            "change_1y":  s.get("return_1yr", ""),
            "rationale":  "Momentum screener: " + "; ".join(drivers) + ".",
            "drivers":    drivers,
        })

    picks.sort(key=lambda x: x["confidence"], reverse=True)
    return picks


all_stocks, meta = [], {}

for sector in SECTORS:
    prices = parse_prices(os.path.join(BASE, sector, "prices-data.js"))
    signals, sig_updated = load_signals(sector)
    meta[sector] = {
        "prices_updated":  prices.get("updated"),
        "signals_updated": sig_updated,
        "fx_gbp_usd":      prices.get("fx_gbp_usd"),
    }

    for s in prices.get("stocks", []):
        row = {"sector": sector}
        for k in PRICE_FIELDS:
            if k != "sector":
                row[k] = s.get(k)
        row["change_1y"] = s.get("return_1yr")  # alias expected by portfolio session

        for label, field in PERIODS:
            pct = to_pct(s.get(field))
            row[f"pct_{label}"] = pct
            for amt in AMOUNTS:
                val, profit = whatsit(pct, amt)
                row[f"val_{amt}_{label}"]    = val
                row[f"profit_{amt}_{label}"] = profit

        for i, n in enumerate(s.get("news", [])[:3], 1):
            ts = n.get("published", 0)
            date = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d") if ts else ""
            row[f"news{i}_title"]     = n.get("title", "")
            row[f"news{i}_publisher"] = n.get("publisher", "")
            row[f"news{i}_date"]      = date
            row[f"news{i}_sentiment"] = n.get("sentiment")
        for i in range(len(s.get("news", [])[:3]) + 1, 4):
            row[f"news{i}_title"] = row[f"news{i}_publisher"] = row[f"news{i}_date"] = ""
            row[f"news{i}_sentiment"] = None

        sig = signals.get(s["ticker"], {})
        row["signal_rank"]       = sig.get("rank")
        row["signal"]            = sig.get("signal")
        row["signal_confidence"] = sig.get("confidence")
        row["signal_rationale"]  = sig.get("rationale", "")
        row["signal_drivers"]    = "; ".join(sig.get("drivers", []))

        all_stocks.append(row)

whatsit_fields = []
for label, _ in PERIODS:
    whatsit_fields.append(f"pct_{label}")
    for amt in AMOUNTS:
        whatsit_fields += [f"val_{amt}_{label}", f"profit_{amt}_{label}"]

csv_fields = PRICE_FIELDS + whatsit_fields + [
    "news1_title", "news1_publisher", "news1_date", "news1_sentiment",
    "news2_title", "news2_publisher", "news2_date", "news2_sentiment",
    "news3_title", "news3_publisher", "news3_date", "news3_sentiment",
    "signal_rank", "signal", "signal_confidence", "signal_rationale", "signal_drivers",
]

os.makedirs(os.path.join(BASE, "exports"), exist_ok=True)

now_utc  = datetime.now(tz=timezone.utc)
uk_off   = timedelta(hours=1) if 3 < now_utc.month < 11 else timedelta(0)
now_uk   = now_utc + uk_off
tz_label = "BST" if uk_off else "GMT"
date_str = now_utc.strftime("%Y-%m-%d")           # file names stay UTC date
gen_str  = now_uk.strftime(f"%Y-%m-%d %H:%M {tz_label}")

# ── Optional T212 portfolio fetch ─────────────────────────────────────────────
t212_data, held_tickers = fetch_t212_portfolio()

# Annotate each stock row with portfolio position if held
if t212_data:
    held_map = {p["ticker"]: p for p in t212_data["positions"]}
    for row in all_stocks:
        pos = held_map.get(row["ticker"])
        row["portfolio_held"]        = True if pos else False
        row["portfolio_quantity"]    = pos["quantity"]    if pos else None
        row["portfolio_avg_price"]   = pos["avg_price"]   if pos else None
        row["portfolio_ppl"]         = pos["ppl"]         if pos else None
        row["portfolio_total_value"] = pos["total_value"] if pos else None
else:
    for row in all_stocks:
        row["portfolio_held"] = row["portfolio_quantity"] = None
        row["portfolio_avg_price"] = row["portfolio_ppl"] = row["portfolio_total_value"] = None

# ── Output filenames ──────────────────────────────────────────────────────────
# Local runs with T212 key → separate portfolio-enriched file, never committed
if t212_data:
    out_json = os.path.join(BASE, "exports", f"{date_str}-portfolio.json")
    out_csv  = os.path.join(BASE, "exports", f"{date_str}-portfolio.csv")
    update_manifest = False
else:
    out_json = os.path.join(BASE, "exports", f"{date_str}.json")
    out_csv  = os.path.join(BASE, "exports", f"{date_str}.csv")
    update_manifest = True

# ── Macro block (SPY / QQQ / VIX / regime) ────────────────────────────────────
# Produced by update_market.py during the price workflow. Optional — null if the
# file is missing so the export never fails on its absence.
def read_macro():
    try:
        with open(os.path.join(BASE, "market.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

# ── Write JSON ────────────────────────────────────────────────────────────────
payload = {
    "generated":        gen_str,
    "total":            len(all_stocks),
    "has_portfolio":    t212_data is not None,
    "sectors":          meta,
    "macro":            read_macro(),
    "momentum_picks":   compute_export_momentum(all_stocks),
    "stocks":           all_stocks,
}
if t212_data:
    payload["portfolio"] = t212_data

with open(out_json, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

# ── Write CSV ─────────────────────────────────────────────────────────────────
portfolio_fields = [
    "portfolio_held", "portfolio_quantity",
    "portfolio_avg_price", "portfolio_ppl", "portfolio_total_value",
]
all_csv_fields = csv_fields + portfolio_fields

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=all_csv_fields, extrasaction="ignore")
    w.writeheader()
    w.writerows(all_stocks)

# ── Update manifest (market-data snapshots only, not portfolio runs) ──────────
if update_manifest:
    manifest_path = os.path.join(BASE, "exports", "manifest.json")
    try:
        manifest = json.load(open(manifest_path, encoding="utf-8"))
    except Exception:
        manifest = {"snapshots": []}

    entry = {
        "date":      date_str,
        "generated": gen_str,
        "total":     len(all_stocks),
        "json":      f"{date_str}.json",
        "csv":       f"{date_str}.csv",
    }
    snapshots = [s for s in manifest["snapshots"] if s["date"] != date_str]
    snapshots.insert(0, entry)
    manifest["snapshots"] = snapshots

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest updated — {len(snapshots)} snapshot(s)")

suffix = "-portfolio" if t212_data else ""
print(f"Exported {len(all_stocks)} stocks → {date_str}{suffix}.json ({os.path.getsize(out_json)//1024} KB)  {date_str}{suffix}.csv ({os.path.getsize(out_csv)//1024} KB)")
if t212_data:
    print(f"Portfolio: {len(t212_data['positions'])} positions · total £{t212_data['summary']['total_value']}")
