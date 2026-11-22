window.SIGNALS_DATA = {
  "updated": "2026-11-22 19:30",
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
      "signal": "buy",
      "confidence": 0.9,
      "rationale": "YTD +19.18%, P/E 20.35, recent ASH hematology data and CIDEB siRNA MASLD results provide strong pipeline catalysts.",
      "drivers": [
        "+14.39% 1M momentum",
        "P/E 20.35 attractive",
        "new ASH & MASLD data",
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
      "rank": 2,
      "ticker": "WMT",
      "signal": "strong_buy",
      "confidence": 0.9,
      "rationale": "Q3 FY27 earnings beat with revenue +5.2% and operating income +16%, driving strong momentum (+14.19% YTD, +8.62% 1-month). Analyst consensus 'buy' (1.55) and raised FY27 outlook reinforce fundamental strength.",
      "drivers": [
        "Q3 revenue +5.2%",
        "operating income +16%",
        "raised FY27 outlook",
        "analyst score 1.55"
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
      "rank": 3,
      "ticker": "TMUS",
      "signal": "strong_buy",
      "confidence": 0.85,
      "rationale": "T-Mobile delivered industry-leading Q3 results with service revenue up 6% YoY and EPS up 34% YoY to $3.22, while trading at a P/E of 15.97 with a 2.83% dividend yield [t-mobile.com](https://www.t-mobile.com/news/business/t-mobile-q3-2026-earnings).",
      "drivers": [
        "+34% EPS growth YoY",
        "P/E 15.97",
        "2.83% dividend yield",
        "industry-leading service revenue growth"
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
      "rank": 4,
      "ticker": "IDXX",
      "signal": "buy",
      "confidence": 0.85,
      "rationale": "+22.17% 1M, raised FY2026 guidance after Q3 beat with EPS $4.01 (+22% comparable).",
      "drivers": [
        "+22.17% 1M",
        "raised guidance",
        "analyst buy consensus",
        "strong volume expansion"
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
      "rank": 5,
      "ticker": "GEHC",
      "signal": "buy",
      "confidence": 0.85,
      "rationale": "+16.92% 1M, Q3 revenue +7.2% and raised FY guidance, P/E only 17.05.",
      "drivers": [
        "low P/E 17.05",
        "raised FY guidance",
        "Q3 beat +7.2% revenue",
        "strong free cash flow"
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
      "rank": 6,
      "ticker": "MDLZ",
      "signal": "strong_buy",
      "confidence": 0.8,
      "rationale": "Strong YTD +26.77% with PE 20.91, solid dividend 3.14%, and analyst 'buy' (1.83). Snacking demand remains resilient, underpinned by pricing power and portfolio strength.",
      "drivers": [
        "YTD +26.77%",
        "analyst score 1.83",
        "PE 20.91",
        "dividend 3.14%"
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
      "ticker": "XEL",
      "signal": "strong_buy",
      "confidence": 0.78,
      "rationale": "Rare strong_buy consensus (score 1.45) with solid YTD +8.65%, 1M +3.28%, P/E 18.48 and 2.99% dividend yield.",
      "drivers": [
        "Analyst strong_buy (score 1.45)",
        "P/E 18.48",
        "+8.65% YTD",
        "3.28% 1M momentum"
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
      "rank": 8,
      "ticker": "CMCSA",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "Comcast generated $4.2B free cash flow in Q3 and Peacock delivered its second consecutive profitable quarter with $261M EBITDA, while the stock trades at a P/E of 7.88 with a 5.3% dividend yield [cmcsa.gcs-web.com](https://cmcsa.gcs-web.com/news-releases/news-release-details/comcast-reports-3rd-quarter-2026-results).",
      "drivers": [
        "P/E 7.88",
        "5.3% dividend yield",
        "$4.2B free cash flow",
        "Peacock profitable"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 3
    },
    {
      "rank": 9,
      "ticker": "LIN",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "Linde has a buy consensus (an_score 1.62), a +23% 1-year return, +18.33% YTD, and a P/E of 33.39, supported by stable industrial gas demand and a low beta of 0.68.",
      "drivers": [
        "buy consensus (1.62)",
        "1Y +23%",
        "YTD +18.33%",
        "P/E 33.39"
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
      "rank": 10,
      "ticker": "TTWO",
      "signal": "strong_buy",
      "confidence": 0.75,
      "rationale": "Take-Two has the strongest analyst score in the group (1.21, strong_buy) and a beta of 0.918, with upcoming game releases providing catalyst potential despite a -16.53% YTD.",
      "drivers": [
        "analyst strong_buy (score 1.21)",
        "beta 0.918",
        "game release catalyst",
        "P/E N/A"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 6
    },
    {
      "rank": 11,
      "ticker": "ROP",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "YTD +6.62%, 1M +15.66%, P/E 18.2, beta 0.66; solid 1-month gain and low valuation.",
      "drivers": [
        "Positive 1-month momentum",
        "Low P/E",
        "Low beta",
        "Analyst buy"
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
      "rank": 12,
      "ticker": "KDP",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "YTD +28.58% and analyst 'buy' (1.85) with diversified beverage portfolio. PE 31.39 is higher but justified by consistent growth and dividend 2.64%.",
      "drivers": [
        "YTD +28.58%",
        "analyst score 1.85",
        "PE 31.39",
        "dividend 2.64%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 9
    },
    {
      "rank": 13,
      "ticker": "CCEP",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "YTD +34.21% with PE 22.3 and analyst 'buy' (2.0). Strong 1-month +6.20% momentum and exposure to European beverage markets with solid free cash flow.",
      "drivers": [
        "YTD +34.21%",
        "PE 22.3",
        "analyst score 2.0",
        "1-month +6.20%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 10
    },
    {
      "rank": 14,
      "ticker": "CPRT",
      "signal": "buy",
      "confidence": 0.6,
      "rationale": "+12.69% 1M, P/E 20.06, analyst buy score 2.33",
      "drivers": [
        "1M momentum",
        "Reasonable P/E",
        "Analyst buy"
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
      "rank": 15,
      "ticker": "APP",
      "signal": "buy",
      "confidence": 0.55,
      "rationale": "AppLovin has a strong 1-month rebound of +30.01% and a buy analyst consensus (score 1.58), though high beta (2.498) and short interest (3.83%) add risk.",
      "drivers": [
        "+30.01% 1M",
        "analyst buy consensus",
        "beta 2.498",
        "short interest 3.83%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 9
    },
    {
      "rank": 16,
      "ticker": "FER",
      "signal": "buy",
      "confidence": 0.5,
      "rationale": "+16.49% 1M, div yield 3.84%, low short interest 1.08%",
      "drivers": [
        "Solid 1M gain",
        "High dividend yield",
        "Low short interest"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 9
    }
  ],
  "momentum_picks": [],
  "previous_picks": [
    {
      "rank": 1,
      "ticker": "REGN",
      "signal": "buy",
      "confidence": 0.9,
      "rationale": "YTD +19.18%, P/E 20.35, recent ASH hematology data and CIDEB siRNA MASLD results provide strong pipeline catalysts.",
      "drivers": [
        "+14.39% 1M momentum",
        "P/E 20.35 attractive",
        "new ASH & MASLD data",
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
      "rank": 2,
      "ticker": "WMT",
      "signal": "strong_buy",
      "confidence": 0.9,
      "rationale": "Q3 FY27 earnings beat with revenue +5.2% and operating income +16%, driving strong momentum (+14.19% YTD, +8.62% 1-month). Analyst consensus 'buy' (1.55) and raised FY27 outlook reinforce fundamental strength.",
      "drivers": [
        "Q3 revenue +5.2%",
        "operating income +16%",
        "raised FY27 outlook",
        "analyst score 1.55"
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
      "rank": 3,
      "ticker": "TMUS",
      "signal": "strong_buy",
      "confidence": 0.85,
      "rationale": "T-Mobile delivered industry-leading Q3 results with service revenue up 6% YoY and EPS up 34% YoY to $3.22, while trading at a P/E of 15.97 with a 2.83% dividend yield [t-mobile.com](https://www.t-mobile.com/news/business/t-mobile-q3-2026-earnings).",
      "drivers": [
        "+34% EPS growth YoY",
        "P/E 15.97",
        "2.83% dividend yield",
        "industry-leading service revenue growth"
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
      "rank": 4,
      "ticker": "IDXX",
      "signal": "buy",
      "confidence": 0.85,
      "rationale": "+22.17% 1M, raised FY2026 guidance after Q3 beat with EPS $4.01 (+22% comparable).",
      "drivers": [
        "+22.17% 1M",
        "raised guidance",
        "analyst buy consensus",
        "strong volume expansion"
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
      "rank": 5,
      "ticker": "GEHC",
      "signal": "buy",
      "confidence": 0.85,
      "rationale": "+16.92% 1M, Q3 revenue +7.2% and raised FY guidance, P/E only 17.05.",
      "drivers": [
        "low P/E 17.05",
        "raised FY guidance",
        "Q3 beat +7.2% revenue",
        "strong free cash flow"
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
      "rank": 6,
      "ticker": "MDLZ",
      "signal": "strong_buy",
      "confidence": 0.8,
      "rationale": "Strong YTD +26.77% with PE 20.91, solid dividend 3.14%, and analyst 'buy' (1.83). Snacking demand remains resilient, underpinned by pricing power and portfolio strength.",
      "drivers": [
        "YTD +26.77%",
        "analyst score 1.83",
        "PE 20.91",
        "dividend 3.14%"
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
      "ticker": "XEL",
      "signal": "strong_buy",
      "confidence": 0.78,
      "rationale": "Rare strong_buy consensus (score 1.45) with solid YTD +8.65%, 1M +3.28%, P/E 18.48 and 2.99% dividend yield.",
      "drivers": [
        "Analyst strong_buy (score 1.45)",
        "P/E 18.48",
        "+8.65% YTD",
        "3.28% 1M momentum"
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
      "rank": 8,
      "ticker": "CMCSA",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "Comcast generated $4.2B free cash flow in Q3 and Peacock delivered its second consecutive profitable quarter with $261M EBITDA, while the stock trades at a P/E of 7.88 with a 5.3% dividend yield [cmcsa.gcs-web.com](https://cmcsa.gcs-web.com/news-releases/news-release-details/comcast-reports-3rd-quarter-2026-results).",
      "drivers": [
        "P/E 7.88",
        "5.3% dividend yield",
        "$4.2B free cash flow",
        "Peacock profitable"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 3
    },
    {
      "rank": 9,
      "ticker": "LIN",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "Linde has a buy consensus (an_score 1.62), a +23% 1-year return, +18.33% YTD, and a P/E of 33.39, supported by stable industrial gas demand and a low beta of 0.68.",
      "drivers": [
        "buy consensus (1.62)",
        "1Y +23%",
        "YTD +18.33%",
        "P/E 33.39"
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
      "rank": 10,
      "ticker": "TTWO",
      "signal": "strong_buy",
      "confidence": 0.75,
      "rationale": "Take-Two has the strongest analyst score in the group (1.21, strong_buy) and a beta of 0.918, with upcoming game releases providing catalyst potential despite a -16.53% YTD.",
      "drivers": [
        "analyst strong_buy (score 1.21)",
        "beta 0.918",
        "game release catalyst",
        "P/E N/A"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 6
    },
    {
      "rank": 11,
      "ticker": "ROP",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "YTD +6.62%, 1M +15.66%, P/E 18.2, beta 0.66; solid 1-month gain and low valuation.",
      "drivers": [
        "Positive 1-month momentum",
        "Low P/E",
        "Low beta",
        "Analyst buy"
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
      "rank": 12,
      "ticker": "KDP",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "YTD +28.58% and analyst 'buy' (1.85) with diversified beverage portfolio. PE 31.39 is higher but justified by consistent growth and dividend 2.64%.",
      "drivers": [
        "YTD +28.58%",
        "analyst score 1.85",
        "PE 31.39",
        "dividend 2.64%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 9
    },
    {
      "rank": 13,
      "ticker": "CCEP",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "YTD +34.21% with PE 22.3 and analyst 'buy' (2.0). Strong 1-month +6.20% momentum and exposure to European beverage markets with solid free cash flow.",
      "drivers": [
        "YTD +34.21%",
        "PE 22.3",
        "analyst score 2.0",
        "1-month +6.20%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 10
    },
    {
      "rank": 14,
      "ticker": "CPRT",
      "signal": "buy",
      "confidence": 0.6,
      "rationale": "+12.69% 1M, P/E 20.06, analyst buy score 2.33",
      "drivers": [
        "1M momentum",
        "Reasonable P/E",
        "Analyst buy"
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
      "rank": 15,
      "ticker": "APP",
      "signal": "buy",
      "confidence": 0.55,
      "rationale": "AppLovin has a strong 1-month rebound of +30.01% and a buy analyst consensus (score 1.58), though high beta (2.498) and short interest (3.83%) add risk.",
      "drivers": [
        "+30.01% 1M",
        "analyst buy consensus",
        "beta 2.498",
        "short interest 3.83%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 9
    },
    {
      "rank": 16,
      "ticker": "FER",
      "signal": "buy",
      "confidence": 0.5,
      "rationale": "+16.49% 1M, div yield 3.84%, low short interest 1.08%",
      "drivers": [
        "Solid 1M gain",
        "High dividend yield",
        "Low short interest"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 9
    }
  ]
};
