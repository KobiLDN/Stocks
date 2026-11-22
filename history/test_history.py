"""Tests for the history database code. No network: a temporary local SQLite file stands
in for D1 (same SQL text). Run: python -m unittest discover -s history -t .
"""
import gzip
import json
import os
import shutil
import sqlite3
import tempfile
import unittest
from unittest import mock

from history import backup, bars, db, snapshot

D1_VARS = ("CLOUDFLARE_ACCOUNT_ID", "D1_DATABASE_ID", "D1_API_TOKEN", "GITHUB_REF", "HISTORY_SQLITE")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "h.sqlite")
        self.env = mock.patch.dict(os.environ, {"HISTORY_SQLITE": self.path})
        self.env.start()
        for k in D1_VARS[:-1]:
            os.environ.pop(k, None)
        self.h = db.connect()
        self.h.ensure_schema()
        self.universe = db.load_universe()

    def tearDown(self):
        self.env.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def count(self, table, where=""):
        return self.h.run(f"SELECT COUNT(*) AS n FROM {table} {where}")[0]["n"]


class Literals(unittest.TestCase):
    def test_values(self):
        self.assertEqual(db.lit(None), "NULL")
        self.assertEqual(db.lit(True), "1")
        self.assertEqual(db.lit(42), "42")
        self.assertEqual(db.lit(0.0000037), "3.7e-06")
        self.assertEqual(db.lit(float("nan")), "NULL")
        self.assertEqual(db.lit(float("inf")), "NULL")
        self.assertEqual(db.lit("O'Neil"), "'O''Neil'")
        with self.assertRaises(TypeError):
            db.lit({"a": 1})

    def test_literals_round_trip_through_sqlite(self):
        con = sqlite3.connect(":memory:")
        for v in ["it's", "a\nb", "£€", 3.7e-06, -12, None, "'); DROP TABLE x; --"]:
            self.assertEqual(con.execute(f"SELECT {db.lit(v)}").fetchone()[0], v)

    def test_statements_split_under_limit(self):
        rows = [[i, "x" * 50] for i in range(1000)]
        stmts = db.insert_statements("t", ["a", "b"], rows, max_bytes=5000)
        self.assertGreater(len(stmts), 10)
        self.assertTrue(all(len(s) <= 5000 for s in stmts))
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE t (a INTEGER, b TEXT)")
        for s in stmts:
            con.execute(s)
        self.assertEqual(con.execute("SELECT COUNT(*) FROM t").fetchone()[0], 1000)


class Schema(Base):
    def test_idempotent(self):
        self.assertFalse(self.h.ensure_schema())          # already at this version
        for s in db.schema_statements():                  # re-applying every statement is harmless
            self.h.run(s)

    def test_universe_sync(self):
        self.assertTrue(self.h.sync_universe(self.universe, db.BENCHMARKS))
        n_assets = len(self.universe["assets"]) + len(self.universe.get("retired") or {}) + len(db.BENCHMARKS)
        self.assertEqual(self.count("assets"), n_assets)
        self.assertEqual(self.count("asset_sectors"), sum(len(m) for m in self.universe["sectors"].values()))
        self.assertFalse(self.h.sync_universe(self.universe, db.BENCHMARKS))   # unchanged -> skipped

    def test_migrates_a_v1_database(self):
        """A database created before #70 (schema v1) gains the new columns, keeps its rows, and can't be migrated twice."""
        path = os.path.join(self.tmp, "old.sqlite")
        con = sqlite3.connect(path)
        for stmt in db.schema_statements():
            con.execute(stmt)
        con.execute("INSERT INTO meta (key, value) VALUES ('schema_version', '1')")
        con.execute("INSERT INTO signal_runs VALUES ('AI:x', 'AI', '2026-06-01T07:00:00Z', 'm', 'live', 'r')")
        con.commit(); con.close()
        with mock.patch.dict(os.environ, {"HISTORY_SQLITE": path}):
            h = db.connect()
            self.assertTrue(h.ensure_schema())
            self.assertFalse(h.ensure_schema())
            row = h.run("SELECT * FROM signal_runs")[0]
            self.assertEqual(row["sector"], "AI")
            self.assertIsNone(row["variant"])
            cols = {r["name"] for r in h.run("PRAGMA table_info(signals)")}
            self.assertTrue({"pre_momentum_label", "momentum_label", "momentum_score"} <= cols)
            self.assertEqual(h.run("SELECT COUNT(*) AS n FROM run_universe")[0]["n"], 0)     # migration 3 (#88)

    def test_migrates_a_v2_database(self):
        """A v2 database (live since #70) gains run_universe and keeps everything else."""
        path = os.path.join(self.tmp, "v2.sqlite")
        with mock.patch.dict(os.environ, {"HISTORY_SQLITE": path}):
            h = db.connect()
            with mock.patch.object(db, "SCHEMA_VERSION", "2"), mock.patch.dict(db.MIGRATIONS, clear=False) as m:
                m.pop("3", None)
                h.ensure_schema()
            self.assertNotIn("run_universe", {r["name"] for r in h.run("SELECT name FROM sqlite_master WHERE type = 'table'")})
            self.assertTrue(h.ensure_schema())
            self.assertIn("run_universe", {r["name"] for r in h.run("SELECT name FROM sqlite_master WHERE type = 'table'")})

    def test_fresh_database_has_new_columns(self):
        cols = {r["name"] for r in self.h.run("PRAGMA table_info(signal_runs)")}
        self.assertTrue({"variant", "prompt_version", "code_commit", "input_version"} <= cols)

    def test_benchmarks_do_not_clash_with_universe(self):
        for aid, _n, yahoo in db.BENCHMARKS:
            self.assertNotIn(aid, self.universe["assets"])


