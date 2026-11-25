"""Tests for the group signal runs (#88 PR 8). The AI is faked; real price files are copied to a
temporary folder, so nothing in the repo is written.

Run: python -m unittest test_group_signals.py   (also run in CI)
"""
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import generate_group_signals as gs
import groups_config


def fake_ai(picks_for):
    """A stand-in for OpenRouter: picks the group's 10 biggest stocks."""
    def call(api_key, sys_prompt, user_prompt, label):
        data = json.loads(user_prompt[user_prompt.index('{"stocks"'):])
        tickers = [s["ticker"] for s in sorted(data["stocks"], key=lambda s: -(s.get("mc_usd_b") or 0))][:10]
        picks_for[label] = tickers
        return json.dumps({"picks": [{"rank": i + 1, "ticker": t, "signal": "buy", "confidence": 0.9 - i * 0.05,
                                      "rationale": "test +1%", "drivers": ["a", "b"]} for i, t in enumerate(tickers)]})
    return call


class GroupRuns(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.assets = groups_config.universe.load()["assets"]
        self.groups = {g["id"]: g for g in groups_config.all_groups(self.assets)}
        for g in self.groups.values():
            os.makedirs(os.path.join(self.tmp, g["path"]))
            shutil.copy(os.path.join(gs.ROOT, g["path"], "prices-data.js"), os.path.join(self.tmp, g["path"]))
        self.root = mock.patch.object(gs, "ROOT", self.tmp)
        self.root.start()

    def tearDown(self):
        self.root.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def read(self, gid):
        return json.load(open(os.path.join(self.tmp, self.groups[gid]["path"], "signals-local.json")))

    def test_run_writes_tagged_picks(self):
        seen = {}
        gs.run_group(self.groups["energy"], self.assets, "k", "2026-11-23 08:00", call=fake_ai(seen))
        out = self.read("energy")
        self.assertEqual(len(out["picks"]), 10)
        self.assertEqual(out["group"], "energy")
        self.assertEqual(out["variant"], "live-2")
        self.assertTrue(out["prompt_version"])
        self.assertTrue(all("pre_momentum_label" in p for p in out["picks"]))
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "sectors/energy/signals-local.js")))

    def test_prompt_names_the_group_and_its_categories(self):
        g = self.groups["health-care"]
        cats = groups_config.categories(g, self.assets)
        sp = gs.system_prompt(g, cats, {})
        self.assertIn("Health Care sector", sp)
        self.assertIn("Biotechnology", sp)
        self.assertIn("trial readouts", sp)
        ftse = gs.system_prompt(self.groups["ftse100"], groups_config.categories(self.groups["ftse100"], self.assets), {})
        self.assertIn("FTSE 100 index", ftse)
        self.assertIn("pence", ftse)

    def test_bad_reply_is_retried_then_fails(self):
        calls = []
        def bad(*a):
            calls.append(1)
            return '{"picks": []}'
        with self.assertRaises(gs.RunFailed):
            gs.run_group(self.groups["energy"], self.assets, "k", "now", call=bad)
        self.assertEqual(len(calls), 1 + gs.RETRY_ON_BAD_JSON)

    def test_two_bad_replies_then_a_good_one(self):
        """25 Nov 2026: replies cut off at the length limit; the third try still gives the run its picks."""
        tries, good = [], fake_ai({})
        def flaky(*a):
            tries.append(1)
            if len(tries) < 3:
                raise ValueError("reply cut off at the length limit (12288 tokens)")
            return good(*a)
        out = gs.run_group(self.groups["energy"], self.assets, "k", "2026-11-25 08:00", call=flaky)
        self.assertEqual((len(tries), len(out["picks"])), (3, 10))

    def test_cut_off_reply_is_an_error(self):
        """call_api turns finish_reason 'length' into a retryable error and asks for capped thinking."""
        import unittest.mock
        class R:
            status_code = 200
            def json(self):
                return {"choices": [{"finish_reason": "length", "message": {"content": '{"picks": [{"rank'}}],
                        "usage": {"prompt_tokens": 9000, "completion_tokens": 12288,
                                  "completion_tokens_details": {"reasoning_tokens": 12000}}}
        sent = {}
        def post(url, headers=None, timeout=None, data=None):
            sent.update(json.loads(data))
            return R()
        with unittest.mock.patch.object(gs.requests, "post", post):
            with self.assertRaises(ValueError) as e:
                gs.call_api("k", "sys", "user", "Technology")
        self.assertIn("length limit", str(e.exception))
        self.assertEqual(sent["reasoning"], {"max_tokens": gs.REASONING_MAX_TOKENS})

    def test_ticker_outside_the_group_is_rejected(self):
        reply = json.dumps({"picks": [{"ticker": "BTC", "signal": "buy", "confidence": 1}] * 10})
        with self.assertRaises(ValueError):
            gs.parse_picks(reply, {"AAPL"})

    def test_derived_market_pages(self):
        seen = {}
        for gid in gs.RUN_GROUPS:
            if self.groups[gid]["kind"] == "sector":
                gs.run_group(self.groups[gid], self.assets, "k", "2026-11-23 08:00", call=fake_ai(seen))
        out = gs.derive_market("sp500", self.groups, self.assets, "2026-11-23 08:00")
        members = set(self.groups["sp500"]["tickers"])
        self.assertTrue(out["derived"])
        self.assertTrue(out["picks"])
        self.assertTrue(all(p["ticker"] in members for p in out["picks"]))
        self.assertEqual([p["rank"] for p in out["picks"]], list(range(1, len(out["picks"]) + 1)))
        self.assertTrue(all(p["from_group"] and p["group_rank"] for p in out["picks"]))
        confs = [p["confidence"] for p in out["picks"]]
        self.assertEqual(confs, sorted(confs, reverse=True))
        self.assertEqual(len(out["derived_from"]), 11)


if __name__ == "__main__":
    unittest.main()
