"""Load universe.yaml — the master list of tracked assets and sector memberships.

The price scripts call sector_stocks() and get the same {ticker: tuple} shape their
hard-coded STOCKS dicts used to have, so their logic is unchanged.

Run `python universe.py` to validate the file (also run in CI).
"""
import os
import re
import sys

import yaml

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "universe.yaml")
_cache = None


def load():
    global _cache
    if _cache is None:
        with open(PATH, encoding="utf-8") as f:
            _cache = yaml.safe_load(f)
    return _cache


def sector_stocks(sector):
    """{ticker: tuple} in display order.
    Equities: (yahoo, category, exchange, special, name)
    Crypto:   (cmc_symbol, yahoo, category, exchange, name)"""
    u = load()
    out = {}
    for ticker, category in u["sectors"][sector]:
        a = u["assets"][ticker]
        if a["exchange"] == "Crypto":
            out[ticker] = (a["cmc_symbol"], a["yahoo"], category, a["exchange"], a["name"])
        else:
            out[ticker] = (a["yahoo"], category, a["exchange"], a.get("special"), a["name"])
    return out


def speculative(sector):
    u = load()
    return {t for t, _ in u["sectors"][sector] if u["assets"][t].get("speculative")}


def crypto_ids(sector="Crypto"):
    """(coingecko_ids, cmc_ids) as {ticker: id}, in display order."""
    u = load()
    tickers = [t for t, _ in u["sectors"][sector]]
    coingecko = {t: u["assets"][t]["coingecko"] for t in tickers}
    cmc = {t: u["assets"][t]["cmc_id"] for t in tickers if "cmc_id" in u["assets"][t]}
    return coingecko, cmc


# Theme folders retired on 22 Nov 2026 (#88): no pages, price script or signal run of their own. Their
# membership stays under `sectors:` (the themes filter on the All pages).
RETIRED_FOLDERS = {"Biotech", "Energy", "MegaCap", "Tech"}


def theme_folders():
    """Themes that still have their own folder: pages, prices.json, signals."""
    return [t for t in load()["sectors"] if t not in RETIRED_FOLDERS]


# The 11 standard sectors (#88). Pages say "Sector"; sector_src says where each came from.
SECTORS = [
    "Communication Services", "Consumer Discretionary", "Consumer Staples", "Energy", "Financials",
    "Health Care", "Industrials", "Materials", "Real Estate", "Technology", "Utilities",
]
# ISIN─────────────────────────────────────────────────────────────────────
ISIN_RE = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")


def isin_ok(isin):
    """Format + check digit (ISO 6166: letters -> numbers, then Luhn)."""
    if not isinstance(isin, str) or not ISIN_RE.match(isin):
        return False
    digits = "".join(str(int(c, 36)) for c in isin[:-1])
    total = 0
    for i, d in enumerate(reversed(digits)):
        n = int(d) * (2 if i % 2 == 0 else 1)
        total += n // 10 + n % 10
    return (10 - total % 10) % 10 == int(isin[-1])


# Index markets (#88): an asset's `markets` lists the indexes it is in (index_refresh.py keeps them
# up to date). The Crypto market is the Crypto group under sectors, not listed here.
MARKETS = ["ftse100", "nasdaq100", "sp500"]
MARKETS_ORDER = ["sp500", "nasdaq100", "ftse100"]   # how menus list them

CURRENCIES = {"USD", "GBp", "GBP", "EUR", "CHF", "JPY", "HKD", "CAD", "AUD", "KRW", "INR", "SAR", "DKK"}

# Health Care pages' industry filter (#88): industry text (GICS sub-industry, ICB sector or Yahoo
# industry) -> one of four groups.
HEALTH_GROUPS = ["Biotechnology", "Pharmaceuticals", "Life Sciences Tools", "Equipment & Services"]


def health_group(industry):
    s = (industry or "").lower()
    if "biotech" in s and "pharma" not in s:
        return "Biotechnology"
    if "pharma" in s or "drug manufacturers" in s:
        return "Pharmaceuticals"
    if "life sciences" in s or "diagnostics" in s:
        return "Life Sciences Tools"
    return "Equipment & Services"


