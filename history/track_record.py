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
import os
import statistics
import sys
from zoneinfo import ZoneInfo

from history.bars import coarse_closes
from history.db import BENCHMARKS, ROOT, HistoryError, connect_for_bot, iso, load_universe, utc_now

UTC = dt.timezone.utc
BUFFER = dt.timedelta(minutes=5)
HORIZONS = (("1w", 7), ("1m", 30), ("3m", 91))
MAX_EXIT_GAP = dt.timedelta(days=7)    # exit bar this far before the target = data gap, not a result
MAX_ENTRY_DELAY = dt.timedelta(days=10)  # first price this long after the signal = data gap (TON's Yahoo
                                         # history starts in Nov), not a purchase; allows long holidays
BUY_SIDE = ("strong_buy", "buy")
BENCHMARK = "SPY"
# Signals whose inputs were wrong at the time: listed, never scored.
UNRELIABLE = {
    "AGIX": "wrong coin priced (several coins share AGIX; fixed in #49)",
}

# Regular session open / close, local time
SESSIONS = {
    "NYSE":    ("America/New_York", (9, 30), (16, 0)),
    "NASDAQ":  ("America/New_York", (9, 30), (16, 0)),
    "Index":   ("America/New_York", (9, 30), (16, 0)),   # benchmarks: SPY, QQQ, VIX
    "LSE":     ("Europe/London", (8, 0), (16, 30)),
    "TSE":     ("Asia/Tokyo", (9, 0), (15, 30)),
    "TADAWUL": ("Asia/Riyadh", (10, 0), (15, 0)),
    # Europe (#110): continuous trading 09:00-17:30 local; Helsinki 10:00-18:30 local (same hours in UTC)
    "XETRA":    ("Europe/Berlin", (9, 0), (17, 30)),
    "EURONEXT": ("Europe/Paris", (9, 0), (17, 30)),
    "MIL":      ("Europe/Rome", (9, 0), (17, 30)),
    "BME":      ("Europe/Madrid", (9, 0), (17, 30)),
    "HEL":      ("Europe/Helsinki", (10, 0), (18, 30)),
    "SIX":      ("Europe/Zurich", (9, 0), (17, 30)),
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


def measure(generated, series, spy, now, windows=None):
    """-> (entry, {horizon: (stock return, spy return) | 'pending' | None}, note)
    windows: optional dict, filled with {horizon: (i, j, target)} (entry bar, exit bar, target date) for
    each finished window, so callers can price the same window in pounds or against another benchmark."""
    if series is None or not series.bars:
        return None, {}, "no price data"
    i = series.first_open_after(generated + BUFFER)
    if i is None:
        late = generated.date().isoformat() >= complete_through(series.exchange, now)
        return None, {}, "awaiting entry" if late else "no price data"
    if series.opens[i] - generated > MAX_ENTRY_DELAY:
        return None, {}, "no price data around the signal date"
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
        if windows is not None:
            windows[name] = (i, j, target)
    return entry, out, ""


# ── Pounds and local benchmarks (#88 PR 10) ───────────────────────────────────
LOCAL_BENCH = {"LSE": ("ISF", "LSE")}          # London listings vs the FTSE 100 (iShares ISF.L)
FX = {"USD": ("GBPUSD", 1.0), "SAR": ("GBPUSD", 3.75), "EUR": ("GBPEUR", 1.0), "JPY": ("GBPJPY", 1.0)}  # SAR is pegged
POUNDS = ("GBP", "GBp")
REVIEW_MIN_DATES = 10                          # run dates with a finished 1-month result before a run is judged


def window_return(bench, start_open, target):
    """A benchmark's return from its first open at or after `start_open` to its close on or before `target`."""
    if bench is None:
        return None
    i = bench.first_open_after(start_open, strict=False)
    j = bench.last_close_on_or_before(target)
    if i is None or j is None or j < i:
        return None
    return bench.total_return(i, j)


def to_gbp(ret, currency, d0, d1, fx):
    """A return in `currency` -> the same holding's return in pounds, using the closes on d0 (entry) and d1
    (exit) of that currency's rate per £1. None if the currency or a rate is missing."""
    if currency in POUNDS:
        return ret
    pair = FX.get(currency or "USD")
    ser = fx.get(pair[0]) if pair else None
    if ser is None:
        return None
    a, b = ser.last_close_on_or_before(d0), ser.last_close_on_or_before(d1)
    if a is None or b is None or not ser.bars[b][2]:
        return None
    if dt.date.fromisoformat(d0) - dt.date.fromisoformat(ser.dates[a]) > MAX_EXIT_GAP:
        return None
    return (1 + ret) * ser.bars[a][2] / ser.bars[b][2] - 1      # units per £ up = that currency weaker


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
    members = {}
    for m in h.fetch_all("asset_sectors", ["asset_id", "sector"]):
        members.setdefault(m["sector"], []).append(m["asset_id"])
    run_members = {}
    for m in h.fetch_all("run_universe", ["signal_run_id", "asset_id"], "signal_run_id, asset_id"):
        run_members.setdefault(m["signal_run_id"], []).append(m["asset_id"])
    return assets, runs, signals, bars, splits, divs, coarse, members, run_members


# Free alternatives the AI is compared with (#70): for every AI run, on the same date and with the same entry/exit rules,
#   random  every stock in that run's sector (= the average result of picking at random from the same list)
#   momentum_rule  the sector's 10 stocks with the best 6-month return skipping the latest month (the textbook momentum rule)
MOMENTUM_PICKS = 10

# Shadow trial (#92, ended 22 Nov 2026 by the owner): its picks stay in D1 under their own run ids
# and are kept out of every figure.
def is_shadow(run):
    return str((run or {}).get("variant") or "").startswith("shadow")


MOM_LONG, MOM_SKIP = 126, 21      # trading days: ~6 months back, skipping the latest ~1 month


def momentum_score(series, generated):
    """6-1 month price return known before the signal (closes only, splits adjusted), or None if history is too short."""
    if series is None:
        return None
    j = series.last_close_on_or_before((generated.date() - dt.timedelta(days=1)).isoformat())
    if j is None or j - MOM_LONG < 0:
        return None
    a, b = j - MOM_LONG, j - MOM_SKIP
    if series.bars[a][2] is None or series.bars[b][2] is None or not series.bars[a][2]:
        return None
    shares = 1.0
    for d, f in series.splits.items():
        if series.dates[a] < d <= series.dates[b]:
            shares *= f
    return series.bars[b][2] * shares / series.bars[a][2] - 1


def build(assets, runs, signals, bars, splits, divs, coarse, members, run_members=None, now=None, situation_flags=None):
    """members: today's list per sector; run_members: the list each signal run actually had (#88).
    The baselines use the run's own list, and today's only for runs recorded before that existed."""
    run_members = run_members or {}
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
    bench_yahoo = {aid: yahoo for aid, _name, yahoo in BENCHMARKS}
    fx = {pair: series_for(bench_yahoo[pair], "Index") for pair in {p for p, _ in FX.values()}}
    local = {ex: series_for(bench_yahoo[aid], bex) for ex, (aid, bex) in LOCAL_BENCH.items()}
    ai_1m, random_1m = {}, {}      # run id -> 1-month excesses vs SPY (AI buy picks; every stock in its list)

    rows, groups = [], {}
    def add(group, key, horizon, pair):
        groups.setdefault(group, {}).setdefault(key, {}).setdefault(horizon, []).append(pair)

    counts = {"signals": 0, "scored": 0, "pending": 0, "no_data": 0, "unreliable": 0}
    for s in sorted(signals, key=lambda x: (runs.get(x["signal_run_id"], {}).get("generated_utc", ""), x["kind"], x["rank"] or 0)):
        run = runs.get(s["signal_run_id"])
        if not run:
            continue
        if is_shadow(run):                                      # never in live rows, counts or summaries
            continue
        counts["signals"] += 1
        a = assets.get(s["asset_id"])
        symbol = a["yahoo"] if a else None
        generated = parse_utc(run["generated_utc"])
        note = ""
        if s["asset_id"] in UNRELIABLE:
            entry, res, note = None, {}, UNRELIABLE[s["asset_id"]]
        elif symbol in coarse or (symbol in bars and coarse_closes([b["close"] for b in bars[symbol]], 10)):
            entry, res, note = None, {}, "unreliable price (Yahoo rounds it too coarsely)"
        else:
            ser = series_for(symbol, a["exchange"]) if a else None
            windows = {}
            entry, res, note = measure(generated, ser, spy, now, windows)
            if s["signal"] in BUY_SIDE:
                for name, (i, j, target) in windows.items():
                    r, sp = res[name]
                    d0, d1 = ser.dates[i], ser.dates[j]
                    rg, sg = to_gbp(r, currency.get(symbol), d0, d1, fx), to_gbp(sp, "USD", d0, d1, fx)
                    if rg is not None and sg is not None:
                        add("in_gbp", "buy signals", name, (rg, sg))
                    bench = local.get(a["exchange"])
                    if bench is not None:
                        b = window_return(bench, ser.opens[i], target)
                        if b is not None:
                            add("vs_local", "vs FTSE 100", name, (r, b))
                            add("vs_local", "vs S&P 500", name, (r, sp))
                if s["kind"] == "ai" and isinstance(res.get("1m"), tuple) and run.get("provenance") == "live":
                    ai_1m.setdefault(s["signal_run_id"], []).append(res["1m"][0] - res["1m"][1])
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
        if s["kind"] == "ai" and s["signal"] in BUY_SIDE:
            for name, _ in HORIZONS:
                v = res.get(name)
                if isinstance(v, tuple):
                    add("baselines", "ai_picks", name, v)
                    add("by_variant", run.get("variant") or "live-1", name, v)
        if note.startswith(("unreliable", "wrong")):
            counts["unreliable"] += 1
        elif scored:
            counts["scored"] += 1
        elif note == "awaiting entry" or "pending" in res.values():
            counts["pending"] += 1
        else:
            counts["no_data"] += 1

    # Baselines: once per AI run, over the same sector's stocks on the same date
    ai_runs = sorted(r for r in {s["signal_run_id"] for s in signals if s["kind"] == "ai"} & set(runs) if not is_shadow(runs[r]))
    lists = {"own": 0, "today": 0}
    for rid in ai_runs if (members or run_members) else []:
        run = runs[rid]
        if run.get("provenance") != "live":
            continue
        generated = parse_utc(run["generated_utc"])
        scored = []
        candidates = run_members.get(rid)
        lists["own" if candidates else "today"] += 1
        for aid in candidates or members.get(run["sector"], []):
            a = assets.get(aid)
            if not a or aid in UNRELIABLE or a["yahoo"] in coarse:
                continue
            ser = series_for(a["yahoo"], a["exchange"])
            if ser is None:
                continue
            _entry, res, _note = measure(generated, ser, spy, now)
            scored.append((momentum_score(ser, generated), res))
            if isinstance(res.get("1m"), tuple):
                random_1m.setdefault(rid, []).append(res["1m"][0] - res["1m"][1])
            for name, _ in HORIZONS:
                if isinstance(res.get(name), tuple):
                    add("baselines", "random", name, res[name])
        ranked = sorted((x for x in scored if x[0] is not None), key=lambda x: -x[0])[:MOMENTUM_PICKS]
        for _score, res in ranked:
            for name, _ in HORIZONS:
                if isinstance(res.get(name), tuple):
                    add("baselines", "momentum_rule", name, res[name])

    summary = {g: {k: {h: summarise(v) for h, v in hs.items()} for k, hs in keys.items()} for g, keys in groups.items()}
    review = run_review(runs, ai_1m, random_1m, now, retired_runs())
    situations = score_situations(situation_flags or [], assets, series_for, now)
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
            "in_gbp": "the same windows with the stock and SPY both converted to pounds at that day's closing exchange rate "
                      "(entry and exit dates); London stocks are already in pounds",
            "vs_local": "London-listed picks are also compared with the FTSE 100 (iShares ISF.L) over the same window",
            "run_review": f"each signal run's AI picks vs picking at random from the same list, per run date, 1-month excess vs SPY; "
                          f"a run is judged once it has {REVIEW_MIN_DATES} run dates with a finished result and flagged when its average "
                          "and most of its run dates are behind random ('mixed' when they disagree). Flags are for the owner's quarterly review; no run is paused automatically.",
            "baselines": "for every AI run, on the same date: 'random' scores every stock in that sector (picking at random from the same list); "
                         "'momentum_rule' scores the sector's 10 stocks with the best 6-month return skipping the latest month. "
                         "Same entry, exit and benchmark rules. Each run uses the list of stocks it could choose from "
                         "that day; runs from before those lists were recorded use today's list.",
        },
        "counts": {**counts, "baseline_lists": lists},
        "summary": summary,
        "run_review": review,
        "situations": situations,
        "columns": ["time_utc", "sector", "kind", "ticker", "signal", "confidence", "rank", "provenance",
                    "entry_date", "entry_price", "currency", "r1w", "x1w", "r1m", "x1m", "r3m", "x3m", "note"],
        "rows": rows,
        "names": {t: names[t] for t in sorted({r[3] for r in rows}) if t in names},
    }


