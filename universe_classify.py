"""Fill in ISIN, currency, sector, industry and the "on T212" flag for every asset (#88).

    python universe_classify.py --catalogue ../portfolio-private/t212-instruments.json

Sources, in order (agreed in #88, "Revised plan"):
  sector   1. S&P 500 members: GICS sector + sub-industry from Wikipedia's S&P 500 table  (sector_src "gics")
           2. FTSE 100 members: ICB sector from Wikipedia, mapped with ICB_TO_SECTOR    (sector_src "icb")
           3. anything else: Yahoo's sector, mapped with YAHOO_TO_SECTOR               (sector_src "yahoo")
           4. sector_overrides in universe.yaml, keyed by ISIN, win over all of these   (sector_src "override")
           none of them -> "Unclassified" (left out of sector signal runs until fixed)
  isin     kept if already set; else the Nasdaq-100 / FTSE 100 tables; else the T212 catalogue
           (ticker match confirmed by name, or exact name match); else the company's Wikipedia infobox.
           Every ISIN must pass its check digit.
  t212     "yes" if the ISIN is in the T212 catalogue, "no" if the ISIN is known and absent (and for
           coins: the catalogue has stocks and ETFs only), "unknown" if there is no ISIN.
  currency Yahoo's quote currency (GBp = pence); coins are USD.

The T212 catalogue lives in the private portfolio repo. It is read, never copied: only yes/no lands here.
Needs network (Wikipedia, Yahoo). Re-run when the catalogue or the index lists change.
"""
import argparse
import io
import json
import random
import re
import sys
import time

import requests

import universe
from universe import SECTORS, isin_ok

UA = {"User-Agent": "Mozilla/5.0 (compatible; stocks-site universe refresh)"}
WIKI = "https://en.wikipedia.org/wiki/"
PAGES = {
    "sp500": "List_of_S%26P_500_companies",
    "ndx": "List_of_NASDAQ-100_companies",
    "ftse": "FTSE_100_Index",
}

GICS_TO_SECTOR = {s: s for s in SECTORS} | {"Information Technology": "Technology"}
YAHOO_TO_SECTOR = {
    "Technology": "Technology", "Healthcare": "Health Care", "Financial Services": "Financials",
    "Consumer Cyclical": "Consumer Discretionary", "Consumer Defensive": "Consumer Staples",
    "Communication Services": "Communication Services", "Industrials": "Industrials",
    "Basic Materials": "Materials", "Energy": "Energy", "Utilities": "Utilities", "Real Estate": "Real Estate",
}
# ICB sectors (the level Wikipedia's FTSE 100 table gives) -> the 11 sectors. ICB groups a few things
# differently from GICS (e.g. household goods with housebuilders); fix single stocks with sector_overrides.
ICB_TO_SECTOR = {
    "Aerospace and Defense": "Industrials", "Alternative Energy": "Energy",
    "Automobiles and Parts": "Consumer Discretionary", "Banks": "Financials", "Beverages": "Consumer Staples",
    "Chemicals": "Materials", "Closed End Investments": "Financials",
    "Construction and Materials": "Industrials", "Consumer Services": "Consumer Discretionary",
    "Electricity": "Utilities", "Electronic and Electrical Equipment": "Industrials",
    "Finance and Credit Services": "Financials", "Food Producers": "Consumer Staples",
    "Gas, Water and Multi-utilities": "Utilities", "General Industrials": "Industrials",
    "Health Care Providers": "Health Care", "Household Goods and Home Construction": "Consumer Discretionary",
    "Industrial Engineering": "Industrials", "Industrial Materials": "Materials",
    "Industrial Metals and Mining": "Materials", "Industrial Support Services": "Industrials",
    "Industrial Transportation": "Industrials", "Investment Banking and Brokerage Services": "Financials",
    "Leisure Goods": "Consumer Discretionary", "Life Insurance": "Financials", "Media": "Communication Services",
    "Medical Equipment and Services": "Health Care", "Mortgage Real Estate Investment Trusts": "Financials",
    "Non-life Insurance": "Financials", "Non-Renewable Energy": "Energy", "Oil, Gas and Coal": "Energy",
    "Personal Care, Drug and Grocery Stores": "Consumer Staples", "Personal Goods": "Consumer Discretionary",
    "Pharmaceuticals, Biotechnology and Marijuana Producers": "Health Care",
    "Precious Metals and Mining": "Materials", "Real Estate Investment and Services": "Real Estate",
    "Real Estate Investment Trusts": "Real Estate", "Retailers": "Consumer Discretionary",
    "Software and Computer Services": "Technology", "Technology Hardware and Equipment": "Technology",
    "Telecommunications Equipment": "Technology", "Telecommunications Service Providers": "Communication Services",
    "Tobacco": "Consumer Staples", "Travel and Leisure": "Consumer Discretionary",
    "Waste and Disposal Services": "Industrials", "Equity Investment Instruments": "Financials",
}


