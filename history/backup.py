"""Dump / restore the history database (#54: D1 Time Travel only covers 30 days).

    python -m history.backup dump backup/          # every table -> backup/<table>.ndjson.gz
    python -m history.backup restore backup/       # load a dump into the configured DB
    python -m history.backup verify backup/        # restore into a throwaway SQLite file, compare row counts

update-history.yml dumps every Friday, verifies the dump (#72, #122) and keeps it as a 90-day GitHub artifact.
`verify` never touches the configured database: it always restores into a temporary SQLite file, even
when the D1 secrets are set, and fails if any table's row count differs from manifest.json.
Restore defaults to a local SQLite file; set the D1 secrets to restore into D1.
Reads page by primary key (no OFFSET), so a dump reads each row once.
"""
import gzip
import json
import os
import sys

from history.db import HistoryError, connect, upsert_clause

PAGE = 5000
# table -> primary key columns (must match schema.sql)
TABLES = {
    "meta": ["key"],
    "runs": ["run_id"],
    "assets": ["asset_id"],
    "asset_sectors": ["asset_id", "sector"],
    "price_snapshots": ["asset_id", "as_of_utc"],
    "daily_bars": ["symbol", "date"],
    "corporate_actions": ["symbol", "date", "kind"],
    "data_flags": ["symbol", "date", "kind"],
    "signal_runs": ["signal_run_id"],
    "signals": ["signal_run_id", "kind", "asset_id"],
    "market_snapshots": ["as_of_utc"],
    "run_universe": ["signal_run_id", "asset_id"],
}


def dump(h, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    counts = {}
    for table, pk in TABLES.items():
        rows = h.fetch_all(table, pk, page=PAGE)
        with gzip.open(os.path.join(out_dir, f"{table}.ndjson.gz"), "wt", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, sort_keys=True) + "\n")
        counts[table] = len(rows)
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"tables": counts}, f, indent=2)
    return counts


def restore(h, in_dir):
    h.ensure_schema()
    counts = {}
    for table, pk in TABLES.items():
        path = os.path.join(in_dir, f"{table}.ndjson.gz")
        if not os.path.exists(path):
            continue
        with gzip.open(path, "rt", encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
        if not rows:
            counts[table] = 0
            continue
        cols = list(rows[0].keys())
        others = [c for c in cols if c not in pk]
        clause = upsert_clause(pk, others) if others else "IGNORE"
        counts[table] = h.write(table, cols, [[r.get(c) for c in cols] for r in rows], clause)
    return counts


def verify(in_dir):
    """Restore a dump into a throwaway SQLite file and compare each table's row count with manifest.json.
    Returns a list of problems (empty = the backup restores completely)."""
    import tempfile
    with open(os.path.join(in_dir, "manifest.json"), encoding="utf-8") as f:
        expected = json.load(f)["tables"]
    with tempfile.TemporaryDirectory() as tmp:
        h = connect(sqlite_path=os.path.join(tmp, "verify.sqlite"))
        restore(h, in_dir)
        problems = []
        for table in TABLES:
            got = h.run(f"SELECT COUNT(*) AS n FROM {table}")[0]["n"]
            want = expected.get(table)
            print(f"  {table:18} manifest {want!s:>8}  restored {got:>8}")
            if want is None:
                problems.append(f"{table}: missing from manifest.json")
            elif got != want:
                problems.append(f"{table}: manifest says {want} rows, restore gave {got}")
    return problems


def main(argv):
    if len(argv) != 3 or argv[1] not in ("dump", "restore", "verify"):
        print(__doc__)
        return 2
    if argv[1] == "verify":
        problems = verify(argv[2])
        for p in problems:
            print("ERROR:", p)
        print("backup verified: every table restores with the manifest's row count" if not problems else
              f"backup FAILED verification: {len(problems)} problem(s)")
        return 1 if problems else 0
    h = connect()
    print(f"History ← {h.db.name}" if argv[1] == "dump" else f"History → {h.db.name}")
    counts = dump(h, argv[2]) if argv[1] == "dump" else restore(h, argv[2])
    for table, n in counts.items():
        print(f"  {table:18} {n:>8} rows")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except HistoryError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
