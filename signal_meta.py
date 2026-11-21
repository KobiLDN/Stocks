"""Tags written on every signal run, so the track record can compare versions fairly (#70).

variant        which signal recipe made the run. Bump it whenever the recipe changes on purpose.
                 live-1  up to 21 Nov 2026: AI label, upgraded to strong_buy by the momentum screen
                 live-2  from 21 Nov 2026: AI label only (momentum upgrade removed, #70)
prompt_version short hash of the system prompt + the user-prompt builder, so silent prompt edits show up
code_commit    the commit the bot ran on (GITHUB_SHA in Actions)
input_version  the input data contract; 2026-11-11 = market caps / yields fixed (PR #61)
"""
import hashlib
import inspect
import os

VARIANT = "live-2"
INPUT_VERSION = "2026-11-11"


def run_meta(system_prompt, user_prompt_builder):
    src = system_prompt + inspect.getsource(user_prompt_builder)
    return {
        "variant": VARIANT,
        "prompt_version": hashlib.sha256(src.encode("utf-8")).hexdigest()[:12],
        "code_commit": (os.environ.get("GITHUB_SHA") or "")[:12] or None,
        "input_version": INPUT_VERSION,
    }


def annotate_momentum(picks, upgrades):
    """Record what the momentum screen thinks of each AI pick, without changing the AI's label.

    pre_momentum_label   the AI's own label
    post_momentum_label  the label published (the same since live-2: no upgrade)
    momentum_label       what the screen would have said (strong_buy / buy), or None if it doesn't flag the stock
    momentum_score       the screen's score (how far past its threshold), or None
    """
    for p in picks:
        m = upgrades.get(p["ticker"])
        p["pre_momentum_label"] = p["signal"]
        p["post_momentum_label"] = p["signal"]
        p["momentum_label"] = m[0] if m else None
        p["momentum_score"] = round(m[1], 3) if m else None
    return picks


# ── Shadow trial (#92) ────────────────────────────────────────────────────────
# A second prompt run quietly next to the live one: same model, inputs and time, stored but never shown,
# exported or counted in the live track record. Decided by the frozen rule in #92 on 20 Feb 2027.
SHADOW_VARIANT = "shadow-runup-1"
SHADOW_FILE = "signals-shadow.json"
SHADOW_ADDENDUM = (
    "\n\nBe wary of stocks that have risen sharply over the past month (roughly +15% or more in 1M). "
    "On this dashboard's own track record, picks made straight after a big one-month run-up have tended to give "
    "the gains back over the next 1-3 months. Only include such a stock if there is a specific, recent fundamental "
    "reason that is not already in the price, and name the run-up as a risk in the rationale. "
    "Do not favour a stock just because it has strong recent momentum."
)
JSON_ONLY_HINT = "\n\nIMPORTANT: Previous reply was not valid. Reply with ONLY the JSON object, no prose, no markdown."


def run_shadow(api_key, call_api, parse_picks, system_prompt, user_prompt_builder, user_prompt,
               valid_tickers, stocks, now_str, model, out_dir="."):
    """Make and save the shadow picks. Never raises: a failed shadow run must not affect the live one."""
    import json
    from momentum_screener import compute_momentum_picks
    prompt = system_prompt + SHADOW_ADDENDUM
    try:
        picks = None
        for attempt in range(2):
            try:
                picks = parse_picks(call_api(api_key, prompt + (JSON_ONLY_HINT if attempt else ""), user_prompt), valid_tickers)
                break
            except ValueError as e:
                print(f"  shadow attempt {attempt + 1} failed: {e}")
        if picks is None:
            print("  shadow run skipped (no valid reply)")
            return None
        _mom, upgrades = compute_momentum_picks(stocks, {p["ticker"] for p in picks})
        annotate_momentum(picks, upgrades)
        meta = run_meta(prompt, user_prompt_builder)
        meta["variant"] = SHADOW_VARIANT
        out = {"updated": now_str, "model": model, **meta, "shadow_of": VARIANT, "picks": picks}
        path = os.path.join(out_dir, SHADOW_FILE)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(f"  shadow ({SHADOW_VARIANT}): wrote {path}")
        return out
    except BaseException as e:          # includes fail() -> SystemExit from call_api
        if isinstance(e, KeyboardInterrupt):
            raise
        print(f"  shadow run skipped: {e!r}")
        return None