class Connect(unittest.TestCase):
    def test_main_without_secrets_skips(self):
        env = {"GITHUB_REF": "refs/heads/main"}
        with mock.patch.dict(os.environ, env, clear=False):
            for k in ("CLOUDFLARE_ACCOUNT_ID", "D1_DATABASE_ID", "D1_API_TOKEN", "HISTORY_SQLITE"):
                os.environ.pop(k, None)
            self.assertIsNone(db.connect_for_bot())

    def test_half_configured_is_an_error(self):
        with mock.patch.dict(os.environ, {"D1_API_TOKEN": "x"}, clear=False):
            for k in ("CLOUDFLARE_ACCOUNT_ID", "D1_DATABASE_ID", "HISTORY_SQLITE"):
                os.environ.pop(k, None)
            with self.assertRaises(db.HistoryError):
                db.connect()

    def test_d1_request_shape(self):
        d1 = db.D1("acct", "dbid", "tok")
        resp = mock.Mock(status_code=200)
        resp.json.return_value = {"success": True, "result": [{"results": [{"n": 1}], "success": True}]}
        with mock.patch.object(d1._requests, "post", return_value=resp) as post:
            self.assertEqual(d1.run("SELECT 1 AS n"), [{"n": 1}])
        url = post.call_args.args[0]
        self.assertEqual(url, "https://api.cloudflare.com/client/v4/accounts/acct/d1/database/dbid/query")
        self.assertEqual(post.call_args.kwargs["json"], {"sql": "SELECT 1 AS n"})
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer tok")

    def test_d1_error_raises(self):
        d1 = db.D1("a", "b", "c")
        resp = mock.Mock(status_code=400)
        resp.json.return_value = {"success": False, "errors": [{"message": "no such table"}]}
        with mock.patch.object(d1._requests, "post", return_value=resp):
            with self.assertRaises(db.HistoryError):
                d1.run("SELECT * FROM nope")


