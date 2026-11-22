"""The market and sector groups (#88): which stocks, where their pages live, and their categories.

Shared by the price bot (update_group_prices.py: each stock's `category`) and the page builder
(site/build.py: filter buttons, colours, labels), so the two can never disagree. Everything here is
worked out from universe.yaml alone.

  markets  sp500, nasdaq100, ftse100 -> pages in markets/<id>/;  categories = the 11 sectors
  sectors  the 11 standard sectors   -> pages in sectors/<slug>/; categories = industries:
           Health Care uses its 4 groups (owner decision, #88); the others show their TOP_INDUSTRIES
           commonest industries (9 above 80 stocks) and put the rest under "Other" (Industrials alone
           has ~30). ICB and Yahoo industry names are mapped to the GICS ones first (INDUSTRY_ALIASES).
"""
import re
from collections import Counter

import universe

MARKET_NAMES = {"sp500": "S&P 500", "nasdaq100": "Nasdaq-100", "ftse100": "FTSE 100"}
MARKET_ICONS = {"sp500": "🇺🇸", "nasdaq100": "📟", "ftse100": "🇬🇧"}
SECTOR_ICONS = {
    "Communication Services": "📡", "Consumer Discretionary": "🛍️", "Consumer Staples": "🛒", "Energy": "🛢️",
    "Financials": "🏦", "Health Care": "⚕️", "Industrials": "🏭", "Materials": "⛏️", "Real Estate": "🏢",
    "Technology": "💻", "Utilities": "💡",
}
TOP_INDUSTRIES = 7          # 9 for groups of more than 80 stocks
# CSS colour tokens (shared.css) with their dark-mode RGB, in the order categories get them
PALETTE = [
    ("accent", "0,212,255"), ("purple", "192,132,252"), ("teal", "45,212,191"), ("rose", "251,113,133"),
    ("blue", "68,136,255"), ("green", "0,230,118"), ("amber", "245,158,11"), ("gold", "255,215,0"),
    ("lime", "163,230,53"), ("indigo", "167,139,250"), ("red", "255,68,68"), ("slate", "148,163,184"),
]


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")


def all_groups(assets=None):
    """[{id, name, kind, path, icon, tickers}] in menu order: markets, then sectors A-Z."""
    assets = assets if assets is not None else universe.load()["assets"]
    # One entry per listing: the themes list Rolls-Royce twice (RR. and RR.L, both RR.L on Yahoo);
    # a group keeps the id that matches the Yahoo symbol, else the first.
    keep = {}
    for t in sorted(assets):
        a = assets[t]
        if a["exchange"] == "Crypto":
            continue
        y = a.get("yahoo", t)
        if y not in keep or (t == y and keep[y] != y):
            keep[y] = t
    stocks = {t: assets[t] for t in keep.values()}
    out = []
    for m in universe.MARKETS_ORDER:
        out.append({"id": m, "name": MARKET_NAMES[m], "kind": "market", "path": f"markets/{m}", "icon": MARKET_ICONS[m],
                    "tickers": sorted(t for t, a in stocks.items() if m in (a.get("markets") or []))})
    for s in universe.SECTORS:
        out.append({"id": slug(s), "name": s, "kind": "sector", "path": f"sectors/{slug(s)}", "icon": SECTOR_ICONS[s],
                    "tickers": sorted(t for t, a in stocks.items() if a.get("sector") == s)})
    return out


