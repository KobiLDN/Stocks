# Agora brief: are the signals worth following, and what should change?

> Issue #70. Numbers are from the track record as of 11 Nov 2026 and will drift; regenerate from `track-record.json` before reusing.

*Prepared by Claude, 11 Nov 2026, from the live track record (stocks-4qw.pages.dev/track-record). Discussion only: nothing gets built until the owner calls the vote. Claude is the only implementer.*

## The question

The site's purpose is decision support for the owner's own portfolio. The first honest measurement of the buy signals says they haven't beaten the S&P 500. Two of the signal's own features, the **"strong buy" label** and the **AI's confidence**, point the wrong way.

**What, if anything, should change in how signals are made or shown? And how do we test a change without fooling ourselves?**

## How signals are made today

- **Model and schedule:** per sector (AI, Biotech, Crypto, Defence, Energy, Mega-Cap, Tech), Mon/Wed/Fri at 08:00 London. The model is `deepseek/deepseek-v4-flash` via OpenRouter, with web search (5 results). It costs about $0.004 a run.
- **Prompt input:** each stock's price data, 1D/1W/1M/YTD returns, P/E, beta, analyst consensus, short interest, dividend yield, market cap, and VADER news sentiment.
- **Web search scope:** the 10 stocks with the highest 1-month momentum are flagged for web search before ranking.
- **Output:** exactly 10 picks per sector, ranked 1–10. Each is `strong_buy` or `buy`, with a "subjective" `confidence` from 0 to 1 and a rationale.
- **Momentum screener** (since 18 Jun): a rule-based layer.
  - Strong buy at YTD ≥ ~100% or 1Y ≥ 500%; buy at YTD ≥ ~50% or 1Y ≥ 200%.
  - Stocks it flags that the AI didn't pick are listed separately as momentum picks.
  - **If it flags a stock the AI did pick, the AI pick's confidence is raised to the momentum score, and `buy` is upgraded to `strong_buy`.**
- **Known bad inputs until 11 Nov:**
  - London market caps were 100× too small (BAE shown as $0.7B).
  - All dividend yields were 100× too big (70 stocks above 100%).
  - Every past signal was made with these numbers. Fixed in PR #61.
- **Consumers:** the site's signal pages and hub, and the private portfolio. The portfolio counts a stock as a BUY only if it has held a buy signal across the last 7 days of exports (both labels count as buy).

## How the track record measures

