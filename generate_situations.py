#!/usr/bin/env python3
"""Situations: stocks with an unresolved event that could move the price a lot, with the AI's odds.

    python generate_situations.py              # after each price run (generate-situations.yml)
    python generate_situations.py --dry-run    # show the candidates, no AI call, nothing written

Not a prediction of which way a stock goes. It flags *situations* (a leadership fight, a takeover bid,
a regulator's or court's decision, a trial readout, results due) and asks the AI, for each one, which
outcomes are possible, how likely each is, and roughly how far the share price would move if it
happened. Every first flag is logged with that day's price (situations/flags.json) and scored 30 days
later in the track record against how often any stock moved that much, so the odds can be checked.

Candidates (no AI call): stocks whose headlines from the last NEWS_DAYS days mention a pending event
(EVENT_WORDS), or that moved a lot (1 day / 1 month) while in the news, plus every situation still open
from the last run. Input files: All/all-data.js (prices, sector, themes) and All/news-data.js
(headlines), both written by update_group_prices.py.
Output: situations/situations-data.js (window.SITUATIONS_DATA, read by situations.html),
situations/situations.json (the same, for the next run) and situations/flags.json (append-only log).
"""
import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "situations")
LONDON = ZoneInfo("Europe/London")

NEWS_DAYS = 4                  # headlines this recent count
MAX_CANDIDATES = 60
BATCH = 15                     # stocks per AI call
WORKERS = 4
KEEP_DAYS = 3                  # an open situation not re-flagged for this long drops off the page
BIG = 10.0                     # a "big move": 10% or more either way within a month
TYPES = ["leadership", "takeover", "regulatory", "legal", "trial", "results", "product", "policy",
         "financing", "activist", "other"]
TYPE_LABEL = {"leadership": "Leadership", "takeover": "Takeover / merger", "regulatory": "Regulator decision",
              "legal": "Court / legal", "trial": "Trial / approval", "results": "Results / guidance",
              "product": "Product / contract", "policy": "Government policy", "financing": "Debt / financing",
              "activist": "Activist investor", "other": "Other"}

# Words in a headline that suggest something is still to be decided (lower case, matched on word starts)
EVENT_WORDS = [
    "ceo", "chief executive", "resign", "steps down", "ousted", "fired", "succession", "reinstat", "board",
    "takeover", "acquisition", "acquire", "merger", "bid", "offer for", "buyout", "deal talks", "in talks",
    "approval", "fda", "ema", "regulator", "antitrust", "probe", "investigation", "sec ", "doj",
    "lawsuit", "court", "ruling", "verdict", "settlement", "trial", "phase 3", "phase iii", "data readout",
    "guidance", "profit warning", "earnings", "results", "downgrade", "upgrade", "export", "ban", "tariff",
    "sanction", "strike", "recall", "bankrupt", "restructur", "spin-off", "spinoff", "activist", "stake",
    "rights issue", "dividend cut", "short seller", "delist",
]
_WORD_RE = re.compile(r"\b(" + "|".join(re.escape(w.strip()) for w in EVENT_WORDS) + r")", re.I)


def read_js(path, name):
    """window.NAME = {...}; -> dict (or None)."""
    try:
        raw = open(path, encoding="utf-8").read()
    except OSError:
        return None
    m = re.match(r"\s*window\." + name + r"\s*=\s*", raw)
    return json.loads(raw[m.end():].strip().rstrip(";")) if m else None


def pct(v):
    try:
        return float(str(v).replace("%", "").replace("+", ""))
    except (TypeError, ValueError):
        return None


# ── candidates ────────────────────────────────────────────────────────────────
def recent(news, now, days=NEWS_DAYS):
    cut = (now - timedelta(days=days)).timestamp()
    return [n for n in news or [] if (n.get("published") or 0) >= cut and n.get("title")]


def candidates(stocks, news_by_ticker, open_tickers, now, limit=MAX_CANDIDATES):
    """[(score, ticker)] best first. Score: event words in recent headlines, plus big recent moves."""
    out = []
    for t, s in stocks.items():
        heads = recent(news_by_ticker.get(t), now)
        hits = sum(len(_WORD_RE.findall(n["title"])) for n in heads)
        d1, m1 = abs(pct(s.get("change_1d")) or 0), abs(pct(s.get("change_1m")) or 0)
        score = hits * 2 + (3 if heads and d1 >= 8 else 0) + (2 if heads and m1 >= 15 else 0)
        if t in open_tickers:
            score += 10                                 # always re-check what is still open
        if score > 0 and (heads or t in open_tickers):
            out.append((score, t))
    out.sort(key=lambda x: (-x[0], x[1]))
    return out[:limit]


