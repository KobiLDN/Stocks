"""Tests for generate_situations.py: candidate choice, cleaning the AI's reply, odds, carrying situations
between runs and the flag log. No network: the AI is a fake.

Run: python -m unittest test_situations.py   (also run in CI)
"""
import json
import os
import tempfile
import unittest
import unittest.mock
from datetime import datetime, timedelta, timezone

import generate_situations as gs

NOW = datetime(2026, 11, 23, 16, 0, tzinfo=timezone.utc)


def head(title, hours_ago=2):
    return {"title": title, "published": int((NOW - timedelta(hours=hours_ago)).timestamp())}


class Candidates(unittest.TestCase):
    def test_event_words_moves_and_open_ones(self):
        stocks = {"NVDA": {"change_1d": "+1%", "change_1m": "-22%"}, "KO": {"change_1d": "+0.2%", "change_1m": "+1%"},
                  "OLD": {"change_1d": "0%", "change_1m": "0%"}, "JUMP": {"change_1d": "+12%", "change_1m": "+3%"},
                  "QUIET": {"change_1d": "+15%", "change_1m": "+40%"}}
        news = {"NVDA": [head("Board weighs CEO succession as Huang ousted")],
                "KO": [head("Coca-Cola launches a new flavour")],
                "OLD": [head("Takeover talks", hours_ago=24 * 9)],          # too old to count
                "JUMP": [head("Shares rise")]}
        got = [t for _, t in gs.candidates(stocks, news, {"OPEN"}, NOW)]
        self.assertEqual(got[0], "NVDA")                 # several event words
        self.assertIn("JUMP", got)                       # big move while in the news
        self.assertNotIn("KO", got)                      # ordinary news
        self.assertNotIn("OLD", got)
        self.assertNotIn("QUIET", got)                   # big move but no headlines: nothing to judge
        got = [t for _, t in gs.candidates({**stocks, "OPEN": {}}, news, {"OPEN"}, NOW)]
        self.assertIn("OPEN", got)                       # an open situation is always re-checked


class Cleaning(unittest.TestCase):
    def test_bad_entries_dropped_probabilities_normalised(self):
        reply = {"situations": [
            {"ticker": "NVDA", "type": "leadership", "title": "CEO's return in doubt", "summary": "s", "key_date": "2026-11-30",
             "outcomes": [{"label": "Huang returns", "probability": 0.5, "move_pct": 25},
                          {"label": "No return", "probability": 0.3, "move_pct": -10},
                          {"label": "Interim stays", "probability": 0.2, "move_pct": 2}]},
            {"ticker": "ZZZ", "type": "leadership", "outcomes": []},                 # not in the batch
            {"ticker": "AMD", "type": "made-up", "title": "t", "key_date": "soon",
             "outcomes": [{"label": "a", "probability": 2, "move_pct": 500}, {"label": "b", "probability": 2, "move_pct": -5}]},
            {"ticker": "DELL", "type": "results", "outcomes": [{"label": "only one", "probability": 1, "move_pct": 5}]},
        ]}
        got = {s["ticker"]: s for s in gs.clean(reply, {"NVDA", "AMD", "DELL"})}
        self.assertEqual(set(got), {"NVDA", "AMD"})
        amd = got["AMD"]
        self.assertEqual(amd["type"], "other")
        self.assertIsNone(amd["key_date"])
        self.assertEqual([o["probability"] for o in amd["outcomes"]], [0.5, 0.5])
        self.assertEqual(amd["outcomes"][0]["move_pct"], 300.0)               # clamped
        nv = got["NVDA"]
        self.assertAlmostEqual(nv["p_big"], 0.8)                              # +25 and -10 count as big
        self.assertAlmostEqual(nv["p_up"], 0.7)
        self.assertEqual(nv["lean"], "up")
        self.assertAlmostEqual(nv["expected_move"], 0.5 * 25 - 0.3 * 10 + 0.2 * 2, places=1)

    def test_source_must_be_a_given_headline(self):
        base = {"type": "takeover", "outcomes": [{"label": "a", "probability": .5, "move_pct": 10}, {"label": "b", "probability": .5, "move_pct": -5}]}
        reply = {"situations": [{**base, "ticker": "GPN", "source": "GTCR considers potential takeover of Global Payments"},
                                {**base, "ticker": "CRWD", "source": "A headline nobody gave it"}]}
        got = {s["ticker"]: s for s in gs.clean(reply, {"GPN", "CRWD"},
                                                 {"GPN": ["GTCR considers potential takeover of Global Payments"], "CRWD": ["x"]})}
        self.assertEqual(got["GPN"]["source"], "GTCR considers potential takeover of Global Payments")
        self.assertIsNone(got["CRWD"]["source"])          # not quoted: the card shows no source line

    def test_lean(self):
        self.assertEqual(gs.odds([{"probability": 0.5, "move_pct": 20}, {"probability": 0.5, "move_pct": -20}])["lean"], "either way")
        self.assertEqual(gs.odds([{"probability": 0.3, "move_pct": 20}, {"probability": 0.7, "move_pct": -5}])["lean"], "down")


