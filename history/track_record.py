"""Track record: how did each signal do against the S&P 500 (SPY)? (#54 step 8)

    python -m history.track_record --out track-record.json

Reads the history DB (signals, raw daily bars, splits/dividends) and writes the one JSON file
the track-record page reads — the site never reads the database itself.

Rules (agreed in #54):
- Every signal counts, including a stock picked again in later runs.
- Entry: the first market open strictly more than 5 minutes after the signal was made, on the
  stock's own exchange (crypto: the next 00:00 UTC daily bar). The entry date is published.
- Exit: the close on the last trading day on or before entry date + 7 / 30 / 91 days.
- Return: price change plus splits and cash dividends (not reinvested), in the stock's own
  currency. Benchmark: SPY over the same window — first SPY open at or after the stock's entry,
  SPY close on or before the same exit date. Excess = stock return - SPY return.
- A window that hasn't finished yet is pending. Signals whose prices are missing or unusable
  (Yahoo rounds PEPE to $0.000005) are listed but not scored.
"""
import argparse
import bisect
import datetime as dt
import json
import statistics
import sys
from zoneinfo import ZoneInfo

from history.db import HistoryError, connect_for_bot, iso, load_universe, utc_now

UTC = dt.timezone.utc
BUFFER = dt.timedelta(minutes=5)
HORIZONS = (("1w", 7), ("1m", 30), ("3m", 91))
MAX_EXIT_GAP = dt.timedelta(days=7)    # exit bar this far before the target = data gap, not a result
BUY_SIDE = ("strong_buy", "buy")
BENCHMARK = "SPY"

# Regular session open / close, local time
SESSIONS = {
    "NYSE":    ("America/New_York", (9, 30), (16, 0)),
    "NASDAQ":  ("America/New_York", (9, 30), (16, 0)),
    "Index":   ("America/New_York", (9, 30), (16, 0)),   # benchmarks: SPY, QQQ, VIX
    "LSE":     ("Europe/London", (8, 0), (16, 30)),
    "TSE":     ("Asia/Tokyo", (9, 0), (15, 30)),
    "TADAWUL": ("Asia/Riyadh", (10, 0), (15, 0)),
    "Crypto":  ("UTC", (0, 0), (24, 0)),                 # daily bar = one UTC day
}


def _local(date, hm, tz):
    h, m = hm
    day = dt.date.fromisoformat(date)
    if h == 24:
        day, h = day + dt.timedelta(days=1), 0
    return dt.datetime(day.year, day.month, day.day, h, m, tzinfo=ZoneInfo(tz))


def open_utc(date, exchange):
    tz, op, _ = SESSIONS.get(exchange, SESSIONS["NYSE"])
    return _local(date, op, tz).astimezone(UTC)


def complete_through(exchange, now):
    """Latest date whose session has closed (plus 15 min for the bar to settle)."""
    tz, _, cl = SESSIONS.get(exchange, SESSIONS["NYSE"])
    for back in range(0, 4):
        d = (now - dt.timedelta(days=back)).date().isoformat()
        if _local(d, cl, tz).astimezone(UTC) + dt.timedelta(minutes=15) <= now:
            return d
    return (now - dt.timedelta(days=4)).date().isoformat()


