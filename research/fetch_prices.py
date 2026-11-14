"""Research only: 5 years of daily OHLCV for every universe asset + SPY, for the trader-rule backtest.

Runs in GitHub Actions on the research/* branch (Yahoo isn't reachable from the dev sandbox).
Prices are auto-adjusted (splits + dividends), so returns are total returns.
Output: research/data/prices-5y.csv.gz  (date, symbol, open, high, low, close, volume)
"""
import os, time, yaml, pandas as pd, yfinance as yf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
u = yaml.safe_load(open(os.path.join(ROOT, "universe.yaml"), encoding="utf-8"))
ids = sorted({t for s in u["sectors"].values() for t, _ in s})
syms = sorted({u["assets"][t]["yahoo"] for t in ids} | {"SPY"})
frames = []
for i in range(0, len(syms), 40):
    batch = syms[i:i + 40]
    for attempt in range(3):
        d = yf.download(batch, period="5y", interval="1d", auto_adjust=True, progress=False, group_by="ticker", threads=True)
        if not d.empty:
            break
        time.sleep(10)
    for s in batch:
        if s not in d.columns.get_level_values(0):
            print("missing", s); continue
        x = d[s].dropna(subset=["Close"]).reset_index()
        x.columns = [c.lower() for c in x.columns]
        x["symbol"] = s
        frames.append(x[["date", "symbol", "open", "high", "low", "close", "volume"]])
    print(f"{i + len(batch)}/{len(syms)}")
out = pd.concat(frames)
os.makedirs(os.path.join(ROOT, "research", "data"), exist_ok=True)
out.to_csv(os.path.join(ROOT, "research", "data", "prices-5y.csv.gz"), index=False, float_format="%.6g")
print("rows", len(out), "symbols", out.symbol.nunique(), "from", out.date.min(), "to", out.date.max())