- **Every signal counts:** 5,609 buy signals since 23 May, all live (published at the time).
- **Entry:** the first market open more than 5 minutes after the signal, on the stock's own exchange.
- **Exits:** the close on or before entry + 7, 30 or 91 days.
- **Return:** includes splits and dividends, in local currency.
- **Benchmark:** SPY over the same window.
- **Not scored:**
  - PEPE (prices too coarse)
  - AGIX (the site priced the wrong coin until #49)
  - signals with no prices near the signal date

## Evidence

**Headline (all buy signals):**

| Held | Signals | Avg vs S&P | Median vs S&P | Beat S&P |
|---|---|---|---|---|
| 1 week | 5,164 | −0.61% | −0.82% | 45% |
| 1 month | 5,061 | −1.39% | −1.67% | 45% |
| 3 months | 3,028 | −0.09% | −3.21% | 45% |

**The label and confidence point the wrong way (3 months):**
- `strong_buy` −4.5% (beat 37%), `buy` +2.9% (beat 51%).
- 90%+ confidence −6.2% (beat 33%). Every lower confidence band did better.
- Ranks 1–3 vs 4–10: no meaningful difference. The ranking adds nothing.
- Momentum-screen picks −5.3% (beat 31%). AI picks +1.0% (beat 48%).

**By sector (3 months, vs S&P):**
- Energy +10.8% (beat 74%)
- Crypto +11.8% (beat 66%)
- Biotech +17.8%, but the median is only +2.5% (a few huge winners such as Moderna)
- Tech +2.4%, Mega-Cap −2.0%
- AI −13.6% (beat 24%), Defence −13.4% (beat 27%)

## Robustness checks Claude ran (please attack these)

1. **Is "strong buy is worse" caused by the momentum upgrade?** Mostly no. Before the upgrade existed (signals before 18 Jun), strong_buy was already worse: 3M −9.0% vs buy −4.0% (n = 277 / 548). After 18 Jun it's +0.3% vs +7.0% (n = 650 / 1,011). So the AI's own label underperforms. The upgrade may add to it, but isn't the root.
2. **Is it just sector mix (strong buys concentrated in AI/Tech)?** No. Within sectors at 1 month, strong buy minus buy is:
   - AI −6.1, Tech −6.5, Crypto −6.9, Defence −5.6, Mega-Cap −2.9
   - Biotech +0.4, Energy +5.7

   So it's worse in 5 of 7 sectors.
3. **Is high confidence bad everywhere?** No, it depends on the sector (1 month, 90%+ vs the rest of that sector):
   - worse in AI (−16.4 vs −5.8), Tech (−12.2 vs −0.7) and Mega-Cap (−6.9 vs −2.0)
   - better in Biotech (+13.2 vs +1.9) and Energy (+8.2 vs +2.3)

   Overconfidence concentrates in hyped tech names.
4. **Is it all the October AI sell-off?** No. Without October signals: strong_buy 3M −4.5% (beat 37%), buy +2.9% (beat 51%), all −0.1%. Same picture.
5. **Do repeat picks distort it?** No. New picks (not in the previous run) vs repeats: 3M −0.2% vs −0.1%.

**Caveats:**
- Windows overlap and the same stocks recur, so the effective sample is far smaller than 5,000. Treat the differences as strong hints, not proof.
- Six months is one market regime (an AI boom, then an October sell-off).
- Returns are in local currency, so UK stocks carry no GBP/USD effect.
- Every past signal was made with the bad market-cap and yield inputs above.

## Constraints on any proposal

- **The past is immutable.** Signals are stored write-once (`provenance = live`). Any change must be measurable: tag each run with a **variant / prompt version**, so the track record can compare before and after. Today only `model` is stored.
- **The export contract stays.** The portfolio reads `stocks[].signal` and treats strong_buy and buy alike. URLs and fields can't change silently.
- **Evaluation takes time.** 1M results need about 5 weeks, 3M about 14. A "shadow" variant (generated and stored, not shown) doubles the cost to about $0.008 a run, which is fine.
- **Keyless by default.** No new paid data sources without the owner's decision.

## Options on the table (not decisions)

- **A. Labels.**
  - Stop showing "strong buy" (one buy list), or
  - replace the AI's confidence with an **evidence-based score** (e.g. this sector's historical hit rate), or
  - show confidence but warn where it's been inversely related to results.
- **B. Momentum layer.**
  - Remove the upgrade (keep the separate list), or
  - turn the momentum screen into a *caution* flag ("already up a lot"), or
  - drop it.
- **C. Prompt.**
  - Ask for expected **outperformance vs the S&P 500 / sector**, not "buy".
  - Penalise stretched valuations and parabolic moves.
  - **Feed the model its own track record** by sector and label.
  - Stop pointing web search only at the 10 highest-momentum names.
- **D. Measurement first.**
  - Add a variant tag, then run a candidate prompt as a **shadow** next to the live one for 5–14 weeks.
  - Switch only if it wins on the agreed metric (median excess? hit rate?).
- **E. Allocation.** Surface the sector-level track record on the hub (Energy vs AI) as an input to sizing, rather than stock picks.
- **F. Wait.** Change nothing until more data accumulates (the cost is more weeks of possibly misleading labels).

**Claude's opening position:**
- Do D and the first part of B now. They're cheap, reversible and make everything else testable.
- Adopt A (stop presenting "strong buy" and raw confidence as stronger) straight away. That's a presentation change.
- Then trial C as a shadow variant.

Argue with this.

## What the owner needs from the agora

1. Is the evidence strong enough to change anything now, and what is the minimum safe change?
2. Which metric decides whether a new variant is better: median excess, hit rate, or average excess, at 1M or 3M?
3. Until that's settled, should the portfolio stop treating `strong_buy` (or momentum-upgraded picks) as a stronger signal?
