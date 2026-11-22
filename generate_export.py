"""
generate_export.py — every stock on the site in one dated snapshot + updates manifest
Run: python generate_export.py  (from repo root)
Also called by .github/workflows/generate-export.yml after each evening price update.
If T212_API_KEY env var is set, portfolio positions are fetched and merged in.

Since #88 (Nov 2026): one row per stock, read from the 11 sector groups' price files plus Crypto.
`sector` is the stock's official sector ("Crypto" for coins); `themes`, `markets` and `t212` say
where else it belongs. Signals come from every live run (the themes that kept a run, the 11 sector
runs and the FTSE 100 run); a stock picked by several runs appears once, with all of them in
`picked_by` and its strongest pick in the `signal*` fields. News comes from the theme price files.
"""
import json, re, csv, os, glob
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

BASE    = os.path.dirname(os.path.abspath(__file__))
# Themes that still have their own signal run (#88 retired Biotech, Energy, Mega-Cap and Tech)
THEME_RUNS = ["AI", "Defence", "Crypto"]
# Theme price files: news headlines, and Crypto's rows (coins are in no sector group)
THEMES = ["AI", "Biotech", "Crypto", "Defence", "Energy", "MegaCap", "Tech"]

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

def read_json(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return None

def signal_runs():
    """[(run name, signals file dict)] for every live run. The S&P 500 / Nasdaq-100 files are
    derived from the sector runs ("derived": true) and skipped, so no pick is counted twice."""
    runs = []
    for theme in THEME_RUNS:
        data = read_json(os.path.join(BASE, theme, "signals-local.json"))
        if data:
            runs.append((theme, data))
    for path in sorted(glob.glob(os.path.join(BASE, "sectors", "*", "signals-local.json")) +
                       glob.glob(os.path.join(BASE, "markets", "*", "signals-local.json"))):
        data = read_json(path)
        if data and not data.get("derived"):
            runs.append((data.get("group_name") or os.path.basename(os.path.dirname(path)), data))
    return runs

def yahoo_aliases():
    """{site ticker: Yahoo symbol} from asset-links.js (generated from universe.yaml), e.g. RR. -> RR.L:
    a theme run may name a stock by a ticker the sector files list under its Yahoo symbol."""
    try:
        raw = open(os.path.join(BASE, "asset-links.js"), encoding="utf-8").read()
        return json.loads(re.search(r"const ASSET_YAHOO = (\{.*?\});", raw).group(1))
    except Exception:
        return {}

def best_pick(picks):
    """The strongest of one stock's picks: highest confidence, then best rank."""
    return min(picks, key=lambda p: (-(p.get("confidence") or 0), p.get("rank") or 99))

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

# ── Rows: one per stock ───────────────────────────────────────────────────────
sources = [(os.path.basename(os.path.dirname(p)), p) for p in sorted(glob.glob(os.path.join(BASE, "sectors", "*", "prices-data.js")))]
sources.append(("Crypto", os.path.join(BASE, "Crypto", "prices-data.js")))
news = {}
for theme in THEMES:
    path = os.path.join(BASE, theme, "prices-data.js")
    if os.path.exists(path):
        for s in parse_prices(path).get("stocks", []):
            if s.get("news") and s["ticker"] not in news:
                news[s["ticker"]] = s["news"]

seen = set()
for name, path in sources:
    prices = parse_prices(path)
    meta[name] = {"prices_updated": prices.get("updated"), "fx_gbp_usd": prices.get("fx_gbp_usd")}
    for s in prices.get("stocks", []):
        if s["ticker"] in seen:
            continue
        seen.add(s["ticker"])
        crypto = name == "Crypto"
        row = {k: s.get(k) for k in PRICE_FIELDS}
        row["sector"]   = "Crypto" if crypto else s.get("sector")
        row["industry"] = None if crypto else s.get("industry")
        row["currency"] = "USD" if crypto else s.get("currency")
        row["themes"]   = ["crypto"] if crypto else [t.lower() for t in s.get("themes") or []]
        row["markets"]  = ["crypto"] if crypto else list(s.get("markets") or [])
        row["t212"]     = None if crypto else s.get("t212")
        row["change_1y"] = s.get("return_1yr")  # alias expected by portfolio session

        for label, field in PERIODS:
            pct = to_pct(s.get(field))
            row[f"pct_{label}"] = pct
            for amt in AMOUNTS:
                val, profit = whatsit(pct, amt)
                row[f"val_{amt}_{label}"]    = val
                row[f"profit_{amt}_{label}"] = profit

        items = (s.get("news") or news.get(s["ticker"]) or [])[:3]
        for i, n in enumerate(items, 1):
            ts = n.get("published", 0)
            date = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d") if ts else ""
            row[f"news{i}_title"]     = n.get("title", "")
            row[f"news{i}_publisher"] = n.get("publisher", "")
            row[f"news{i}_date"]      = date
            row[f"news{i}_sentiment"] = n.get("sentiment")
        for i in range(len(items) + 1, 4):
            row[f"news{i}_title"] = row[f"news{i}_publisher"] = row[f"news{i}_date"] = ""
            row[f"news{i}_sentiment"] = None
        all_stocks.append(row)

# ── Signals: every live run; one stock once, with every run that picked it ────
runs_meta, picks_by_ticker = {}, {}
alias = yahoo_aliases()
for run, data in signal_runs():
    variant = data.get("variant") or "live-1"   # runs before #70 carry no tag: they used the momentum upgrade
    runs_meta[run] = {"signals_updated": data.get("updated", ""), "model": data.get("model"),
                      "variant": variant, "picks": len(data.get("picks") or [])}
    for p in data.get("picks") or []:
        picks_by_ticker.setdefault(alias.get(p["ticker"], p["ticker"]), []).append({**p, "run": run, "variant": variant})

for row in all_stocks:
    picks = picks_by_ticker.pop(alias.get(row["ticker"], row["ticker"]), [])
    sig = best_pick(picks) if picks else {}
    row["signal_rank"]       = sig.get("rank")
    row["signal"]            = sig.get("signal")
    row["signal_confidence"] = sig.get("confidence")
    row["signal_rationale"]  = sig.get("rationale", "")
    row["signal_drivers"]    = "; ".join(sig.get("drivers", []))
    # #70: the AI's own label, what the momentum screen thinks, and which recipe made the signal.
    # Since variant live-2, signal == pre_momentum_label (no upgrade).
    row["pre_momentum_label"] = sig.get("pre_momentum_label") if sig else None
    row["momentum_label"]     = sig.get("momentum_label") if sig else None
    row["momentum_score"]     = sig.get("momentum_score") if sig else None
    row["signal_variant"]     = sig.get("variant") if sig else None
    row["signal_run"]         = sig.get("run") if sig else None
    row["picked_by"] = [{"run": p["run"], "rank": p.get("rank"), "signal": p.get("signal"),
                         "confidence": p.get("confidence")}
                        for p in sorted(picks, key=lambda p: (-(p.get("confidence") or 0), p.get("rank") or 99))]
if picks_by_ticker:
    print(f"  WARNING: picks for stocks with no price row: {sorted(picks_by_ticker)}")

whatsit_fields = []
for label, _ in PERIODS:
    whatsit_fields.append(f"pct_{label}")
    for amt in AMOUNTS:
        whatsit_fields += [f"val_{amt}_{label}", f"profit_{amt}_{label}"]

csv_fields = PRICE_FIELDS + ["industry", "currency", "themes", "markets", "t212"] + whatsit_fields + [
    "news1_title", "news1_publisher", "news1_date", "news1_sentiment",
    "news2_title", "news2_publisher", "news2_date", "news2_sentiment",
    "news3_title", "news3_publisher", "news3_date", "news3_sentiment",
    "signal_rank", "signal", "signal_confidence", "signal_rationale", "signal_drivers",
    "pre_momentum_label", "momentum_label", "momentum_score", "signal_variant",
    "signal_run", "picked_by",
]

os.makedirs(os.path.join(BASE, "exports"), exist_ok=True)

now_utc  = datetime.now(tz=timezone.utc)
LONDON   = ZoneInfo("Europe/London")
now_uk   = now_utc.astimezone(LONDON)
tz_label = now_uk.tzname()                         # "GMT" or "BST" on the real change dates
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

# ── Data freshness (as_of, ISO UTC) ──────────────────────────────────────────
# The bots write London wall-clock strings ("YYYY-MM-DD HH:MM"). The oldest sector
# is reported so a sector that failed to update shows up as old.
def london_to_iso(value):
    try:
        local = datetime.strptime(str(value)[:16], "%Y-%m-%d %H:%M").replace(tzinfo=LONDON)
        return local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError):
        return None