class Snapshot(Base):
    def test_london_time(self):
        self.assertEqual(snapshot.london_to_iso("2026-07-01 08:00"), "2026-07-01T07:00:00Z")   # BST
        self.assertEqual(snapshot.london_to_iso("2026-11-11 08:00 GMT"), "2026-11-11T08:00:00Z")
        self.assertIsNone(snapshot.london_to_iso("soon"))

    def test_signal_file_carries_run_tags_and_labels(self):
        data = {"updated": "2026-11-23 08:00 GMT", "model": "m", "variant": "live-2", "prompt_version": "abc123",
                "code_commit": "deadbeef", "input_version": "2026-11-11",
                "picks": [{"ticker": "NVDA", "rank": 1, "signal": "buy", "confidence": 0.8, "pre_momentum_label": "buy",
                           "post_momentum_label": "buy", "momentum_label": "strong_buy", "momentum_score": 0.9}],
                "momentum_picks": []}
        run, sigs = snapshot.rows_from_signal_file("AI", data, "r")
        self.assertEqual(dict(zip(snapshot.SIGNAL_RUN_COLS, run))["variant"], "live-2")
        row = dict(zip(snapshot.SIGNAL_COLS, sigs[0]))
        self.assertEqual((row["signal"], row["pre_momentum_label"], row["momentum_label"], row["momentum_score"]),
                         ("buy", "buy", "strong_buy", 0.9))
        old = {"updated": "2026-06-01 08:00", "picks": [{"ticker": "NVDA", "signal": "strong_buy"}]}   # pre-#70 file
        run, sigs = snapshot.rows_from_signal_file("AI", old, "r")
        self.assertEqual(len(run), len(snapshot.SIGNAL_RUN_COLS)); self.assertEqual(len(sigs[0]), len(snapshot.SIGNAL_COLS))
        self.assertIsNone(dict(zip(snapshot.SIGNAL_COLS, sigs[0]))["pre_momentum_label"])

    def test_momentum_no_longer_upgrades(self):
        import signal_meta
        picks = [{"ticker": "A", "signal": "buy", "confidence": 0.6}, {"ticker": "B", "signal": "strong_buy", "confidence": 0.9}]
        signal_meta.annotate_momentum(picks, {"A": ("strong_buy", 0.95)})
        self.assertEqual((picks[0]["signal"], picks[0]["confidence"]), ("buy", 0.6))     # label and confidence untouched
        self.assertEqual((picks[0]["momentum_label"], picks[0]["momentum_score"]), ("strong_buy", 0.95))
        self.assertIsNone(picks[1]["momentum_label"])
        meta = signal_meta.run_meta("prompt", signal_meta.run_meta)
        self.assertEqual(meta["variant"], "live-2"); self.assertEqual(len(meta["prompt_version"]), 12)

    def test_num(self):
        self.assertEqual(snapshot.num("-0.11%"), -0.11)
        self.assertEqual(snapshot.num("+5.00%"), 5.0)
        self.assertEqual(snapshot.num("1,234.5"), 1234.5)
        self.assertIsNone(snapshot.num("N/A"))
        self.assertIsNone(snapshot.num(True))

    def test_prices_recorded_once(self):
        with mock.patch("sys.argv", ["x", "prices"]):
            self.assertEqual(snapshot.main(["x", "prices"]), 0)
        n = self.count("price_snapshots")
        expected = len({(r[0], r[1]) for r in snapshot.price_rows(self.universe, "r", warn=lambda *_: None)})
        self.assertEqual(n, expected)
        self.assertGreater(n, 200)
        self.assertEqual(self.count("market_snapshots"), 1)
        snapshot.main(["x", "prices"])                    # unchanged files -> nothing new
        self.assertEqual(self.count("price_snapshots"), n)
        runs = self.h.run("SELECT status FROM runs WHERE bot = 'prices'")
        self.assertEqual([r["status"] for r in runs], ["complete", "complete"])

    def test_every_published_row_maps_to_the_universe(self):
        warnings = []
        snapshot.price_rows(self.universe, "r", warn=warnings.append)
        self.assertEqual(warnings, [])

    def test_signals_written_once(self):
        snapshot.main(["x", "signals"])
        n = self.count("signals")
        self.assertGreater(n, 0)
        self.assertEqual(self.count("signal_runs", "WHERE provenance <> 'live'"), 0)
        u = self.count("run_universe")
        self.assertGreater(u, 0)
        snapshot.main(["x", "signals"])
        self.assertEqual(self.count("signals"), n)
        self.assertEqual(self.count("run_universe"), u)

    def test_group_runs_recorded_derived_skipped(self):
        """#88 PR 8: a sector run is recorded with its own list; the derived S&P 500 file is not (no double count)."""
        pick = {"rank": 1, "ticker": "XOM", "signal": "buy", "confidence": 0.8, "rationale": "r", "drivers": []}
        files = {"sectors/energy/signals-local.json": {"updated": "2026-11-23 08:00", "variant": "live-2", "picks": [pick]},
                 "markets/sp500/signals-local.json": {"updated": "2026-11-23 08:00", "derived": True, "picks": [pick]}}
        real = snapshot.read_json
        with mock.patch.object(snapshot, "read_json", side_effect=lambda rel: files[rel] if rel in files else real(rel)), \
             mock.patch.object(snapshot, "group_signal_files", return_value=[("sectors/energy", "energy"), ("markets/sp500", "sp500")]), \
             mock.patch.object(snapshot, "read_js_data", return_value={"stocks": [{"ticker": "XOM"}, {"ticker": "CVX"}]}):
            runs, sigs, members = snapshot.signal_rows(self.universe, "r")
        ids = [r[0] for r in runs]
        self.assertIn("energy:2026-11-23T08:00:00Z", ids)
        self.assertFalse(any(i.startswith("sp500:") for i in ids))
        self.assertEqual(sorted(m[1] for m in members if m[0] == "energy:2026-11-23T08:00:00Z"), ["CVX", "XOM"])
        self.assertEqual(sum(1 for x in sigs if x[0] == "energy:2026-11-23T08:00:00Z"), 1)

    def test_run_universe_is_the_prices_file(self):
        """#88: each run's list of choosable stocks = the tickers in that sector's prices.json."""
        runs, _sigs, members = snapshot.signal_rows(self.universe, "r")
        ai = next(r[0] for r in runs if r[1] == "AI" and not str(r[6] or "").startswith("shadow"))
        got = sorted(m[1] for m in members if m[0] == ai)
        want = sorted(s["ticker"] for s in snapshot.read_json("AI/prices.json")["stocks"])
        self.assertEqual(got, want)
        self.assertTrue(all(m[2] == "live" for m in members))
        self.assertEqual(snapshot.universe_rows("X:1", None, "git"), [])


