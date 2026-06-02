"""
generate_export.py — combines all sector data into all_stocks.csv + all_stocks.json
Run: python generate_export.py  (from repo root)
Also called by .github/workflows/generate-export.yml after each evening price update.
"""
import json, re, csv, os
from datetime import datetime, timezone

SECTORS = ["AI", "Biotech", "Crypto", "Defence", "Energy", "Tech"]
BASE    = os.path.dirname(os.path.abspath(__file__))

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
    "market_cap_gbp_b", "beta", "pe_ratio",
    "avg_volume_m", "div_yield_pct", "short_pct",
    "analyst", "analyst_score",
]

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

        # What-if: value + profit for each period × amount
        for label, field in PERIODS:
            pct = to_pct(s.get(field))
            row[f"pct_{label}"] = pct
            for amt in AMOUNTS:
                val, profit = whatsit(pct, amt)
                row[f"val_{amt}_{label}"]    = val
                row[f"profit_{amt}_{label}"] = profit

        # News: top 3 articles
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

        # Signals
        sig = signals.get(s["ticker"], {})
        row["signal_rank"]       = sig.get("rank")
        row["signal"]            = sig.get("signal")
        row["signal_confidence"] = sig.get("confidence")
        row["signal_rationale"]  = sig.get("rationale", "")
        row["signal_drivers"]    = "; ".join(sig.get("drivers", []))

        all_stocks.append(row)

# Build field list for CSV
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
out_json = os.path.join(BASE, "exports", "all_stocks.json")
out_csv  = os.path.join(BASE, "exports", "all_stocks.csv")

with open(out_json, "w", encoding="utf-8") as f:
    json.dump({
        "generated": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "total":     len(all_stocks),
        "sectors":   meta,
        "stocks":    all_stocks,
    }, f, indent=2)

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
    w.writeheader()
    w.writerows(all_stocks)

print(f"Exported {len(all_stocks)} stocks → all_stocks.csv ({os.path.getsize(out_csv)//1024} KB)  all_stocks.json ({os.path.getsize(out_json)//1024} KB)")