# ── Situations (generate_situations.py): were the odds right? ─────────────────
SITUATION_DAYS = 30
SITUATION_BIG = 0.10


def close_return(series, i, j):
    """Close at bar i to close at bar j, splits and cash dividends counted (like total_return, close-based)."""
    d0, d1 = series.dates[i], series.dates[j]
    shares, cash = 1.0, 0.0
    for d in sorted(set(series.splits) | set(series.dividends)):
        if d0 < d <= d1:
            shares *= series.splits.get(d, 1.0)
            cash += series.dividends.get(d, 0.0) * shares
    return (series.bars[j][2] * shares + cash) / series.bars[i][2] - 1


def month_move(series, date, now):
    """Return from the close on/before `date` to the close on/before date + 30 days; 'pending' or None."""
    if series is None:
        return None
    target = (dt.date.fromisoformat(date) + dt.timedelta(days=SITUATION_DAYS)).isoformat()
    if target > complete_through(series.exchange, now):
        return "pending"
    i, j = series.last_close_on_or_before(date), series.last_close_on_or_before(target)
    if i is None or j is None or j <= i or not series.bars[i][2]:
        return None
    if dt.date.fromisoformat(date) - dt.date.fromisoformat(series.dates[i]) > MAX_EXIT_GAP:
        return None
    return close_return(series, i, j)