# ── names ──────────────────────────────────────────────────────────────────────
_SUFFIXES = r"\b(inc|incorporated|corp|corporation|co|company|plc|ltd|limited|holdings?|group|sa|nv|n\.v|ag|se|ab|asa|the|class [abc]|cl [abc]|adr|ads|sponsored|common stock|ordinary shares?)\b"


_TRANSLIT = str.maketrans({"ø": "o", "æ": "ae", "å": "a", "ß": "ss", "é": "e", "è": "e", "ü": "u", "ö": "o", "ä": "a"})


def norm_name(name):
    s = (name or "").lower().translate(_TRANSLIT).replace("&", " and ").replace(".com", "")
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(_SUFFIXES, " ", s)
    return " ".join(s.split())


def names_agree(a, b):
    """Loose match: equal after normalising, or one name's words all appear in the other."""
    na, nb = norm_name(a), norm_name(b)
    if not na or not nb:
        return False
    if na == nb or na.startswith(nb) or nb.startswith(na):
        return True
    wa, wb = set(na.split()), set(nb.split())
    return wa <= wb or wb <= wa


# Hand-checked ISINs for stocks the automatic match can't settle (renamed, listed under another
# ticker, or not on T212). Checked on 22 Nov 2026 against the T212 catalogue entry's name and ticker,
# or (2222.SR) against the company's Wikipedia infobox.
ISIN_PINS = {
    "2222.SR": ("SA14TG012N13", "Saudi Aramco: Wikipedia infobox; not in the T212 catalogue"),
    "285A":  ("JP3236330001", "Kioxia: TSE share; T212 lists it on Xetra (KI5d_EQ)"),
    "DNNGY": ("US68750L1026", "Orsted ADR (DNNGY_US_EQ); name spelt without the accent"),
    "HEI":   ("US4228061093", "HEICO common share; T212 ticker HEICO_US_EQ (HEI/A is the A share)"),
    "HUT":   ("US44812J1043", "Hut 8 Corp (renamed from Hut 8 Mining); T212 HUTMF_US_EQ"),
    "IREN":  ("AU0000185993", "IREN (renamed from Iris Energy); T212 IREN_US_EQ"),
}


# ── sources ────────────────────────────────────────────────────────────────────
def fetch_html(page):
    for attempt in range(4):
        try:
            r = requests.get(WIKI + page, headers=UA, timeout=30)
            if r.status_code == 200:
                return r.text
        except requests.RequestException:
            pass
        time.sleep(2 ** attempt + random.random())
    raise RuntimeError(f"could not fetch {page}")


def read_tables(html):
    import pandas as pd
    return pd.read_html(io.StringIO(html))


def _table_with(tables, *cols):
    for t in tables:
        names = [re.sub(r"\[\d+\]", "", str(c)).strip() for c in t.columns]
        if all(c in names for c in cols):
            t = t.copy()
            t.columns = names
            return t
    raise RuntimeError(f"no table with columns {cols}")


def us_yahoo(symbol):
    return str(symbol).strip().replace(".", "-")


def lse_yahoo(epic):
    return str(epic).strip().rstrip(".").replace(".", "-") + ".L"


def index_tables(pages=None):
    """{name: [row]} for S&P 500, Nasdaq-100, FTSE 100. Rows: yahoo, name, isin?, sector_raw, industry_raw."""
    pages = pages or {k: fetch_html(v) for k, v in PAGES.items()}
    sp = _table_with(read_tables(pages["sp500"]), "Symbol", "Security", "GICS Sector", "GICS Sub-Industry")
    nd = _table_with(read_tables(pages["ndx"]), "Ticker", "Company", "ISIN")
    ft = _table_with(read_tables(pages["ftse"]), "Company", "Ticker", "ISIN")
    ft_sector = [c for c in ft.columns if "classification" in c.lower() or "sector" in c.lower()][0]
    return {
        "sp500": [{"yahoo": us_yahoo(r["Symbol"]), "name": r["Security"], "isin": None,
                   "sector_raw": r["GICS Sector"], "industry_raw": r["GICS Sub-Industry"]} for _, r in sp.iterrows()],
        "ndx": [{"yahoo": us_yahoo(r["Ticker"]), "name": r["Company"], "isin": r["ISIN"],
                 "sector_raw": None, "industry_raw": None} for _, r in nd.iterrows()],
        "ftse": [{"yahoo": lse_yahoo(r["Ticker"]), "name": r["Company"], "isin": r["ISIN"],
                  "sector_raw": r[ft_sector], "industry_raw": r[ft_sector]} for _, r in ft.iterrows()],
    }