# The same industry under ICB (FTSE 100) or Yahoo names -> the GICS sub-industry name the S&P 500
# uses, so one industry gets one filter button. Only clear one-to-one matches; anything else keeps
# its own label (and may fall under "Other").
INDUSTRY_ALIASES = {
    # ICB (Wikipedia's FTSE 100 table)
    "Aerospace and Defense": "Aerospace & Defense",
    "Banks": "Diversified Banks",
    "Electricity": "Electric Utilities",
    "Gas, Water and Multi-utilities": "Multi-Utilities",
    "Industrial Metals and Mining": "Diversified Metals & Mining",
    "Investment Banking and Brokerage Services": "Investment Banking & Brokerage",
    "Life Insurance": "Life & Health Insurance",
    "Non-life Insurance": "Property & Casualty Insurance",
    "Non-Renewable Energy": "Integrated Oil & Gas",
    "Precious Metals and Mining": "Gold",
    "Software and Computer Services": "Application Software",
    "Telecommunications Service Providers": "Integrated Telecommunication Services",
    "Tobacco": "Tobacco",
    # Yahoo
    "Auto Manufacturers": "Automobile Manufacturers",
    "Banks - Diversified": "Diversified Banks",
    "Banks - Regional": "Regional Banks",
    "Capital Markets": "Investment Banking & Brokerage",
    "Communication Equipment": "Communications Equipment",
    "Consulting Services": "Research & Consulting Services",
    "Electrical Equipment & Parts": "Electrical Components & Equipment",
    "Information Technology Services": "IT Consulting & Other Services",
    "Internet Content & Information": "Interactive Media & Services",
    "Internet Retail": "Broadline Retail",
    "Oil & Gas E&P": "Oil & Gas Exploration & Production",
    "Oil & Gas Integrated": "Integrated Oil & Gas",
    "Oil & Gas Midstream": "Oil & Gas Storage & Transportation",
    "Semiconductor Equipment & Materials": "Semiconductor Materials & Equipment",
    "Software - Application": "Application Software",
    "Software - Infrastructure": "Systems Software",
    "Specialty Industrial Machinery": "Industrial Machinery & Supplies & Components",
    "Uranium": "Coal & Consumable Fuels",
    "Utilities - Independent Power Producers": "Independent Power Producers & Energy Traders",
    "Utilities - Regulated Electric": "Electric Utilities",
    "Utilities - Renewable": "Renewable Electricity",
}


def industry_label(a):
    raw = (a.get("industry") or "Other").strip()
    return INDUSTRY_ALIASES.get(raw, raw)


def categories(group, assets):
    """Ordered [(category id, label)] for a group's filter buttons and colours."""
    members = [assets[t] for t in group["tickers"]]
    if group["kind"] == "market":
        counts = Counter(a.get("sector") or "Unclassified" for a in members)
        return [(slug(s), s) for s, _ in sorted(counts.items(), key=lambda x: (-x[1], x[0]))]
    if group["name"] == "Health Care":
        present = {universe.health_group(a.get("industry")) for a in members}
        return [(slug(g), g) for g in universe.HEALTH_GROUPS if g in present]
    counts = Counter(industry_label(a) for a in members)
    n = TOP_INDUSTRIES + (2 if len(members) > 80 else 0)
    top = [i for i, _ in sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:n]]
    cats = [(slug(i), i) for i in top]
    if len(counts) > len(top):
        cats.append(("other", "Other"))
    return cats


def category_of(group, a, cats=None):
    """The category id one stock gets in one group (must be one of categories(group))."""
    if group["kind"] == "market":
        return slug(a.get("sector") or "Unclassified")
    if group["name"] == "Health Care":
        return slug(universe.health_group(a.get("industry")))
    ids = {c for c, _ in cats} if cats is not None else None
    c = slug(industry_label(a))
    return c if ids is None or c in ids else "other"


def colours(cats):
    """{category id: (css token, rgb)}: palette in order; "Other" is always slate."""
    out, i = {}, 0
    for cid, _ in cats:
        if cid == "other":
            out[cid] = ("slate", "148,163,184")
            continue
        out[cid] = PALETTE[i % len(PALETTE)]
        i += 1
    return out


def tradingview_symbol(t, a):
    """TradingView symbol for the charts page. LSE: the EPIC, with a trailing dot when it is
    shorter than 3 letters (BA. for BAE, RR. for Rolls-Royce); US class shares use a dot (BRK.B)."""
    y = a["yahoo"]
    if a["exchange"] == "LSE":
        epic = y[:-2].replace("-", ".")
        return f"LSE:{epic}." if len(epic) < 3 else f"LSE:{epic}"
    if a["exchange"] == "TSE":
        return f"TSE:{y.split('.')[0]}"
    if a["exchange"] == "TADAWUL":
        return f"TADAWUL:{y.split('.')[0]}"
    return f"{a['exchange']}:{y.replace('-', '.')}"
