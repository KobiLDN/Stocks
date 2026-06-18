#!/usr/bin/env python3
"""
Generate the AI Top 10 Picks signals via OpenRouter (deepseek/deepseek-v4-flash).

Runs BOTH locally and in GitHub Actions (generate-signals.yml).

API key resolution (first found wins):
  1. OPENROUTER_API_KEY environment variable  ← used by GitHub Actions
  2. key.txt in the same directory            ← used for local runs
     (key.txt is gitignored — never committed)

Run locally:  python generate_signals_local.py
CI:           triggered by generate-signals.yml (weekly + workflow_dispatch)

Inputs:  prices.json   (written by update_prices.py / GitHub Actions)
Outputs: signals-local.json
         signals-local.js   (window.SIGNALS_DATA = {...})
"""

import json
import os
import re
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from momentum_screener import compute_momentum_picks

# ---- Configuration --------------------------------------------------------

ENDPOINT          = "https://openrouter.ai/api/v1/chat/completions"
MODEL             = "deepseek/deepseek-v4-flash"
INPUT_JSON        = "prices.json"
OUTPUT_JSON       = "signals-local.json"
OUTPUT_JS         = "signals-local.js"

TEMPERATURE       = 0.3
MAX_TOKENS        = 8192
REQUEST_TIMEOUT_S = (15, 120) # (connect_s, read_s) — 15s to connect, 120s to read
MAX_HEADLINES     = 1
TOP_N             = 10
RETRY_ON_BAD_JSON = 1


# ---- Key loading ----------------------------------------------------------

def load_api_key():
    """Try env var first (CI), then key.txt (local dev)."""
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        print("  API key: OPENROUTER_API_KEY env var")
        return key
    key_path = os.path.join(os.path.dirname(__file__), "key.txt")
    if os.path.exists(key_path):
        key = open(key_path, encoding="utf-8").read().strip()
        if key:
            print("  API key: key.txt")
            return key
    fail(
        "No OpenRouter API key found.\n"
        "  Locally: create key.txt with your key.\n"
        "  CI: add OPENROUTER_API_KEY to GitHub Actions secrets."
    )


# ---- Helpers --------------------------------------------------------------

