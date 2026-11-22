"""Tests for the group price bot (#88 PR 4): price maths, currency conversion, fundamentals,
grouping and the once-a-day fundamentals schedule. No network.

Run: python -m unittest test_group_prices.py   (also run in CI)
"""
import unittest
from datetime import date, datetime, timedelta, timezone

import groups_config as gc
import update_group_prices as gp

FX = {"USD": 1.25, "EUR": 1.15, "JPY": 190.0}
NAN = float("nan")


def bars(closes, start=date(2026, 1, 2)):
    """Daily bars on consecutive weekdays: (date, high, low, close, volume)."""
    out, d = [], start
    for c in closes:
        while d.weekday() >= 5:
            d += timedelta(days=1)
        out.append((d, c * 1.01, c * 0.99, c, 1000))
        d += timedelta(days=1)
    return out


class Stats(unittest.TestCase):
    def test_changes(self):
        b = bars([100 + i for i in range(260)])          # a year of steady rises
        s = gp.stats(b, b[-1][0])
        last = 359
        self.assertEqual(s["price"], last)
        self.assertAlmostEqual(s["change_1d"], round((last - 358) / 358 * 100, 2))
        self.assertAlmostEqual(s["change_1w"], round((last - 354) / 354 * 100, 2))   # 5 sessions back
        self.assertEqual(s["return_1yr"], round((last - 100) / 100 * 100))
        self.assertEqual(s["vol_1w"], 5000)
        self.assertEqual(s["high"], last * 1.01)
        self.assertEqual(s["low"], 100 * 0.99)

    def test_ytd_uses_first_bar_of_this_year(self):
        b = bars([50, 60], start=date(2025, 12, 30)) + bars([80, 88], start=date(2026, 1, 2))
        self.assertAlmostEqual(gp.stats(b, b[-1][0])["change_ytd"], 10.0)

    def test_empty_days_skipped(self):
        # another market's holiday shows up as a NaN row in a batched download
        b = bars([100, 101, 102])
        b.insert(2, (b[1][0] + timedelta(days=1), NAN, NAN, NAN, NAN))
        s = gp.stats(b, b[-1][0])
        self.assertEqual(s["price"], 102)
        self.assertAlmostEqual(s["change_1d"], round(1 / 101 * 100, 2))

    def test_stale_or_short_is_none(self):
        b = bars([100, 101])
        self.assertIsNone(gp.stats(b, b[-1][0] + timedelta(days=8)))
        self.assertIsNone(gp.stats(b[:1], b[0][0]))


class Laggards(unittest.TestCase):
    def test_behind_own_exchange_only(self):
        st = {"A": {"price_as_of": "2026-11-20"}, "B": {"price_as_of": "2026-11-19"},
              "C": {"price_as_of": "2026-11-22"}}                     # C: Saudi, trades on Sundays
        self.assertEqual(gp.laggards(st, {"A": "NYSE", "B": "NASDAQ", "C": "TADAWUL"}), [])
        self.assertEqual(gp.laggards(st, {"A": "NYSE", "B": "NYSE", "C": "TADAWUL"}), ["B"])


class FillClose(unittest.TestCase):
    def test_missing_close_filled_from_quote(self):
        b = bars([94.39])
        b.append((b[0][0] + timedelta(days=1), 90.67, 78.25, NAN, 127147042))
        filled = gp.fill_last_close(b, 79.24)
        self.assertEqual(filled[-1][3], 79.24)
        self.assertEqual(gp.stats(filled, filled[-1][0])["price_as_of"], filled[-1][0].isoformat())

    def test_quote_outside_day_range_ignored(self):
        b = bars([94.39]) + [(date(2026, 1, 5), 90.67, 78.25, NAN, 1)]
        self.assertTrue(gp.fill_last_close(b, 120.0)[-1][3] != gp.fill_last_close(b, 120.0)[-1][3])