class RawBars(unittest.TestCase):
    # Yahoo-style split-adjusted rows for a 10-for-1 split on 01-03:
    # real closes 100, 105 then 11 (post-split), 11.2
    ROWS = [("2026-01-01", 10.0, 10.2, 9.9, 10.0, 5000, 0, 0),
            ("2026-01-02", 10.1, 10.6, 10.0, 10.5, 6000, 0, 0.05),
            ("2026-01-03", 10.9, 11.1, 10.8, 11.0, 70000, 10.0, 0),
            ("2026-01-04", 11.0, 11.3, 10.9, 11.2, 65000, 0, 0)]

    def test_split_undone(self):
        b, splits, divs = bars.to_raw(self.ROWS)
        self.assertEqual([x[4] for x in b], [100.0, 105.0, 11.0, 11.2])
        self.assertEqual([x[5] for x in b], [500.0, 600.0, 70000.0, 65000.0])
        self.assertEqual(splits, [("2026-01-03", 10.0)])
        self.assertEqual(divs, [("2026-01-02", 0.5)])           # raw dividend per pre-split share

    def test_gap_kept(self):
        b, _, _ = bars.to_raw([("2026-01-01", 1, 1, 1, 1, 1, 0, 0), ("2026-01-02", None, None, None, float("nan"), None, 0, 0)])
        self.assertEqual(len(b), 1)

    def test_tiny_prices_survive(self):
        b, _, _ = bars.to_raw([("2026-01-01", 0.00000374, 0.000004, 0.0000036, 0.00000374, 1e12, 0, 0)])
        self.assertEqual(b[0][4], 3.74e-06)

    def test_flags(self):
        b, splits, _ = bars.to_raw(self.ROWS)
        self.assertEqual(bars.jump_flags(b, {d for d, _ in splits}), [])           # recorded split: no flag
        self.assertEqual([f[1] for f in bars.jump_flags(b, set())], ["split_like_jump"])
        pence = [("d1", 0, 0, 0, 1250.0, 0), ("d2", 0, 0, 0, 12.6, 0)]
        self.assertEqual(bars.jump_flags(pence, set())[0][1], "unit_jump")
        normal = [("d1", 0, 0, 0, 100.0, 0), ("d2", 0, 0, 0, 103.0, 0)]
        self.assertEqual(bars.jump_flags(normal, set()), [])

    def test_coarse_series(self):
        flat = [(f"d{i}", 0, 0, 0, 5e-06, 0) for i in range(6)]
        self.assertTrue(bars.coarse(flat))
        self.assertFalse(bars.coarse(flat[:3]))                                    # too few days to judge
        b, _, _ = bars.to_raw(self.ROWS)
        self.assertFalse(bars.coarse(b))

    def test_coarse_by_step_size(self):
        pepe = [5e-06, 4e-06, 5e-06, 6e-06, 5e-06, 4e-06, 5e-06, 6e-06, 7e-06, 5e-06]   # moves in 20% steps
        self.assertTrue(bars.coarse_closes(pepe))
        btc = [73708.88, 74026.92, 75223.15, 74584.65, 75747.58, 75746.93]
        self.assertFalse(bars.coarse_closes(btc))
        pence = [1909.0, 1925.0, 1913.0, 1846.0, 1880.5, 1988.0]                        # BAE in pence
        self.assertFalse(bars.coarse_closes(pence))

    def test_float32_noise_rounded(self):
        b, _, _ = bars.to_raw([("2026-01-01", 25.62000084, 26.0, 25.5, 26.02000046, 10517133, 0, 0)])
        self.assertEqual((b[0][1], b[0][4], b[0][5]), (25.62, 26.02, 10517133.0))

    def test_crypto_fallback_symbols(self):
        inst = bars.instruments(db.load_universe())
        self.assertEqual(inst["GRT6719-USD"][2], ["GRT-USD"])                     # ours is the id form already
        self.assertEqual(inst["AAPL"][2], [])
        fake = {"assets": {"XYZ": {"name": "X", "exchange": "Crypto", "yahoo": "XYZ-USD",
                                   "cmc_symbol": "XYZ", "cmc_id": 123}}, "sectors": {}}
        self.assertEqual(bars.instruments(fake)["XYZ-USD"][2], ["XYZ123-USD"])

    def test_instruments_dedupe_shared_symbols(self):
        u = db.load_universe()
        inst = bars.instruments(u)
        self.assertEqual(sum(1 for s in inst if s == "RR.L"), 1)                  # RR. and RR.L
        self.assertIn("SPY", inst)
        self.assertIn("^VIX", inst)


