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