class Money(unittest.TestCase):
    def test_to_gbp(self):
        self.assertEqual(gp.to_gbp_factor("GBp", FX), 0.01)
        self.assertEqual(gp.to_gbp_factor("GBP", FX), 1.0)
        self.assertAlmostEqual(gp.to_gbp_factor("USD", FX), 0.8)
        self.assertAlmostEqual(gp.to_gbp_factor("SAR", FX), 1 / (1.25 * 3.75))
        self.assertIsNone(gp.to_gbp_factor("XXX", FX))

    def test_row_pence_and_market_cap(self):
        a = {"name": "Unilever", "exchange": "LSE", "currency": "GBp", "markets": ["ftse100"],
             "sector": "Consumer Staples", "industry": "Personal Goods", "t212": "yes"}
        s = gp.stats(bars([4800 + i for i in range(30)]), date(2026, 2, 13))
        f = {"market_cap": 120e9, "market_cap_currency": "GBP", "pe_ratio": 20.0}
        r = gp.make_row("ULVR.L", a, s, f, FX, {}, "consumer-staples")
        self.assertEqual(r["price_gbp"], "48")                    # 4829p = £48.29
        self.assertAlmostEqual(r["price_usd"], 48.29 * 1.25, places=2)
        self.assertEqual(r["market_cap_gbp_b"], 120.0)            # GBP cap: not divided by 100
        self.assertEqual(r["markets"], ["ftse100"])
        self.assertEqual(r["news"], [])

    def test_fundamentals_from_info(self):
        f = gp.fundamentals_from_info({"marketCap": 3e12, "trailingPE": 30.123, "beta": -0.2,
                                       "dividendYield": 0.41, "shortPercentOfFloat": 0.0071,
                                       "recommendationKey": "buy", "averageVolume": 5.5e7}, "USD")
        self.assertEqual(f["pe_ratio"], 30.12)
        self.assertEqual(f["beta"], -0.2)                         # negative beta is real
        self.assertEqual(f["div_yield_pct"], 0.41)                # already a percentage
        self.assertEqual(f["short_pct"], 0.71)
        self.assertEqual(f["avg_volume_m"], 55.0)
        self.assertEqual(f["market_cap_currency"], "USD")
        self.assertIsNone(gp.fundamentals_from_info({"trailingPE": -5}, "GBp")["pe_ratio"])
        self.assertEqual(gp.fundamentals_from_info({}, "GBp")["market_cap_currency"], "GBP")


class Schedule(unittest.TestCase):
    def test_due_once_a_day_oldest_first(self):
        now = datetime(2026, 11, 23, 8, 0, tzinfo=timezone.utc)
        cache = {"A": {"fetched": (now - timedelta(hours=2)).isoformat()},
                 "B": {"fetched": (now - timedelta(hours=30)).isoformat()},
                 "C": {"fetched": (now - timedelta(days=3)).isoformat()}}
        self.assertEqual(gp.due(cache, ["A", "B", "C", "D"], now), ["D", "C", "B"])


class Groups(unittest.TestCase):
    def test_groups(self):
        assets = {
            "AAPL": {"exchange": "NASDAQ", "markets": ["nasdaq100", "sp500"], "sector": "Technology"},
            "AZN": {"exchange": "LSE", "markets": ["ftse100"], "sector": "Health Care"},
            "X": {"exchange": "NYSE", "sector": "Unclassified"},
        }
        g = gp.groups(assets)
        self.assertEqual(g["sp500"]["tickers"], ["AAPL"])
        self.assertEqual(g["ftse100"]["tickers"], ["AZN"])
        self.assertEqual(g["technology"]["tickers"], ["AAPL"])
        self.assertEqual(g["health-care"]["tickers"], ["AZN"])
        self.assertEqual(g["health-care"]["path"], "sectors/health-care")
        self.assertEqual(g["sp500"]["path"], "markets/sp500")
        self.assertNotIn("X", {t for v in g.values() for t in v["tickers"]})
        self.assertEqual(len(g), 14)
        self.assertEqual(list(g)[:3], ["sp500", "nasdaq100", "ftse100"])