def score_situations(flags, assets, series_for, now):
    """Each first flag: did a 10%+ move happen within 30 days (vs the stated chance), and which way?
    Base rate: how often any stock on the site moved that much over the same 30 days."""
    by_ticker = {aid: a for aid, a in assets.items()}
    scored, pending, base_cache = [], 0, {}
    for f in flags:
        a = by_ticker.get(f.get("ticker"))
        r = month_move(series_for(a["yahoo"], a["exchange"]), f["date"], now) if a else None
        if r == "pending":
            pending += 1
            continue
        if r is None:
            continue
        if f["date"] not in base_cache:
            moves = [month_move(series_for(x["yahoo"], x["exchange"]), f["date"], now) for x in assets.values()
                     if x.get("kind") != "benchmark"]
            moves = [m for m in moves if isinstance(m, float)]
            base_cache[f["date"]] = sum(abs(m) >= SITUATION_BIG for m in moves) / len(moves) if moves else None
        scored.append((f, r, base_cache[f["date"]]))
    out = {"days": SITUATION_DAYS, "big_move_pct": SITUATION_BIG * 100, "flags": len(flags), "pending": pending,
           "scored": len(scored),
           "first_due": min(((dt.date.fromisoformat(f["date"]) + dt.timedelta(days=SITUATION_DAYS)).isoformat()
                             for f in flags), default=None)}
    if not scored:
        return out
    big = [abs(r) >= SITUATION_BIG for _f, r, _b in scored]
    ps = [f["p_big"] for f, _r, _b in scored]
    bases = [b for _f, _r, b in scored if b is not None]
    base = statistics.fmean(bases) if bases else None
    brier = statistics.fmean((p - y) ** 2 for p, y in zip(ps, big))
    leaned = [(f, r) for f, r, _b in scored if f.get("lean") in ("up", "down")]
    buckets = []
    for lo, hi in ((0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.01)):
        xs = [(p, y) for p, y in zip(ps, big) if lo <= p < hi]
        if xs:
            buckets.append({"range": f"{int(lo * 100)}–{min(100, int(hi * 100))}%", "n": len(xs),
                            "predicted": round(100 * statistics.fmean(p for p, _ in xs), 1),
                            "actual": round(100 * sum(y for _, y in xs) / len(xs), 1)})
    out.update({
        "predicted_big": round(100 * statistics.fmean(ps), 1),
        "actual_big": round(100 * sum(big) / len(big), 1),
        "base_rate": round(100 * base, 1) if base is not None else None,
        "brier": round(brier, 4),
        "brier_base": round(statistics.fmean((base - y) ** 2 for y in big), 4) if base is not None else None,
        "direction": {"n": len(leaned), "right": round(100 * sum((r > 0) == (f["lean"] == "up") for f, r in leaned)
                                                       / len(leaned), 1) if leaned else None},
        "calibration": buckets,
    })
    return out