def oldest_iso(values):
    isos = [london_to_iso(v) for v in values]
    return None if not isos or None in isos else min(isos)

macro_block = read_macro()
as_of = {
    "generated": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "prices":    oldest_iso([m["prices_updated"] for m in meta.values()]),
    "signals":   oldest_iso([m["signals_updated"] for m in runs_meta.values()]),
    "market":    london_to_iso(macro_block.get("updated")) if macro_block else None,
}

# ── Write JSON ────────────────────────────────────────────────────────────────
payload = {
    "generated":        gen_str,
    "as_of":            as_of,
    "total":            len(all_stocks),
    "has_portfolio":    t212_data is not None,
    "sectors":          meta,          # price files: the 11 sector groups + Crypto
    "signal_runs":      runs_meta,     # every live signal run (#88)
    "macro":            macro_block,
    "momentum_picks":   compute_export_momentum(all_stocks),
    "stocks":           all_stocks,
}
if t212_data:
    payload["portfolio"] = t212_data

with open(out_json, "w", encoding="utf-8") as f:
    json.dump(payload, f, separators=(",", ":"))   # compact: ~720 rows (#88)

# ── Write CSV ─────────────────────────────────────────────────────────────────
portfolio_fields = [
    "portfolio_held", "portfolio_quantity",
    "portfolio_avg_price", "portfolio_ppl", "portfolio_total_value",
]
all_csv_fields = csv_fields + portfolio_fields

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=all_csv_fields, extrasaction="ignore")
    w.writeheader()
    for row in all_stocks:      # lists as text in the CSV: "ai|defence", "Technology #3|AI #1"
        w.writerow({**row, "themes": "|".join(row["themes"]), "markets": "|".join(row["markets"]),
                    "picked_by": "|".join(f"{p['run']} #{p['rank']}" for p in row["picked_by"])})

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
