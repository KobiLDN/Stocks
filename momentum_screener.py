"""
Momentum screener — additive signal layer for all sector signal generators.

Computes monthly-compounding YTD thresholds and produces:
  - momentum_picks: stocks NOT in the AI top-10 that qualify via momentum
  - upgrades:       {ticker: (signal, conf)} for AI picks where momentum is higher

Thresholds (never downgrade existing signals):
  STRONG BUY  12.25%/mo  →  ~100% at month 6,  ~300% at month 12
  BUY          7.00%/mo  →  ~50%  at month 6,  ~125% at month 12

Confidence:  min((ytd / threshold) / 2, 1.0)
"""

import re
from datetime import datetime


def get_thresholds():
    m = datetime.now().month
    return (1.1225 ** m - 1) * 100, (1.07 ** m - 1) * 100


def parse_ytd(s):
    try:
        return float(re.sub(r'[%*+\s]', '', str(s)))
    except (ValueError, TypeError):
        return 0.0


def momentum_signal(ytd_pct, sb_thresh, b_thresh):
    """Return (signal, confidence) or (None, None)."""
    if ytd_pct >= sb_thresh:
        return 'strong_buy', min((ytd_pct / sb_thresh) / 2, 1.0)
    if ytd_pct >= b_thresh:
        return 'buy', min((ytd_pct / b_thresh) / 2, 1.0)
    return None, None


def compute_momentum_picks(stocks, existing_tickers):
    """
    Returns (momentum_picks, upgrades).

    momentum_picks — list of pick dicts for stocks not already in the AI top-10
                     that qualify via the YTD momentum thresholds, sorted by
                     confidence descending.
    upgrades       — dict {ticker: (signal, conf)} for stocks already in the AI
                     top-10 where the momentum confidence is higher than the AI's.
                     Callers should only apply an upgrade, never a downgrade.
    """
    sb_thresh, b_thresh = get_thresholds()
    momentum_picks = []
    upgrades = {}

    for s in stocks:
        ticker = s.get('ticker')
        if not ticker:
            continue
        ytd = parse_ytd(s.get('change_ytd', ''))
        signal, conf = momentum_signal(ytd, sb_thresh, b_thresh)
        if not signal:
            continue
        thresh = sb_thresh if signal == 'strong_buy' else b_thresh
        if ticker in existing_tickers:
            upgrades[ticker] = (signal, round(conf, 3))
        else:
            momentum_picks.append({
                'ticker':     ticker,
                'signal':     signal,
                'confidence': round(conf, 3),
                'ytd':        s.get('change_ytd', ''),
                'rationale':  (
                    f"Momentum screener: {s.get('change_ytd', '')} YTD exceeds "
                    f"{signal.replace('_', ' ')} threshold "
                    f"({round(thresh, 1)}%)."
                ),
                'drivers': [
                    f"YTD {s.get('change_ytd', '')}",
                    f"Threshold {round(thresh, 1)}%",
                ],
            })

    momentum_picks.sort(key=lambda x: x['confidence'], reverse=True)
    return momentum_picks, upgrades