class BarsJob(Base):
    def fake_fetch(self, symbol, start, end):
        if symbol == "BAD":
            raise RuntimeError("boom")
        cur = "GBp" if symbol.endswith(".L") else "USD"
        return [("2026-11-09", 1, 2, 0.5, 1.5, 100, 0, 0), ("2026-11-10", 1.5, 2, 1, 1.6, 120, 0, 0)], cur

    def run_bars(self, *args):
        with mock.patch.object(bars, "fetch", side_effect=self.fake_fetch), mock.patch.object(bars.time, "sleep"):
            return bars.main(list(args))

    def test_nightly_is_idempotent(self):
        self.assertEqual(self.run_bars("--only", "AAPL,BA.L,SPY"), 0)
        self.assertEqual(self.count("daily_bars"), 6)
        self.run_bars("--only", "AAPL,BA.L,SPY")
        self.assertEqual(self.count("daily_bars"), 6)
        cur = self.h.run("SELECT currency FROM daily_bars WHERE symbol = 'BA.L' LIMIT 1")[0]["currency"]
        self.assertEqual(cur, "GBp")

    def test_backfill_resumes_and_respects_budget(self):
        self.run_bars("--days", "400", "--budget", "3", "--only", "AAPL,MSFT,NVDA")
        self.assertEqual(self.count("daily_bars"), 4)                             # stopped after 2 instruments
        self.run_bars("--days", "400", "--only", "AAPL,MSFT,NVDA")
        self.assertEqual(self.count("daily_bars"), 6)                             # only the third fetched
        self.assertEqual(self.count("meta", "WHERE key LIKE 'backfill:%'"), 3)

    def test_crypto_falls_back_and_flags(self):
        real = self.fake_fetch
        def fetch(symbol, start, end):
            return ([], None) if symbol == "SUI20947-USD" else real(symbol, start, end)
        with mock.patch.object(bars, "fetch", side_effect=fetch), mock.patch.object(bars.time, "sleep"):
            self.assertEqual(bars.main(["--only", "SUI20947-USD"]), 0)
        self.assertEqual(self.count("daily_bars", "WHERE symbol = 'SUI20947-USD'"), 2)   # stored under our symbol
        flag = self.h.run("SELECT detail FROM data_flags WHERE kind = 'yahoo_symbol'")[0]["detail"]
        self.assertIn("fetched as SUI-USD", flag)

    def test_mostly_failing_run_is_red(self):
        with mock.patch.object(bars, "fetch", side_effect=RuntimeError("yahoo down")), mock.patch.object(bars.time, "sleep"):
            self.assertEqual(bars.main(["--only", "AAPL,MSFT"]), 1)


class Backup(Base):
    def test_round_trip(self):
        snapshot.main(["x", "prices"])
        snapshot.main(["x", "signals"])
        out = os.path.join(self.tmp, "dump")
        with mock.patch.object(backup, "PAGE", 50):                            # force several pages
            counts = backup.dump(self.h, out)
        self.assertEqual(counts["price_snapshots"], self.count("price_snapshots"))
        with gzip.open(os.path.join(out, "signals.ndjson.gz"), "rt") as f:
            self.assertEqual(sum(1 for _ in f), self.count("signals"))
        other = db.connect(os.path.join(self.tmp, "restored.sqlite"))
        backup.restore(other, out)
        for table in backup.TABLES:
            a = self.h.run(f"SELECT * FROM {table} ORDER BY 1, 2")
            b = other.run(f"SELECT * FROM {table} ORDER BY 1, 2")
            self.assertEqual(a, b, table)

    def test_tables_match_schema(self):
        tables = {r["name"] for r in self.h.run("SELECT name FROM sqlite_master WHERE type = 'table'")}
        self.assertEqual(tables, set(backup.TABLES))


if __name__ == "__main__":
    unittest.main()


# ── Track record ──────────────────────────────────────────────────────────────
import datetime as _dt  # noqa: E402

from history import import_signals, track_record as tr  # noqa: E402

UTC = _dt.timezone.utc


def _days(start, n, price=100.0, step=1.0):
    """n consecutive calendar days of bars: (date, open, close), close = open + step."""
    d0 = _dt.date.fromisoformat(start)
    return [((d0 + _dt.timedelta(days=k)).isoformat(), price + k * step, price + k * step + step) for k in range(n)]


