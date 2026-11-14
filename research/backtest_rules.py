"""Research only: test famous traders' stock rules on this site's universe, scored like the track record.

Each rule fires on a day; entry = next trading day's open; exits = close ~1 week / 1 month / 3 months later
(5 / 21 / 63 trading days); excess = asset return - SPY return over the same dates. Prices are total-return.

Rules (price + volume only, so no look-ahead from today's fundamentals):
  minervini   Trend template: close > SMA50 > SMA150 > SMA200, SMA200 rising over 1 month,
              close within 25% of the 52-week high and >= 30% above the 52-week low.   (state, checked weekly)
  ptj200      Paul Tudor Jones: close above its 200-day average.                      (state, weekly)
  darvas      Darvas box + O'Neil volume: close breaks the prior 20-day high after a tight box
              (20-day range <= 15%), on volume >= 1.5x the 50-day average.            (event, daily)
  newhigh50   Livermore/Seykota trend following: close at a new 50-day closing high.  (event, daily)
  runup       The site's current momentum screen, roughly: up >= 50% over the past year. (state, weekly)
  mom12_1     Academic momentum: top fifth of the universe by 12-month return skipping the last month. (weekly)
  universe    Baseline: every asset, every week (what picking at random from this list gives).
"""
import sys, numpy as np, pandas as pd

H = {"1w": 5, "1m": 21, "3m": 63}

def load(path):
    df = pd.read_csv(path, parse_dates=["date"])
    df["date"] = df["date"].dt.tz_localize(None).dt.normalize()
    return df

def build(df):
    p = {f: df.pivot_table(index="date", columns="symbol", values=f) for f in ["open", "high", "low", "close", "volume"]}
    spy = p["close"]["SPY"]
    cal = spy.dropna().index                     # US trading calendar drives everything
    p = {k: v.reindex(cal) for k, v in p.items()}
    return p, cal

def rules(p):
    c, h, v = p["close"], p["high"], p["volume"]
    sma = lambda n: c.rolling(n, min_periods=n).mean()
    s50, s150, s200 = sma(50), sma(150), sma(200)
    hi252, lo252 = c.rolling(252, min_periods=252).max(), c.rolling(252, min_periods=252).min()
    out = {}
    out["minervini"] = (c > s50) & (s50 > s150) & (s150 > s200) & (s200 > s200.shift(21)) & (c >= 0.75 * hi252) & (c >= 1.30 * lo252)
    out["ptj200"] = c > s200
    box_hi = h.shift(1).rolling(20, min_periods=20).max(); box_lo = p["low"].shift(1).rolling(20, min_periods=20).min()
    out["darvas"] = (c > box_hi) & ((box_hi - box_lo) / box_hi <= 0.15) & (v >= 1.5 * v.shift(1).rolling(50, min_periods=50).mean())
    out["newhigh50"] = (c >= c.rolling(50, min_periods=50).max()) & (c.shift(1) < c.shift(1).rolling(50, min_periods=50).max())
    out["runup"] = c / c.shift(252) - 1 >= 0.50
    r121 = c.shift(21) / c.shift(252) - 1
    out["mom12_1"] = r121.ge(r121.drop(columns=["SPY"]).quantile(0.8, axis=1), axis=0)
    out["universe"] = c.notna() & c.shift(252).notna()
    return out

STATE = {"minervini", "ptj200", "runup", "mom12_1", "universe"}

def signals(p, cal, fired):
    """Rows: rule, date, symbol, x1w, x1m, x3m (excess vs SPY, %)."""
    o, c = p["open"], p["close"]
    spy_o, spy_c = o["SPY"], c["SPY"]
    weekly = pd.Series(cal, index=cal).groupby(cal.to_period("W")).first().values   # first trading day each week
    idx = {d: i for i, d in enumerate(cal)}
    rows = []
    for rule, m in fired.items():
        m = m.drop(columns=["SPY"], errors="ignore").fillna(False)
        if rule in STATE:
            m = m.loc[m.index.isin(weekly)]
        st = m.stack(); st = st[st]
        for (d, sym) in st.index:
            i = idx[d]
            if i + 1 >= len(cal): continue
            e = i + 1; eo = o.at[cal[e], sym]; so = spy_o.iat[e]
            if not (eo > 0) or not (so > 0): continue
            r = {"rule": rule, "date": d, "symbol": sym}
            for k, n in H.items():
                j = e + n - 1
                if j < len(cal) and c.at[cal[j], sym] > 0:
                    r["x" + k] = 100 * ((c.at[cal[j], sym] / eo) - (spy_c.iat[j] / so))
                else:
                    r["x" + k] = np.nan
            rows.append(r)
    return pd.DataFrame(rows)

def boot_median_diff(a, b, n=1000, seed=1):
    """Median(a) - median(b), resampling whole symbols (repeat picks of one stock are not independent)."""
    rng = np.random.default_rng(seed)
    ga = {s: g.values for s, g in a.groupby(level=0)}; gb = {s: g.values for s, g in b.groupby(level=0)}
    syms = sorted(set(ga) | set(gb)); out = []
    for _ in range(n):
        pick = rng.choice(len(syms), len(syms))
        A = np.concatenate([ga[syms[k]] for k in pick if syms[k] in ga] or [np.array([np.nan])])
        B = np.concatenate([gb[syms[k]] for k in pick if syms[k] in gb] or [np.array([np.nan])])
        out.append(np.nanmedian(A) - np.nanmedian(B))
    return np.nanpercentile(out, [2.5, 97.5])

def summarise(sig, crypto):
    base = sig[sig.rule == "universe"]
    lines = []
    for rule in ["minervini", "ptj200", "darvas", "newhigh50", "mom12_1", "runup", "universe"]:
        g = sig[sig.rule == rule]
        row = {"rule": rule, "signals": len(g), "symbols": g.symbol.nunique()}
        for k in H:
            x = g["x" + k].dropna()
            row[f"{k}_median"] = round(x.median(), 2); row[f"{k}_avg"] = round(x.mean(), 2); row[f"{k}_beat"] = round(100 * (x > 0).mean(), 1)
        if rule != "universe":
            for k in ("1m", "3m"):
                a = g.set_index("symbol")["x" + k].dropna(); b = base.set_index("symbol")["x" + k].dropna()
                lo, hi = boot_median_diff(a, b)
                row[f"{k}_vs_universe"] = f"{a.median() - b.median():+.1f} [{lo:+.1f}, {hi:+.1f}]"
        lines.append(row)
    return pd.DataFrame(lines)

if __name__ == "__main__":
    df = load(sys.argv[1])
    p, cal = build(df)
    sig = signals(p, cal, rules(p))
    sig.to_csv(sys.argv[2], index=False)
    crypto = {s for s in sig.symbol.unique() if s.endswith("-USD")}
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print("period:", cal[0].date(), "to", cal[-1].date())
    for label, part in [("ALL", sig), ("STOCKS ONLY", sig[~sig.symbol.isin(crypto)])]:
        print("\n==", label); print(summarise(part, crypto).to_string(index=False))
    sig["year"] = sig.date.dt.year
    print("\n== 3-month median excess by year (stocks only)")
    s = sig[~sig.symbol.isin(crypto)]
    print(s.pivot_table(index="rule", columns="year", values="x3m", aggfunc="median").round(1).to_string())
