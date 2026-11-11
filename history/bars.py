"""End-of-day daily bars -> history database (#54 step 3). The ONLY writer of daily_bars.

    python -m history.bars                          # nightly: re-fetch the last 10 days
    python -m history.bars --days 400 --budget 80000   # one-off backfill (resumable)

Runs after the evening export (update-history.yml). Every write is an upsert keyed on
(symbol, date), so re-fetching overlapping days just corrects them (late or revised
bars). Missing days are left missing.

RAW prices: Yahoo's daily Open/High/Low/Close (even with auto_adjust=False) are already
split-adjusted. We undo that with the split events in the same fetch:
    raw(t) = yahoo(t) * product of split ratios dated after t
so a later split never changes a stored price; adjust when reading instead.
Prices stay in the instrument's own quote currency — LSE is usually GBp (pence).

Flags (data_flags): a day-over-day move that matches a split ratio with no split
recorded (split_like_jump), a x100 move (unit_jump: pence/pounds mix-up), and an LSE
pence asset whose quote currency isn't GBp (currency_mismatch).
"""
import argparse
import datetime as dt
import sys
import time

from history.db import BENCHMARKS, HistoryError, connect_for_bot, lit, load_universe, upsert_clause

BAR_COLS = ["symbol", "date", "open", "high", "low", "close", "volume", "currency", "run_id"]
ACTION_COLS = ["symbol", "date", "kind", "value", "currency", "run_id"]
FLAG_COLS = ["symbol", "date", "kind", "detail", "run_id"]
SPLIT_RATIOS = (2, 3, 4, 5, 8, 10, 15, 20, 25, 30, 40, 50)
FLAG_KINDS = ("split_like_jump", "unit_jump")
TOLERANCE = 0.06   # a split day can also move a few % on the day
FALLBACK_CURRENCY = {"lse_pence": "GBp", "jpy": "JPY", "sar": "SAR"}


def sig(x, digits=10):
    """Round to significant figures (keeps tiny prices like PEPE's 0.0000037)."""
    if x is None:
        return None
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    if f != f:          # NaN
        return None
    return float(f"{f:.{digits}g}")


def instruments(universe):
    """{yahoo symbol: (asset_id, special)} — one entry per instrument, plus benchmarks."""
    out = {}
    for aid, a in universe["assets"].items():
        out.setdefault(a["yahoo"], (aid, a.get("special")))
    for aid, _name, yahoo in BENCHMARKS:
        out.setdefault(yahoo, (aid, None))
    return out


# ── Pure transform (tested without network) ───────────────────────────────────
def _scale(x, f):
    return None if x is None or x != x else sig(x * f)


def to_raw(rows):
    """rows: [(date, open, high, low, close, volume, split_ratio, dividend)] oldest first,
    Yahoo split-adjusted. Returns (bars, splits, dividends) with prices un-adjusted."""
    rows = sorted(rows, key=lambda r: r[0])
    factor, factors = 1.0, [1.0] * len(rows)
    for i in range(len(rows) - 1, -1, -1):        # walk back: splits dated after t apply to t
        factors[i] = factor
        split = rows[i][6] or 0
        if split and split > 0 and split != 1:
            factor *= split
    bars, splits, divs = [], [], []
    for (d, o, h, l, c, v, split, div), f in zip(rows, factors):
        if c is None or c != c:
            continue                               # no trade data for this row: leave the gap
        bars.append((d, _scale(o, f), _scale(h, f), _scale(l, f), _scale(c, f), _scale(v, 1 / f)))
        if split and split > 0 and split != 1:
            splits.append((d, sig(split)))
        if div and div == div and div > 0:
            divs.append((d, sig(div * f)))
    return bars, splits, divs


def jump_flags(bars, split_dates):
    """[(date, kind, detail)] for raw day-over-day moves that look like units or splits."""
    flags = []
    for (d0, *_r0, c0, _v0), (d1, *_r1, c1, _v1) in zip(bars, bars[1:]):
        if not c0 or not c1 or d1 in split_dates:
            continue
        r = c1 / c0
        if abs(r * 100 - 1) < TOLERANCE or abs(r / 100 - 1) < TOLERANCE:
            flags.append((d1, "unit_jump", f"close {c0:g} -> {c1:g} (x{r:.4g}): pence/pounds?"))
            continue
        for k in SPLIT_RATIOS:
            if abs(r * k - 1) < TOLERANCE or abs(r / k - 1) < TOLERANCE:
                flags.append((d1, "split_like_jump", f"close {c0:g} -> {c1:g} (x{r:.4g}) ~ {k}:1, no split recorded"))
                break
    return flags


# ── yfinance adapter ──────────────────────────────────────────────────────────
def fetch(symbol, start, end):
    """Returns (rows, currency) from Yahoo, rows as to_raw() expects."""
    import yfinance as yf
    t = yf.Ticker(symbol)
    df = t.history(start=start.isoformat(), end=end.isoformat(), interval="1d",
                   auto_adjust=False, actions=True)
    meta = getattr(t, "history_metadata", None) or {}
    rows = []
    for idx, r in df.iterrows():
        rows.append((idx.strftime("%Y-%m-%d"), r.get("Open"), r.get("High"), r.get("Low"), r.get("Close"),
                     r.get("Volume"), r.get("Stock Splits"), r.get("Dividends")))
    return rows, meta.get("currency")


