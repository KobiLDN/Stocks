#!/usr/bin/env python3
"""AI signal runs for the market and sector groups (#88 phase 1, PR 8).

    python generate_group_signals.py                  # every group with its own run, then the derived ones
    python generate_group_signals.py --group energy --group ftse100

Runs (one AI call each, same model and pick format as the theme runs):
  the 11 sectors and the FTSE 100 -> <group path>/signals-local.json (+ .js)
Derived (no AI call, revised plan point 1): the S&P 500 and Nasdaq-100 are too big for one prompt, and
a pre-screen by recent strength would repeat the run-up mistake, so their Signals pages show the sector
runs' picks that are members of the index. Marked "derived": true; the history recorder skips them so
no pick is counted twice.

Input per group: its own prices-data.js (written by update_group_prices.py). The prompt is built from
the group's name and categories (groups_config.py), so a new group needs no new prompt file.
API key: OPENROUTER_API_KEY, or key.txt next to this file for local runs (gitignored).
A failed group keeps its previous file; the others still run. Exit code 1 if any group failed.
"""
import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

import groups_config
import universe
from momentum_screener import compute_momentum_picks
from signal_meta import annotate_momentum, run_meta

ROOT = os.path.dirname(os.path.abspath(__file__))
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "deepseek/deepseek-v4-flash"
TEMPERATURE = 0.3
MAX_TOKENS = 12288
REQUEST_TIMEOUT_S = (15, 170)
TOP_N = 10
RETRY_ON_BAD_JSON = 1
RUN_GROUPS = [groups_config.slug(s) for s in universe.SECTORS] + ["ftse100"]
DERIVED = ["sp500", "nasdaq100"]

# One line of what matters most in each group, for the prompt
GROUP_FACTORS = {
    "Technology": "AI and cloud demand, product cycles, earnings beats, market share, chip supply and export rules",
    "Health Care": "trial readouts, drug approvals, patent cliffs, pricing and reimbursement policy, pipeline deals",
    "Financials": "interest-rate outlook, credit quality, capital returns, trading and fee income, regulation",
    "Consumer Discretionary": "consumer spending, pricing power, inventories, travel and housing demand",
    "Communication Services": "advertising spend, subscriber growth, content costs, regulation",
    "Industrials": "order books and backlog, defence and infrastructure budgets, margins, supply chains",
    "Consumer Staples": "pricing versus volumes, input costs, brand strength, dividend safety",
    "Energy": "oil and gas prices, production guidance, capital discipline, dividends and buybacks",
    "Utilities": "rate cases and regulation, power demand from data centres, interest rates, renewables build-out",
    "Real Estate": "interest rates, occupancy and rents, refinancing, data-centre and tower demand",
    "Materials": "commodity prices, China demand, costs, capacity and pricing",
    "FTSE 100": "sterling moves (many FTSE companies earn abroad), Bank of England rates, commodity prices, "
                "dividends and buybacks; prices are in pence",
}


# ── helpers (same behaviour as the theme generators) ──────────────────────────
class RunFailed(Exception):
    pass


def load_api_key():
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    path = os.path.join(ROOT, "key.txt")
    if os.path.exists(path):
        key = open(path, encoding="utf-8").read().strip()
        if key:
            return key
    raise RunFailed("no OpenRouter API key (OPENROUTER_API_KEY, or key.txt for local runs)")


def first_json_object(text):
    if not text:
        return None
    start = text.find("{")
    if start < 0:
        return None
    depth, in_str, esc = 0, False, False
    for i in range(start, len(text)):
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def read_js(path, var):
    raw = open(path, encoding="utf-8").read()
    return json.loads(re.sub(r"^\s*window\." + var + r"\s*=\s*", "", raw).rstrip().rstrip(";"))


def compact_stock(s, cat_labels):
    return {
        "ticker": s.get("ticker"), "name": s.get("company_name"),
        "cat": cat_labels.get(s.get("category"), s.get("category")),
        "price": s.get("price_usd"), "ret_1y": s.get("return_1yr"), "ytd": s.get("change_ytd"),
        "ch_1m": s.get("change_1m"), "ch_1w": s.get("change_1w"), "ch_1d": s.get("change_1d"),
        "mc_usd_b": s.get("market_cap_usd_b"), "beta": s.get("beta"), "pe": s.get("pe_ratio"),
        "div_pct": s.get("div_yield_pct"), "short": s.get("short_pct"),
        "analyst": s.get("analyst"), "an_score": s.get("analyst_score"),
    }