def fail(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def first_json_object(text):
    """Find and return the first balanced JSON object substring, or None."""
    if not text:
        return None
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        c = text[i]
        if in_str:
            if esc:        esc = False
            elif c == "\\": esc = True
            elif c == '"':  in_str = False
        else:
            if c == '"':    in_str = True
            elif c == "{":  depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
    return None


def load_input():
    try:
        with open(INPUT_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        fail(f"{INPUT_JSON} not found. Run update_prices.py first.")
    except json.JSONDecodeError as e:
        fail(f"{INPUT_JSON} is not valid JSON: {e}")


def compact_stock(s):
    """Trim each stock to the fields the model actually needs."""
    news = (s.get("news") or [])[:MAX_HEADLINES]
    headline = (news[0].get("title") if news else None) or None
    return {
        "ticker":   s.get("ticker"),
        "cat":      s.get("category"),
        "price":    s.get("price_gbp"),
        "ret_1y":   s.get("return_1yr"),
        "ytd":      s.get("change_ytd"),
        "ch_1m":    s.get("change_1m"),
        "ch_1w":    s.get("change_1w"),
        "ch_1d":    s.get("change_1d"),
        "mc_gbp_b": s.get("market_cap_gbp_b"),
        "beta":     s.get("beta"),
        "pe":       s.get("pe_ratio"),
        "div_pct":  s.get("div_yield_pct"),
        "short":    s.get("short_pct"),
        "analyst":  s.get("analyst"),
        "an_score": s.get("analyst_score"),
        "news_s":   s.get("news_sentiment"),
        "headline": headline,
    }


SYSTEM_PROMPT = """You are an investment research assistant analysing a curated universe of AI infrastructure stocks for a UK-based research dashboard. Output is for informational and educational purposes only — NOT financial advice.

You will be given a JSON snapshot of every tracked stock: prices in GBP, year-to-date and 1-year returns, short-term momentum (1D/1W/1M %), fundamentals (market cap in £B, beta, P/E, dividend yield, short interest %, analyst recommendation and score), recent news headlines and an aggregate news sentiment score in [-1, +1].

Before ranking, use web search to find the latest news, analyst upgrades, earnings surprises, or deal announcements for the highest-momentum stocks listed in the user prompt. Use what you find to enrich your rationale with live catalysts.

Pick the 10 most attractive stocks RIGHT NOW based on a BALANCED view of:
  - Momentum (recent 1D/1W/1M moves, YTD)
  - Fundamentals (P/E, market cap, beta — avoid extreme over-extension)
  - Analyst consensus (strong_buy / buy weighted positively, sell weighted negatively)
  - News sentiment and any live catalysts found via web search

Rank them 1 (best) to 10. Use the "signal" field to distinguish strong_buy from buy where appropriate. Confidence is your subjective certainty in [0, 1].

Output ONLY a single JSON object with this EXACT shape:
{
  "picks": [
    {
      "rank": 1,
      "ticker": "<must be one of the input tickers>",
      "signal": "strong_buy" | "buy",
      "confidence": 0.0,
      "rationale": "1-2 sentences citing specific numbers from the input (e.g. '+45% YTD, P/E 22, positive news sentiment 0.32')",
      "drivers": ["short metric phrase", "short metric phrase"]
    }
  ]
}

Hard rules:
- Exactly 10 picks, ranks 1 through 10, no duplicates.
- Use ONLY tickers present in the input.
- "rationale" must cite at least one concrete number from the input.
- "drivers" is a list of 2-4 short metric phrases that drove the rank.
- Output ONLY the JSON object — no prose, no markdown fences, no explanation.
"""


def build_user_prompt(stocks):
    # Identify top 10 by 1M momentum for targeted web search
    def parse_pct(v):
        try:
            return float(str(v).replace('%', '').replace('+', ''))
        except Exception:
            return 0.0

    top_momentum = sorted(
        stocks,
        key=lambda s: parse_pct(s.get('change_1m', '0')),
        reverse=True
    )[:10]
    search_tickers = ', '.join(s['ticker'] for s in top_momentum)

    payload = {"stocks": [compact_stock(s) for s in stocks]}
    return (
        f"Search for the latest news on these high-momentum tickers before ranking: {search_tickers}.\n\n"
        "Stock universe snapshot follows as compact JSON. "
        "Field keys: cat=category, ret_1y=1-year return, ytd=YTD %, "
        "ch_1m/1w/1d=% change, mc_gbp_b=market cap in GBP billions, "
        "pe=trailing P/E, div_pct=dividend yield %, short=short interest %, "
        "an_score=analyst recommendation mean (lower=more bullish), "
        "news_s=aggregate news sentiment in [-1,+1], headline=latest headline. "
        f"Return your top {TOP_N} picks.\n\n"
        + json.dumps(payload, separators=(",", ":"))
    )


# ---- API call -------------------------------------------------------------

def call_api(api_key, system_prompt, user_prompt):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json",
        "HTTP-Referer":  "https://kobildn.github.io/aiSTOCKS/",
        "X-Title":       "AI Stocks Dashboard - Signals",
    }
    body = {
        "model":           MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "temperature":     TEMPERATURE,
        "max_tokens":      MAX_TOKENS,
        "response_format": {"type": "json_object"},
        "stream":          False,
        "plugins":         [{"id": "web", "max_results": 5}],
    }

    print(f"  POST {ENDPOINT}  ({MODEL})")
    t0 = time.time()
    try:
        r = requests.post(
            ENDPOINT,
            headers=headers,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            timeout=REQUEST_TIMEOUT_S,
        )
    except requests.exceptions.ConnectionError:
        fail("Could not connect to OpenRouter. Check internet connection.")
    except requests.exceptions.Timeout:
        fail(f"Request timed out after {REQUEST_TIMEOUT_S[1]}s read / {REQUEST_TIMEOUT_S[0]}s connect.")

    dt = time.time() - t0
    print(f"  HTTP {r.status_code}  ({dt:.1f}s)")

    if r.status_code != 200:
        fail(f"OpenRouter returned {r.status_code}: {r.text[:500]}")

    data   = r.json()
    usage  = data.get("usage", {})
    in_tok = usage.get("prompt_tokens", 0)
    out_tok= usage.get("completion_tokens", 0)
    finish = data["choices"][0].get("finish_reason")
    print(f"  finish={finish}  in={in_tok}  out={out_tok}  "
          f"est. cost=${(in_tok*0.15 + out_tok*0.60)/1_000_000:.5f}")

    content = data["choices"][0]["message"].get("content", "").strip()
    if not content:
        fail("Empty response from model.")
    return content


# ---- Parse & validate -----------------------------------------------------

def parse_picks(content, valid_tickers):
    candidate = first_json_object(content) or content
    try:
        obj = json.loads(candidate)
    except json.JSONDecodeError as e:
        raise ValueError(f"Not valid JSON: {e}\n---raw---\n{content[:600]}")

    picks = obj.get("picks")
    if not isinstance(picks, list) or not picks:
        raise ValueError("Missing or empty 'picks' array.")
    if len(picks) != TOP_N:
        raise ValueError(f"Expected {TOP_N} picks, got {len(picks)}.")

    seen = set()
    cleaned = []
    for i, p in enumerate(picks, 1):
        if not isinstance(p, dict):
            raise ValueError(f"Pick {i} is not an object.")
        t = p.get("ticker")
        if t not in valid_tickers:
            raise ValueError(f"Pick {i} ticker {t!r} not in universe.")
        if t in seen:
            raise ValueError(f"Duplicate ticker {t!r} at rank {i}.")
        seen.add(t)

        signal = (p.get("signal") or "").lower()
        if signal not in ("strong_buy", "buy"):
            signal = "buy"  # normalise unexpected values (e.g. 'hold', 'none')

        try:
            conf = float(p.get("confidence", 0))
        except (TypeError, ValueError):
            conf = 0.0
        conf = max(0.0, min(1.0, conf))

        drivers = p.get("drivers") or []
        if not isinstance(drivers, list):
            drivers = []
        drivers = [str(d).strip() for d in drivers if str(d).strip()][:5]

        cleaned.append({
            "rank":       i,
            "ticker":     t,
            "signal":     signal,
            "confidence": round(conf, 3),
            "rationale":  (p.get("rationale") or "").strip(),
            "drivers":    drivers,
        })

    return cleaned


# ---- Write outputs --------------------------------------------------------

def write_outputs(picks, stocks, now_str):
    # Carry forward previous picks so the UI can show rank deltas
    previous_picks = []
    if os.path.exists(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
                old = json.load(f)
                previous_picks = old.get("picks") or []
        except Exception:
            pass

    # --- momentum post-processing (additive — never downgrades AI signals) ---
    existing_tickers = {p['ticker'] for p in picks}
    momentum_picks, upgrades = compute_momentum_picks(stocks, existing_tickers)
    for p in picks:
        if p['ticker'] in upgrades:
            m_signal, m_conf = upgrades[p['ticker']]
            if m_conf > p['confidence']:
                p['confidence'] = m_conf
            if m_signal == 'strong_buy' and p['signal'] == 'buy':
                p['signal'] = 'strong_buy'

    out = {
        "updated":        now_str,
        "model":          MODEL,
        "endpoint":       ENDPOINT,
        "source":         "openrouter",
        "picks":          picks,
        "momentum_picks": momentum_picks,
        "previous_picks": previous_picks,
    }
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    with open(OUTPUT_JS, "w", encoding="utf-8") as f:
        f.write(f"window.SIGNALS_DATA = {json.dumps(out, indent=2)};\n")
    print(f"  wrote {OUTPUT_JSON} and {OUTPUT_JS}")


# ---- Main -----------------------------------------------------------------

def main():
    api_key = load_api_key()

    print(f"\nLoading {INPUT_JSON}...")
    snapshot = load_input()
    stocks = snapshot.get("stocks") or []
    if not stocks:
        fail("No stocks in input snapshot.")
    valid_tickers = {s.get("ticker") for s in stocks}
    print(f"  {len(stocks)} stocks, snapshot updated {snapshot.get('updated')}")

    system_prompt = SYSTEM_PROMPT
    user_prompt   = build_user_prompt(stocks)

    last_err = None
    for attempt in range(1 + RETRY_ON_BAD_JSON):
        print(f"\nAttempt {attempt + 1}: requesting top {TOP_N} picks...")
        content = call_api(api_key, system_prompt, user_prompt)
        try:
            picks = parse_picks(content, valid_tickers)
            break
        except ValueError as e:
            print(f"  parse failed: {e}")
            last_err = e
            system_prompt = (
                SYSTEM_PROMPT
                + "\n\nIMPORTANT: Previous reply was not valid. "
                  "Reply with ONLY the JSON object, no prose, no markdown."
            )
    else:
        fail(f"Could not get valid signals after {1 + RETRY_ON_BAD_JSON} attempts.\n"
             f"Last error: {last_err}")

    now_str = datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%d %H:%M")
    write_outputs(picks, stocks, now_str)

    print("\nTop 10 picks:")
    for p in picks:
        print(f"  {p['rank']:>2}. {p['ticker']:<6}  {p['signal']:<10}  "
              f"conf {p['confidence']:.2f}  | {p['rationale'][:80]}")
    print("\nDone.")


if __name__ == "__main__":
    main()
