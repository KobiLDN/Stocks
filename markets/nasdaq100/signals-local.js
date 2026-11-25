window.SIGNALS_DATA = {
  "updated": "2026-11-25 09:34",
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
      "ticker": "REGN",
      "signal": "strong_buy",
      "confidence": 0.85,
      "rationale": "Q3 revenues surged 36% to $5.1B, EPS $20.07 non-GAAP (+70% YoY), with Dupixent +35% and EYLEA HD +62%; P/E 20.8 is attractive for this growth. [globenewswire.com]",
      "drivers": [
        "+36% revenue growth Q3",
        "P/E 20.8",
        "+22% 1M momentum",
        "FDA approval Pasatru"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "health-care",
      "from_group_name": "Health Care",
      "group_rank": 1
    },
    {
      "rank": 2,
      "ticker": "IDXX",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "Q3 revenue +10% to $1.21B, EPS $4.01 (+18%), raised FY26 guidance to $4.74-4.77B; strong volume and 1,900 inVue Dx placements. [ir.idexx.com]",
      "drivers": [
        "+10% Q3 revenue growth",
        "raised FY26 guidance",
        "+25% 1M momentum",
        "analyst buy"
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
      "rank": 3,
      "ticker": "TTWO",
      "signal": "strong_buy",
      "confidence": 0.8,
      "rationale": "Best analyst score of 1.21 (strong_buy) and accelerating short-term momentum with 1W +8.08% and 1D +5.28%.",
      "drivers": [
        "analyst score 1.21",
        "1W +8.08%",
        "1D +5.28%",
        "strong_buy signal"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 3
    },
    {
      "rank": 4,
      "ticker": "WMT",
      "signal": "strong_buy",
      "confidence": 0.8,
      "rationale": "Walmart beat Q3 estimates (EPS $0.65 vs $0.64), raised annual guidance, e-commerce +17%; +25% 1Y, P/E 46.95 but strong buy consensus (score 1.55).",
      "drivers": [
        "Q3 EPS beat",
        "raised FY guidance",
        "e-commerce +17%",
        "analyst score 1.55"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 3
    },
    {
      "rank": 5,
      "ticker": "ROP",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "ROP has positive momentum with +7.89% 1M and +10.48% YTD, a low beta of 0.66, a reasonable P/E of 18.13, and a buy rating, offering defensive growth.",
      "drivers": [
        "+7.89% 1M",
        "+10.48% YTD",
        "P/E 18.13",
        "beta 0.66"
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
      "rank": 6,
      "ticker": "COST",
      "signal": "strong_buy",
      "confidence": 0.75,
      "rationale": "Costco +32% YTD, +11.8% 1M, P/E 52.89 but consistent growth and low short interest 1.78%; analyst buy consensus.",
      "drivers": [
        "+32% YTD",
        "+11.8% 1-month",
        "low short interest 1.78%",
        "buy consensus"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 4
    },
    {
      "rank": 7,
      "ticker": "CMCSA",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "Low P/E of 7.82 and high dividend yield of 5.34% provide a strong value proposition, with a 1-month surge of +15.10% and low beta of 0.707.",
      "drivers": [
        "P/E 7.82",
        "dividend 5.34%",
        "1M +15.10%",
        "low beta 0.707"
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
      "rank": 8,
      "ticker": "MRNA",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "Q3 EPS $0.38 vs -$1.25 expected, revenue $1.31B (+29%), raised FY26 growth outlook to 15-25% from up to 10%. [cnbc.com]",
      "drivers": [
        "Q3 earnings beat",
        "raised FY26 guidance",
        "+637% YTD momentum",
        "new product launches"
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
      "rank": 9,
      "ticker": "AAPL",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "AAPL shows steady gains with +31.10% YTD, +3.03% 1M, and +1.43% 1D, supported by a low beta of 1.09, a P/E of 38.87, and a buy rating.",
      "drivers": [
        "+31.10% YTD",
        "+3.03% 1M",
        "beta 1.09",
        "buy rating"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 6
    },
    {
      "rank": 10,
      "ticker": "CPRT",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "Copart +11.0% 1M, P/E 20.4, analyst buy, though YTD -14.4% offers a contrarian entry.",
      "drivers": [
        "+11.0% 1-month return",
        "P/E 20.4",
        "analyst buy",
        "contrarian value"
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
      "rank": 11,
      "ticker": "TMUS",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "Solid 1-month momentum of +13.86%, a buy analyst rating (score 1.61), and low beta of 0.378 indicate stability and growth potential.",
      "drivers": [
        "1M +13.86%",
        "buy analyst",
        "beta 0.378",
        "score 1.61"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 10
    },
    {
      "rank": 12,
      "ticker": "APP",
      "signal": "buy",
      "confidence": 0.6,
      "rationale": "Explosive 1-month rebound of +46.16% and a buy analyst rating (score 1.58) signal a potential turnaround despite negative YTD.",
      "drivers": [
        "1M +46.16%",
        "buy analyst",
        "score 1.58",
        "1D +1.92%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 6
    },
    {
      "rank": 13,
      "ticker": "ADSK",
      "signal": "strong_buy",
      "confidence": 0.6,
      "rationale": "ADSK has a strong_buy analyst consensus (score 1.5) and recent positive momentum (+2.51% 1M, +0.19% 1W), with a P/E of 33.12, despite a negative YTD of -10.82%.",
      "drivers": [
        "strong_buy rating",
        "+2.51% 1M",
        "P/E 33.12",
        "analyst score 1.5"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 7
    },
    {
      "rank": 14,
      "ticker": "FER",
      "signal": "buy",
      "confidence": 0.6,
      "rationale": "Ferrovial +19.2% 1M, low short 1.08%, but no analyst rating and P/E 32.8; momentum-driven.",
      "drivers": [
        "+19.2% 1-month return",
        "low short interest 1.08%",
        "momentum play"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 7
    }
  ],
  "momentum_picks": [],
  "previous_picks": [
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
  ]
};