def system_prompt(group, cats, counts):
    kind = "index" if group["kind"] == "market" else "sector"
    cat_word = "sector" if group["kind"] == "market" else "industry"
    cat_lines = ", ".join(f"{label} ({counts.get(cid, 0)})" for cid, label in cats)
    return f"""You are an investment research assistant analysing the {len(group['tickers'])} stocks of the {group['name']} {kind} for a UK-based research dashboard. Output is for informational and educational purposes only — NOT financial advice.

The stocks are grouped by {cat_word}: {cat_lines}.

You will be given a JSON snapshot of every stock: price in USD, year-to-date and 1-year returns, short-term moves (1D/1W/1M %), market cap in $B, beta, P/E, dividend yield, short interest %, and the analyst recommendation and score.

Before ranking, use web search to find the latest news, analyst changes, earnings surprises and deals for the stocks listed in the user prompt. Use what you find to enrich your rationale with live catalysts.

Pick the 10 most attractive stocks RIGHT NOW based on a BALANCED view of:
  - Momentum (recent 1D/1W/1M moves, YTD)
  - Fundamentals (P/E, market cap, beta — avoid extreme over-extension)
  - Analyst consensus (strong_buy / buy weighted positively, sell weighted negatively)
  - Live catalysts found via web search
  - What matters most here: {GROUP_FACTORS.get(group['name'], 'company-specific catalysts')}

Rank them 1 (best) to 10. Use the "signal" field to distinguish strong_buy from buy where appropriate. Confidence is your subjective certainty in [0, 1].

Output ONLY a single JSON object with this EXACT shape:
{{
  "picks": [
    {{
      "rank": 1,
      "ticker": "<must be one of the input tickers>",
      "signal": "strong_buy" | "buy",
      "confidence": 0.0,
      "rationale": "1-2 sentences citing specific numbers from the input (e.g. '+45% YTD, P/E 22')",
      "drivers": ["short metric phrase", "short metric phrase"]
    }}
  ]
}}

Hard rules:
- Exactly 10 picks, ranks 1 through 10, no duplicates.
- Use ONLY tickers present in the input.
- "rationale" must cite at least one concrete number from the input.
- "drivers" is a list of 2-4 short metric phrases that drove the rank.
- Output ONLY the JSON object — no prose, no markdown fences, no explanation.
"""


def build_user_prompt(stocks, cat_labels):
    def pct(v):
        try:
            return float(str(v).replace("%", "").replace("+", ""))
        except (TypeError, ValueError):
            return 0.0
    search = ", ".join(s["ticker"] for s in sorted(stocks, key=lambda s: pct(s.get("change_1m")), reverse=True)[:10])
    payload = {"stocks": [compact_stock(s, cat_labels) for s in stocks]}
    return (f"Search for the latest news on these tickers before ranking: {search}.\n\n"
            "Stock snapshot follows as compact JSON. Field keys: cat=sector or industry, ret_1y=1-year return, "
            "ytd=YTD %, ch_1m/1w/1d=% change, mc_usd_b=market cap in USD billions, pe=trailing P/E, "
            "div_pct=dividend yield %, short=short interest %, an_score=analyst recommendation mean "
            f"(lower=more bullish). Return your top {TOP_N} picks.\n\n"
            + json.dumps(payload, separators=(",", ":")))


def call_api(api_key, sys_prompt, user_prompt, label):
    body = {
        "model": MODEL,
        "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
        "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS,
        "response_format": {"type": "json_object"}, "stream": False,
        "plugins": [{"id": "web", "max_results": 5}],
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
               "HTTP-Referer": "https://stocks-4qw.pages.dev/", "X-Title": f"{label} - Signals"}
    t0 = time.time()
    try:
        r = requests.post(ENDPOINT, headers=headers, timeout=REQUEST_TIMEOUT_S,
                          data=json.dumps(body, ensure_ascii=False).encode("utf-8"))
    except requests.exceptions.RequestException as e:
        raise RunFailed(f"OpenRouter request failed: {e}")
    if r.status_code != 200:
        raise RunFailed(f"OpenRouter returned {r.status_code}: {r.text[:300]}")
    data = r.json()
    usage = data.get("usage", {})
    print(f"  [{label}] HTTP 200 in {time.time() - t0:.0f}s, tokens in={usage.get('prompt_tokens')} "
          f"out={usage.get('completion_tokens')}")
    content = (data["choices"][0]["message"].get("content") or "").strip()
    if not content:
        raise ValueError("empty reply")
    return content


def parse_picks(content, valid):
    try:
        obj = json.loads(first_json_object(content) or content)
    except json.JSONDecodeError as e:
        raise ValueError(f"not valid JSON: {e}")
    picks = obj.get("picks")
    if not isinstance(picks, list) or len(picks) != TOP_N:
        raise ValueError(f"expected {TOP_N} picks, got {len(picks) if isinstance(picks, list) else 'none'}")
    out, seen = [], set()
    for i, p in enumerate(picks, 1):
        if not isinstance(p, dict):
            raise ValueError(f"pick {i} is not an object")
        t = p.get("ticker")
        if t not in valid:
            raise ValueError(f"pick {i} ticker {t!r} not in this group")
        if t in seen:
            raise ValueError(f"duplicate ticker {t!r}")
        seen.add(t)
        sig = (p.get("signal") or "").lower()
        try:
            conf = max(0.0, min(1.0, float(p.get("confidence", 0))))
        except (TypeError, ValueError):
            conf = 0.0
        drivers = p.get("drivers") if isinstance(p.get("drivers"), list) else []
        out.append({"rank": i, "ticker": t, "signal": sig if sig in ("strong_buy", "buy") else "buy",
                    "confidence": round(conf, 3), "rationale": (p.get("rationale") or "").strip(),
                    "drivers": [str(d).strip() for d in drivers if str(d).strip()][:5]})
    return out