class TrackRecordRules(unittest.TestCase):
    def test_open_times(self):
        self.assertEqual(tr.open_utc("2026-11-11", "NYSE").hour, 14)          # 09:30 EST = 14:30 UTC
        self.assertEqual(tr.open_utc("2026-07-01", "NASDAQ").hour, 13)        # 09:30 EDT = 13:30 UTC
        self.assertEqual(tr.open_utc("2026-07-01", "LSE").hour, 7)            # 08:00 BST
        self.assertEqual(tr.open_utc("2026-07-01", "Crypto").hour, 0)
        self.assertEqual(tr.open_utc("2026-07-01", "TSE").hour, 0)            # 09:00 JST = 00:00 UTC

    def test_entry_is_strictly_after_the_signal(self):
        signal = _dt.datetime(2026, 7, 1, 7, 0, tzinfo=UTC)                   # 08:00 London, LSE opens 08:00
        lse = tr.Series("LSE", _days("2026-07-01", 5))
        self.assertEqual(lse.dates[lse.first_open_after(signal + tr.BUFFER)], "2026-07-02")
        us = tr.Series("NYSE", _days("2026-07-01", 5))
        self.assertEqual(us.dates[us.first_open_after(signal + tr.BUFFER)], "2026-07-01")   # opens 13:30 UTC
        coin = tr.Series("Crypto", _days("2026-07-01", 5))
        self.assertEqual(coin.dates[coin.first_open_after(signal + tr.BUFFER)], "2026-07-02")

    def test_split_and_dividend(self):
        bars = [("2026-01-01", 100.0, 100.0), ("2026-01-02", 101, 102), ("2026-01-03", 51, 52), ("2026-01-04", 53, 55)]
        s = tr.Series("NYSE", bars, splits={"2026-01-03": 2.0}, dividends={"2026-01-04": 1.0, "2026-01-01": 9.0})
        # 1 share -> 2 shares on the split; dividend 1.0 x 2 shares; the entry-day dividend is not ours
        self.assertAlmostEqual(s.total_return(0, 3), (55 * 2 + 2) / 100 - 1)

    def test_complete_through(self):
        now = _dt.datetime(2026, 11, 11, 22, 0, tzinfo=UTC)
        self.assertEqual(tr.complete_through("NYSE", now), "2026-11-11")       # closed 21:00 UTC
        self.assertEqual(tr.complete_through("Crypto", now), "2026-11-10")     # today's UTC bar still forming
        early = _dt.datetime(2026, 11, 11, 20, 0, tzinfo=UTC)
        self.assertEqual(tr.complete_through("NYSE", early), "2026-11-10")

    def test_measure_pending_and_scored(self):
        stock = tr.Series("NYSE", _days("2026-06-01", 60, step=1.0))
        spy = tr.Series("Index", _days("2026-06-01", 60, step=0.5))
        signal = _dt.datetime(2026, 6, 1, 7, 0, tzinfo=UTC)
        now = _dt.datetime(2026, 7, 30, 22, 0, tzinfo=UTC)
        entry, res, note = tr.measure(signal, stock, spy, now)
        self.assertEqual(entry["date"], "2026-06-01")
        r, s = res["1w"]
        self.assertAlmostEqual(r, (100 + 7 + 1) / 100 - 1)                    # close on 06-08 = 108
        self.assertAlmostEqual(s, (100 + 3.5 + 0.5) / 100 - 1)
        self.assertIsInstance(res["1m"], tuple)
        self.assertEqual(res["3m"], "pending")

    def test_late_first_price_is_a_gap_not_a_purchase(self):
        stock = tr.Series("Crypto", _days("2026-11-11", 3))                  # history starts months later
        spy = tr.Series("Index", _days("2026-06-01", 170))
        entry, res, note = tr.measure(_dt.datetime(2026, 6, 2, 8, 0, tzinfo=UTC), stock, spy,
                                      _dt.datetime(2026, 11, 13, 22, 0, tzinfo=UTC))
        self.assertIsNone(entry)
        self.assertEqual(note, "no price data around the signal date")
        holiday = tr.Series("TADAWUL", [("2026-06-01", 10, 10), ("2026-06-10", 11, 11), ("2026-06-11", 11, 12)])
        entry, _, _ = tr.measure(_dt.datetime(2026, 6, 1, 9, 0, tzinfo=UTC), holiday, spy,
                                 _dt.datetime(2026, 6, 20, 22, 0, tzinfo=UTC))
        self.assertEqual(entry["date"], "2026-06-10")                         # 9-day holiday is still a purchase

    def test_summary(self):
        st = tr.summarise([(0.10, 0.02), (-0.05, 0.01), (0.03, 0.03)])
        self.assertEqual(st["n"], 3)
        self.assertEqual(st["beat_spy"], 33.3)
        self.assertEqual(st["excess"], round((0.08 - 0.06 + 0) / 3 * 100, 2))


class TrackRecordBuild(Base):
    def test_end_to_end(self):
        h = self.h
        h.sync_universe(self.universe, db.BENCHMARKS)
        bars_rows = []
        for sym, step in (("AAPL", 1.0), ("SPY", 0.5)):
            for d, o, c in _days("2026-06-01", 150, step=step):
                bars_rows.append([sym, d, o, o, o, c, 1000, "USD", "r"])
        for k, (d, _o, _c) in enumerate(_days("2026-06-01", 150)):              # 20% steps, no flag needed
            bars_rows.append(["PEPE24478-USD", d, 5e-06, 5e-06, 5e-06, (4e-06, 5e-06, 6e-06)[k % 3], 1, "USD", "r"])
        h.write("daily_bars", bars.BAR_COLS, bars_rows)
        h.write("signal_runs", snapshot.SIGNAL_RUN_COLS, [["AI:2026-06-01T07:00:00Z", "AI", "2026-06-01T07:00:00Z", "m", "live", "git:abc", None, None, None, None],
                                                         ["Crypto:2026-10-25T07:00:00Z", "Crypto", "2026-10-25T07:00:00Z", "m", "live", "r", None, None, None, None]])
        h.write("signals", snapshot.SIGNAL_COLS, [
            ["AI:2026-06-01T07:00:00Z", "ai", "AAPL", 1, "strong_buy", 0.95, "x", None, None, None, None],
            ["AI:2026-06-01T07:00:00Z", "momentum", "AAPL", 1, "buy", 0.7, "x", None, None, None, None],
            ["AI:2026-06-01T07:00:00Z", "ai", "NOPE", 2, "buy", 0.6, "x", None, None, None, None],
            ["Crypto:2026-10-25T07:00:00Z", "ai", "PEPE", 1, "buy", 0.8, "x", None, None, None, None],
            ["Crypto:2026-10-25T07:00:00Z", "ai", "AGIX", 2, "strong_buy", 1.0, "x", None, None, None, None],
        ])
        out = tr.build(*tr.load(h), now=_dt.datetime(2026, 11, 1, 22, 0, tzinfo=UTC))
        self.assertEqual(out["counts"], {"signals": 5, "scored": 2, "pending": 0, "no_data": 1, "unreliable": 2,
                                         "baseline_lists": {"own": 0, "today": 2}})
        allbuy = out["summary"]["all"]["buy signals"]
        self.assertEqual(allbuy["3m"]["n"], 2)
        self.assertGreater(allbuy["1w"]["excess"], 0)                          # AAPL rose twice as fast as SPY
        cols = out["columns"]
        rows = {(r[cols.index("ticker")], r[cols.index("kind")]): r for r in out["rows"]}
        self.assertEqual(rows[("NOPE", "ai")][cols.index("note")], "no price data")
        self.assertTrue(rows[("PEPE", "ai")][cols.index("note")].startswith("unreliable price"))
        self.assertIn("#49", rows[("AGIX", "ai")][cols.index("note")])
        aapl = rows[("AAPL", "ai")]
        self.assertEqual(aapl[cols.index("entry_date")], "2026-06-01")
        self.assertEqual(aapl[cols.index("provenance")], "live")
        self.assertEqual(out["names"]["AAPL"], "Apple")
        json.dumps(out)                                                       # serialisable


