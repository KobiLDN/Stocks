"""Tests for the group price bot (#88 PR 4): price maths, currency conversion, fundamentals,
grouping and the once-a-day fundamentals schedule. No network.

Run: python -m unittest test_group_prices.py   (also run in CI)
"""
import unittest
import unittest.mock
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
             "sector": "Consumer Staples", "industry": "Personal Goods", "t212": "yes", "isin": "GB00B10RZP78"}
        s = gp.stats(bars([4800 + i for i in range(30)]), date(2026, 2, 13))
        f = {"market_cap": 120e9, "market_cap_currency": "GBP", "pe_ratio": 20.0}
        r = gp.make_row("ULVR.L", a, s, f, FX, {}, "consumer-staples")
        self.assertEqual(r["price_gbp"], "48")                    # 4829p = £48.29
        self.assertAlmostEqual(r["price_usd"], 48.29 * 1.25, places=2)
        self.assertEqual(r["market_cap_gbp_b"], 120.0)            # GBP cap: not divided by 100
        self.assertEqual(r["markets"], ["ftse100"])
        self.assertEqual(r["news"], [])
        self.assertEqual(r["isin"], "GB00B10RZP78")                  # for the export (portfolio request)
        self.assertNotIn("isin", gp.all_row(r))                     # the big All file stays small

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


class News(unittest.TestCase):
    NOW = datetime(2026, 11, 23, 12, 0, tzinfo=timezone.utc)

    def test_parse_both_shapes(self):
        new = [{"content": {"title": "Up big", "provider": {"displayName": "Reuters"},
                            "canonicalUrl": {"url": "https://x/1"}, "pubDate": "2026-11-23T08:00:00Z"}}]
        old = [{"title": "Down", "publisher": "FT", "link": "https://x/2", "providerPublishTime": 1700000000}, "junk", {}]
        items, agg = gp.parse_news(new + old, None)
        self.assertEqual([i["title"] for i in items], ["Up big", "Down"])
        self.assertEqual(items[0]["published"], int(datetime(2026, 11, 23, 8, tzinfo=timezone.utc).timestamp()))
        self.assertEqual(items[1]["publisher"], "FT")
        self.assertIsNone(agg)                                   # no analyser: headlines kept, no sentiment

    def test_order_picks_then_movers_then_themes(self):
        assets = {t: {"yahoo": t + ".Y"} for t in "ABCDEFG"}
        prices = {a["yahoo"]: {"change_1d": i} for i, a in enumerate(assets.values())}
        g = {"tickers": list("ABCDEFG")}
        with unittest.mock.patch.object(gp, "MOVERS_PER_GROUP", 1):
            order = gp.news_wanted({"x": g}, assets, prices, picks={"D", "ZZ"}, themed={"C", "A"})
        self.assertEqual(order, ["D.Y", "A.Y", "G.Y", "C.Y"])   # pick, faller, riser, theme (A already in)

    def test_refresh_due_only_and_keeps_old_on_failure(self):
        fresh = (self.NOW - timedelta(hours=1)).isoformat()
        old = (self.NOW - timedelta(hours=9)).isoformat()
        cache = {"A": {"fetched": fresh, "news": [{"title": "kept"}]},
                 "B": {"fetched": old, "news": [{"title": "old B"}]},
                 "C": {"fetched": old, "news": [{"title": "old C"}]}}
        calls = []
        def fetch(y):
            calls.append(y)
            if y == "C":
                raise RuntimeError("429")
            return [{"title": "new " + y}]
        with unittest.mock.patch.object(gp.time, "sleep"):
            gp.refresh_news(cache, ["A", "B", "C", "D"], self.NOW, 1, fetch=fetch, analyzer=object())
        self.assertEqual(calls, ["B", "C", "D"])                # A was fresh
        self.assertEqual(cache["B"]["news"][0]["title"], "new B")
        self.assertEqual(cache["C"]["news"][0]["title"], "old C")   # failed: last good headlines stay
        self.assertEqual(cache["D"]["fetched"], self.NOW.isoformat(timespec="seconds"))

    def test_old_cache_not_shown(self):
        cache = {"A": {"fetched": (self.NOW - timedelta(days=8)).isoformat(), "news": [{"title": "x"}], "sentiment": 0.1},
                 "B": {"fetched": (self.NOW - timedelta(days=1)).isoformat(), "news": [{"title": "y"}], "sentiment": 0.2}}
        self.assertEqual(gp.news_for(cache, "A", self.NOW), ([], None))
        self.assertEqual(gp.news_for(cache, "B", self.NOW), ([{"title": "y"}], 0.2))
        self.assertEqual(gp.news_for(cache, "Z", self.NOW), ([], None))

    def test_live_picks_read_every_run(self):
        picks = gp.live_picks()
        self.assertGreater(len(picks), 100)                      # 14 run files, ~150 picks


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
        self.assertEqual(len(g), 15)                       # 3 index markets + Europe (#110) + 11 sectors
        self.assertEqual(list(g)[:4], ["sp500", "nasdaq100", "ftse100", "europe"])
        self.assertEqual(g["europe"]["tickers"], [])        # no European stock in this test list