def write_signals(path, out):
    with open(os.path.join(path, "signals-local.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    with open(os.path.join(path, "signals-local.js"), "w", encoding="utf-8") as f:
        f.write(f"window.SIGNALS_DATA = {json.dumps(out, indent=2)};\n")


def previous(path):
    try:
        return json.load(open(os.path.join(path, "signals-local.json"), encoding="utf-8")).get("picks") or []
    except (OSError, ValueError):
        return []


# ── one group ──────────────────────────────────────────────────────────────────
def run_group(group, assets, api_key, now_str, call=call_api):
    path = os.path.join(ROOT, group["path"])
    stocks = read_js(os.path.join(path, "prices-data.js"), "PRICES_DATA").get("stocks") or []
    if not stocks:
        raise RunFailed("no prices for this group")
    cats = groups_config.categories(group, assets)
    labels = dict(cats)
    counts = {}
    for s in stocks:
        counts[s.get("category")] = counts.get(s.get("category"), 0) + 1
    sp = system_prompt(group, cats, counts)
    up = build_user_prompt(stocks, labels)
    valid = {s["ticker"] for s in stocks}
    picks, err = None, None
    for attempt in range(1 + RETRY_ON_BAD_JSON):
        try:
            picks = parse_picks(call(api_key, sp + ("\n\nIMPORTANT: Previous reply was not valid. Reply with ONLY "
                                                     "the JSON object." if attempt else ""), up, group["name"]), valid)
            break
        except ValueError as e:
            err = e
            print(f"  [{group['name']}] attempt {attempt + 1} failed: {e}")
    if picks is None:
        raise RunFailed(f"no valid reply ({err})")
    momentum_picks, upgrades = compute_momentum_picks(stocks, {p["ticker"] for p in picks})
    annotate_momentum(picks, upgrades)
    out = {
        "updated": now_str, "model": MODEL, "endpoint": ENDPOINT, "source": "openrouter",
        "group": group["id"], "group_name": group["name"], "group_kind": group["kind"],
        **run_meta(sp, build_user_prompt),
        "picks": picks, "momentum_picks": momentum_picks, "previous_picks": previous(path),
    }
    write_signals(path, out)
    return out


# ── derived market pages (S&P 500, Nasdaq-100) ────────────────────────────────
def derive_market(market, groups, assets, now_str):
    """The sector runs' picks that are members of `market`, best first (confidence, then sector rank)."""
    members = set(groups[market]["tickers"])
    picks, sources, latest = [], [], None
    for g in groups.values():
        if g["kind"] != "sector":
            continue
        try:
            data = json.load(open(os.path.join(ROOT, g["path"], "signals-local.json"), encoding="utf-8"))
        except (OSError, ValueError):
            continue
        sources.append(g["id"])
        latest = max(latest or "", data.get("updated") or "")
        for p in data.get("picks") or []:
            if p["ticker"] in members:
                picks.append({**p, "from_group": g["id"], "from_group_name": g["name"], "group_rank": p["rank"]})
    picks.sort(key=lambda p: (-p.get("confidence", 0), p["group_rank"], p["ticker"]))
    for i, p in enumerate(picks, 1):
        p["rank"] = i
    path = os.path.join(ROOT, groups[market]["path"])
    out = {"updated": latest or now_str, "derived": True, "derived_from": sources,
           "group": market, "group_name": groups[market]["name"], "group_kind": "market",
           "note": f"Picks from the 11 sector runs that are members of the {groups[market]['name']}; "
                   "no separate AI run (too many stocks for one prompt).",
           "picks": picks, "momentum_picks": [], "previous_picks": previous(path)}
    write_signals(path, out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--group", action="append", help=f"one of {RUN_GROUPS} (default: all)")
    ap.add_argument("--workers", type=int, default=4, help="groups run at the same time")
    args = ap.parse_args(argv)
    assets = universe.load()["assets"]
    groups = {g["id"]: g for g in groups_config.all_groups(assets)}
    todo = args.group or RUN_GROUPS
    unknown = [g for g in todo if g not in RUN_GROUPS]
    if unknown:
        sys.exit(f"unknown group(s): {unknown}; choose from {RUN_GROUPS}")
    api_key = load_api_key()
    now_str = datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%d %H:%M")

    def one(gid):
        try:
            out = run_group(groups[gid], assets, api_key, now_str)
            return gid, None, out
        except (RunFailed, OSError, ValueError, KeyError) as e:
            return gid, str(e), None

    failed = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        for gid, err, out in pool.map(one, todo):
            if err:
                failed.append(gid)
                print(f"FAILED {groups[gid]['name']}: {err} (previous picks kept)")
            else:
                print(f"{groups[gid]['name']}: " + ", ".join(p["ticker"] for p in out["picks"]))
    for m in DERIVED:
        out = derive_market(m, groups, assets, now_str)
        print(f"{groups[m]['name']} (from the sector runs): {len(out['picks'])} picks")
    if failed:
        print(f"{len(failed)} group(s) failed: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