def parse_utc(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


class Series:
    """One instrument's raw daily bars plus splits/dividends."""

    def __init__(self, exchange, bars, splits=None, dividends=None):
        self.exchange = exchange
        self.bars = sorted((b for b in bars if b[1] is not None or b[2] is not None), key=lambda b: b[0])
        self.dates = [b[0] for b in self.bars]
        self.opens = [open_utc(d, exchange) for d in self.dates]
        self.splits = splits or {}
        self.dividends = dividends or {}

    def first_open_after(self, t, strict=True):
        i = (bisect.bisect_right if strict else bisect.bisect_left)(self.opens, t)
        while i < len(self.bars) and self.bars[i][1] is None:
            i += 1
        return i if i < len(self.bars) else None

    def last_close_on_or_before(self, date):
        j = bisect.bisect_right(self.dates, date) - 1
        while j >= 0 and self.bars[j][2] is None:
            j -= 1
        return j if j >= 0 else None

    def total_return(self, i, j):
        """Buy at bar i's open, value at bar j's close: splits change the share count, cash
        dividends are added (not reinvested). Events dated after the entry day up to the exit day."""
        d0, d1 = self.dates[i], self.dates[j]
        shares, cash = 1.0, 0.0
        for d in sorted(set(self.splits) | set(self.dividends)):
            if d0 < d <= d1:
                shares *= self.splits.get(d, 1.0)
                cash += self.dividends.get(d, 0.0) * shares
        return (self.bars[j][2] * shares + cash) / self.bars[i][1] - 1


def measure(generated, series, spy, now):
    """-> (entry, {horizon: (stock return, spy return) | 'pending' | None}, note)"""
    if series is None or not series.bars:
        return None, {}, "no price data"
    i = series.first_open_after(generated + BUFFER)
    if i is None:
        late = generated.date().isoformat() >= complete_through(series.exchange, now)
        return None, {}, "awaiting entry" if late else "no price data"
    entry = {"date": series.dates[i], "price": series.bars[i][1]}
    si = spy.first_open_after(series.opens[i], strict=False) if spy else None
    ready_through = min(complete_through(series.exchange, now), complete_through("Index", now))
    out = {}
    for name, days in HORIZONS:
        target = (dt.date.fromisoformat(entry["date"]) + dt.timedelta(days=days)).isoformat()
        if target > ready_through:
            out[name] = "pending"
            continue
        j = series.last_close_on_or_before(target)
        sj = spy.last_close_on_or_before(target) if spy else None
        if (j is None or j < i or si is None or sj is None or sj < si
                or dt.date.fromisoformat(target) - dt.date.fromisoformat(series.dates[j]) > MAX_EXIT_GAP):
            out[name] = None
            continue
        out[name] = (series.total_return(i, j), spy.total_return(si, sj))
    return entry, out, ""


def summarise(pairs):
    """pairs: [(stock return, spy return)] -> stats in %, or None if empty."""
    if not pairs:
        return None
    ex = [r - s for r, s in pairs]
    pct = lambda x: round(x * 100, 2)
    return {"n": len(pairs), "avg": pct(statistics.fmean(r for r, _ in pairs)),
            "spy": pct(statistics.fmean(s for _, s in pairs)), "excess": pct(statistics.fmean(ex)),
            "median_excess": pct(statistics.median(ex)), "beat_spy": round(100 * sum(e > 0 for e in ex) / len(ex), 1)}


def confidence_bucket(c):
    if c is None:
        return "unknown"
    for lo in (0.9, 0.8, 0.7, 0.6):
        if c >= lo:
            return f"{int(lo * 100)}%+"
    return "under 60%"


# ── Build ─────────────────────────────────────────────────────────────────────
def load(h):
    assets = {r["asset_id"]: r for r in h.fetch_all("assets", ["asset_id"])}
    runs = {r["signal_run_id"]: r for r in h.fetch_all("signal_runs", ["signal_run_id"])}
    signals = h.fetch_all("signals", ["signal_run_id", "kind", "asset_id"],
                          "signal_run_id, kind, asset_id, rank, signal, confidence")
    bars = {}
    for b in h.fetch_all("daily_bars", ["symbol", "date"], "symbol, date, open, close, currency"):
        bars.setdefault(b["symbol"], []).append(b)
    splits, divs = {}, {}
    for a in h.fetch_all("corporate_actions", ["symbol", "date", "kind"]):
        (splits if a["kind"] == "split" else divs).setdefault(a["symbol"], {})[a["date"]] = a["value"]
    coarse = {f["symbol"] for f in h.fetch_all("data_flags", ["symbol", "date", "kind"]) if f["kind"] == "coarse_prices"}
    return assets, runs, signals, bars, splits, divs, coarse


def build(assets, runs, signals, bars, splits, divs, coarse, now):
    series_cache = {}

    def series_for(symbol, exchange):
        if symbol not in series_cache:
            rows = bars.get(symbol) or []
            series_cache[symbol] = Series(exchange, [(b["date"], b["open"], b["close"]) for b in rows],
                                          splits.get(symbol), divs.get(symbol)) if rows else None
        return series_cache[symbol]

    spy_asset = assets.get(BENCHMARK) or {"yahoo": BENCHMARK, "exchange": "Index"}
    spy = series_for(spy_asset["yahoo"], spy_asset["exchange"])
    currency = {s: (rows[-1]["currency"] if rows else None) for s, rows in bars.items()}

    rows, groups = [], {}
    def add(group, key, horizon, pair):
        groups.setdefault(group, {}).setdefault(key, {}).setdefault(horizon, []).append(pair)

    counts = {"signals": 0, "scored": 0, "pending": 0, "no_data": 0, "unreliable": 0}
    for s in sorted(signals, key=lambda x: (runs.get(x["signal_run_id"], {}).get("generated_utc", ""), x["kind"], x["rank"] or 0)):
        run = runs.get(s["signal_run_id"])
        if not run:
            continue
        counts["signals"] += 1
        a = assets.get(s["asset_id"])
        symbol = a["yahoo"] if a else None
        generated = parse_utc(run["generated_utc"])
        note = ""
        if symbol in coarse:
            entry, res, note = None, {}, "unreliable price"
        else:
            entry, res, note = measure(generated, series_for(symbol, a["exchange"]) if a else None, spy, now)
        cells = []
        for name, _ in HORIZONS:
            v = res.get(name)
            if isinstance(v, tuple):
                cells += [round(v[0] * 100, 2), round((v[0] - v[1]) * 100, 2)]
            else:
                cells += [None, None]
        row = [run["generated_utc"][:16].replace("T", " "), run["sector"], s["kind"], s["asset_id"], s["signal"],
               s["confidence"], s["rank"], run["provenance"], entry["date"] if entry else None,
               entry["price"] if entry else None, currency.get(symbol), *cells,
               note or ("" if entry else "no price data")]
        rows.append(row)
        scored = False
        for name, _ in HORIZONS:
            v = res.get(name)
            if not isinstance(v, tuple):
                continue
            scored = True
            add("by_signal", s["signal"], name, v)
            add("by_kind", s["kind"], name, v)
            if s["signal"] in BUY_SIDE:
                add("all", "buy signals", name, v)
                add("by_sector", run["sector"], name, v)
                add("by_confidence", confidence_bucket(s["confidence"]), name, v)
                add("by_month", run["generated_utc"][:7], name, v)
        if note == "unreliable price":
            counts["unreliable"] += 1
        elif scored:
            counts["scored"] += 1
        elif note == "awaiting entry" or "pending" in res.values():
            counts["pending"] += 1
        else:
            counts["no_data"] += 1

    summary = {g: {k: {h: summarise(v) for h, v in hs.items()} for k, hs in keys.items()} for g, keys in groups.items()}
    names = {aid: a["name"] for aid, a in assets.items()}
    return {
        "generated_utc": iso(now),
        "data_through": spy.dates[-1] if spy and spy.dates else None,
        "first_signal": rows[0][0] if rows else None,
        "last_signal": rows[-1][0] if rows else None,
        "rules": {
            "entry": "first market open more than 5 minutes after the signal, on the stock's own exchange (crypto: next 00:00 UTC)",
            "exits": {"1w": 7, "1m": 30, "3m": 91},
            "exit": "close on the last trading day on or before entry date + 7 / 30 / 91 days",
            "return": "price change plus splits and cash dividends (not reinvested), in the stock's own currency",
            "benchmark": "SPY over the same window",
            "counting": "every signal counts, including a stock picked again in later runs",
        },
        "counts": counts,
        "summary": summary,
        "columns": ["time_utc", "sector", "kind", "ticker", "signal", "confidence", "rank", "provenance",
                    "entry_date", "entry_price", "currency", "r1w", "x1w", "r1m", "x1m", "r3m", "x3m", "note"],
        "rows": rows,
        "names": {t: names[t] for t in sorted({r[3] for r in rows}) if t in names},
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="track-record.json")
    args = ap.parse_args(argv)
    load_universe()
    h = connect_for_bot()
    if h is None:
        return 0
    print(f"History ← {h.db.name}")
    h.ensure_schema()
    result = build(*load(h), now=utc_now())
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, separators=(",", ":"))
    c = result["counts"]
    print(f"  {c['signals']} signals: {c['scored']} scored, {c['pending']} pending, {c['no_data']} no price data,"
          f" {c['unreliable']} unreliable — {h.calls} calls → {args.out}")
    best = (result["summary"].get("all") or {}).get("buy signals") or {}
    for name, _ in HORIZONS:
        st = best.get(name)
        if st:
            print(f"  {name}: n={st['n']} avg {st['avg']:+.2f}% vs SPY {st['spy']:+.2f}% → excess {st['excess']:+.2f}%, beat SPY {st['beat_spy']}%")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except HistoryError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
