"""
Trading 212 MCP Server — exposes T212 portfolio as tools for Claude Code.

Setup:
  1. pip install -r t212_mcp/requirements.txt
  2. Put your T212 API key in t212_mcp/.key  (gitignored)
     OR set env var T212_API_KEY
  3. MCP server is configured in .claude/settings.json — reload the session.

Tools exposed:
  get_positions        — all open positions with quantity, avg price, P&L
  get_account_summary  — total value, free cash, invested, overall P&L
  get_orders           — recent order history (last 50)
  get_portfolio_vs_signals — positions cross-referenced against site signal picks
"""

import os, json, re, sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import httpx

# ── API key resolution ────────────────────────────────────────────────────────
_KEY_FILE = Path(__file__).parent / ".key"
API_KEY   = _KEY_FILE.read_text().strip() if _KEY_FILE.exists() else os.getenv("T212_API_KEY", "")
BASE_URL  = "https://live.trading212.com/api/v0"
REPO_ROOT = Path(__file__).parent.parent

mcp = FastMCP("Trading 212")

# ── HTTP helper ───────────────────────────────────────────────────────────────
def t212(endpoint: str):
    if not API_KEY:
        raise RuntimeError("T212_API_KEY not set. Add it to t212_mcp/.key or set the env var.")
    r = httpx.get(f"{BASE_URL}{endpoint}", headers={"Authorization": API_KEY}, timeout=15)
    r.raise_for_status()
    return r.json()

def clean_ticker(t212_ticker: str) -> str:
    """'AAPL_US_EQ' → 'AAPL',  'SHEL_EQ' → 'SHEL'"""
    return re.split(r'_', t212_ticker)[0]

# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_positions() -> str:
    """
    All open portfolio positions from Trading 212.
    Returns ticker, quantity, average open price, current price, and P&L (in account currency).
    """
    raw = t212("/equity/portfolio")
    positions = []
    for p in raw:
        positions.append({
            "ticker":        clean_ticker(p.get("ticker", "")),
            "t212_ticker":   p.get("ticker"),
            "quantity":      p.get("quantity"),
            "avg_price":     p.get("averagePrice"),
            "current_price": p.get("currentPrice"),
            "ppl":           p.get("ppl"),         # profit/loss in account currency
            "fx_ppl":        p.get("fxPpl"),
            "total_value":   round((p.get("quantity") or 0) * (p.get("currentPrice") or 0), 2),
        })
    positions.sort(key=lambda x: (x["total_value"] or 0), reverse=True)
    return json.dumps(positions, indent=2)


@mcp.tool()
def get_account_summary() -> str:
    """
    Account-level summary: total portfolio value, free cash, amount invested, and overall P&L.
    """
    cash = t212("/equity/account/cash")
    info = t212("/equity/account/info")
    return json.dumps({
        "currency":       info.get("currencyCode"),
        "total_value":    cash.get("total"),
        "invested":       cash.get("invested"),
        "free_cash":      cash.get("free"),
        "total_ppl":      cash.get("result"),
        "blocked":        cash.get("blocked"),
        "pie_cash":       cash.get("pieCash"),
    }, indent=2)


@mcp.tool()
def get_orders() -> str:
    """
    Last 50 executed orders (buys and sells) from Trading 212.
    """
    raw = t212("/equity/orders")
    return json.dumps(raw, indent=2)


@mcp.tool()
def get_portfolio_vs_signals() -> str:
    """
    Cross-references your T212 holdings against the site's AI signal picks across all sectors.
    Shows: which of your holdings have a signal, their rank and confidence, and current P&L.
    Also highlights signal picks you DON'T hold yet.
    """
    # Load positions
    raw_positions = t212("/equity/portfolio")
    held = {}
    for p in raw_positions:
        ticker = clean_ticker(p.get("ticker", ""))
        held[ticker] = {
            "quantity":    p.get("quantity"),
            "avg_price":   p.get("averagePrice"),
            "ppl":         p.get("ppl"),
            "total_value": round((p.get("quantity") or 0) * (p.get("currentPrice") or 0), 2),
        }

    # Load signals from all sectors
    sectors = ["AI", "Biotech", "Crypto", "Defence", "Energy", "Tech"]
    all_picks = []
    for sector in sectors:
        sig_path = REPO_ROOT / sector / "signals-local.json"
        if not sig_path.exists():
            continue
        try:
            data = json.loads(sig_path.read_text())
            for p in data.get("picks", []):
                p["sector"] = sector
                all_picks.append(p)
        except Exception:
            pass

    # Cross-reference
    held_with_signal, signals_not_held = [], []
    tickers_with_signal = set()

    for pick in all_picks:
        ticker = pick["ticker"]
        tickers_with_signal.add(ticker)
        if ticker in held:
            held_with_signal.append({
                "ticker":     ticker,
                "sector":     pick["sector"],
                "signal":     pick["signal"],
                "rank":       pick["rank"],
                "confidence": pick.get("confidence"),
                "rationale":  pick.get("rationale", ""),
                **held[ticker],
            })
        else:
            signals_not_held.append({
                "ticker":     ticker,
                "sector":     pick["sector"],
                "signal":     pick["signal"],
                "rank":       pick["rank"],
                "confidence": pick.get("confidence"),
                "rationale":  pick.get("rationale", ""),
            })

    held_no_signal = [
        {"ticker": t, **v}
        for t, v in held.items()
        if t not in tickers_with_signal
    ]

    return json.dumps({
        "summary": {
            "total_positions":        len(held),
            "positions_with_signal":  len(held_with_signal),
            "positions_without_signal": len(held_no_signal),
            "signal_picks_not_held":  len(signals_not_held),
        },
        "your_holdings_with_signal":    held_with_signal,
        "your_holdings_without_signal": held_no_signal,
        "signal_picks_you_dont_hold":   signals_not_held,
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