def load_flags():
    try:
        with open(os.path.join(ROOT, "situations", "flags.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def retired_runs():
    """Signal runs that no longer run (#88): the retired theme folders."""
    try:
        sys.path.insert(0, ROOT)
        import universe  # noqa: E402
        return set(universe.RETIRED_FOLDERS)
    except ImportError:
        return set()


def next_quarter(now):
    q = (now.month - 1) // 3 + 1
    y, m = (now.year + 1, 1) if q == 4 else (now.year, 3 * q + 1)
    return dt.date(y, m, 1).isoformat()


def run_review(runs, ai_1m, random_1m, now, retired=()):
    """Per signal run (sector / group / theme): on each run date, the AI picks' mean 1-month excess and every
    stock in its list's mean. Judged once REVIEW_MIN_DATES dates are finished. Averages over dates, so
    AI minus random adds up; 'behind' needs the average AND most dates behind, 'ahead' both ahead."""
    per = {}
    for rid, ai in ai_1m.items():
        rnd = random_1m.get(rid)
        if not ai or not rnd:
            continue
        run = runs[rid]
        per.setdefault(run["sector"], {}).setdefault(run["generated_utc"][:10], []).append(
            (statistics.fmean(ai), statistics.fmean(rnd)))
    last_run = {}
    for r in runs.values():
        if r.get("provenance") == "live" and not is_shadow(r):
            last_run[r["sector"]] = max(last_run.get(r["sector"], ""), r["generated_utc"])
    pct = lambda x: round(x * 100, 2)
    out = []
    for sector, days in per.items():
        rows = [(statistics.fmean(a for a, _ in v), statistics.fmean(b for _, b in v)) for v in days.values()]
        n = len(rows)
        ai_avg, rnd_avg = statistics.fmean(a for a, _ in rows), statistics.fmean(b for _, b in rows)
        behind = sum(a < b for a, b in rows)
        if n < REVIEW_MIN_DATES:
            status = "too few dates"
        elif ai_avg < rnd_avg and behind * 2 > n:
            status = "behind random"
        elif ai_avg > rnd_avg and behind * 2 < n:
            status = "ahead of random"
        else:
            status = "mixed"
        out.append({"run": sector, "dates": n, "ai_avg": pct(ai_avg), "random_avg": pct(rnd_avg),
                    "diff_avg": pct(ai_avg - rnd_avg), "dates_behind": behind, "status": status,
                    "active": sector not in retired, "last_run": last_run.get(sector, "")[:10]})
    order = {"behind random": 0, "mixed": 1, "ahead of random": 2, "too few dates": 3}
    out.sort(key=lambda x: (not x["active"], order[x["status"]], x["run"]))
    return {"horizon": "1m", "min_dates": REVIEW_MIN_DATES, "next_review": next_quarter(now), "runs": out}


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
    result = build(*load(h), now=utc_now(), situation_flags=load_flags())
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