class TrackRecordBaselines(unittest.TestCase):
    """#70: AI picks are compared with a random pick from the same sector and a simple momentum rule."""
    def test_random_and_momentum_baselines(self):
        def bars_for(step):
            return [{"date": d, "open": o, "close": c, "currency": "USD"} for d, o, c in _days("2026-01-01", 260, step=step)]
        assets = {t: {"asset_id": t, "yahoo": t, "exchange": "Crypto", "name": t} for t in ("UP", "FLAT", "DOWN")}
        assets["SPY"] = {"asset_id": "SPY", "yahoo": "SPY", "exchange": "Crypto", "name": "SPY"}
        bars_ = {"UP": bars_for(1.0), "FLAT": bars_for(0.01), "DOWN": bars_for(-0.2), "SPY": bars_for(0.1)}
        gen = "2026-08-01T07:00:00Z"                                       # ~212 days of history before it
        runs = {"T:1": {"signal_run_id": "T:1", "sector": "T", "generated_utc": gen, "provenance": "live", "variant": "live-2"}}
        signals = [{"signal_run_id": "T:1", "kind": "ai", "asset_id": "FLAT", "rank": 1, "signal": "buy", "confidence": 0.5}]
        members = {"T": ["UP", "FLAT", "DOWN"]}
        with mock.patch.object(tr, "MOMENTUM_PICKS", 1):
            out = tr.build(assets, runs, signals, bars_, {}, {}, set(), members, now=_dt.datetime(2026, 9, 20, tzinfo=UTC))
        b = out["summary"]["baselines"]
        self.assertEqual(b["ai_picks"]["1w"]["n"], 1)
        self.assertEqual(b["random"]["1w"]["n"], 3)                        # every stock in the sector
        self.assertEqual(b["momentum_rule"]["1w"]["n"], 1)                 # the single best 6-1 month stock...
        self.assertGreater(b["momentum_rule"]["1w"]["avg"], b["ai_picks"]["1w"]["avg"])   # ...is UP, which beat FLAT
        self.assertEqual(out["summary"]["by_variant"]["live-2"]["1w"]["n"], 1)
        # #88: with the run's own recorded list (here without UP), the baselines use that list, not today's
        with mock.patch.object(tr, "MOMENTUM_PICKS", 1):
            own = tr.build(assets, runs, signals, bars_, {}, {}, set(), members, run_members={"T:1": ["FLAT", "DOWN"]},
                           now=_dt.datetime(2026, 9, 20, tzinfo=UTC))
        self.assertEqual(own["summary"]["baselines"]["random"]["1w"]["n"], 2)
        self.assertEqual(own["counts"]["baseline_lists"], {"own": 1, "today": 0})
        self.assertEqual(out["counts"]["baseline_lists"], {"own": 0, "today": 1})
        ser = tr.Series("Crypto", [(x["date"], x["open"], x["close"]) for x in bars_["UP"]])
        self.assertGreater(tr.momentum_score(ser, tr.parse_utc(gen)), 0)
        self.assertIsNone(tr.momentum_score(ser, tr.parse_utc("2026-03-01T07:00:00Z")))   # too little history