class Categories(unittest.TestCase):
    """groups_config: one category list shared by the price data and the pages."""
    def test_market_and_health_care(self):
        mkt = {"kind": "market", "name": "S&P 500", "tickers": ["A", "B", "C"]}
        assets = {"A": {"sector": "Real Estate"}, "B": {"sector": "Technology"}, "C": {"sector": "Technology"}}
        self.assertEqual(gc.categories(mkt, assets), [("technology", "Technology"), ("real-estate", "Real Estate")])
        self.assertEqual(gc.category_of(mkt, assets["A"]), "real-estate")
        hc = {"kind": "sector", "name": "Health Care", "tickers": ["X", "Y"]}
        hca = {"X": {"industry": "Biotechnology"}, "Y": {"industry": "Medical Devices"}}
        self.assertEqual(gc.categories(hc, hca), [("biotechnology", "Biotechnology"), ("equipment-services", "Equipment & Services")])

    def test_top_industries_aliases_and_other(self):
        names = ["Aerospace & Defense", "Aerospace and Defense"] + [f"Ind {i}" for i in range(9)]
        assets = {str(i): {"industry": n} for i, n in enumerate(names)}
        assets["0b"] = {"industry": "Aerospace & Defense"}
        grp = {"kind": "sector", "name": "Industrials", "tickers": list(assets)}
        cats = gc.categories(grp, assets)
        self.assertEqual(cats[0], ("aerospace-defense", "Aerospace & Defense"))    # ICB name merged: 3 stocks
        self.assertEqual(len(cats), gc.TOP_INDUSTRIES + 1)                         # 7 + Other
        self.assertEqual(cats[-1], ("other", "Other"))
        self.assertEqual(gc.category_of(grp, {"industry": "Ind 8"}, cats), "other")
        self.assertEqual(gc.colours(cats)["other"][0], "slate")

    def test_one_entry_per_listing(self):
        assets = {"RR.": {"exchange": "LSE", "yahoo": "RR.L", "markets": ["ftse100"], "sector": "Industrials"},
                  "RR.L": {"exchange": "LSE", "yahoo": "RR.L", "markets": ["ftse100"], "sector": "Industrials"}}
        g = {x["id"]: x for x in gc.all_groups(assets)}
        self.assertEqual(g["ftse100"]["tickers"], ["RR.L"])
        self.assertEqual(g["industrials"]["tickers"], ["RR.L"])
        real = {x["id"]: x for x in gc.all_groups()}
        self.assertEqual(len(real["ftse100"]["tickers"]), 100)

    def test_every_real_stock_lands_in_a_listed_category(self):
        assets = gc.universe.load()["assets"]
        for g in gc.all_groups(assets):
            cats = gc.categories(g, assets)
            ids = {c for c, _ in cats}
            for t in g["tickers"]:
                self.assertIn(gc.category_of(g, assets[t], cats), ids, (g["id"], t))

    def test_tradingview(self):
        self.assertEqual(gc.tradingview_symbol("BA.L", {"exchange": "LSE", "yahoo": "BA.L"}), "LSE:BA.")
        self.assertEqual(gc.tradingview_symbol("ULVR.L", {"exchange": "LSE", "yahoo": "ULVR.L"}), "LSE:ULVR")
        self.assertEqual(gc.tradingview_symbol("BT-A.L", {"exchange": "LSE", "yahoo": "BT-A.L"}), "LSE:BT.A")
        self.assertEqual(gc.tradingview_symbol("BRK-B", {"exchange": "NYSE", "yahoo": "BRK-B"}), "NYSE:BRK.B")
        self.assertEqual(gc.tradingview_symbol("285A", {"exchange": "TSE", "yahoo": "285A.T"}), "TSE:285A")


if __name__ == "__main__":
    unittest.main()
