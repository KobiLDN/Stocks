"""Copy what a bot just published into the history database (dual-write, #54 step 3).

    python -m history.snapshot prices    # after update-prices: every */prices.json + market.json
    python -m history.snapshot signals   # after generate-signals: every */signals-local.json

It reads the files the bot wrote, so the bots themselves are unchanged. Rows are keyed
on the data's own timestamp, so re-reading an unchanged file writes nothing new — safe
to run after a single-sector run or twice in a row.
"""
import json
import os
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from history.db import BENCHMARKS, ROOT, HistoryError, connect_for_bot, load_universe

LONDON = ZoneInfo("Europe/London")


def london_to_iso(value):
    """'2026-11-11 13:44' (London, optional ' GMT'/' BST') -> '2026-11-11T13:44:00Z'.
    Same rule as generate_export.py."""
    try:
        local = datetime.strptime(str(value)[:16], "%Y-%m-%d %H:%M").replace(tzinfo=LONDON)
    except (TypeError, ValueError):
        return None
    return local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def num(v):
    """'-0.11%' / '+5.00%' / '262.1' / 349 / None -> float or None."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", "").replace("%", "").replace("£", "").replace("$", "")
    if s in ("", "-", "—", "N/A", "n/a", "None", "null"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def read_json(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Prices + market ───────────────────────────────────────────────────────────
PRICE_COLS = ["asset_id", "as_of_utc", "sector", "price_usd", "price_gbp",
              "change_1d_pct", "market_cap_usd_b", "volume_1d", "run_id"]


def price_rows(universe, run_id, warn=print):
    rows, seen = [], set()
    for sector in universe["sectors"]:
        data = read_json(f"{sector}/prices.json")
        if not data:
            warn(f"  WARNING: {sector}/prices.json missing")
            continue
        as_of = london_to_iso(data.get("updated"))
        if not as_of:
            warn(f"  WARNING: {sector}/prices.json has no usable 'updated' ({data.get('updated')!r})")
            continue
        for s in data.get("stocks", []):
            aid = s.get("ticker")
            if aid not in universe["assets"]:
                warn(f"  WARNING: {sector}: {aid!r} is not in universe.yaml — skipped")
                continue
            if (aid, as_of) in seen:      # same asset in two sectors updated in the same minute
                continue
            seen.add((aid, as_of))
            rows.append([aid, as_of, sector, num(s.get("price_usd")), num(s.get("price_gbp")),
                         num(s.get("change_1d")), num(s.get("market_cap_usd_b")), num(s.get("vol_1d")), run_id])
    return rows


def market_row(run_id):
    m = read_json("market.json")
    if not m or not london_to_iso(m.get("updated")):
        return None
    spy, qqq, vix = (m.get(k) or {} for k in ("spy", "qqq", "vix"))
    return [london_to_iso(m["updated"]), num(spy.get("price")), num(qqq.get("price")), num(vix.get("level")),
            m.get("market_regime"), vix.get("signal"), json.dumps(m, sort_keys=True), run_id]


def record_prices(h, universe, run_id):
    n = h.write("price_snapshots", PRICE_COLS, price_rows(universe, run_id), on_conflict="IGNORE")
    row = market_row(run_id)
    if row:
        h.write("market_snapshots", ["as_of_utc", "spy", "qqq", "vix", "market_regime", "vix_signal", "payload", "run_id"],
                [row], on_conflict="IGNORE")
    else:
        print("  WARNING: market.json missing or has no 'updated'")
    return n


# ── Signals ───────────────────────────────────────────────────────────────────
def normalise_signal(v):
    """'strong_buy' / 'STRONG BUY' / 'Buy' -> 'strong_buy' / 'buy'."""
    return str(v or "").strip().lower().replace(" ", "_").replace("-", "_")


def rows_from_signal_file(sector, data, run_id, provenance="live"):
    """One signals-local.json -> (signal_run row, signal rows), or None if it isn't a real run
    (placeholder files have no parseable 'updated'). Shared by the live recorder and the git import."""
    generated = london_to_iso((data or {}).get("updated"))
    if not generated:
        return None
    srid = f"{sector}:{generated}"
    run = [srid, sector, generated, data.get("model"), provenance, run_id]
    sigs = []
    for kind, key in (("ai", "picks"), ("momentum", "momentum_picks")):
        seen = set()
        for i, p in enumerate(data.get(key) or []):
            t = p.get("ticker")
            if not t or t in seen:
                continue
            seen.add(t)
            drivers = p.get("drivers")
            sigs.append([srid, kind, t, p.get("rank", i + 1), normalise_signal(p.get("signal")), num(p.get("confidence")),
                         p.get("rationale"), json.dumps(drivers) if drivers is not None else None])
    return run, sigs


def signal_rows(universe, run_id):
    runs, sigs = [], []
    for sector in universe["sectors"]:
        got = rows_from_signal_file(sector, read_json(f"{sector}/signals-local.json"), run_id)
        if not got:
            print(f"  WARNING: {sector}/signals-local.json missing or has no 'updated'")
            continue
        runs.append(got[0])
        sigs += got[1]
    return runs, sigs


SIGNAL_RUN_COLS = ["signal_run_id", "sector", "generated_utc", "model", "provenance", "run_id"]
SIGNAL_COLS = ["signal_run_id", "kind", "asset_id", "rank", "signal", "confidence", "rationale", "drivers"]


def record_signals(h, universe, run_id):
    runs, sigs = signal_rows(universe, run_id)
    h.write("signal_runs", SIGNAL_RUN_COLS, runs, on_conflict="IGNORE")
    return h.write("signals", SIGNAL_COLS, sigs, on_conflict="IGNORE")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main(argv):
    what = argv[1] if len(argv) > 1 else ""
    if what not in ("prices", "signals"):
        print(__doc__)
        return 2
    universe = load_universe()
    h = connect_for_bot()
    if h is None:
        return 0
    print(f"History → {h.db.name}")
    if h.ensure_schema():
        print("  schema applied")
    if h.sync_universe(universe, BENCHMARKS):
        print("  universe synced")
    run_id = h.begin_run(what)
    try:
        n = record_prices(h, universe, run_id) if what == "prices" else record_signals(h, universe, run_id)
    except Exception as e:
        h.finish_run(run_id, "failed", note=str(e)[:500])
        raise
    h.finish_run(run_id)
    print(f"  {what}: {n} rows offered (already-stored rows are skipped), {h.calls} calls — run {run_id}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except HistoryError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
