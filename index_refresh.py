"""Index membership refresh (#88, #110): S&P 500, Nasdaq-100, FTSE 100, Euro Stoxx 50, DAX, CAC 40 and
SMI members -> universe.yaml.

    python index_refresh.py                      # fetch, check, snapshot, update universe.yaml
    python index_refresh.py --catalogue PATH     # also set the "on T212" flag for new stocks
    python index_refresh.py --dry-run            # fetch and check only; write nothing

Run quarterly by .github/workflows/refresh-index-members.yml, or by hand.

Each index's fresh list must pass every check, or it is rejected (logged to
index_members/rejected/, nothing changes for that index, and the run exits non-zero):
  - at least MIN_ROWS rows;
  - every one of KNOWN members present;
  - joiners + leavers no more than MAX_CHURN of the last accepted list.

An accepted list is kept as a dated snapshot in index_members/<index>/<date>.json, never overwritten
by a later date (point-in-time membership, #88). A stock counts as a member if it is in either of the
last two accepted snapshots, so a leaver goes only after two refreshes in a row agree. A joiner is
added at once: new asset, classified like the rest (universe_classify.py). A stock in no index and in
no theme (universe.yaml sectors) moves to retired:, so past signals on it still resolve.
"""
import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone

import universe
import universe_classify as uc