class ShadowTrial(unittest.TestCase):
    """#92: shadow picks are stored apart, never counted live, and judged only by the frozen rule."""
    def _world(self):
        def bars_for(step):
            return [{"date": d, "open": o, "close": c, "currency": "USD"} for d, o, c in _days("2026-01-01", 300, step=step)]
        assets = {t: {"asset_id": t, "yahoo": t, "exchange": "Crypto", "name": t} for t in ("UP", "FLAT", "SPY")}
        bars_ = {"UP": bars_for(1.0), "FLAT": bars_for(0.01), "SPY": bars_for(0.1)}
        runs, signals = {}, []
        for k in range(30):                                     # 30 run dates, live picks FLAT, shadow picks UP
            gen = (_dt.date(2026, 6, 1) + _dt.timedelta(days=2 * k)).isoformat() + "T07:00:00Z"
            runs[f"T:{gen}"] = {"signal_run_id": f"T:{gen}", "sector": "T", "generated_utc": gen, "provenance": "live", "variant": "live-2"}
            runs[f"T:{gen}:shadow-runup-1"] = {"signal_run_id": f"T:{gen}:shadow-runup-1", "sector": "T", "generated_utc": gen,
                                               "provenance": "live", "variant": "shadow-runup-1"}
            signals.append({"signal_run_id": f"T:{gen}", "kind": "ai", "asset_id": "FLAT", "rank": 1, "signal": "buy", "confidence": 0.5})
            signals.append({"signal_run_id": f"T:{gen}:shadow-runup-1", "kind": "ai", "asset_id": "UP", "rank": 1, "signal": "buy", "confidence": 0.5})
        return assets, runs, signals, bars_

    def test_shadow_kept_out_and_judged_only_at_decision(self):
        assets, runs, signals, bars_ = self._world()
        before = tr.build(assets, runs, signals, bars_, {}, {}, set(), {"T": ["UP", "FLAT"]}, now=_dt.datetime(2026, 10, 25, tzinfo=UTC))
        self.assertEqual(before["counts"]["signals"], 30)                       # only the live picks are counted
        self.assertTrue(all(r[3] == "FLAT" for r in before["rows"]))
        st = before["summary"]["shadow_trial"]
        self.assertEqual(st["status"], "running")
        self.assertNotIn("median_diff", st)                                     # no peeking before the decision date
        self.assertEqual(st["dates_collected"], 30)
        with mock.patch.dict(tr.SHADOW, {"decision_date": "2026-10-01"}):
            after = tr.build(assets, runs, signals, bars_, {}, {}, set(), {"T": ["UP", "FLAT"]}, now=_dt.datetime(2026, 10, 25, tzinfo=UTC))
        st = after["summary"]["shadow_trial"]
        self.assertEqual(st["status"], "decided")
        self.assertGreater(st["median_diff"], 0)
        self.assertTrue(st["switch"])                                           # UP beat FLAT on every date

    def test_shadow_needs_enough_dates(self):
        out = tr.shadow_result({"2026-12-01": [([0.01], [0.02])]}, _dt.datetime(2027, 3, 1, tzinfo=UTC))
        self.assertEqual(out["status"], "running")                              # 1 of 24 dates, even after the date

    def test_shadow_file_gets_its_own_run_id(self):
        data = {"updated": "2026-11-23 08:00 GMT", "variant": "shadow-runup-1", "picks": [{"ticker": "NVDA", "signal": "buy"}]}
        run, _ = snapshot.rows_from_signal_file("AI", data, "r")
        self.assertEqual(run[0], "AI:2026-11-23T08:00:00Z:shadow-runup-1")
        self.assertIsNone(snapshot.rows_from_signal_file("AI", {"updated": None, "picks": []}, "r"))   # the placeholder

    def test_failed_shadow_never_breaks_the_live_run(self):
        import signal_meta
        def boom(*a):
            raise SystemExit("OpenRouter returned 500")
        self.assertIsNone(signal_meta.run_shadow("k", boom, None, "p", signal_meta.run_meta, "u", set(), [], "now", "m", self_tmp := tempfile.mkdtemp()))
        self.assertFalse(os.path.exists(os.path.join(self_tmp, signal_meta.SHADOW_FILE)))
        ok = signal_meta.run_shadow("k", lambda *a: "x", lambda c, v: [{"rank": 1, "ticker": "A", "signal": "buy", "confidence": 0.5}],
                                    "p", signal_meta.run_meta, "u", {"A"}, [], "2026-11-23 08:00", "m", self_tmp)
        self.assertEqual(ok["variant"], "shadow-runup-1")
        self.assertIn("one-month run-up", signal_meta.SHADOW_ADDENDUM)
        with open(os.path.join(self_tmp, signal_meta.SHADOW_FILE)) as f:
            self.assertEqual(json.load(f)["picks"][0]["ticker"], "A")


class ImportSignals(unittest.TestCase):
    def test_git_history(self):
        if subprocess_shallow():
            self.skipTest("shallow clone")
        runs, sigs, members, skipped = import_signals.collect(db.load_universe()["sectors"], warn=lambda *_: None)
        self.assertGreater(len(runs), 400)
        with_list = {m[0] for m in members}
        self.assertGreater(len(with_list), len(runs) * 0.9)          # nearly every past run has its prices.json
        self.assertTrue(all(m[2] == "git" for m in members))
        self.assertTrue(all(r[4] == "live" and r[5].startswith("git:") for r in runs))
        self.assertEqual(len({r[0] for r in runs}), len(runs))
        self.assertTrue(all(s[4] in ("buy", "strong_buy", "hold", "sell", "strong_sell") for s in sigs))


def subprocess_shallow():
    import subprocess
    out = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], capture_output=True, text=True, cwd=db.ROOT)
    return out.stdout.strip() != "false"
