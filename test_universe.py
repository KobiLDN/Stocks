"""Tests for the #88 master-list fields: ISIN check digit, name matching, ISIN resolution, sector
precedence and the "on T212" flag. No network: Yahoo, Wikipedia and the catalogue are faked.

Run: python -m unittest test_universe.py   (also run in CI)
"""
import unittest

import universe
from universe import health_group, isin_ok
from universe_classify import Catalogue, classify, names_agree, norm_name


def catalogue(*items):
    c = Catalogue.__new__(Catalogue)
    c.as_of, c.items = "test", [dict(type="STOCK", **i) for i in items]
    c.isins = {i["isin"] for i in c.items}
    c.by_ticker = {i["ticker"]: i for i in c.items}
    return c


TABLES = {
    "sp500": [{"yahoo": "AAPL", "name": "Apple Inc.", "isin": None,
               "sector_raw": "Information Technology", "industry_raw": "Technology Hardware"}],
    "ndx": [{"yahoo": "ASML", "name": "ASML", "isin": "NL0010273215", "sector_raw": None, "industry_raw": None}],
    "ftse": [{"yahoo": "AZN.L", "name": "AstraZeneca", "isin": "GB0009895292",
              "sector_raw": "Pharmaceuticals, Biotechnology and Marijuana Producers",
              "industry_raw": "Pharmaceuticals, Biotechnology and Marijuana Producers"}],
}


def run(assets, cat, overrides=None, yahoo=None):
    yahoo = yahoo or (lambda y: {"sector": "Technology", "industry": "Semiconductors", "currency": "USD"})
    return classify(assets, TABLES, cat, overrides or {}, yahoo=yahoo, wiki_isin=lambda n: None)


class Isin(unittest.TestCase):
    def test_check_digit(self):
        for good in ("US0378331005", "GB0002634946", "NL0010273215", "SA14TG012N13", "AU0000185993"):
            self.assertTrue(isin_ok(good), good)
        for bad in ("US0378331006", "us0378331005", "US037833100", None, "XX123"):
            self.assertFalse(isin_ok(bad), bad)


class Names(unittest.TestCase):
    def test_agree(self):
        self.assertTrue(names_agree("Meta Platforms", "Meta Platforms, Inc."))
        self.assertTrue(names_agree("HEICO Corporation", "Heico"))
        self.assertTrue(names_agree("Ørsted", "Orsted"))
        self.assertFalse(names_agree("Iris Energy", "IREN"))
        self.assertFalse(names_agree("Talen Energy", "Talon Capital"))

    def test_norm(self):
        self.assertEqual(norm_name("Johnson & Johnson"), "johnson johnson")
        self.assertEqual(norm_name("D. R. Horton"), norm_name("DR Horton"))
        self.assertEqual(norm_name("U.S. Bancorp"), "us bancorp")
        self.assertEqual(norm_name("Bank of America"), "bank of america")

    def test_ticker_match_allows_renamed_company(self):
        from universe_classify import first_word_agrees
        self.assertTrue(first_word_agrees("Franklin Resources", "Franklin Templeton"))
        self.assertFalse(first_word_agrees("Talen Energy", "Talon Capital"))
        self.assertFalse(first_word_agrees("GE Aerospace", "GE HealthCare"))   # too short to trust