class Carry(unittest.TestCase):
    def sit(self, t, typ="leadership", p_big=0.5):
        return {"ticker": t, "type": typ, "title": t, "summary": "", "key_date": None, "outcomes": [],
                "p_big": p_big, "p_up": 0.5, "expected_move": 1.0, "lean": "either way"}

    def test_first_flag_kept_and_logged_once(self):
        stocks = {"NVDA": {"price_usd": 168.8}, "AMD": {"price_usd": 200}, "OLD": {"price_usd": 1}}
        prev = [{**self.sit("NVDA"), "id": "NVDA:leadership", "first_flagged": "2026-11-20", "last_seen": "2026-11-22",
                 "price_at_flag": 125.5},
                {**self.sit("GONE"), "id": "GONE:legal", "type": "legal", "first_flagged": "2026-11-10", "last_seen": "2026-11-18",
                 "price_at_flag": 3},
                {**self.sit("KEEP"), "id": "KEEP:trial", "type": "trial", "first_flagged": "2026-11-21", "last_seen": "2026-11-22",
                 "price_at_flag": 9}]
        cur, flags = gs.merge(prev, [self.sit("NVDA", p_big=0.8), self.sit("AMD", "takeover")], stocks, NOW)
        by = {s["id"]: s for s in cur}
        self.assertEqual(by["NVDA:leadership"]["first_flagged"], "2026-11-20")
        self.assertEqual(by["NVDA:leadership"]["price_at_flag"], 125.5)        # the price when first flagged
        self.assertEqual(by["NVDA:leadership"]["last_seen"], "2026-11-23")
        self.assertIn("KEEP:trial", by)                                         # missed one run: kept a few days
        self.assertNotIn("GONE:legal", by)                                      # not seen for 5 days: dropped
        self.assertEqual([f["id"] for f in flags], ["AMD:takeover"])            # only new situations are logged
        self.assertEqual(flags[0]["price_usd"], 200)
        self.assertEqual(cur[0]["ticker"], "NVDA")                              # most likely big move first


class EndToEnd(unittest.TestCase):
    def test_run_writes_files(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "All"))
            all_data = {"stocks": [{"ticker": "NVDA", "company_name": "NVIDIA", "price_usd": 168.8, "change_1d": "+34%",
                                    "change_1m": "-22%"}]}
            news = {"stocks": [{"ticker": "NVDA", "news": [head("Jensen Huang reinstated as CEO, board review continues")]}]}
            open(os.path.join(d, "All", "all-data.js"), "w").write("window.ALL_DATA = " + json.dumps(all_data) + ";\n")
            open(os.path.join(d, "All", "news-data.js"), "w").write("window.NEWS_DATA = " + json.dumps(news) + ";\n")
            reply = json.dumps({"situations": [{"ticker": "NVDA", "type": "leadership", "title": "Board review", "summary": "x",
                                                "key_date": None, "outcomes": [{"label": "a", "probability": 0.6, "move_pct": 12},
                                                                               {"label": "b", "probability": 0.4, "move_pct": -8}]}]})
            with unittest.mock.patch.object(gs, "ROOT", d), unittest.mock.patch.object(gs, "OUT", os.path.join(d, "situations")):
                self.assertEqual(gs.main([], call=lambda sp, up: reply, now=NOW), 0)
                self.assertEqual(gs.main([], call=lambda sp, up: reply, now=NOW + timedelta(hours=8)), 0)   # second run
                data = json.load(open(os.path.join(d, "situations", "situations.json")))
                flags = json.load(open(os.path.join(d, "situations", "flags.json")))
                js = open(os.path.join(d, "situations", "situations-data.js")).read()
        self.assertEqual(data["count"], 1)
        self.assertEqual(len(flags), 1)                   # flagged twice, logged once
        self.assertEqual(flags[0]["price_usd"], 168.8)
        self.assertTrue(js.startswith("window.SITUATIONS_DATA = "))

    def test_quiet_day_still_saves(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "All"))
            open(os.path.join(d, "All", "all-data.js"), "w").write('window.ALL_DATA = {"stocks":[{"ticker":"KO","change_1d":"+0.1%"}]};\n')
            open(os.path.join(d, "All", "news-data.js"), "w").write('window.NEWS_DATA = {"stocks":[]};\n')
            def never(sp, up):
                raise AssertionError("no AI call on a quiet day")
            with unittest.mock.patch.object(gs, "ROOT", d), unittest.mock.patch.object(gs, "OUT", os.path.join(d, "situations")):
                self.assertEqual(gs.main([], call=never, now=NOW), 0)
                data = json.load(open(os.path.join(d, "situations", "situations.json")))
        self.assertEqual((data["count"], data["updated"]), (0, "2026-11-23 16:00"))   # /health sees a fresh run

    def test_all_calls_fail_keeps_previous(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "All"))
            open(os.path.join(d, "All", "all-data.js"), "w").write('window.ALL_DATA = {"stocks":[{"ticker":"A","change_1d":"+20%"}]};\n')
            open(os.path.join(d, "All", "news-data.js"), "w").write(
                "window.NEWS_DATA = " + json.dumps({"stocks": [{"ticker": "A", "news": [head("CEO resigns")]}]}) + ";\n")
            def boom(sp, up):
                raise RuntimeError("500")
            with unittest.mock.patch.object(gs, "ROOT", d), unittest.mock.patch.object(gs, "OUT", os.path.join(d, "situations")):
                self.assertEqual(gs.main([], call=boom, now=NOW), 1)
                self.assertFalse(os.path.exists(os.path.join(d, "situations")))


if __name__ == "__main__":
    unittest.main()
