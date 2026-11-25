window.SIGNALS_DATA = {
  "updated": "2026-11-25 08:02",
  "derived": true,
  "derived_from": [
    "communication-services",
    "consumer-discretionary",
    "consumer-staples",
    "energy",
    "financials",
    "health-care",
    "industrials",
    "materials",
    "real-estate",
    "technology",
    "utilities"
  ],
  "model": "deepseek/deepseek-v4-flash",
  "group": "nasdaq100",
  "group_name": "Nasdaq-100",
  "group_kind": "market",
  "note": "Picks from the 11 sector runs that are members of the Nasdaq-100; no separate AI run (too many stocks for one prompt).",
  "picks": [
    {
      "rank": 1,
      "ticker": "TTWO",
      "signal": "strong_buy",
      "confidence": 0.95,
      "rationale": "Strong buy analyst (score 1.21) with robust momentum: +5.28% 1D, +8.08% 1W, +8.39% 1M, despite -12.40% YTD; beta 0.92.",
      "drivers": [
        "strong_buy analyst",
        "+5.28% 1D",
        "+8.08% 1W",
        "low beta 0.92"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 1
    },
    {
      "rank": 2,
      "ticker": "REGN",
      "signal": "buy",
      "confidence": 0.9,
      "rationale": "FDA approval for Livsayis in gMG and Q3 revenue up 36% to $5.1B drive momentum; YTD +27.77%, 1M +22.34%, P/E 20.8, beta 0.095.",
      "drivers": [
        "FDA approval Livsayis",
        "Q3 revenue +36%",
        "YTD +27.77%",
        "low beta 0.095"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "health-care",
      "from_group_name": "Health Care",
      "group_rank": 1
    },
    {
      "rank": 3,
      "ticker": "IDXX",
      "signal": "buy",
      "confidence": 0.85,
      "rationale": "Q3 EPS $4.01 (+18%) and raised 2026 guidance; 1M +24.88%, YTD +6.28%, P/E 46.3.",
      "drivers": [
        "Q3 EPS beat",
        "raised guidance",
        "1M +24.88%",
        "strong volume growth"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "health-care",
      "from_group_name": "Health Care",
      "group_rank": 2
    },
    {
      "rank": 4,
      "ticker": "TMUS",
      "signal": "buy",
      "confidence": 0.85,
      "rationale": "Buy analyst (score 1.61) with Q3 earnings catalyst: net income +27% YoY, raised guidance [T-Mobile Newsroom](https://www.t-mobile.com/news/business/t-mobile-q3-2026-earnings); 1M +13.86%, beta 0.38.",
      "drivers": [
        "Q3 earnings beat",
        "+13.86% 1M",
        "low beta 0.38",
        "buy analyst"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 5
    },
    {
      "rank": 5,
      "ticker": "DXCM",
      "signal": "strong_buy",
      "confidence": 0.8,
      "rationale": "Strong_buy analyst, YTD +27.20%, 1M +7.73%, P/E 32.45, beta 1.44.",
      "drivers": [
        "strong_buy analyst",
        "YTD +27.20%",
        "P/E 32.45",
        "solid fundamentals"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "health-care",
      "from_group_name": "Health Care",
      "group_rank": 5
    },
    {
      "rank": 6,
      "ticker": "ROP",
      "signal": "buy",
      "confidence": 0.78,
      "rationale": "ROP has solid momentum with +7.89% 1M and +10.48% YTD, a reasonable P/E of 18.13, low beta of 0.66, and a buy analyst consensus (score 2.37).",
      "drivers": [
        "+7.89% 1M",
        "P/E 18.13",
        "low beta 0.66",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 3
    },
    {
      "rank": 7,
      "ticker": "WMT",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "Q3 revenue +5.2% to $188.8B, raised FY2027 sales growth forecast to 4.9%-5.2%, analyst consensus strong_buy (score 1.55), +25% 1Y return.",
      "drivers": [
        "Revenue beat and raised guidance",
        "Strong analyst consensus",
        "Market leader in retail",
        "Solid YTD momentum"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 3
    },
    {
      "rank": 8,
      "ticker": "COST",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "P/E 52.9 is elevated but +32% YTD, +26% 1Y return, low short interest 1.78%, analyst buy consensus, strong membership model.",
      "drivers": [
        "Strong YTD momentum",
        "Low short interest",
        "Analyst buy consensus",
        "Premium brand strength"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 4
    },
    {
      "rank": 9,
      "ticker": "MRNA",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "Q3 EPS $0.38 vs expected -$1.25, raised 2026 growth outlook to 15-25%; YTD +636.81%, 1M +14.35%.",
      "drivers": [
        "Q3 earnings beat",
        "raised outlook",
        "YTD +636.81%",
        "new vaccine traction"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": "strong_buy",
      "momentum_score": 1.0,
      "from_group": "health-care",
      "from_group_name": "Health Care",
      "group_rank": 4
    },
    {
      "rank": 10,
      "ticker": "ADSK",
      "signal": "strong_buy",
      "confidence": 0.7,
      "rationale": "ADSK has a strong_buy analyst consensus (score 1.50) and positive short-term momentum with +2.51% 1M and +0.19% 1W, despite a -10.82% YTD.",
      "drivers": [
        "strong_buy consensus",
        "+2.51% 1M",
        "analyst score 1.50"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 6
    },
    {
      "rank": 11,
      "ticker": "CPRT",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "1M +11.0%, YTD -14.4% but recovering; P/E 20.4; analyst buy; strong used vehicle auction demand; low beta 1.0.",
      "drivers": [
        "1M +11.0%",
        "P/E 20.4",
        "buy consensus",
        "recovery momentum"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 6
    },
    {
      "rank": 12,
      "ticker": "CMCSA",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "Hold analyst but strong momentum: 1M +15.10%, 1D +2.67%, low P/E 7.82, high dividend 5.34%.",
      "drivers": [
        "+15.10% 1M",
        "low P/E 7.82",
        "high dividend 5.34%",
        "positive 1D"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 8
    },
    {
      "rank": 13,
      "ticker": "MPWR",
      "signal": "strong_buy",
      "confidence": 0.65,
      "rationale": "MPWR has a strong_buy analyst consensus (score 1.19), strong YTD return of +27.75%, and positive 1M momentum of +1.96%, though recent 1D/1W pullbacks are notable.",
      "drivers": [
        "strong_buy consensus",
        "+27.75% YTD",
        "+1.96% 1M",
        "analyst score 1.19"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 8
    },
    {
      "rank": 14,
      "ticker": "AAPL",
      "signal": "buy",
      "confidence": 0.62,
      "rationale": "AAPL shows steady momentum with +31.10% YTD, +3.03% 1M, and +0.61% 1W, low beta of 1.09, low short interest of 1.0%, and a buy analyst consensus (score 2.18).",
      "drivers": [
        "+31.10% YTD",
        "+3.03% 1M",
        "low short interest 1.0%",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 9
    },
    {
      "rank": 15,
      "ticker": "FER",
      "signal": "buy",
      "confidence": 0.62,
      "rationale": "1M +19.2%, YTD -6.1% but strong short-term momentum; P/E 32.8, div yield 3.7%; infrastructure & toll road exposure; low beta 0.76.",
      "drivers": [
        "1M +19.2%",
        "div yield 3.7%",
        "infrastructure exposure",
        "low beta 0.76"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 10
    }
  ],
  "momentum_picks": [],
  "previous_picks": [
    {
      "rank": 1,
      "ticker": "WMT",
      "signal": "strong_buy",
      "confidence": 0.9,
      "rationale": "Q3 FY27 revenue +5.2%, operating income +16%, raised outlook; P/E 46 but analyst consensus best at 1.55.",
      "drivers": [
        "Q3 beat & raised guidance",
        "strong omnichannel growth",
        "low short interest 1.65%",
        "analyst consensus strong_buy"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 1
    },
    {
      "rank": 2,
      "ticker": "IDXX",
      "signal": "buy",
      "confidence": 0.85,
      "rationale": "Q3 EPS $4.01 beat estimates, revenue +10% YoY, raised FY guidance, 1M +22.17% momentum.",
      "drivers": [
        "Q3 EPS beat",
        "raised FY guidance",
        "1M +22.17%",
        "analyst buy"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "health-care",
      "from_group_name": "Health Care",
      "group_rank": 1
    },
    {
      "rank": 3,
      "ticker": "GEHC",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "BTIG raised PT to $91, Q3 EPS $1.34 beat, revenue +7.2% YoY, P/E 17.05 attractive.",
      "drivers": [
        "BTIG upgrade",
        "Q3 earnings beat",
        "P/E 17.05",
        "1M +16.92%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "health-care",
      "from_group_name": "Health Care",
      "group_rank": 2
    },
    {
      "rank": 4,
      "ticker": "REGN",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "EU approved Libtayo extended dosing, 1M +14.39%, P/E 20.35, low beta 0.095.",
      "drivers": [
        "EU Libtayo approval",
        "1M +14.39%",
        "P/E 20.35",
        "low beta"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "health-care",
      "from_group_name": "Health Care",
      "group_rank": 3
    },
    {
      "rank": 5,
      "ticker": "ROP",
      "signal": "strong_buy",
      "confidence": 0.8,
      "rationale": "ROP gained +15.66% in the past month and +6.62% YTD, with a reasonable P/E of 18.2 and low beta of 0.662. Its diversified software and industrial portfolio offers stability and growth.",
      "drivers": [
        "+15.66% 1M momentum",
        "P/E 18.2",
        "low beta 0.662",
        "buy analyst consensus"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 3
    },
    {
      "rank": 6,
      "ticker": "XEL",
      "signal": "strong_buy",
      "confidence": 0.78,
      "rationale": "Xcel Energy carries a strong_buy analyst consensus (score 1.45), YTD +8.65%, 1M +3.28%, and a P/E of 18.48 with 2.99% yield. The strong analyst backing and reasonable valuation make it attractive.",
      "drivers": [
        "strong_buy consensus",
        "P/E 18.48",
        "positive YTD",
        "low beta 0.345"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "utilities",
      "from_group_name": "Utilities",
      "group_rank": 3
    },
    {
      "rank": 7,
      "ticker": "LIN",
      "signal": "buy",
      "confidence": 0.73,
      "rationale": "Linde has a buy consensus (an_score 1.62), a 1-month gain of +0.45%, YTD +18.33%, and a P/E of 33.39, with a massive $230.8B market cap and low short interest of 1.45%.",
      "drivers": [
        "buy consensus",
        "1M +0.45%",
        "YTD +18.33%",
        "low short 1.45%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "materials",
      "from_group_name": "Materials",
      "group_rank": 5
    },
    {
      "rank": 8,
      "ticker": "MDLZ",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "+26.77% YTD, P/E 20.91, analyst buy; solid branded food portfolio.",
      "drivers": [
        "consistent YTD growth",
        "reasonable P/E",
        "buy analyst consensus",
        "low short interest 2.6%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 5
    },
    {
      "rank": 9,
      "ticker": "FER",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "Ferrovial has gained +16.49% in the past month, driven by infrastructure spending tailwinds; a 3.84% dividend yield and low short interest of 1.08% add to its defensive appeal.",
      "drivers": [
        "+16.49% 1M momentum",
        "3.84% dividend yield",
        "low short interest 1.08%",
        "infrastructure catalyst"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 3
    },
    {
      "rank": 10,
      "ticker": "CMCSA",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "CMCSA has a very low P/E of 7.88 and a high dividend yield of 5.30%, with a 1M return of +12.77%. Despite a Bernstein price target cut due to SpaceX competition, the stock is cheap and offers strong income, with analyst consensus 'hold' but a score of 2.63.",
      "drivers": [
        "P/E 7.88",
        "Dividend yield 5.30%",
        "+12.77% 1M return",
        "Low valuation"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 5
    },
    {
      "rank": 11,
      "ticker": "CPRT",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "Copart has surged +12.69% in the past month, with a P/E of 20.06 and a buy consensus; its strong YTD performance of -17.69% is misleading given the recent momentum shift.",
      "drivers": [
        "+12.69% 1M momentum",
        "P/E 20.06 attractive",
        "buy consensus",
        "recent momentum shift"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 7
    },
    {
      "rank": 12,
      "ticker": "EXC",
      "signal": "buy",
      "confidence": 0.58,
      "rationale": "Exelon reported Q3 adjusted EPS of $0.87 above expectations and narrowed 2026 guidance to $2.85-$2.91. YTD +6.94% and 1M +6.16%, P/E 17.85, 3.68% yield. [exeloncorp.com](https://www.exeloncorp.com/newsroom/exelon-reports-third-quarter-2026-results)",
      "drivers": [
        "Q3 earnings beat",
        "narrowed guidance",
        "P/E 17.85",
        "3.68% yield"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "utilities",
      "from_group_name": "Utilities",
      "group_rank": 10
    },
    {
      "rank": 13,
      "ticker": "TMUS",
      "signal": "buy",
      "confidence": 0.55,
      "rationale": "TMUS has a 1M return of +7.71% and a P/E of 15.97, with a low beta of 0.378. Despite SpaceX competition concerns, Raymond James upgraded TMUS to 'Outperform' and set a $170 price target, citing overblown fears. Analyst consensus is 'buy' with a score of 1.61.",
      "drivers": [
        "+7.71% 1M return",
        "P/E 15.97",
        "Low beta 0.378",
        "Raymond James upgrade"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 7
    },
    {
      "rank": 14,
      "ticker": "TTWO",
      "signal": "strong_buy",
      "confidence": 0.45,
      "rationale": "TTWO has the strongest analyst consensus in the sector ('strong_buy', score 1.21), with a 1M return of +1.86%. The stock has no P/E due to negative earnings, but upcoming game releases (e.g., GTA VI) are key catalysts. High short interest of 4.99% adds risk.",
      "drivers": [
        "Analyst consensus 'strong_buy'",
        "Score 1.21",
        "+1.86% 1M return",
        "Upcoming game catalysts"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 9
    },
    {
      "rank": 15,
      "ticker": "APP",
      "signal": "buy",
      "confidence": 0.4,
      "rationale": "APP has explosive 1M momentum (+30.01%) despite a -43.67% YTD decline, with a P/E of 23.45 and analyst consensus 'buy' (score 1.58). The stock is highly volatile (beta 2.498) and has high short interest (3.83%), but the recent rally suggests a turnaround in advertising demand.",
      "drivers": [
        "+30.01% 1M return",
        "Analyst consensus 'buy'",
        "P/E 23.45",
        "High beta 2.498"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 10
    }
  ]
};
