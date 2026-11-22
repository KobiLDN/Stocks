"""Tests for the index membership refresh (#88): the safety checks, the two-refresh leaver rule,
joiners/leavers, and joiner ids. No network.

Run: python -m unittest test_index_refresh.py   (also run in CI)
"""
import unittest

import index_refresh as ir


def rows(symbols):
    return [{"yahoo": s, "name": s} for s in symbols]


FTSE = [f"S{i}.L" for i in range(95)] + sorted(ir.KNOWN["ftse100"])   # 100 rows incl. the known members


class Checks(unittest.TestCase):
    def test_good_list_accepted(self):
        self.assertEqual(ir.check("ftse100", rows(FTSE), None), [])

    def test_too_few_rows(self):
        self.assertTrue(any("only" in p for p in ir.check("ftse100", rows(FTSE[:60] + FTSE[-5:]), None)))

    def test_known_member_missing(self):
        broken = [s for s in FTSE if s != "AZN.L"] + ["X.L"]
        self.assertTrue(any("AZN.L" in p for p in ir.check("ftse100", rows(broken), None)))

    def test_churn_limit(self):
        previous = {s: {} for s in FTSE}
        ten = FTSE[:90] + [f"N{i}.L" for i in range(5)] + FTSE[95:]          # 5 out, 5 in = 10% of 100
        self.assertEqual(ir.check("ftse100", rows(ten), previous), [])
        twelve = FTSE[:89] + [f"N{i}.L" for i in range(6)] + FTSE[95:]       # 6 out, 6 in = 12%
        self.assertTrue(any("churn" in p for p in ir.check("ftse100", rows(twelve), previous)))

    def test_duplicates(self):
        self.assertTrue(any("duplicate" in p for p in ir.check("ftse100", rows(FTSE + ["AZN.L"]), None)))


class LeaverRule(unittest.TestCase):
    def test_leaver_needs_two_refreshes(self):
        a, b, c = {"X": 1, "Y": 1}, {"X": 1}, {"X": 1}
        self.assertEqual(ir.members([("d1", a), ("d2", b)]), {"X", "Y"})   # gone once: still a member
        self.assertEqual(ir.members([("d1", a), ("d2", b), ("d3", c)]), {"X"})   # gone twice: out

    def test_joiner_counts_at_once(self):
        self.assertEqual(ir.members([("d1", {"X": 1}), ("d2", {"X": 1, "Z": 1})]), {"X", "Z"})

    def test_no_snapshots(self):
        self.assertEqual(ir.members([]), set())


class Plan(unittest.TestCase):
    ASSETS = {
        "AAPL": {"exchange": "NASDAQ", "yahoo": "AAPL"},
        "AZN": {"exchange": "LSE", "yahoo": "AZN.L"},
        "OLD": {"exchange": "NYSE", "yahoo": "OLD"},          # in no index, no theme -> retired
        "KEEP": {"exchange": "NYSE", "yahoo": "KEEP"},        # in no index, but in a theme -> stays
        "BTC": {"exchange": "Crypto", "yahoo": "BTC-USD"},    # coins never retire here
    }

    def test_plan(self):
        current = {"sp500": {"AAPL", "NEW"}, "nasdaq100": {"AAPL"}, "ftse100": {"AZN.L"}}
        by_asset, joiners, leavers = ir.plan(self.ASSETS, current, themed={"KEEP", "BTC"})
        self.assertEqual(by_asset["AAPL"], {"sp500", "nasdaq100"})
        self.assertEqual(by_asset["AZN"], {"ftse100"})
        self.assertEqual(joiners, {"NEW": {"sp500"}})
        self.assertEqual(leavers, ["OLD"])

    def test_joiner_id(self):
        self.assertEqual(ir.new_asset_id("ULVR.L", self.ASSETS), "ULVR.L")
        self.assertEqual(ir.new_asset_id("AZN", self.ASSETS | {"AZN": {}}), "AZN.US")


if __name__ == "__main__":
    unittest.main()
