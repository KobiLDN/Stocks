"""History database client: Cloudflare D1 over its REST API, or a local SQLite file.

Both backends run the exact same SQL text, so tests and branch runs (local SQLite)
exercise the statements production (D1) will run.

Backend choice (connect()):
  - D1 when CLOUDFLARE_ACCOUNT_ID, D1_DATABASE_ID and D1_API_TOKEN are all set.
    They exist only in the GitHub `production` environment, which only `main` can use,
    so a branch run can never write production history (#54, "Previews").
  - otherwise a local SQLite file (HISTORY_SQLITE, default history/history.sqlite).

Values are written as SQL literals via lit(), not bound parameters: D1 allows only
100 bound parameters per statement, which would mean ~10 rows per HTTP call.
Every write is an upsert or INSERT OR IGNORE keyed on a primary key, so retrying a
call is always safe.
"""
import datetime as dt
import hashlib
import json
import math
import numbers
import os
import sqlite3
import sys
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCHEMA_VERSION = "1"
MAX_STATEMENT_BYTES = 90_000   # D1's limit is 100 KB per statement

# Not in any sector, but needed for history: the track record is measured against
# SPY (#54), and market.json shows SPY / QQQ / VIX. (asset_id, name, yahoo symbol)
BENCHMARKS = [
    ("SPY", "SPDR S&P 500 ETF", "SPY"),
    ("QQQ", "Invesco QQQ Trust", "QQQ"),
    ("VIX", "CBOE Volatility Index", "^VIX"),
]


class HistoryError(RuntimeError):
    pass