# ── AI ────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""You review stocks for PENDING SITUATIONS: a specific event that has not been decided yet
and could move the share price by {BIG:.0f}% or more within about a month. Types: {", ".join(TYPES)}.
Examples: a CEO's future in doubt, a takeover bid not yet accepted, a regulator or court decision due,
a drug trial readout due, results or guidance due within two weeks after a big run, an export ban under review.

For each stock you are given its recent moves and headlines (and you may search the web). Include a stock
ONLY if there is a genuinely unresolved event. Skip news that is already decided and priced in, unless a
follow-on decision is still pending. Skip general market commentary. Most stocks you see should be skipped.

For each situation give 2 to 4 OUTCOMES that cover what could happen, each with:
  - probability (0 to 1; they must add up to 1),
  - move_pct: your estimate of the share price move over the next month if that outcome happens
    (for example +25, -15, +2). Use the stock's own history and similar past events; be calibrated:
    many events move a stock much less than headlines suggest.
Do not guess which outcome will happen beyond these probabilities. Plain English, no hype.

Reply with ONLY this JSON:
{{"situations": [{{"ticker": "...", "type": "one of the types", "title": "under 80 characters",
  "summary": "under 240 characters: what is unresolved and why it matters",
  "key_date": "YYYY-MM-DD or null (when it should be decided, if known)",
  "outcomes": [{{"label": "under 60 characters", "probability": 0.0, "move_pct": 0.0}}]}}]}}
