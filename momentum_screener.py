"""
Momentum screener — additive signal layer for all sector signal generators.

Thresholds (never downgrade existing signals):
  STRONG BUY  YTD ≥ 12.25%/mo (~100% at mo 6, ~300% at mo 12)  OR  1Y ≥ 500%
  BUY         YTD ≥  7.00%/mo (~50%  at mo 6, ~125% at mo 12)  OR  1Y ≥ 200%

Confidence:  min((metric / threshold) / 2, 1.0)  — best qualifying metric wins.
"""

import re
from datetime import datetime

SB_1Y = 500.0
B_1Y  = 200.0


def get_thresholds():
    m = datetime.now().month
    return (1.1225 ** m - 1) * 100, (1.07 ** m - 1) * 100


def parse_pct(s):
    try:
        return float(re.sub(r'[%*+\s]', '', str(s)))
    except (ValueError, TypeError):
        return 0.0


parse_ytd = parse_pct  # backwards-compat alias


def momentum_signal(ytd_pct, sb_ytd, b_ytd, y1_pct=0.0):
    """Return (signal, confidence) or (None, None).

    Triggers on YTD ≥ sb_ytd/b_ytd  OR  1Y ≥ SB_1Y/B_1Y.
    Confidence uses the best (highest ratio) qualifying metric.
    """
    is_sb = ytd_pct >= sb_ytd or y1_pct >= SB_1Y
    is_b  = ytd_pct >= b_ytd  or y1_pct >= B_1Y

    if is_sb:
        confs = []
        if ytd_pct >= sb_ytd: confs.append(ytd_pct / sb_ytd / 2)
        if y1_pct  >= SB_1Y:  confs.append(y1_pct  / SB_1Y  / 2)
        return 'strong_buy', min(max(confs), 1.0)
    if is_b:
        confs = []
        if ytd_pct >= b_ytd: confs.append(ytd_pct / b_ytd / 2)
        if y1_pct  >= B_1Y:  confs.append(y1_pct  / B_1Y  / 2)
        return 'buy', min(max(confs), 1.0)
    return None, None


def compute_momentum_picks(stocks, existing_tickers):
    """
    Returns (momentum_picks, upgrades).

    momentum_picks — list of pick dicts for stocks not already in the AI top-10
                     that qualify via momentum thresholds, sorted by confidence desc.
    upgrades       — dict {ticker: (signal, conf)} for stocks already in the AI
                     top-10 where momentum confidence is higher than the AI's.
    """
    sb_ytd, b_ytd = get_thresholds()
    momentum_picks = []
    upgrades = {}

    for s in stocks:
        ticker = s.get('ticker')
        if not ticker:
            continue

        ytd = parse_pct(s.get('change_ytd', ''))
        y1  = parse_pct(s.get('ret_1y', ''))
        signal, conf = momentum_signal(ytd, sb_ytd, b_ytd, y1)
        if not signal:
            continue

        drivers = []
        if ytd >= sb_ytd:
            drivers.append(f"YTD {s.get('change_ytd', '')} ≥ {round(sb_ytd, 1)}% SB")
        elif ytd >= b_ytd:
            drivers.append(f"YTD {s.get('change_ytd', '')} ≥ {round(b_ytd, 1)}% B")
        if y1 >= SB_1Y:
            drivers.append(f"1Y {s.get('ret_1y', '')} ≥ {SB_1Y:.0f}% SB")
        elif y1 >= B_1Y:
            drivers.append(f"1Y {s.get('ret_1y', '')} ≥ {B_1Y:.0f}% B")

        rationale_parts = []
        if ytd >= sb_ytd:
            rationale_parts.append(f"{s.get('change_ytd', '')} YTD")
        elif ytd >= b_ytd:
            rationale_parts.append(f"{s.get('change_ytd', '')} YTD")
        if y1 >= SB_1Y:
            rationale_parts.append(f"{s.get('ret_1y', '')} 1Y")
        elif y1 >= B_1Y:
            rationale_parts.append(f"{s.get('ret_1y', '')} 1Y")

        pick = {
            'ticker':     ticker,
            'signal':     signal,
            'confidence': round(conf, 3),
            'ytd':        s.get('change_ytd', ''),
            'ret_1y':     s.get('ret_1y', ''),
            'rationale':  (
                f"Momentum screener: {' + '.join(rationale_parts)} exceeds "
                f"{signal.replace('_', ' ')} threshold."
            ),
            'drivers':    drivers,
        }
        if ticker in existing_tickers:
            upgrades[ticker] = (signal, round(conf, 3))
        else:
            momentum_picks.append(pick)

    momentum_picks.sort(key=lambda x: x['confidence'], reverse=True)
    return momentum_picks, upgrades