def yahoo_info(symbol):
    import yfinance as yf
    for attempt in range(4):
        try:
            i = yf.Ticker(symbol).info or {}
            return {"sector": i.get("sector"), "industry": i.get("industry"), "currency": i.get("currency")}
        except Exception as e:  # 429s and proxy hiccups: jittered backoff
            if attempt == 3:
                print(f"  yahoo {symbol}: {str(e)[:80]}")
            time.sleep(1.5 * 2 ** attempt + random.random())
    return {}


def wikipedia_isin(name):
    """ISIN from the company's own Wikipedia infobox, if it shows exactly one valid one."""
    html = None
    for attempt in range(3):
        try:
            r = requests.get("https://en.wikipedia.org/w/api.php", headers=UA, timeout=30, params={
                "action": "opensearch", "search": name, "limit": 1, "namespace": 0, "format": "json"})
            hits = r.json()[3]
            if not hits:
                return None
            html = requests.get(hits[0], headers=UA, timeout=30).text
            break
        except (requests.RequestException, ValueError, IndexError):
            time.sleep(2 ** attempt + random.random())
    if not html:
        return None
    box = re.search(r'<table class="infobox.*?</table>', html, re.S)
    found = {m for m in re.findall(r"\b[A-Z]{2}[A-Z0-9]{9}[0-9]\b", box.group(0) if box else "") if isin_ok(m)}
    return found.pop() if len(found) == 1 else None