An empty list is a fine answer."""


def user_prompt(batch, stocks, news_by_ticker, now):
    lines = [f"Today is {now.astimezone(LONDON):%d %b %Y}. Stocks to review:"]
    for t in batch:
        s = stocks[t]
        lines.append(f"\n{t} | {s.get('company_name') or t} | {s.get('sector') or 'Crypto'} | price ${s.get('price_usd')} | "
                     f"1D {s.get('change_1d')} 1W {s.get('change_1w')} 1M {s.get('change_1m')} YTD {s.get('change_ytd')}")
        for n in sorted(recent(news_by_ticker.get(t), now), key=lambda n: -(n.get("published") or 0))[:6]:
            day = datetime.fromtimestamp(n["published"], timezone.utc).strftime("%d %b")
            lines.append(f"  - {day}: {n['title']}")
    return "\n".join(lines)


def clean(obj, allowed):
    """AI reply -> valid situations. Bad ones are dropped one by one, never the whole reply."""
    out = []
    for s in (obj or {}).get("situations") or []:
        if not isinstance(s, dict) or s.get("ticker") not in allowed:
            continue
        outs = []
        for o in s.get("outcomes") or []:
            try:
                p, m = float(o.get("probability")), float(o.get("move_pct"))
            except (TypeError, ValueError, AttributeError):
                continue
            if p > 0 and str(o.get("label") or "").strip():
                outs.append({"label": str(o["label"]).strip()[:80], "probability": p, "move_pct": max(-95.0, min(300.0, m))})
        if not 2 <= len(outs) <= 4:
            continue
        total = sum(o["probability"] for o in outs)
        for o in outs:
            o["probability"] = round(o["probability"] / total, 3)
        kd = s.get("key_date")
        kd = kd if isinstance(kd, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", kd) else None
        typ = s.get("type") if s.get("type") in TYPES else "other"
        out.append({"ticker": s["ticker"], "type": typ, "title": str(s.get("title") or "").strip()[:100],
                    "summary": str(s.get("summary") or "").strip()[:300], "key_date": kd,
                    "outcomes": sorted(outs, key=lambda o: -o["probability"]), **odds(outs)})
    return out


def odds(outcomes):
    """What the outcomes add up to: chance of a big move, chance it goes up, expected move, the lean."""
    p_big = sum(o["probability"] for o in outcomes if abs(o["move_pct"]) >= BIG)
    p_up = sum(o["probability"] for o in outcomes if o["move_pct"] > 0)
    exp = sum(o["probability"] * o["move_pct"] for o in outcomes)
    lean = "up" if p_up >= 0.6 else "down" if p_up <= 0.4 else "either way"
    return {"p_big": round(p_big, 3), "p_up": round(p_up, 3), "expected_move": round(exp, 1), "lean": lean}


def ask(batch, stocks, news_by_ticker, now, call):
    from generate_group_signals import first_json_object
    content = call(SYSTEM_PROMPT, user_prompt(batch, stocks, news_by_ticker, now))
    try:
        obj = json.loads(first_json_object(content) or content)
    except json.JSONDecodeError:
        print(f"  batch {batch[0]}..: reply was not JSON, skipped")
        return []
    return clean(obj, set(batch))


# ── state ─────────────────────────────────────────────────────────────────────
def merge(previous, found, stocks, now):
    """Carry `first_flagged` and the price on that day forward; drop situations not seen for KEEP_DAYS.
    Returns (current situations, new first flags for the log)."""
    today = now.astimezone(LONDON).date().isoformat()
    prev = {f"{s['ticker']}:{s['type']}": s for s in previous}
    current, new_flags = {}, []
    for s in found:
        sid = f"{s['ticker']}:{s['type']}"
        old = prev.get(sid)
        price = (stocks.get(s["ticker"]) or {}).get("price_usd")
        first = old["first_flagged"] if old else today
        current[sid] = {**s, "id": sid, "first_flagged": first, "last_seen": today,
                        "price_at_flag": old.get("price_at_flag") if old else price}
        if not old:
            new_flags.append({"id": sid, "date": today, "ticker": s["ticker"], "type": s["type"],
                              "price_usd": price, "p_big": s["p_big"], "p_up": s["p_up"],
                              "expected_move": s["expected_move"], "lean": s["lean"]})
    for sid, old in prev.items():
        if sid not in current and (datetime.fromisoformat(today) - datetime.fromisoformat(old["last_seen"])).days < KEEP_DAYS:
            current[sid] = old                              # not re-flagged this run: keep it for a few days
    order = sorted(current.values(), key=lambda s: (-s["p_big"], -abs(s["expected_move"]), s["ticker"]))
    return order, new_flags


def write(situations, flags_log, now, model):
    os.makedirs(OUT, exist_ok=True)
    data = {"updated": now.astimezone(LONDON).strftime("%Y-%m-%d %H:%M"), "model": model, "big_move_pct": BIG,
            "type_labels": TYPE_LABEL, "count": len(situations), "situations": situations}
    with open(os.path.join(OUT, "situations.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(OUT, "situations-data.js"), "w", encoding="utf-8") as f:
        f.write(f"window.SITUATIONS_DATA = {json.dumps(data, separators=(',', ':'), ensure_ascii=False)};\n")
    with open(os.path.join(OUT, "flags.json"), "w", encoding="utf-8") as f:
        json.dump(flags_log, f, indent=0, ensure_ascii=False)
        f.write("\n")


def load_json(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return default


def main(argv=None, call=None, now=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    now = now or datetime.now(timezone.utc)

    all_data = read_js(os.path.join(ROOT, "All", "all-data.js"), "ALL_DATA") or {}
    news_data = read_js(os.path.join(ROOT, "All", "news-data.js"), "NEWS_DATA") or {}
    stocks = {s["ticker"]: s for s in all_data.get("stocks") or []}
    news_by_ticker = {s["ticker"]: s.get("news") for s in news_data.get("stocks") or []}
    previous = load_json(os.path.join(OUT, "situations.json"), {}).get("situations") or []
    open_tickers = {s["ticker"] for s in previous}
    cands = [t for _, t in candidates(stocks, news_by_ticker, open_tickers, now) if t in stocks]
    print(f"{len(stocks)} stocks, {len(news_by_ticker)} with headlines → {len(cands)} candidates: {', '.join(cands[:25])}"
          f"{' …' if len(cands) > 25 else ''}")
    if args.dry_run or not cands:
        return 0

    from generate_group_signals import MODEL
    if call is None:
        from generate_group_signals import call_api, load_api_key
        key = load_api_key()
        call = lambda sp, up: call_api(key, sp, up, "Situations")
    batches = [cands[i:i + BATCH] for i in range(0, len(cands), BATCH)]
    found, failed = [], 0
    with ThreadPoolExecutor(WORKERS) as ex:
        for got in ex.map(lambda b: _safe(ask, b, stocks, news_by_ticker, now, call), batches):
            if got is None:
                failed += 1
            else:
                found += got
    if failed == len(batches):
        print("ERROR: every AI call failed; the previous situations are kept")
        return 1
    situations, new_flags = merge(previous, found, stocks, now)
    log = load_json(os.path.join(OUT, "flags.json"), []) + new_flags
    write(situations, log, now, MODEL)
    print(f"{len(found)} situations this run ({len(new_flags)} new), {len(situations)} on the page; "
          f"{failed} of {len(batches)} AI calls failed")
    for s in situations[:15]:
        print(f"  {s['ticker']:7} {s['type']:11} big move {s['p_big']:.0%}  lean {s['lean']:10} {s['title']}")
    return 0


def _safe(fn, *a):
    try:
        return fn(*a)
    except Exception as e:                 # one failed batch must not lose the others
        print(f"  AI call failed: {e}")
        return None


if __name__ == "__main__":
    sys.exit(main())