def validate():
    """Return a list of problems (empty = valid)."""
    u = load()
    errors = []
    assets, sectors = u.get("assets") or {}, u.get("sectors") or {}
    specials = {None, "lse_pence", "jpy", "sar"}
    for t, a in assets.items():
        for field in ("name", "exchange", "yahoo"):
            if not a.get(field):
                errors.append(f"{t}: missing {field}")
        if a.get("special") not in specials:
            errors.append(f"{t}: unknown special {a.get('special')!r}")
        if a.get("exchange") == "Crypto":
            for field in ("cmc_symbol", "coingecko"):
                if not a.get(field):
                    errors.append(f"{t}: crypto asset missing {field}")
    # #88 fields: written by universe_classify.py
    seen_isin = {}
    for t, a in assets.items():
        if a.get("t212") not in ("yes", "no", "unknown"):
            errors.append(f"{t}: t212 must be yes | no | unknown, got {a.get('t212')!r}")
        if a.get("currency") not in CURRENCIES:
            errors.append(f"{t}: unknown currency {a.get('currency')!r}")
        if a.get("exchange") == "Crypto":
            continue
        if a.get("sector") not in SECTORS + ["Unclassified"]:
            errors.append(f"{t}: unknown sector {a.get('sector')!r}")
        if a.get("sector_src") not in ("gics", "icb", "yahoo", "override", None):
            errors.append(f"{t}: unknown sector_src {a.get('sector_src')!r}")
        isin = a.get("isin")
        if isin is not None and not isin_ok(isin):
            errors.append(f"{t}: ISIN {isin} fails its check digit")
        if isin is None and a.get("t212") != "unknown":
            errors.append(f"{t}: no ISIN, so t212 must be unknown")
        other = seen_isin.get(isin)
        # one ISIN may appear twice only as the same listing (RR./RR.L) or on two exchanges (CCEP on
        # Nasdaq and CCEP.L in London: one security, two venues)
        if isin and other and assets[other]["yahoo"] != a["yahoo"] and assets[other]["exchange"] == a["exchange"]:
            errors.append(f"{t}: same ISIN as {other}")
        seen_isin.setdefault(isin, t)
    for isin, ov in (u.get("sector_overrides") or {}).items():
        if not isin_ok(isin) or ov.get("sector") not in SECTORS or not ov.get("reason"):
            errors.append(f"sector_overrides {isin}: need a valid ISIN, one of the 11 sectors, and a reason")
    used = set()
    for s, members in sectors.items():
        seen = set()
        for entry in members:
            if not (isinstance(entry, list) and len(entry) == 2):
                errors.append(f"{s}: bad entry {entry!r} (want [ticker, category])")
                continue
            t, category = entry
            if t not in assets:
                errors.append(f"{s}: {t} is not in assets")
            if t in seen:
                errors.append(f"{s}: {t} listed twice")
            if not category:
                errors.append(f"{s}: {t} has no category")
            seen.add(t)
            used.add(t)
    in_market = set()
    for t, a in assets.items():
        m = a.get("markets")
        if m is None:
            continue
        if not isinstance(m, list) or not m or m != sorted(set(m)) or not set(m) <= set(MARKETS):
            errors.append(f"{t}: markets must be a sorted list from {MARKETS}, got {m!r}")
        else:
            in_market.add(t)
    for t in sorted(set(assets) - used - in_market):
        errors.append(f"{t}: in assets but in no sector and no market")
    for t, a in (u.get("retired") or {}).items():
        if t in assets:
            errors.append(f"{t}: in both assets and retired")
        for field in ("name", "exchange", "yahoo"):
            if not a.get(field):
                errors.append(f"retired {t}: missing {field}")
    return errors


LINKS_JS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asset-links.js")


def links_js():
    """asset-links.js: where each ticker links to — CoinGecko for coins, Yahoo (with the right
    exchange suffix, e.g. AZN -> AZN.L) for everything else. Generated; pages include it."""
    u = load()
    cg, yh = {}, {}
    for t, a in sorted({**(u.get("retired") or {}), **u["assets"]}.items()):
        if a["exchange"] == "Crypto" and a.get("coingecko"):
            cg[t] = a["coingecko"]
        elif a["yahoo"] != t:
            yh[t] = a["yahoo"]
    import json
    return (
        "/* asset-links.js — GENERATED from universe.yaml by `python universe.py --write-links`.\n"
        "   Do not edit by hand; CI fails if it is out of date. */\n"
        f"const ASSET_COINGECKO = {json.dumps(cg, sort_keys=True)};\n"
        f"const ASSET_YAHOO = {json.dumps(yh, sort_keys=True)};\n"
        "function assetUrl(t) {\n"
        "  if (ASSET_COINGECKO[t]) return 'https://www.coingecko.com/en/coins/' + ASSET_COINGECKO[t];\n"
        "  return 'https://finance.yahoo.com/quote/' + encodeURIComponent(ASSET_YAHOO[t] || t) + '/';\n"
        "}\n"
    )


def all_assets():
    """assets + retired: every asset any signal has ever named (history / track record)."""
    u = load()
    return {**(u.get("retired") or {}), **u["assets"]}


if __name__ == "__main__":
    if "--write-links" in sys.argv:
        with open(LINKS_JS, "w", encoding="utf-8") as f:
            f.write(links_js())
        print(f"wrote {os.path.basename(LINKS_JS)}")
        sys.exit(0)
    problems = validate()
    current = open(LINKS_JS, encoding="utf-8").read() if os.path.exists(LINKS_JS) else ""
    if current != links_js():
        problems.append("asset-links.js is out of date — run: python universe.py --write-links")
    for p in problems:
        print("ERROR:", p)
    u = load()
    print(f"{len(u['assets'])} assets (+{len(u.get('retired') or {})} retired), {sum(len(m) for m in u['sectors'].values())} sector memberships"
          f" across {len(u['sectors'])} sectors — {'OK' if not problems else f'{len(problems)} problem(s)'}")
    sys.exit(1 if problems else 0)