def utc_now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── SQL literals ──────────────────────────────────────────────────────────────
def lit(v):
    """Python value -> SQLite literal. NaN/inf -> NULL. Rejects anything unexpected."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, numbers.Integral):
        return str(int(v))
    if isinstance(v, numbers.Real):
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return "NULL"
        return repr(f)
    if isinstance(v, str):
        return "'" + v.replace("\x00", "").replace("'", "''") + "'"
    raise TypeError(f"cannot store {type(v).__name__}: {v!r}")


def insert_statements(table, columns, rows, on_conflict="", max_bytes=MAX_STATEMENT_BYTES):
    """Multi-row INSERTs, each under max_bytes. `on_conflict` is appended verbatim,
    e.g. 'ON CONFLICT(symbol, date) DO UPDATE SET close = excluded.close'.
    Use verb 'INSERT OR IGNORE' by passing on_conflict='IGNORE'."""
    verb = "INSERT OR IGNORE INTO" if on_conflict == "IGNORE" else "INSERT INTO"
    tail = "" if on_conflict in ("", "IGNORE") else " " + on_conflict
    head = f"{verb} {table} ({', '.join(columns)}) VALUES "
    out, chunk, size = [], [], len(head) + len(tail)
    for row in rows:
        if len(row) != len(columns):
            raise ValueError(f"{table}: row has {len(row)} values, want {len(columns)}")
        values = "(" + ", ".join(lit(v) for v in row) + ")"
        if len(values) + len(head) + len(tail) > max_bytes:
            raise ValueError(f"{table}: one row is larger than {max_bytes} bytes")
        if chunk and size + len(values) + 2 > max_bytes:
            out.append(head + ", ".join(chunk) + tail)
            chunk, size = [], len(head) + len(tail)
        chunk.append(values)
        size += len(values) + 2
    if chunk:
        out.append(head + ", ".join(chunk) + tail)
    return out


def upsert_clause(key_cols, value_cols):
    sets = ", ".join(f"{c} = excluded.{c}" for c in value_cols)
    return f"ON CONFLICT({', '.join(key_cols)}) DO UPDATE SET {sets}"


def schema_statements():
    with open(os.path.join(HERE, "schema.sql"), encoding="utf-8") as f:
        text = "\n".join(line for line in f.read().splitlines() if not line.strip().startswith("--"))
    return [s.strip() for s in text.split(";") if s.strip()]


# ── Backends ──────────────────────────────────────────────────────────────────
class LocalSQLite:
    name = "local SQLite"

    def __init__(self, path):
        self.path = path
        self.con = sqlite3.connect(path)
        self.con.row_factory = sqlite3.Row

    def run(self, sql):
        cur = self.con.execute(sql)
        rows = [dict(r) for r in cur.fetchall()]
        self.con.commit()
        return rows


class D1:
    name = "Cloudflare D1"

    def __init__(self, account_id, database_id, token):
        import requests  # only needed for D1
        self._requests = requests
        self.url = (f"https://api.cloudflare.com/client/v4/accounts/{account_id}"
                    f"/d1/database/{database_id}/query")
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def run(self, sql):
        """One statement. Retries on rate limits / server errors (writes are idempotent)."""
        last = None
        for attempt in range(5):
            try:
                r = self._requests.post(self.url, headers=self.headers, json={"sql": sql}, timeout=60)
            except self._requests.RequestException as e:
                last = f"network error: {e}"
            else:
                if r.status_code in (429, 500, 502, 503, 504):
                    last = f"HTTP {r.status_code}: {r.text[:300]}"
                else:
                    try:
                        body = r.json()
                    except ValueError:
                        raise HistoryError(f"D1 HTTP {r.status_code}, not JSON: {r.text[:300]}")
                    if not body.get("success"):
                        raise HistoryError(f"D1 error (HTTP {r.status_code}): {body.get('errors')} — SQL: {sql[:200]}")
                    results = body.get("result") or []
                    return (results[-1].get("results") or []) if results else []
            time.sleep(2 ** attempt)
        raise HistoryError(f"D1 failed after retries: {last}")


def connect(sqlite_path=None):
    acct, dbid, token = (os.getenv(k, "").strip() for k in ("CLOUDFLARE_ACCOUNT_ID", "D1_DATABASE_ID", "D1_API_TOKEN"))
    if acct and dbid and token and not sqlite_path:
        return History(D1(acct, dbid, token))
    if any((acct, dbid, token)) and not sqlite_path:
        missing = [k for k, v in (("CLOUDFLARE_ACCOUNT_ID", acct), ("D1_DATABASE_ID", dbid), ("D1_API_TOKEN", token)) if not v]
        raise HistoryError(f"D1 is half-configured: missing {', '.join(missing)}")
    path = sqlite_path or os.getenv("HISTORY_SQLITE") or os.path.join(HERE, "history.sqlite")
    return History(LocalSQLite(path))


def connect_for_bot():
    """connect(), except on `main` without D1 secrets: warn and return None (caller exits 0).
    Until the owner adds the secrets, history is simply not recorded; once they exist,
    any D1 error fails the step loudly."""
    configured = all(os.getenv(k, "").strip() for k in ("CLOUDFLARE_ACCOUNT_ID", "D1_DATABASE_ID", "D1_API_TOKEN"))
    if os.getenv("GITHUB_REF") == "refs/heads/main" and not configured and not os.getenv("HISTORY_SQLITE"):
        print("::warning::History not recorded — D1 secrets are not set in the GitHub 'production' environment.")
        return None
    return connect()


# ── History: schema, runs, writes ─────────────────────────────────────────────
class History:
    def __init__(self, backend):
        self.db = backend
        self.rows_offered = 0
        self.calls = 0

    def run(self, sql):
        self.calls += 1
        return self.db.run(sql)

    def ensure_schema(self):
        try:
            rows = self.run("SELECT value FROM meta WHERE key = 'schema_version'")
            current = rows[0]["value"] if rows else None
        except (HistoryError, sqlite3.Error):
            current = None
        if current == SCHEMA_VERSION:
            return False
        for stmt in schema_statements():
            self.run(stmt)
        self.run(f"INSERT INTO meta (key, value) VALUES ('schema_version', {lit(SCHEMA_VERSION)}) "
                 "ON CONFLICT(key) DO UPDATE SET value = excluded.value")
        return True

    def write(self, table, columns, rows, on_conflict=""):
        rows = list(rows)
        for stmt in insert_statements(table, columns, rows, on_conflict):
            self.run(stmt)
        self.rows_offered += len(rows)
        return len(rows)

    # Runs ---------------------------------------------------------------------
    def begin_run(self, bot):
        started = utc_now()
        gh = os.getenv("GITHUB_RUN_ID", "local")
        run_id = f"{bot}-{started.strftime('%Y%m%dT%H%M%SZ')}-{gh}-{uuid.uuid4().hex[:6]}"
        self.run(insert_statements("runs", ["run_id", "bot", "status", "started_utc", "git_sha", "gh_run"],
                                   [[run_id, bot, "running", iso(started), os.getenv("GITHUB_SHA"), gh]])[0])
        return run_id

    def finish_run(self, run_id, status="complete", note=None):
        self.run(f"UPDATE runs SET status = {lit(status)}, finished_utc = {lit(iso(utc_now()))}, "
                 f"rows_offered = {lit(self.rows_offered)}, note = {lit(note)} WHERE run_id = {lit(run_id)}")

    # Universe -----------------------------------------------------------------
    def sync_universe(self, universe, extra_assets=()):
        """Mirror universe.yaml (+ benchmark assets) into assets/asset_sectors when it changed."""
        blob = json.dumps([universe, list(extra_assets)], sort_keys=True, default=str)
        digest = hashlib.sha256(blob.encode()).hexdigest()[:16]
        rows = self.run("SELECT value FROM meta WHERE key = 'universe_hash'")
        if rows and rows[0]["value"] == digest:
            return False
        now = iso(utc_now())
        asset_rows = []
        for aid, a in universe["assets"].items():
            kind = "crypto" if a["exchange"] == "Crypto" else "equity"
            asset_rows.append([aid, a["name"], a["exchange"], kind, a["yahoo"], a.get("special"),
                               a.get("cmc_symbol"), a.get("cmc_id"), a.get("coingecko"), now])
        for aid, name, yahoo in extra_assets:
            asset_rows.append([aid, name, "Index", "benchmark", yahoo, None, None, None, None, now])
        cols = ["asset_id", "name", "exchange", "kind", "yahoo", "special", "cmc_symbol", "cmc_id", "coingecko", "updated_utc"]
        self.write("assets", cols, asset_rows, upsert_clause(["asset_id"], cols[1:]))
        self.run("DELETE FROM asset_sectors")
        member_rows = [[t, sector, category, i]
                       for sector, members in universe["sectors"].items()
                       for i, (t, category) in enumerate(members)]
        self.write("asset_sectors", ["asset_id", "sector", "category", "position"], member_rows)
        self.run(f"INSERT INTO meta (key, value) VALUES ('universe_hash', {lit(digest)}) "
                 "ON CONFLICT(key) DO UPDATE SET value = excluded.value")
        return True


def load_universe():
    sys.path.insert(0, ROOT)
    import universe  # noqa: E402
    return universe.load()