# ── T212 catalogue (private; read only) ────────────────────────────────────────
class Catalogue:
    def __init__(self, path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.as_of = data.get("as_of")
        self.items = [i for i in data["instruments"] if i.get("isin")]
        self.isins = {i["isin"] for i in self.items}
        self.by_ticker = {i["ticker"]: i for i in self.items}

    def candidates(self, asset):
        y = asset["yahoo"]
        if asset["exchange"] == "LSE":
            return [y[:-2].replace("-", ".") + "l_EQ", y[:-2].replace("-", "_") + "l_EQ"]
        if asset["exchange"] in ("NYSE", "NASDAQ"):
            return [y.replace("-", "_") + "_US_EQ", y.replace("-", "") + "_US_EQ"]
        return []

    def by_ticker_match(self, asset):
        """ISIN of a T212 instrument with our ticker, if its name agrees. (isin, how)."""
        for t in dict.fromkeys(self.candidates(asset)):
            i = self.by_ticker.get(t)
            if i and names_agree(i["name"], asset["name"]):
                return i["isin"], f"t212 ticker {t}"
            if i:
                print(f"  {asset['yahoo']}: T212 {t} is '{i['name']}', not '{asset['name']}' — ignored")
        return None, "no T212 ticker match"

    def by_name_match(self, asset, currency):
        """ISIN of the one T212 stock with exactly our name (renamed tickers: Meta = FB_US_EQ)."""
        same = [i for i in self.items if i["type"] == "STOCK" and norm_name(i["name"]) == norm_name(asset["name"])]
        isins = {i["isin"] for i in same}
        if len(isins) > 1 and currency:   # ADR and local share both listed: take the one in our currency
            cur = {"GBp": "GBX"}.get(currency, currency)
            isins = {i["isin"] for i in same if i["currency"] == cur} or isins
        if len(isins) == 1:
            return isins.pop(), "t212 name"
        return None, f"{len(isins)} T212 name matches"


# ── classification ─────────────────────────────────────────────────────────────
def resolve_isins(equities, isin_from_index, catalogue, currencies, wiki_isin, report):
    """{ticker: isin or None}. Pass 1 uses the reliable sources for every stock; pass 2 (name match,
    Wikipedia infobox) only fills gaps, and may not reuse an ISIN pass 1 gave another stock — BEP and
    BEPC are both "Brookfield Renewable" in the catalogue, but only BEPC owns that ISIN."""
    isins, how = {}, {}
    for t, a in equities.items():
        if t in ISIN_PINS:
            isins[t], how[t] = ISIN_PINS[t][0], "pinned"
        elif a.get("isin"):
            isins[t], how[t] = a["isin"], "kept"
        elif isin_from_index.get(a["yahoo"]):
            isins[t], how[t] = isin_from_index[a["yahoo"]], "index table"
        else:
            isins[t], how[t] = catalogue.by_ticker_match(a)
    taken = {}
    for t, v in isins.items():
        if v:
            taken.setdefault(v, t)
    for t, a in equities.items():
        if isins[t]:
            continue
        v, h = catalogue.by_name_match(a, currencies.get(t))
        if v and v in taken and equities[taken[v]]["yahoo"] != a["yahoo"]:
            report.append(f"{t}: name match gave {v}, which is {taken[v]}'s — dropped")
            v, h = None, "name clash"
        if not v:
            v = wiki_isin(a["name"])
            h = "wikipedia infobox" if v else h
        isins[t], how[t] = v, h
        if v:
            taken.setdefault(v, t)
    for t, v in isins.items():
        if v and not isin_ok(v):
            report.append(f"{t}: ISIN {v} fails its check digit — dropped")
            isins[t] = None
        if isins[t] and how[t] not in ("kept", "index table"):
            report.append(f"{t}: ISIN {isins[t]} via {how[t]}")
        if not isins[t]:
            report.append(f"{t}: no ISIN ({how[t]}) — t212 unknown")
    return isins


def classify(assets, tables, catalogue, overrides, yahoo=yahoo_info, wiki_isin=wikipedia_isin):
    """Return {ticker: {field: value}} updates and a list of report lines. Pure apart from the lookups."""
    sp = {r["yahoo"]: r for r in tables["sp500"]}
    ft = {r["yahoo"]: r for r in tables["ftse"]}
    isin_from_index = {r["yahoo"]: r["isin"] for k in ("ndx", "ftse") for r in tables[k] if isin_ok(r.get("isin"))}
    updates, report = {}, []
    equities = {t: a for t, a in assets.items() if a["exchange"] != "Crypto"}
    for t in assets:
        if t not in equities:   # coins: not in the T212 catalogue (stocks and ETFs only)
            updates[t] = {"currency": "USD", "t212": "no"}
    info, currencies = {}, {}
    for t, a in equities.items():
        y = a["yahoo"]
        if not a.get("currency") or (y not in sp and y not in ft):
            info[t] = yahoo(y)
        currencies[t] = a.get("currency") or info.get(t, {}).get("currency")
    isins = resolve_isins(equities, isin_from_index, catalogue, currencies, wiki_isin, report)
    for t, a in equities.items():
        y, isin = a["yahoo"], isins[t]
        if y in sp:
            sector, src, industry = GICS_TO_SECTOR.get(sp[y]["sector_raw"]), "gics", sp[y]["industry_raw"]
        elif y in ft:
            sector, src, industry = ICB_TO_SECTOR.get(ft[y]["sector_raw"]), "icb", ft[y]["industry_raw"]
            if not sector:
                report.append(f"{t}: ICB sector '{ft[y]['sector_raw']}' not in ICB_TO_SECTOR")
        else:
            i = info.get(t, {})
            sector, src, industry = YAHOO_TO_SECTOR.get(i.get("sector")), "yahoo", i.get("industry")
        ov = overrides.get(isin) if isin else None
        if ov:
            sector, src, industry = ov["sector"], "override", ov.get("industry", industry)
        if not sector:
            report.append(f"{t}: no sector found — Unclassified")
            sector, src = "Unclassified", None
        on = "unknown" if not isin else ("yes" if isin in catalogue.isins else "no")
        updates[t] = {"isin": isin, "currency": currencies[t], "sector": sector, "sector_src": src,
                      "industry": industry, "t212": on}
    return updates, report


FIELD_ORDER = ["isin", "currency", "sector", "sector_src", "industry", "t212"]


def apply(updates):
    """Rewrite universe.yaml's asset lines in place (same one-line layout), adding/refreshing FIELD_ORDER."""
    text = open(universe.PATH, encoding="utf-8").read()
    u = universe.load()
    out = []
    section = None
    for line in text.split("\n"):
        if re.match(r"^[a-z_]+:", line):
            section = line.split(":")[0]
        m = re.match(r'^  "([^"]+)":', line)
        if section == "assets" and m and m.group(1) in updates:
            t = m.group(1)
            a = {k: v for k, v in u["assets"][t].items() if k not in FIELD_ORDER}
            for k in FIELD_ORDER:
                v = updates[t].get(k)
                if v is not None:
                    a[k] = v
            line = f'  {(json.dumps(t) + ":").ljust(10)} {json.dumps(a)}'
        out.append(line)
    with open(universe.PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--catalogue", required=True, help="path to t212-instruments.json (private portfolio repo)")
    args = p.parse_args()
    catalogue = Catalogue(args.catalogue)
    print(f"T212 catalogue {catalogue.as_of}: {len(catalogue.items)} instruments with ISINs")
    tables = index_tables()
    print("index tables:", {k: len(v) for k, v in tables.items()})
    u = universe.load()
    updates, report = classify(u["assets"], tables, catalogue, u.get("sector_overrides") or {})
    for line in report:
        print(" ", line)
    apply(updates)
    universe._cache = None
    counts = {}
    for v in updates.values():
        counts[v["t212"]] = counts.get(v["t212"], 0) + 1
    print("t212:", counts)
    problems = universe.validate()
    for pr in problems:
        print("ERROR:", pr)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