ROOT = os.path.dirname(os.path.abspath(__file__))
SNAP_DIR = os.path.join(ROOT, "index_members")
INDEXES = {           # market id -> key in universe_classify.index_tables()
    "sp500": "sp500",
    "nasdaq100": "ndx",
    "ftse100": "ftse",
    "eurostoxx50": "sx5e",      # phase 2 (#110): one Europe group, index tags kept per stock
    "dax": "dax",
    "cac40": "cac",
    "smi": "smi",
}
MIN_ROWS = {"sp500": 480, "nasdaq100": 95, "ftse100": 95, "eurostoxx50": 48, "dax": 38, "cac40": 38, "smi": 19}
KNOWN = {
    "sp500": {"AAPL", "MSFT", "JPM", "XOM", "JNJ"},
    "nasdaq100": {"AAPL", "MSFT", "NVDA", "AMZN", "COST"},
    "ftse100": {"AZN.L", "HSBA.L", "SHEL.L", "ULVR.L", "BP.L"},
    "eurostoxx50": {"SAP.DE", "ASML.AS", "MC.PA", "SIE.DE", "TTE.PA"},
    "dax": {"SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "BAS.DE"},
    "cac40": {"MC.PA", "OR.PA", "TTE.PA", "SAN.PA", "AIR.PA"},
    "smi": {"NESN.SW", "NOVN.SW", "ROP.SW", "UBSG.SW", "ABBN.SW"},
}
MAX_CHURN = 0.10
# Yahoo's exchange codes -> the exchange names universe.yaml uses
YAHOO_EXCHANGE = {"NMS": "NASDAQ", "NGM": "NASDAQ", "NCM": "NASDAQ", "NYQ": "NYSE", "ASE": "NYSE",
                  "PCX": "NYSE", "BTS": "NYSE", "LSE": "LSE"}


# ── snapshots ──────────────────────────────────────────────────────────────────
def snapshots(market):
    """Accepted snapshots for one index, oldest first: [(date, {yahoo: row})]."""
    out = []
    for path in sorted(glob.glob(os.path.join(SNAP_DIR, market, "*.json"))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        out.append((data["date"], {m["yahoo"]: m for m in data["members"]}))
    return out


def write_snapshot(market, date, rows, rejected=False, why=None):
    folder = os.path.join(SNAP_DIR, "rejected") if rejected else os.path.join(SNAP_DIR, market)
    os.makedirs(folder, exist_ok=True)
    name = f"{market}-{date}.json" if rejected else f"{date}.json"
    data = {"index": market, "date": date, "source": "en.wikipedia.org", "count": len(rows)}
    if why:
        data["rejected_because"] = why
    data["members"] = [{"yahoo": r["yahoo"], "name": r["name"], "isin": r.get("isin")}
                       for r in sorted(rows, key=lambda r: r["yahoo"])]
    with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")


# ── checks (pure) ──────────────────────────────────────────────────────────────
def check(market, rows, previous):
    """Problems with a fresh list (empty = accept). previous: {yahoo: row} of the last accepted list."""
    symbols = [r["yahoo"] for r in rows]
    problems = []
    if len(set(symbols)) != len(symbols):
        problems.append("duplicate symbols")
    if len(rows) < MIN_ROWS[market]:
        problems.append(f"only {len(rows)} rows (need {MIN_ROWS[market]})")
    missing = KNOWN[market] - set(symbols)
    if missing:
        problems.append(f"known members missing: {sorted(missing)}")
    if previous:
        new, old = set(symbols), set(previous)
        churn = len(new ^ old) / len(old)
        if churn > MAX_CHURN:
            problems.append(f"churn {churn:.0%} (+{len(new - old)} / -{len(old - new)}) over {MAX_CHURN:.0%}")
    return problems


def members(snaps):
    """Current members: in either of the last two accepted snapshots (a leaver needs two in a row)."""
    if not snaps:
        return set()
    recent = [s for _, s in snaps[-2:]]
    return set().union(*recent)


# ── universe update ────────────────────────────────────────────────────────────
def new_asset_id(yahoo, assets):
    """Asset id for a joiner: the Yahoo symbol (LSE ones keep their .L, like BA.L and SSE.L).
    If that id is already another asset's (our London AstraZeneca is "AZN"), add the listing's
    country: "AZN.US"."""
    if yahoo not in assets:
        return yahoo
    alt = yahoo + ".US"
    if alt in assets:
        raise SystemExit(f"{yahoo}: ids {yahoo} and {alt} both taken — pick an id by hand")
    return alt


def plan(assets, current, themed):
    """What changes in universe.yaml. current: {market: set(yahoo)}; themed: ids in any theme group.
    Returns (markets_by_asset, joiners {yahoo: market set}, leavers [asset id])."""
    by_yahoo = {}
    for t, a in assets.items():
        by_yahoo.setdefault(a["yahoo"], []).append(t)
    markets_by_asset = {t: set() for t in assets}
    joiners = {}
    for market, symbols in current.items():
        for y in symbols:
            if y in by_yahoo:
                for t in by_yahoo[y]:
                    markets_by_asset[t].add(market)
            else:
                joiners.setdefault(y, set()).add(market)
    leavers = [t for t, a in assets.items()
               if a["exchange"] != "Crypto" and not markets_by_asset[t] and t not in themed]
    return markets_by_asset, joiners, leavers


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--catalogue", help="t212-instruments.json (private portfolio repo), for new stocks' t212 flag")
    ap.add_argument("--dry-run", action="store_true", help="fetch and check only")
    args = ap.parse_args(argv)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    tables = uc.index_tables()
    rejected = []
    for market, key in INDEXES.items():
        rows = tables[key]
        snaps = snapshots(market)
        previous = snaps[-1][1] if snaps else None
        problems = check(market, rows, previous)
        old = set(previous or ())
        new = {r["yahoo"] for r in rows}
        print(f"{market}: {len(rows)} rows, +{len(new - old)} / -{len(old - new)} vs "
              f"{snaps[-1][0] if snaps else 'nothing (first run)'}")
        if problems:
            print(f"  REJECTED: {'; '.join(problems)}")
            rejected.append(market)
            if not args.dry_run:
                write_snapshot(market, today, rows, rejected=True, why=problems)
            continue
        if not args.dry_run:
            if snaps and snaps[-1][0] == today:
                os.remove(os.path.join(SNAP_DIR, market, f"{today}.json"))   # same-day re-run replaces itself
            write_snapshot(market, today, rows)
    if args.dry_run:
        sys.exit(1 if rejected else 0)

    u = universe.load()
    assets = {t: dict(a) for t, a in u["assets"].items()}
    current, names = {}, {}
    for market in INDEXES:
        snaps = snapshots(market)
        current[market] = members(snaps)
        for _, s in snaps[-2:]:
            names.update({y: r["name"] for y, r in s.items()})
    for market in rejected:          # keep what universe.yaml already says for a rejected index
        current[market] = {a["yahoo"] for a in assets.values() if market in (a.get("markets") or [])}

    themed = {t for m in u["sectors"].values() for t, _ in m}
    markets_by_asset, joiners, leavers = plan(assets, current, themed)
    for t, m in markets_by_asset.items():
        if assets[t]["exchange"] != "Crypto":
            assets[t]["markets"] = sorted(m) or None

    added, unretired = {}, []
    retired_now = u.get("retired") or {}
    for y, m in sorted(joiners.items()):
        back = [t for t, a in retired_now.items() if a["yahoo"] == y]
        if back:                         # rejoined (Coinbase, Robinhood: old Crypto stocks, now S&P 500)
            t = back[0]
            assets[t] = {**retired_now[t], "markets": sorted(m)}
            unretired.append(t)
            added[t] = uc.yahoo_info(y)
            continue
        t = new_asset_id(y, assets)
        info = uc.yahoo_info(y)
        exchange = "LSE" if y.endswith(".L") else (uc.eu_exchange(y) or YAHOO_EXCHANGE.get(info.get("exchange")))
        if not exchange:
            print(f"  {y}: unknown Yahoo exchange {info.get('exchange')!r} — recorded as NYSE, check it")
            exchange = "NYSE"
        a = {"name": names.get(y) or info.get("name") or y, "exchange": exchange, "yahoo": y}
        if info.get("currency") == "GBp":
            a["special"] = "lse_pence"
        a["markets"] = sorted(m)
        a["currency"] = info.get("currency")
        assets[t] = a
        added[t] = info
    retire = {t: assets.pop(t) for t in leavers}
    for a in retire.values():
        a.pop("markets", None)

    catalogue = uc.Catalogue(args.catalogue) if args.catalogue else None
    seen = {assets[t]["yahoo"]: info for t, info in added.items()}    # joiners: already looked up
    updates, report = uc.classify(assets, tables, catalogue, u.get("sector_overrides") or {},
                                  yahoo=lambda y: seen.get(y) or uc.yahoo_info(y))
    for t, up in updates.items():
        assets[t].update(up)
    uc.write_universe(assets, retire=retire, unretire=unretired,
                      retire_note=f"Left every index and theme (index refresh {today})" if retire else None)
    for line in report:
        print(" ", line)
    print(f"universe.yaml: +{len(added) - len(unretired)} new, {len(unretired)} back from retired"
          + (f" ({', '.join(unretired)})" if unretired else "") + f", {len(retire)} retired"
          + (f" ({', '.join(sorted(retire))})" if retire else ""))
    problems = universe.validate()
    for p in problems:
        print("ERROR:", p)
    sys.exit(1 if problems or rejected else 0)


if __name__ == "__main__":
    main()