class AllFile(unittest.TestCase):
    """All/all-data.js (#88 PR 7): every stock once, theme keys the All pages use, small rows."""
    def test_all_row(self):
        r = {"ticker": "MU", "sector": "Technology", "themes": ["AI", "Tech", "MegaCap"], "news": [1],
             "news_sentiment": 0.1, "price_gbp": "1", "low_gbp": "1", "high_gbp": "1", "price_usd": 1.0}
        out = gp.all_row(r)
        self.assertEqual(out["themes"], ["ai", "tech", "megacap"])
        self.assertEqual(out["category"], "technology")
        for k in gp.ALL_DROP:
            self.assertNotIn(k, out)
        self.assertEqual(out["price_usd"], 1.0)

    def test_crypto_rows_from_the_crypto_page(self):
        rows = gp.crypto_rows()
        self.assertGreater(len(rows), 20)
        self.assertTrue(all(r["markets"] == ["crypto"] and r["themes"] == ["crypto"] and r["t212"] == "no" for r in rows))

    def test_written_file(self):
        import json, re, tempfile, os
        with tempfile.TemporaryDirectory() as d, unittest.mock.patch.object(gp, "ROOT", d):
            os.makedirs(os.path.join(d, "Crypto"))
            with open(os.path.join(d, "Crypto", "prices-data.js"), "w") as f:
                f.write('window.PRICES_DATA = {"stocks":[{"ticker":"BTC","price_usd":90000,"news":[{"title":"b"}]}]};\n')
            gp.write_all({}, {"AAPL": {"ticker": "AAPL", "sector": "Technology", "themes": ["Tech"], "news": [{"title": "a"}]},
                              "IBM": {"ticker": "IBM", "sector": "Technology", "themes": [], "news": []}},
                         "2026-11-22 18:00", {"USD": 1.3})
            raw = open(os.path.join(d, gp.ALL_PATH)).read()
            news_raw = open(os.path.join(d, gp.NEWS_ALL_PATH)).read()
        data = json.loads(re.sub(r"^window\.ALL_DATA = ", "", raw).rstrip().rstrip(";"))
        self.assertEqual([r["ticker"] for r in data["stocks"]], ["AAPL", "IBM", "BTC"])
        self.assertEqual(data["count"], 3)
        self.assertNotIn("news", data["stocks"][0])                     # the big file stays small
        news = json.loads(re.sub(r"^window\.NEWS_DATA = ", "", news_raw).rstrip().rstrip(";"))
        self.assertEqual([(r["ticker"], r["themes"]) for r in news["stocks"]], [("AAPL", ["tech"]), ("BTC", ["crypto"])])


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
