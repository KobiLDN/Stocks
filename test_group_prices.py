"""Tests for the group price bot (#88 PR 4): price maths, currency conversion, fundamentals,
grouping and the once-a-day fundamentals schedule. No network.

Run: python -m unittest test_group_prices.py   (also run in CI)
"""
import unittest
from datetime import date, datetime, timedelta, timezone

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
        g = gp.groups(assets, {})
        self.assertEqual(g["sp500"]["tickers"], ["AAPL"])
        self.assertEqual(g["ftse100"]["tickers"], ["AZN"])
        self.assertEqual(g["technology"]["tickers"], ["AAPL"])
        self.assertEqual(g["health-care"]["tickers"], ["AZN"])
        self.assertNotIn("X", {t for v in g.values() for t in v["tickers"]})
        self.assertEqual(len(g), 14)

    def test_category(self):
        self.assertEqual(gp.category_for({"kind": "market", "name": "S&P 500"}, {"sector": "Real Estate"}), "real-estate")
        self.assertEqual(gp.category_for({"kind": "sector", "name": "Health Care"}, {"industry": "Biotechnology"}), "biotechnology")
        self.assertEqual(gp.category_for({"kind": "sector", "name": "Energy"}, {"industry": "Oil & Gas"}), "oil-gas")


if __name__ == "__main__":
    unittest.main()