class Classify(unittest.TestCase):
    def test_sector_precedence_and_isin_sources(self):
        assets = {
            "AAPL": {"name": "Apple", "exchange": "NASDAQ", "yahoo": "AAPL"},
            "ASML": {"name": "ASML Holding", "exchange": "NASDAQ", "yahoo": "ASML"},
            "AZN": {"name": "AstraZeneca", "exchange": "LSE", "yahoo": "AZN.L", "special": "lse_pence"},
        }
        cat = catalogue({"ticker": "AAPL_US_EQ", "isin": "US0378331005", "name": "Apple", "currency": "USD"},
                        {"ticker": "AZNl_EQ", "isin": "GB0009895292", "name": "AstraZeneca", "currency": "GBX"})
        up, _ = run(assets, cat, yahoo=lambda y: {"sector": "Healthcare", "currency": "GBp" if y.endswith(".L") else "USD"})
        self.assertEqual((up["AAPL"]["sector"], up["AAPL"]["sector_src"], up["AAPL"]["isin"]),
                         ("Technology", "gics", "US0378331005"))
        self.assertEqual((up["AZN"]["sector"], up["AZN"]["sector_src"], up["AZN"]["currency"]), ("Health Care", "icb", "GBp"))
        self.assertEqual((up["ASML"]["sector"], up["ASML"]["sector_src"]), ("Health Care", "yahoo"))   # not in S&P/FTSE
        self.assertEqual(up["ASML"]["isin"], "NL0010273215")       # from the Nasdaq-100 table
        self.assertEqual(up["ASML"]["t212"], "no")                 # ISIN known, not in the catalogue
        self.assertEqual(up["AAPL"]["t212"], "yes")

    def test_override_wins(self):
        assets = {"AAPL": {"name": "Apple", "exchange": "NASDAQ", "yahoo": "AAPL"}}
        cat = catalogue({"ticker": "AAPL_US_EQ", "isin": "US0378331005", "name": "Apple", "currency": "USD"})
        up, _ = run(assets, cat, overrides={"US0378331005": {"sector": "Consumer Staples", "reason": "test"}})
        self.assertEqual((up["AAPL"]["sector"], up["AAPL"]["sector_src"]), ("Consumer Staples", "override"))

    def test_renamed_ticker_found_by_name(self):
        assets = {"META": {"name": "Meta Platforms", "exchange": "NASDAQ", "yahoo": "META"}}
        cat = catalogue({"ticker": "FB_US_EQ", "isin": "US30303M1027", "name": "Meta Platforms", "currency": "USD"})
        up, _ = run(assets, cat)
        self.assertEqual((up["META"]["isin"], up["META"]["t212"]), ("US30303M1027", "yes"))

    def test_name_match_cannot_steal_another_stocks_isin(self):
        # BEP (partnership) and BEPC (corporation): the catalogue has only BEPC, named like both.
        assets = {
            "BEP": {"name": "Brookfield Renewable", "exchange": "NYSE", "yahoo": "BEP"},
            "BEPC": {"name": "Brookfield Renewable Corp", "exchange": "NYSE", "yahoo": "BEPC"},
        }
        cat = catalogue({"ticker": "BEPC_US_EQ", "isin": "CA11285B1085", "name": "Brookfield Renewable", "currency": "USD"})
        up, report = run(assets, cat)
        self.assertEqual(up["BEPC"]["isin"], "CA11285B1085")
        self.assertIsNone(up["BEP"]["isin"])
        self.assertEqual(up["BEP"]["t212"], "unknown")
        self.assertTrue(any("BEP: name match gave" in r for r in report))

    def test_ticker_match_needs_agreeing_name(self):
        assets = {"TLN": {"name": "Talen Energy", "exchange": "NASDAQ", "yahoo": "TLN"}}
        cat = catalogue({"ticker": "TLN_US_EQ", "isin": "KYG866521076", "name": "Talon Capital", "currency": "USD"})
        up, _ = run(assets, cat)
        self.assertIsNone(up["TLN"]["isin"])
        self.assertEqual(up["TLN"]["t212"], "unknown")

    def test_coins_are_not_on_t212(self):
        up, _ = run({"BTC": {"name": "Bitcoin", "exchange": "Crypto", "yahoo": "BTC-USD"}}, catalogue())
        self.assertEqual(up["BTC"], {"currency": "USD", "t212": "no"})

    def test_unclassified_when_no_source(self):
        assets = {"XYZ": {"name": "Nowhere Ltd", "exchange": "NYSE", "yahoo": "XYZ"}}
        up, report = run(assets, catalogue(), yahoo=lambda y: {"currency": "USD"})
        self.assertEqual(up["XYZ"]["sector"], "Unclassified")


class HealthGroups(unittest.TestCase):
    def test_groups(self):
        self.assertEqual(health_group("Biotechnology"), "Biotechnology")
        self.assertEqual(health_group("Pharmaceuticals"), "Pharmaceuticals")
        self.assertEqual(health_group("Pharmaceuticals, Biotechnology and Marijuana Producers"), "Pharmaceuticals")
        self.assertEqual(health_group("Drug Manufacturers - General"), "Pharmaceuticals")
        self.assertEqual(health_group("Life Sciences Tools & Services"), "Life Sciences Tools")
        self.assertEqual(health_group("Diagnostics & Research"), "Life Sciences Tools")
        self.assertEqual(health_group("Medical Devices"), "Equipment & Services")


class MasterList(unittest.TestCase):
    def test_universe_valid(self):
        self.assertEqual(universe.validate(), [])

    def test_every_stock_classified(self):
        for t, a in universe.load()["assets"].items():
            self.assertIn(a.get("t212"), ("yes", "no", "unknown"), t)
            if a["exchange"] != "Crypto":
                self.assertIn(a.get("sector"), universe.SECTORS + ["Unclassified"], t)


if __name__ == "__main__":
    unittest.main()