# ── Job ───────────────────────────────────────────────────────────────────────
def backfilled(h, start):
    """Symbols already backfilled back to `start` (or earlier)."""
    rows = h.run("SELECT key, value FROM meta WHERE key LIKE 'backfill:%'")
    return {r["key"][len("backfill:"):] for r in rows if r["value"] <= start}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=10, help="calendar days to (re)fetch (default 10)")
    ap.add_argument("--budget", type=int, default=80_000, help="max bar rows to write this run (D1 free: 100k/day)")
    ap.add_argument("--only", help="comma-separated Yahoo symbols (testing)")
    args = ap.parse_args(argv)

    universe = load_universe()
    h = connect_for_bot()
    if h is None:
        return 0
    print(f"History → {h.db.name}")
    h.ensure_schema()
    h.sync_universe(universe, BENCHMARKS)

    today = dt.datetime.now(dt.timezone.utc).date()
    start, end = today - dt.timedelta(days=args.days), today + dt.timedelta(days=1)
    backfill = args.days > 31
    insts = instruments(universe)
    if args.only:
        wanted = set(args.only.split(","))
        insts = {s: v for s, v in insts.items() if s in wanted}
    skip = backfilled(h, start.isoformat()) if backfill else set()
    todo = [s for s in insts if s not in skip]
    print(f"  {'backfill' if backfill else 'nightly'}: {start} → {today}, {len(todo)} instruments"
          f"{f' ({len(skip)} already backfilled)' if skip else ''}, budget {args.budget} rows")

    run_id = h.begin_run("bars")
    bars_up = upsert_clause(["symbol", "date"], BAR_COLS[2:])
    act_up = upsert_clause(["symbol", "date", "kind"], ACTION_COLS[3:])
    flag_up = upsert_clause(["symbol", "date", "kind"], FLAG_COLS[3:])
    pending = {"bars": [], "actions": [], "flags": [], "done": []}
    written, failed, empty = 0, [], []

    def flush():
        nonlocal written
        h.write("daily_bars", BAR_COLS, pending["bars"], bars_up)
        h.write("corporate_actions", ACTION_COLS, pending["actions"], act_up)
        h.write("data_flags", FLAG_COLS, pending["flags"], flag_up)
        if backfill and pending["done"]:
            h.write("meta", ["key", "value"], [[f"backfill:{s}", start.isoformat()] for s in pending["done"]],
                    upsert_clause(["key"], ["value"]))
        written += len(pending["bars"])
        for k in pending:
            pending[k] = []

    try:
        # Flags in the window are recomputed from scratch (a split Yahoo reports a day late
        # turns yesterday's split_like_jump into a recorded split).
        kinds = ", ".join(f"'{k}'" for k in FLAG_KINDS)
        scope = f" AND symbol IN ({', '.join(lit(s) for s in insts)})" if args.only else ""
        h.run(f"DELETE FROM data_flags WHERE date >= {lit(start.isoformat())} AND kind IN ({kinds}){scope}")
        for i, symbol in enumerate(todo, 1):
            if written + len(pending["bars"]) >= args.budget:
                print(f"  budget reached after {i - 1} instruments — run again to continue")
                break
            aid, special = insts[symbol]
            try:
                rows, currency = fetch(symbol, start, end)
            except Exception as e:      # one bad ticker must not stop the rest
                failed.append(f"{symbol}: {e}")
                continue
            finally:
                time.sleep(0.3)
            bars, splits, divs = to_raw(rows)
            if not bars:
                empty.append(symbol)
                continue
            if not currency:
                currency = "USD" if aid not in universe["assets"] else FALLBACK_CURRENCY.get(special, "USD")
                pending["flags"].append([symbol, today.isoformat(), "currency_missing", f"assumed {currency}", run_id])
            if special == "lse_pence" and currency != "GBp":
                pending["flags"].append([symbol, today.isoformat(), "currency_mismatch",
                                         f"universe says pence, Yahoo says {currency}", run_id])
            pending["bars"] += [[symbol, d, o, hi, lo, c, v, currency, run_id] for d, o, hi, lo, c, v in bars]
            pending["actions"] += [[symbol, d, "split", r, None, run_id] for d, r in splits]
            pending["actions"] += [[symbol, d, "dividend", a, currency, run_id] for d, a in divs]
            pending["flags"] += [[symbol, d, k, detail, run_id] for d, k, detail in jump_flags(bars, {d for d, _ in splits})]
            pending["done"].append(symbol)
            if len(pending["bars"]) >= 5000:
                flush()
                print(f"  … {i}/{len(todo)} instruments, {written} bars written")
        flush()
    except Exception as e:
        h.finish_run(run_id, "failed", note=str(e)[:500])
        raise
    note = "; ".join(failed[:20]) or None
    h.finish_run(run_id, note=note)
    print(f"  {written} bars written, {len(failed)} failed, {len(empty)} returned no data, {h.calls} calls — run {run_id}")
    for f in failed:
        print(f"  FAILED {f}")
    if empty:
        print(f"  NO DATA: {', '.join(empty)}")
    # Most instruments failing means Yahoo (or our code) is broken — make the run red.
    if todo and len(failed) + len(empty) > len(todo) // 2:
        print(f"::error::{len(failed) + len(empty)} of {len(todo)} instruments returned nothing")
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except HistoryError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
