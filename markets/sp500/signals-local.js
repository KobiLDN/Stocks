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
  "group": "sp500",
  "group_name": "S&P 500",
  "group_kind": "market",
  "note": "Picks from the 11 sector runs that are members of the S&P 500; no separate AI run (too many stocks for one prompt).",
  "picks": [
    {
      "rank": 1,
      "ticker": "TRGP",
      "signal": "strong_buy",
      "confidence": 0.95,
      "rationale": "YTD +54%, P/E 24.5, strong_buy consensus. Q3 adj. EBITDA $1.5B (+18% YoY), 20% dividend increase for 2027, and new Permian midstream deals with ExxonMobil [targaresources.com].",
      "drivers": [
        "strong_buy consensus (1.27)",
        "YTD +54%",
        "Q3 EBITDA +18% YoY",
        "20% dividend hike for 2027"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 1
    },
    {
      "rank": 2,
      "ticker": "AIZ",
      "signal": "strong_buy",
      "confidence": 0.9,
      "rationale": "+37% YTD, P/E 15, strong_buy consensus, strong 1m momentum of +12%.",
      "drivers": [
        "+37% YTD",
        "P/E 15",
        "strong_buy consensus",
        "1m +12%"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 1
    },
    {
      "rank": 3,
      "ticker": "PPG",
      "signal": "buy",
      "confidence": 0.9,
      "rationale": "PPG reported record Q3 EPS of $2.25, raised full-year guidance to $7.90-$8.10, and organic sales grew 5% YoY. With +11% 1M momentum, P/E 16.9, and a buy consensus, it offers strong value and growth.",
      "drivers": [
        "+11% 1M momentum",
        "P/E 16.9",
        "record Q3 EPS and raised guidance",
        "buy analyst consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "materials",
      "from_group_name": "Materials",
      "group_rank": 1
    },
    {
      "rank": 4,
      "ticker": "TGT",
      "signal": "strong_buy",
      "confidence": 0.9,
      "rationale": "Target surged +110% 1Y, +81% YTD, with Q3 comp sales +5.6% and EPS $2.65 vs $1.51, raised full-year guidance; P/E 15.63 is attractive for the growth.",
      "drivers": [
        "+110% 1-year return",
        "Q3 earnings beat",
        "raised FY guidance",
        "P/E 15.63"
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
      "rank": 5,
      "ticker": "UPS",
      "signal": "buy",
      "confidence": 0.9,
      "rationale": "UPS beat Q3 earnings with $1.69 adj. EPS vs $1.63 est., raised full-year guidance to ~$92.6B revenue; P/E 20.9, 6.05% dividend, +12.1% 1M momentum.",
      "drivers": [
        "earnings beat & raised guidance",
        "P/E 20.9",
        "6.05% dividend yield",
        "+12.1% 1-month return"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 1
    },
    {
      "rank": 6,
      "ticker": "VZ",
      "signal": "strong_buy",
      "confidence": 0.9,
      "rationale": "YTD +24.13% and 1-year +24%, with a low P/E of 11.85, high dividend yield of 6.09%, and beta of 0.26, indicating strong value and stability.",
      "drivers": [
        "+24% YTD return",
        "P/E 11.85",
        "dividend yield 6.09%",
        "low beta 0.26"
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
      "rank": 7,
      "ticker": "WMB",
      "signal": "strong_buy",
      "confidence": 0.9,
      "rationale": "YTD +11%, P/E 25.8, strong_buy consensus. Q3 adj. EBITDA $2.04B (+6% YoY), closed Momentum Midstream acquisition, and expanded storage/pipeline projects [investor.williams.com].",
      "drivers": [
        "strong_buy consensus (1.40)",
        "Q3 EBITDA +6% YoY",
        "Momentum Midstream acquisition",
        "storage expansion"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 2
    },
    {
      "rank": 8,
      "ticker": "EXR",
      "signal": "strong_buy",
      "confidence": 0.85,
      "rationale": "Q3 Core FFO +4.3% YoY, same-store NOI +4.6%, occupancy 94.0%, and net income +50% per share; YTD +25.5% with 1M +10.8% momentum [extraspace.com](https://news.extraspace.com/press-releases/press-release-details/2026/Extra-Space-Storage-Inc--Reports-2026-Third-Quarter-Results/default.aspx).",
      "drivers": [
        "+25.5% YTD",
        "Core FFO +4.3% YoY",
        "same-store NOI +4.6%",
        "analyst buy"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 1
    },
    {
      "rank": 9,
      "ticker": "LNT",
      "signal": "strong_buy",
      "confidence": 0.85,
      "rationale": "Q3 EPS $1.52 vs $1.09, raised guidance to top half, 19% capex increase to $15.9B, P/E 20.19, YTD +14.1%.",
      "drivers": [
        "Q3 EPS beat",
        "Capex +19% to $15.9B",
        "Rate stability through 2030",
        "Analyst buy score 2.0"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "utilities",
      "from_group_name": "Utilities",
      "group_rank": 1
    },
    {
      "rank": 10,
      "ticker": "MSI",
      "signal": "buy",
      "confidence": 0.85,
      "rationale": "MSI has strong momentum with +9.16% 1M and +40.27% YTD, supported by a Q3 earnings beat (sales +12%) and an 11% dividend increase, with a P/E of 42.63 and a buy rating.",
      "drivers": [
        "+9.16% 1M",
        "+40.27% YTD",
        "P/E 42.63",
        "earnings beat & dividend hike"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 1
    },
    {
      "rank": 11,
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
      "rank": 12,
      "ticker": "CPAY",
      "signal": "buy",
      "confidence": 0.85,
      "rationale": "+49% YTD, P/E 24, buy consensus, strong 1m momentum of +12%.",
      "drivers": [
        "+49% YTD",
        "P/E 24",
        "buy consensus",
        "1m +12%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 2
    },
    {
      "rank": 13,
      "ticker": "CRH",
      "signal": "strong_buy",
      "confidence": 0.85,
      "rationale": "CRH has a strong_buy consensus (score 1.35), +10% 1M rebound, and a reasonable P/E of 17.4 despite a YTD decline. Recent momentum and low valuation make it attractive.",
      "drivers": [
        "strong_buy analyst consensus",
        "+10% 1M momentum",
        "P/E 17.4",
        "YTD -24.8% offers value entry"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "materials",
      "from_group_name": "Materials",
      "group_rank": 2
    },
    {
      "rank": 14,
      "ticker": "DLTR",
      "signal": "strong_buy",
      "confidence": 0.85,
      "rationale": "Dollar Tree reported Q3 revenue +6.9%, comp sales +4.6%, raised FY adjusted EPS to $8.05-$8.25; stock +46% 1Y, +23.8% 1M, P/E 16.94.",
      "drivers": [
        "Q3 revenue +6.9%",
        "raised FY EPS outlook",
        "+23.8% 1-month",
        "P/E 16.94"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 2
    },
    {
      "rank": 15,
      "ticker": "LYV",
      "signal": "strong_buy",
      "confidence": 0.85,
      "rationale": "Exceptional 1-year return of +42% and YTD +26.37%, with strong recent momentum (1M +6.40%, 1W +4.16%) and a buy analyst consensus (score 1.64).",
      "drivers": [
        "+42% 1-year return",
        "+26.37% YTD",
        "buy analyst",
        "1M +6.40%"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 2
    },
    {
      "rank": 16,
      "ticker": "MAS",
      "signal": "buy",
      "confidence": 0.85,
      "rationale": "Masco has strong YTD +34.3%, P/E 18.5, +13.1% 1M momentum, and analyst buy consensus.",
      "drivers": [
        "YTD +34.3%",
        "P/E 18.5",
        "+13.1% 1-month return",
        "low valuation"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 2
    },
    {
      "rank": 17,
      "ticker": "KIM",
      "signal": "strong_buy",
      "confidence": 0.82,
      "rationale": "Record portfolio occupancy 96.6%, same-property NOI +4.9%, FFO per share +6.8% YoY, and raised 2026 guidance; YTD +33% with 1M +9% [kimcorealty.com](https://investors.kimcorealty.com/news/detail/606/kimco-realty-announces-third-quarter-2026-results).",
      "drivers": [
        "+33% YTD",
        "record occupancy 96.6%",
        "FFO +6.8% YoY",
        "raised guidance"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 2
    },
    {
      "rank": 18,
      "ticker": "DRI",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "+38% 1Y, +32% YTD, P/E 22.55, low beta 0.634, strong momentum in restaurants.",
      "drivers": [
        "+38% 1Y return",
        "+32% YTD",
        "P/E 22.55",
        "low beta 0.634"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 1
    },
    {
      "rank": 19,
      "ticker": "GEN",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "GEN shows exceptional near-term momentum with +23.20% 1M and +17.11% YTD, a low P/E of 15.25, and a buy rating, making it a resilient value play amid tech sell-offs.",
      "drivers": [
        "+23.20% 1M",
        "+17.11% YTD",
        "P/E 15.25",
        "buy rating"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 2
    },
    {
      "rank": 20,
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
      "rank": 21,
      "ticker": "RCL",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "+22% 1Y, +14% YTD, +13.4% 1M, P/E 18.17, analyst buy consensus 1.52, cruise demand catalyst.",
      "drivers": [
        "+22% 1Y",
        "+13.4% 1M",
        "P/E 18.17",
        "buy consensus 1.52"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 2
    },
    {
      "rank": 22,
      "ticker": "GPN",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "+26% YTD, 1m +15%, Q3 adjusted EPS beat, raised synergy outlook to $650M.",
      "drivers": [
        "+26% YTD",
        "1m +15%",
        "earnings beat",
        "raised synergy outlook"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 3
    },
    {
      "rank": 23,
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
      "rank": 24,
      "ticker": "VLTO",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "Veralto shows +15.2% 1M, YTD +21.4%, P/E 29.1, analyst buy, and low beta 0.67.",
      "drivers": [
        "+15.2% 1-month return",
        "YTD +21.4%",
        "low beta 0.67",
        "analyst buy"
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
      "rank": 25,
      "ticker": "WEC",
      "signal": "strong_buy",
      "confidence": 0.8,
      "rationale": "Q3 net income $1.18/share vs $0.83, raised guidance to $5.60-$5.64, P/E 21.32, YTD +14.8%.",
      "drivers": [
        "Q3 EPS beat",
        "Guidance raised",
        "Retail electricity deliveries +3.3%",
        "Analyst buy"
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
      "rank": 26,
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
      "rank": 27,
      "ticker": "MRSH",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "+19% YTD, P/E 25, buy consensus, strong 1m momentum of +9.5%.",
      "drivers": [
        "+19% YTD",
        "P/E 25",
        "buy consensus",
        "1m +9.5%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 4
    },
    {
      "rank": 28,
      "ticker": "DIS",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "Solid double-digit YTD (+10.37%) and 1-year (+20%) returns, strong recent momentum (1M +10.97%, 1W +4.76%), and a favourable analyst score of 1.56.",
      "drivers": [
        "+10.37% YTD",
        "+20% 1-year",
        "analyst score 1.56",
        "1M +10.97%"
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
      "rank": 29,
      "ticker": "ICE",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "+10% YTD, record North American power futures OI catalyst, buy consensus.",
      "drivers": [
        "+10% YTD",
        "record power futures OI",
        "buy consensus",
        "1m +9.3%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 5
    },
    {
      "rank": 30,
      "ticker": "NUE",
      "signal": "strong_buy",
      "confidence": 0.8,
      "rationale": "Nucor is rated strong_buy (score 1.47), with +47.6% YTD and a low P/E of 15.8. Despite a slight 1M dip, the steelmaker's strong fundamentals and analyst support stand out.",
      "drivers": [
        "strong_buy analyst consensus",
        "+47.6% YTD",
        "P/E 15.8",
        "low short interest 2.58%"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "materials",
      "from_group_name": "Materials",
      "group_rank": 5
    },
    {
      "rank": 31,
      "ticker": "AMT",
      "signal": "strong_buy",
      "confidence": 0.8,
      "rationale": "Proposed $525M settlement with DISH/EchoStar enhances financial flexibility; strong_buy rating, P/E 25.25, YTD +7.8% [americantower.gcs-web.com](https://americantower.gcs-web.com/news-releases/news-release-details/american-tower-announces-proposed-settlement-dishechostar).",
      "drivers": [
        "$525M settlement",
        "strong_buy rating",
        "P/E 25.25",
        "telecom tower demand"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 7
    },
    {
      "rank": 32,
      "ticker": "PSA",
      "signal": "buy",
      "confidence": 0.78,
      "rationale": "YTD +32.3%, 1M +8.1%, P/E 34.75 with 3.6% dividend; self-storage tailwinds mirroring EXR's strong Q3 results.",
      "drivers": [
        "+32.3% YTD",
        "1M +8.1%",
        "self-storage demand",
        "analyst buy"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 3
    },
    {
      "rank": 33,
      "ticker": "SPG",
      "signal": "buy",
      "confidence": 0.76,
      "rationale": "YTD +29.1%, 1M +8.1%, P/E 16.39 (lowest among top retail REITs), 4.1% dividend; strong consumer spending supports mall traffic.",
      "drivers": [
        "+29.1% YTD",
        "P/E 16.39",
        "1M +8.1%",
        "retail strength"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 4
    },
    {
      "rank": 34,
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
      "rank": 35,
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
      "rank": 36,
      "ticker": "PNR",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "Pentair surged +29.1% in 1M, P/E 19.1, analyst buy, despite YTD -31.4% offering a value rebound play.",
      "drivers": [
        "+29.1% 1-month return",
        "P/E 19.1",
        "value rebound",
        "analyst buy"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 4
    },
    {
      "rank": 37,
      "ticker": "TKO",
      "signal": "strong_buy",
      "confidence": 0.75,
      "rationale": "Strong analyst consensus (strong_buy, score 1.41) and robust 1-month momentum of +10.64%, with a 1-day gain of +2.33%.",
      "drivers": [
        "strong_buy analyst",
        "1M +10.64%",
        "score 1.41",
        "1D +2.33%"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 4
    },
    {
      "rank": 38,
      "ticker": "CVX",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "YTD +39%, P/E 15.1, div 3.5%, beta 0.45. Solid integrated major with strong YTD returns and reasonable valuation.",
      "drivers": [
        "YTD +39%",
        "div yield 3.5%",
        "P/E 15.1",
        "beta 0.45"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 5
    },
    {
      "rank": 39,
      "ticker": "LH",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "YTD +51%, 1M +14%, P/E 30.5, analyst buy score 1.59; strong revenue growth and margin expansion.",
      "drivers": [
        "+51% YTD",
        "+14% 1M",
        "P/E 30.5",
        "analyst buy"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "health-care",
      "from_group_name": "Health Care",
      "group_rank": 5
    },
    {
      "rank": 40,
      "ticker": "AON",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "Completed USI acquisition, 1m +13.8%, P/E 18, buy consensus.",
      "drivers": [
        "USI acquisition completed",
        "1m +13.8%",
        "P/E 18",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 6
    },
    {
      "rank": 41,
      "ticker": "EQIX",
      "signal": "strong_buy",
      "confidence": 0.75,
      "rationale": "YTD +31.2%, 1Y +34%, strong_buy rating; data center REIT benefiting from AI/cloud demand despite high P/E of 60.",
      "drivers": [
        "+31.2% YTD",
        "strong_buy rating",
        "data center demand",
        "1Y +34%"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 8
    },
    {
      "rank": 42,
      "ticker": "A",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "Q4 FY26 revenue $2.04B (+9.6%), non-GAAP EPS $1.86 (+17%), FY27 guidance $8.0-8.15B; P/E 34.7, analyst buy. [investor.agilent.com]",
      "drivers": [
        "+9.6% Q4 revenue",
        "raised FY27 guidance",
        "+34% YTD",
        "analyst buy"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "health-care",
      "from_group_name": "Health Care",
      "group_rank": 9
    },
    {
      "rank": 43,
      "ticker": "BLK",
      "signal": "strong_buy",
      "confidence": 0.75,
      "rationale": "Strong_buy consensus, P/E 26, YTD +7.4%, asset management leader.",
      "drivers": [
        "strong_buy consensus",
        "P/E 26",
        "YTD +7.4%",
        "market leader"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 9
    },
    {
      "rank": 44,
      "ticker": "MSCI",
      "signal": "strong_buy",
      "confidence": 0.75,
      "rationale": "Strong_buy consensus, YTD +13.8%, 1m +3%, P/E 33.",
      "drivers": [
        "strong_buy consensus",
        "YTD +13.8%",
        "1m +3%",
        "P/E 33"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 10
    },
    {
      "rank": 45,
      "ticker": "DOC",
      "signal": "buy",
      "confidence": 0.74,
      "rationale": "YTD +33.4%, 1M +5.8%, 1W +4.7%, dividend 6.1%; health care REIT benefiting from aging demographics and stable occupancy.",
      "drivers": [
        "+33.4% YTD",
        "1M +5.8%",
        "dividend 6.1%",
        "analyst buy"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 5
    },
    {
      "rank": 46,
      "ticker": "VICI",
      "signal": "buy",
      "confidence": 0.72,
      "rationale": "P/E 11.19 (cheapest in peer group), dividend 7.6%, 1M +3.1%, 1D +2.5%; experiential REIT with high yield and buy rating.",
      "drivers": [
        "P/E 11.19",
        "dividend 7.6%",
        "1M +3.1%",
        "analyst buy"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 6
    },
    {
      "rank": 47,
      "ticker": "CMG",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "+30.4% 1M, P/E 33.88, analyst buy, strong short-term momentum despite flat YTD.",
      "drivers": [
        "+30.4% 1M",
        "P/E 33.88",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 3
    },
    {
      "rank": 48,
      "ticker": "TSCO",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "+22% 1M, P/E 20.2, low beta 0.484, defensive retailer with dividend 2.56%.",
      "drivers": [
        "+22% 1M",
        "P/E 20.2",
        "low beta 0.484",
        "div 2.56%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 4
    },
    {
      "rank": 49,
      "ticker": "VRSN",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "VRSN has strong YTD performance (+33.48%) and positive 1M (+3.03%) and 1W (+3.78%) moves, with a low beta of 0.67, a P/E of 33.79, and a buy rating.",
      "drivers": [
        "+33.48% YTD",
        "+3.03% 1M",
        "beta 0.67",
        "buy rating"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 4
    },
    {
      "rank": 50,
      "ticker": "DG",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "Dollar General +35% 1Y, +8% 1M, P/E 17.43, dividend 1.76%, analyst buy (score 2.34); value and momentum play.",
      "drivers": [
        "+35% 1-year",
        "+8% 1-month",
        "P/E 17.43",
        "analyst buy"
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
      "rank": 51,
      "ticker": "ES",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "Updated 2026 guidance to $4.62-$4.70, reaffirmed 5-7% long-term growth, P/E 18.85, YTD +10.5%.",
      "drivers": [
        "Guidance updated",
        "Long-term growth 5-7%",
        "Div yield 4.41%",
        "Analyst hold but improving"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "utilities",
      "from_group_name": "Utilities",
      "group_rank": 5
    },
    {
      "rank": 52,
      "ticker": "IR",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "Ingersoll Rand gained +11.3% 1M, P/E 23.5, YTD +4.1%, analyst buy, with steady momentum.",
      "drivers": [
        "+11.3% 1-month return",
        "P/E 23.5",
        "analyst buy",
        "steady momentum"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 5
    },
    {
      "rank": 53,
      "ticker": "LOW",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "+16.6% 1M, P/E 18.97, low beta 0.811, home improvement demand, analyst buy.",
      "drivers": [
        "+16.6% 1M",
        "P/E 18.97",
        "low beta 0.811",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 5
    },
    {
      "rank": 54,
      "ticker": "DUK",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "YTD +15.4%, 1M +6.1%, P/E 18.85, div 3.35%, analyst buy score 2.13, large cap stable.",
      "drivers": [
        "YTD +15.4%",
        "P/E 18.85",
        "Div yield 3.35%",
        "Analyst buy"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "utilities",
      "from_group_name": "Utilities",
      "group_rank": 6
    },
    {
      "rank": 55,
      "ticker": "ECL",
      "signal": "strong_buy",
      "confidence": 0.7,
      "rationale": "Ecolab has a strong_buy consensus (score 1.42), +6.3% 1M, and +17.9% YTD. Recent quarterly results showed accelerating sales, though RSI of 78.6 suggests overbought conditions.",
      "drivers": [
        "strong_buy analyst consensus",
        "+6.3% 1M momentum",
        "+17.9% YTD",
        "accelerating sales growth"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "materials",
      "from_group_name": "Materials",
      "group_rank": 6
    },
    {
      "rank": 56,
      "ticker": "EOG",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "YTD +41%, P/E 9.4, div 3.0%, beta 0.27. Low P/E and strong YTD performance with capital discipline.",
      "drivers": [
        "P/E 9.4",
        "YTD +41%",
        "div yield 3.0%",
        "beta 0.27"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 6
    },
    {
      "rank": 57,
      "ticker": "COP",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "YTD +43%, P/E 13.9, div 2.8%, beta 0.16. Strong YTD and 1-year returns with low beta and reasonable valuation.",
      "drivers": [
        "YTD +43%",
        "P/E 13.9",
        "beta 0.16",
        "1-year +60%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 7
    },
    {
      "rank": 58,
      "ticker": "JKHY",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "+0.6% YTD, 1m +9.2%, P/E 23.6, buy consensus, low beta 0.54.",
      "drivers": [
        "1m +9.2%",
        "P/E 23.6",
        "buy consensus",
        "low beta 0.54"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 7
    },
    {
      "rank": 59,
      "ticker": "T",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "Attractive valuation with P/E 11.93 and dividend yield 4.98%, plus strong recent momentum (1M +9.74%, 1D +2.60%) and a buy analyst rating.",
      "drivers": [
        "P/E 11.93",
        "dividend 4.98%",
        "1M +9.74%",
        "buy analyst"
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
      "rank": 60,
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
      "rank": 61,
      "ticker": "FRT",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "YTD +17.2%, P/E 22.11, dividend 4.2%, short interest 0.03% (near zero); retail REIT with stable occupancy and analyst buy (1.89).",
      "drivers": [
        "+17.2% YTD",
        "short interest 0.03%",
        "P/E 22.11",
        "analyst buy"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 10
    },
    {
      "rank": 62,
      "ticker": "WY",
      "signal": "strong_buy",
      "confidence": 0.68,
      "rationale": "Strong_buy rating (score 1.5), 1M +3.2%, 1D +2.3%, dividend 4.3%; timber REIT undervalued with YTD -12.8% offering turnaround potential.",
      "drivers": [
        "strong_buy rating",
        "1M +3.2%",
        "dividend 4.3%",
        "value play"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 9
    },
    {
      "rank": 63,
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
      "rank": 64,
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
      "rank": 65,
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
      "rank": 66,
      "ticker": "TPR",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "+16.3% 1M, P/E 16.28, analyst buy, luxury goods with pricing power.",
      "drivers": [
        "+16.3% 1M",
        "P/E 16.28",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 6
    },
    {
      "rank": 67,
      "ticker": "EW",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "YTD +24%, 1M +17%, analyst buy score 1.53; strong momentum in structural heart despite P/E 61.",
      "drivers": [
        "+24% YTD",
        "+17% 1M",
        "analyst buy",
        "market leader"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "health-care",
      "from_group_name": "Health Care",
      "group_rank": 7
    },
    {
      "rank": 68,
      "ticker": "KMI",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "YTD +16%, P/E 18.9, div 3.9%, beta 0.57. Stable midstream cash flows with attractive dividend yield.",
      "drivers": [
        "div yield 3.9%",
        "YTD +16%",
        "P/E 18.9",
        "beta 0.57"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 8
    },
    {
      "rank": 69,
      "ticker": "VMC",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "Vulcan Materials gained +9% in the past month and +3.5% in the past week, with a P/E of 33.4. No analyst rating, but strong recent momentum and construction demand support the pick.",
      "drivers": [
        "+9% 1M momentum",
        "+3.5% 1W momentum",
        "P/E 33.4",
        "YTD -2% near breakeven"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "materials",
      "from_group_name": "Materials",
      "group_rank": 8
    },
    {
      "rank": 70,
      "ticker": "EVRG",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "YTD +23.4%, 1M +3.9%, P/E 19.38, div 3.32%, analyst buy score 1.81.",
      "drivers": [
        "YTD +23.4%",
        "P/E 19.38",
        "Div yield 3.32%",
        "Analyst buy"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "utilities",
      "from_group_name": "Utilities",
      "group_rank": 9
    },
    {
      "rank": 71,
      "ticker": "MLM",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "Martin Marietta Materials has a buy consensus, +4.4% 1M and +4.3% 1W momentum. P/E of 38.9 is elevated, but the stock is recovering from YTD losses of -16.7%.",
      "drivers": [
        "+4.4% 1M momentum",
        "+4.3% 1W momentum",
        "buy analyst consensus",
        "YTD -16.7% recovery potential"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "materials",
      "from_group_name": "Materials",
      "group_rank": 9
    },
    {
      "rank": 72,
      "ticker": "OKE",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "YTD +20%, P/E 13.0, div 5.1%, beta 0.74. High dividend yield and reasonable P/E in midstream space.",
      "drivers": [
        "div yield 5.1%",
        "P/E 13.0",
        "YTD +20%",
        "beta 0.74"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 9
    },
    {
      "rank": 73,
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
      "rank": 74,
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
      "rank": 75,
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
      "rank": 76,
      "ticker": "DPZ",
      "signal": "buy",
      "confidence": 0.6,
      "rationale": "+13.8% 1M, P/E 19.57, dividend 2.24%, analyst buy, value in restaurants.",
      "drivers": [
        "+13.8% 1M",
        "P/E 19.57",
        "div 2.24%",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 7
    },
    {
      "rank": 77,
      "ticker": "TSN",
      "signal": "buy",
      "confidence": 0.6,
      "rationale": "Tyson Foods +15% 1Y, +12.5% 1M, dividend 3.3%, P/E 49.18 but recent momentum strong; analyst hold but improving fundamentals.",
      "drivers": [
        "+12.5% 1-month",
        "dividend 3.3%",
        "recent momentum",
        "P/E 49.18"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 7
    },
    {
      "rank": 78,
      "ticker": "AWK",
      "signal": "buy",
      "confidence": 0.6,
      "rationale": "YTD +18.5%, 1M +6.8%, P/E 25.48, div 2.43%, strong momentum in regulated water.",
      "drivers": [
        "YTD +18.5%",
        "1M +6.8%",
        "Regulated water utility",
        "Analyst hold"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "utilities",
      "from_group_name": "Utilities",
      "group_rank": 8
    },
    {
      "rank": 79,
      "ticker": "WYNN",
      "signal": "strong_buy",
      "confidence": 0.6,
      "rationale": "strong_buy consensus (score 1.29), +13.7% 1M, P/E 23.54, Macau recovery catalyst.",
      "drivers": [
        "strong_buy consensus",
        "+13.7% 1M",
        "P/E 23.54"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 8
    },
    {
      "rank": 80,
      "ticker": "CHTR",
      "signal": "buy",
      "confidence": 0.6,
      "rationale": "Recent 1-month surge of +32.97% and 1-day +6.21%, supported by a new operating model targeting $2B in cost savings and strong mobile subscriber growth.",
      "drivers": [
        "1M +32.97%",
        "1D +6.21%",
        "cost savings catalyst",
        "mobile subscriber growth"
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
      "rank": 81,
      "ticker": "EQT",
      "signal": "strong_buy",
      "confidence": 0.6,
      "rationale": "YTD -7%, P/E 11.5, strong_buy consensus. Q3 free cash flow $283M, announced Range Resources acquisition and 10-year LNG deal with Ignitis [ir.eqt.com]. Turnaround catalyst.",
      "drivers": [
        "strong_buy consensus (1.50)",
        "P/E 11.5",
        "Range Resources acquisition",
        "LNG sales agreement"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 10
    },
    {
      "rank": 82,
      "ticker": "DD",
      "signal": "buy",
      "confidence": 0.55,
      "rationale": "DuPont +10.6% 1M, YTD +24.5%, analyst buy, but P/E 52.7 is elevated; growth priced in.",
      "drivers": [
        "+10.6% 1-month return",
        "YTD +24.5%",
        "analyst buy",
        "high P/E 52.7"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 8
    },
    {
      "rank": 83,
      "ticker": "HRL",
      "signal": "buy",
      "confidence": 0.55,
      "rationale": "Hormel Foods +7% 1Y, +11.1% 1M, dividend 5.07%, P/E 37.23; high yield and recent uptick in momentum.",
      "drivers": [
        "+11.1% 1-month",
        "dividend 5.07%",
        "P/E 37.23"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 8
    },
    {
      "rank": 84,
      "ticker": "TYL",
      "signal": "buy",
      "confidence": 0.55,
      "rationale": "TYL has positive 1M (+6.76%) and 1W (+0.75%) moves, a low beta of 0.73, a buy rating, and a P/E of 50.78, with YTD -5.36% but recent uptick.",
      "drivers": [
        "+6.76% 1M",
        "beta 0.73",
        "buy rating",
        "P/E 50.78"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 8
    },
    {
      "rank": 85,
      "ticker": "MGM",
      "signal": "buy",
      "confidence": 0.5,
      "rationale": "+20.3% 1M, low P/E 12.96, but Morgan Stanley cut target to $28 and Q3 miss; high short interest 17.42%.",
      "drivers": [
        "+20.3% 1M",
        "P/E 12.96",
        "high short 17.42%",
        "analyst mixed"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 9
    },
    {
      "rank": 86,
      "ticker": "ROL",
      "signal": "buy",
      "confidence": 0.5,
      "rationale": "Rollins +10.8% 1M, analyst buy, but P/E 35.0 and short interest 9.25% indicate risk.",
      "drivers": [
        "+10.8% 1-month return",
        "analyst buy",
        "high short interest 9.25%",
        "P/E 35.0"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 9
    },
    {
      "rank": 87,
      "ticker": "CDW",
      "signal": "buy",
      "confidence": 0.5,
      "rationale": "CDW has stable momentum with +0.57% 1M and +0.67% 1W, a strong YTD of +25.23%, a low P/E of 19.84, and a buy rating, offering consistent performance.",
      "drivers": [
        "+25.23% YTD",
        "P/E 19.84",
        "buy rating",
        "stable 1M/1W"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 10
    },
    {
      "rank": 88,
      "ticker": "CLX",
      "signal": "buy",
      "confidence": 0.5,
      "rationale": "Clorox +24.9% 1M, P/E 18.72, dividend 4.8%, Q1 earnings beat; analyst hold but strong short-term catalyst from earnings.",
      "drivers": [
        "+24.9% 1-month",
        "dividend 4.8%",
        "Q1 earnings beat",
        "P/E 18.72"
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
      "rank": 89,
      "ticker": "SHW",
      "signal": "buy",
      "confidence": 0.5,
      "rationale": "Sherwin-Williams reported Q3 sales up 7.9% and narrowed FY26 EPS guidance to $11.85-$12.15. With +5.4% 1M and a buy rating, but RSI of 71.4 signals overbought risk.",
      "drivers": [
        "+5.4% 1M momentum",
        "Q3 sales +7.9%",
        "buy analyst consensus",
        "RSI 71.4 overbought caution"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "materials",
      "from_group_name": "Materials",
      "group_rank": 10
    },
    {
      "rank": 90,
      "ticker": "CVNA",
      "signal": "buy",
      "confidence": 0.4,
      "rationale": "+16.5% 1M, but high beta 3.65, P/E 32.6, short interest 12.1%, risky momentum play.",
      "drivers": [
        "+16.5% 1M",
        "high beta 3.65",
        "P/E 32.6",
        "short 12.1%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 10
    }
  ],
  "momentum_picks": [],
  "previous_picks": [
    {
      "rank": 1,
      "ticker": "TRGP",
      "signal": "strong_buy",
      "confidence": 0.95,
      "rationale": "Strong buy with +54.47% YTD, P/E 24.54, and analyst strong_buy score 1.27; news of 20% dividend increase for 2027 and record Permian volumes.",
      "drivers": [
        "+54.47% YTD",
        "strong_buy analyst 1.27",
        "20% dividend increase",
        "record Permian volumes"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 1
    },
    {
      "rank": 2,
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
      "rank": 3,
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
      "rank": 4,
      "ticker": "CVX",
      "signal": "buy",
      "confidence": 0.9,
      "rationale": "Buy with +38.77% YTD, P/E 15.14, beta 0.453, and low short interest 1.35%; strong integrated major with solid fundamentals.",
      "drivers": [
        "+38.77% YTD",
        "low beta 0.453",
        "low short interest 1.35%",
        "P/E 15.14"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 2
    },
    {
      "rank": 5,
      "ticker": "TKO",
      "signal": "strong_buy",
      "confidence": 0.9,
      "rationale": "Strong buy rating (score 1.41) and solid momentum: +10.64% 1M, +2.33% 1D, YTD -7.35%; low beta 0.65.",
      "drivers": [
        "strong_buy analyst",
        "+10.64% 1M",
        "low beta 0.65",
        "+2.33% 1D"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 2
    },
    {
      "rank": 6,
      "ticker": "CPAY",
      "signal": "strong_buy",
      "confidence": 0.85,
      "rationale": "Corpay has surged +53% over 1Y and +49% YTD, with a +12% 1M gain, P/E 24.17, and a strong buy consensus (an_score 1.69).",
      "drivers": [
        "+53% 1Y return",
        "+49% YTD",
        "strong_buy consensus",
        "low P/E 24.17"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 1
    },
    {
      "rank": 7,
      "ticker": "CRH",
      "signal": "strong_buy",
      "confidence": 0.85,
      "rationale": "Strong buy consensus (an_score 1.35), +10.09% 1M momentum, P/E 17.38; Q3 2026 results showed resilient performance and a new $6B buyback program despite a challenging cost environment [crh.com](https://www.crh.com/media/press-releases/2026/crh-reports-third-quarter-2026-results/).",
      "drivers": [
        "strong_buy consensus",
        "P/E 17.38",
        "+10.09% 1M",
        "$6B buyback program"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "materials",
      "from_group_name": "Materials",
      "group_rank": 1
    },
    {
      "rank": 8,
      "ticker": "DLTR",
      "signal": "strong_buy",
      "confidence": 0.85,
      "rationale": "Revenue up 6.9% to $5.1B, comp sales +4.6% with traffic accelerating 3.8%; raised FY2026 adjusted EPS outlook to $8.05-$8.25, P/E 16.9, +46% 1Y return.",
      "drivers": [
        "Strong Q3 earnings beat",
        "Raised guidance",
        "Accelerating traffic growth",
        "Attractive P/E 16.9"
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
      "rank": 9,
      "ticker": "KIM",
      "signal": "strong_buy",
      "confidence": 0.85,
      "rationale": "Kimco Realty shows +32.98% YTD, record 96.6% occupancy, and raised 2026 FFO guidance to $1.84-$1.86 per share, with a 7.7% dividend increase and $295M acquisition of grocery-anchored centers at a 6% cap rate.",
      "drivers": [
        "+32.98% YTD",
        "record 96.6% occupancy",
        "raised FFO guidance",
        "7.7% dividend increase"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 1
    },
    {
      "rank": 10,
      "ticker": "MSI",
      "signal": "strong_buy",
      "confidence": 0.85,
      "rationale": "MSI has strong momentum with +40.27% YTD, +9.16% 1M, and a recent 11% dividend increase, supported by a buy analyst consensus (score 1.64) and low beta of 0.87.",
      "drivers": [
        "+40.27% YTD",
        "+9.16% 1M",
        "11% dividend hike",
        "low beta 0.87"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 1
    },
    {
      "rank": 11,
      "ticker": "RCL",
      "signal": "buy",
      "confidence": 0.85,
      "rationale": "RCL shows strong momentum with +14.22% YTD, +13.42% 1M, and +3.62% 1D, supported by a P/E of 18.17 and a buy consensus (an_score 1.52).",
      "drivers": [
        "+14% YTD",
        "P/E 18.2",
        "buy consensus",
        "strong 1M momentum"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 1
    },
    {
      "rank": 12,
      "ticker": "UPS",
      "signal": "strong_buy",
      "confidence": 0.85,
      "rationale": "Q3 earnings beat with adj. EPS $1.69 vs $1.63 est., revenue +6.7% to $22.9B, raised full-year guidance to ~$92.6B revenue and adj. EPS ~$7.28; multiple analysts raised PTs (Citi to $131, Truist to $120) citing sustained earnings recovery; YTD +16.6%, P/E 20.9, div yield 6.05%.",
      "drivers": [
        "Q3 beat & raised guidance",
        "multiple PT upgrades",
        "strong YTD +16.6%",
        "P/E 20.9, div 6.05%"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 1
    },
    {
      "rank": 13,
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
      "rank": 14,
      "ticker": "COP",
      "signal": "buy",
      "confidence": 0.85,
      "rationale": "Buy with +43.24% YTD, P/E 13.93, beta 0.162, and low short interest 1.35%; excellent momentum and low volatility.",
      "drivers": [
        "+43.24% YTD",
        "low beta 0.162",
        "low short interest 1.35%",
        "P/E 13.93"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 3
    },
    {
      "rank": 15,
      "ticker": "DIS",
      "signal": "buy",
      "confidence": 0.85,
      "rationale": "Buy analyst (score 1.56) with consistent positive momentum: YTD +10.37%, 1M +10.97%, 1W +4.76%; P/E 21.36.",
      "drivers": [
        "+10.37% YTD",
        "+10.97% 1M",
        "buy analyst",
        "P/E 21.36"
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
      "rank": 16,
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
      "rank": 17,
      "ticker": "WMB",
      "signal": "strong_buy",
      "confidence": 0.85,
      "rationale": "Strong_buy with analyst score 1.4, YTD +10.85%, and positive news on Momentum Midstream acquisition and strong Q3 cash flow.",
      "drivers": [
        "strong_buy analyst 1.4",
        "Momentum Midstream acquisition",
        "strong Q3 cash flow",
        "dividend yield 3.21%"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 6
    },
    {
      "rank": 18,
      "ticker": "ECL",
      "signal": "strong_buy",
      "confidence": 0.82,
      "rationale": "Strong buy consensus (an_score 1.42), +17.89% YTD, +6.32% 1M; Mizuho raised price target to $350 on growth outlook from Ecolab 3.0 and data center/semiconductor expansion [investing.com](https://www.investing.com/news/analyst-ratings/mizuho-raises-ecolab-stock-price-target-to-350-on-growth-outlook-93CH-5038634).",
      "drivers": [
        "strong_buy consensus",
        "+17.89% YTD",
        "Mizuho $350 PT",
        "growth engines in data centers"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "materials",
      "from_group_name": "Materials",
      "group_rank": 2
    },
    {
      "rank": 19,
      "ticker": "AIZ",
      "signal": "strong_buy",
      "confidence": 0.82,
      "rationale": "Assurant delivered +43% 1Y and +37% YTD returns, with a +12.4% 1M gain, P/E 15.05, and a strong_buy consensus (an_score 1.43).",
      "drivers": [
        "+43% 1Y",
        "+37% YTD",
        "strong_buy consensus",
        "low P/E 15.05"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 3
    },
    {
      "rank": 20,
      "ticker": "AON",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "Aon completed the $17B USI acquisition on Nov 16, 2026, boosting its middle-market platform; KBW raised its price target to $376 on the deal, and the stock rallied +13.8% in 1M with a buy consensus.",
      "drivers": [
        "+13.8% 1M",
        "USI acquisition catalyst",
        "KBW $376 PT",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 2
    },
    {
      "rank": 21,
      "ticker": "DRI",
      "signal": "strong_buy",
      "confidence": 0.8,
      "rationale": "DRI has delivered +32.38% YTD and +12.64% 1M, with a low beta of 0.634 and a P/E of 22.55, reflecting strong consumer spending in dining.",
      "drivers": [
        "+32% YTD",
        "low beta 0.63",
        "strong 1M momentum",
        "consumer dining demand"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 2
    },
    {
      "rank": 22,
      "ticker": "EXR",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "Extra Space Storage delivered +25.51% YTD, Q3 Core FFO of $2.17 (+4.3% YoY), same-store NOI growth of 4.6%, and repurchased $327M in stock, with strong self-storage demand.",
      "drivers": [
        "+25.51% YTD",
        "Q3 Core FFO $2.17",
        "same-store NOI +4.6%",
        "$327M buyback"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 2
    },
    {
      "rank": 23,
      "ticker": "GEN",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "GEN shows strong recent momentum with +23.20% 1M and +17.11% YTD, a low P/E of 15.25, and a buy analyst consensus (score 2.09), offering value in cybersecurity.",
      "drivers": [
        "+23.20% 1M",
        "P/E 15.25",
        "low valuation",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 2
    },
    {
      "rank": 24,
      "ticker": "TGT",
      "signal": "strong_buy",
      "confidence": 0.8,
      "rationale": "Q3 EPS $2.65 vs $1.51 YoY, net sales +7.1%, comp sales +5.6% with 5% traffic growth; raised full-year sales guidance to ~6%, P/E 15.6.",
      "drivers": [
        "Exceptional earnings beat",
        "Strong traffic and sales growth",
        "Raised guidance",
        "Low P/E 15.6"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 2
    },
    {
      "rank": 25,
      "ticker": "WEC",
      "signal": "strong_buy",
      "confidence": 0.8,
      "rationale": "WEC has +14.75% YTD, +7.17% 1-month, P/E 21.32, and a buy consensus. Q3 net income rose to $1.18/share from $0.83, guidance raised to $5.60-$5.64, driven by weather, capital execution, and operating efficiency.",
      "drivers": [
        "+14.75% YTD",
        "Q3 EPS beat ($1.18 vs $0.83)",
        "raised guidance",
        "buy consensus (2.4)"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "utilities",
      "from_group_name": "Utilities",
      "group_rank": 2
    },
    {
      "rank": 26,
      "ticker": "VZ",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "Excellent fundamentals: YTD +24.13%, P/E 11.85, beta 0.26, dividend 6.09%, with 1M +9.42%.",
      "drivers": [
        "+24.13% YTD",
        "low beta 0.26",
        "high dividend 6.09%",
        "P/E 11.85"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "communication-services",
      "from_group_name": "Communication Services",
      "group_rank": 4
    },
    {
      "rank": 27,
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
      "rank": 28,
      "ticker": "EOG",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "Buy with +41.00% YTD, P/E 9.38, beta 0.269, and dividend yield 3.03%; low P/E and strong production growth.",
      "drivers": [
        "+41.00% YTD",
        "low P/E 9.38",
        "beta 0.269",
        "dividend yield 3.03%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 5
    },
    {
      "rank": 29,
      "ticker": "T",
      "signal": "buy",
      "confidence": 0.8,
      "rationale": "Buy analyst (score 2.08) with solid fundamentals: P/E 11.93, beta 0.49, dividend 4.98%, 1M +9.74%.",
      "drivers": [
        "+9.74% 1M",
        "low beta 0.49",
        "high dividend 4.98%",
        "buy analyst"
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
      "rank": 30,
      "ticker": "DVN",
      "signal": "strong_buy",
      "confidence": 0.8,
      "rationale": "Strong_buy with analyst score 1.32, P/E 9.61, dividend yield 3.13%, and YTD +11.20%; solid fundamentals and strong consensus.",
      "drivers": [
        "strong_buy analyst 1.32",
        "low P/E 9.61",
        "dividend yield 3.13%",
        "YTD +11.20%"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 8
    },
    {
      "rank": 31,
      "ticker": "PNR",
      "signal": "buy",
      "confidence": 0.78,
      "rationale": "Massive 1M reversal +29.1% after YTD -31.4%, P/E 19.1 attractive; strong 1W +6.6% momentum; analyst consensus buy with room for recovery in water treatment demand.",
      "drivers": [
        "1M +29.1% reversal",
        "P/E 19.1",
        "1W +6.6%",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 2
    },
    {
      "rank": 32,
      "ticker": "DUK",
      "signal": "strong_buy",
      "confidence": 0.78,
      "rationale": "Duke Energy has +15.40% YTD, +6.14% 1-month, P/E 18.85, and a buy consensus (an_score 2.13). Strong regulated utility with 3.35% dividend yield and low beta 0.308, benefiting from data centre demand and rate case outcomes.",
      "drivers": [
        "+15.40% YTD",
        "P/E 18.85",
        "low beta 0.308",
        "buy consensus (2.13)"
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
      "rank": 33,
      "ticker": "PPG",
      "signal": "buy",
      "confidence": 0.78,
      "rationale": "Buy consensus (an_score 2.12), +19.23% YTD, +11.14% 1M, P/E 16.94; Q3 2026 record EPS and raised full-year guidance to $7.90-$8.10, driven by aerospace and Latin America coatings [ppg.com](https://news.ppg.com/Press-Releases/news-details/2026/PPG-reports-record-third-quarter-2026-EPS-and-raises-midpoint-of-full-year-EPS-guidance/default.aspx).",
      "drivers": [
        "+19.23% YTD",
        "P/E 16.94",
        "raised FY guidance",
        "record Q3 EPS"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "materials",
      "from_group_name": "Materials",
      "group_rank": 3
    },
    {
      "rank": 34,
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
      "rank": 35,
      "ticker": "MRSH",
      "signal": "buy",
      "confidence": 0.78,
      "rationale": "Marsh McLennan gained +20% 1Y and +19.4% YTD, with a +9.5% 1M move, P/E 24.77, and a buy consensus; strong organic growth and insurance brokerage tailwinds.",
      "drivers": [
        "+20% 1Y",
        "+19.4% YTD",
        "+9.5% 1M",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 4
    },
    {
      "rank": 36,
      "ticker": "VLTO",
      "signal": "buy",
      "confidence": 0.76,
      "rationale": "1M +15.2%, YTD +21.4%, P/E 29.1 with low beta 0.67; strong momentum in water quality & sustainability; analyst buy rating.",
      "drivers": [
        "1M +15.2%",
        "YTD +21.4%",
        "low beta 0.67",
        "buy consensus"
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
      "rank": 37,
      "ticker": "CMG",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "CMG surged +30.41% in the past month and +3.40% in the past week, with a P/E of 33.88 and a buy consensus, driven by menu innovation and pricing power.",
      "drivers": [
        "+30% 1M",
        "buy consensus",
        "pricing power",
        "menu innovation"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 3
    },
    {
      "rank": 38,
      "ticker": "PSA",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "Public Storage has +32.29% YTD, +8.13% 1-month momentum, a 3.63% dividend yield, and benefits from steady self-storage demand and rate stability.",
      "drivers": [
        "+32.29% YTD",
        "+8.13% 1M",
        "3.63% dividend yield",
        "self-storage demand"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 3
    },
    {
      "rank": 39,
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
      "rank": 40,
      "ticker": "ES",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "Eversource has +10.45% YTD, +7.56% 1-month, P/E 18.85, and a hold consensus (an_score 2.76). Q3 non-GAAP EPS $0.92, guidance raised to $4.62-$4.70, with constructive PURA storm cost decision and 5-7% long-term EPS growth target.",
      "drivers": [
        "+10.45% YTD",
        "raised guidance $4.62-$4.70",
        "P/E 18.85",
        "constructive regulatory decision"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "utilities",
      "from_group_name": "Utilities",
      "group_rank": 4
    },
    {
      "rank": 41,
      "ticker": "SPG",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "Simon Property Group has +29.13% YTD, a low P/E of 16.39, +8.06% 1-month momentum, and benefits from strong retail foot traffic and high-quality mall assets.",
      "drivers": [
        "+29.13% YTD",
        "P/E 16.39",
        "+8.06% 1M",
        "strong retail demand"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 4
    },
    {
      "rank": 42,
      "ticker": "VRSN",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "VRSN has strong momentum with +33.48% YTD, +3.03% 1M, and +3.78% 1W, low beta of 0.67, and a buy analyst consensus (score 2.00).",
      "drivers": [
        "+33.48% YTD",
        "+3.03% 1M",
        "low beta 0.67",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 4
    },
    {
      "rank": 43,
      "ticker": "ICE",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "Intercontinental Exchange rose +14% 1Y and +10.4% YTD, with a +9.3% 1M gain, P/E 23.46, and a buy consensus; benefits from trading volumes and data services.",
      "drivers": [
        "+9.3% 1M",
        "+14% 1Y",
        "buy consensus",
        "P/E 23.46"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 5
    },
    {
      "rank": 44,
      "ticker": "CHTR",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "Despite hold analyst, massive surge: 1M +32.97%, 1D +6.21%, driven by restructuring and $2B cost savings plan [Charter Communications Inc.](https://ir.charter.com/news-releases/news-release-details/charter-announces-third-quarter-2026-results-and-launches-new/); P/E 12.02.",
      "drivers": [
        "+32.97% 1M",
        "+6.21% 1D",
        "restructuring catalyst",
        "P/E 12.02"
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
      "rank": 45,
      "ticker": "EQT",
      "signal": "strong_buy",
      "confidence": 0.75,
      "rationale": "Strong_buy with analyst score 1.5, despite -6.55% YTD, but positive 1d move +1.96% and transformative Range Resources acquisition.",
      "drivers": [
        "strong_buy analyst 1.5",
        "Range Resources acquisition",
        "cost discipline",
        "positive 1d +1.96%"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 7
    },
    {
      "rank": 46,
      "ticker": "LH",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "YTD +50.85%, 1M +14.23%, analyst buy, P/E 30.54, beta 0.83.",
      "drivers": [
        "YTD +50.85%",
        "1M +14.23%",
        "analyst buy",
        "P/E 30.54"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "health-care",
      "from_group_name": "Health Care",
      "group_rank": 8
    },
    {
      "rank": 47,
      "ticker": "KMI",
      "signal": "buy",
      "confidence": 0.75,
      "rationale": "Buy with +16.39% YTD, P/E 18.87, dividend yield 3.89%, and low short interest 2.22%; stable midstream infrastructure play.",
      "drivers": [
        "+16.39% YTD",
        "dividend yield 3.89%",
        "low short interest 2.22%",
        "stable midstream"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "energy",
      "from_group_name": "Energy",
      "group_rank": 9
    },
    {
      "rank": 48,
      "ticker": "MAS",
      "signal": "buy",
      "confidence": 0.74,
      "rationale": "1M +13.1%, YTD +34.3%, P/E 18.5; strong building products demand; analyst buy rating; short interest 4.8% manageable.",
      "drivers": [
        "1M +13.1%",
        "YTD +34.3%",
        "P/E 18.5",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 4
    },
    {
      "rank": 49,
      "ticker": "EIX",
      "signal": "buy",
      "confidence": 0.72,
      "rationale": "Edison International has +7.86% YTD, +7.68% 1-month, P/E 6.63, and a hold consensus (an_score 3.19). Very low P/E and high dividend yield 5.62% offer value, though short interest 5.62% and regulatory risks in California warrant caution.",
      "drivers": [
        "P/E 6.63",
        "high dividend yield 5.62%",
        "+7.68% 1-month",
        "value play"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "utilities",
      "from_group_name": "Utilities",
      "group_rank": 5
    },
    {
      "rank": 50,
      "ticker": "IR",
      "signal": "buy",
      "confidence": 0.72,
      "rationale": "1M +11.3%, YTD +4.1%, P/E 23.5; strong industrial machinery momentum; analyst buy rating; low dividend yield but solid growth profile.",
      "drivers": [
        "1M +11.3%",
        "P/E 23.5",
        "buy consensus",
        "industrial momentum"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 5
    },
    {
      "rank": 51,
      "ticker": "VMC",
      "signal": "buy",
      "confidence": 0.72,
      "rationale": "Buy consensus, +9.05% 1M, +3.45% 1W, P/E 33.37; steady momentum in construction materials with infrastructure demand underpinning recovery.",
      "drivers": [
        "+9.05% 1M",
        "+3.45% 1W",
        "buy consensus",
        "infrastructure demand"
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
      "rank": 52,
      "ticker": "GPN",
      "signal": "buy",
      "confidence": 0.72,
      "rationale": "Global Payments rallied +29% 1Y and +26% YTD, with a +15.2% 1M and +10.5% 1W surge, P/E 163.34 (elevated), but strong momentum and buy consensus.",
      "drivers": [
        "+29% 1Y",
        "+26% YTD",
        "+15.2% 1M",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 6
    },
    {
      "rank": 53,
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
      "rank": 54,
      "ticker": "MGM",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "MGM rallied +20.25% in 1M and +2.91% in 1W, with a P/E of 12.96 and a buy consensus; recent Q3 results showed record MGM China revenue and strong digital growth.",
      "drivers": [
        "+20% 1M",
        "P/E 13.0",
        "buy consensus",
        "record MGM China revenue"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 4
    },
    {
      "rank": 55,
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
      "rank": 56,
      "ticker": "DOC",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "Healthpeak Properties has +33.40% YTD, +5.75% 1-month momentum, a 6.1% dividend yield, and benefits from aging demographics and healthcare real estate demand.",
      "drivers": [
        "+33.40% YTD",
        "6.1% dividend yield",
        "+5.75% 1M",
        "healthcare demand"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 5
    },
    {
      "rank": 57,
      "ticker": "DPZ",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "DPZ gained +13.79% in 1M, with a P/E of 19.57 and a 2.24% dividend yield, supported by a buy consensus and resilient demand in the quick-service restaurant space.",
      "drivers": [
        "+14% 1M",
        "P/E 19.6",
        "dividend 2.2%",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 5
    },
    {
      "rank": 58,
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
      "rank": 59,
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
      "rank": 60,
      "ticker": "LNT",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "Alliant Energy has +14.11% YTD, +5.23% 1-month, P/E 20.19, and a buy consensus (an_score 2.0). Steady regulated utility with 2.95% dividend yield, though short interest is elevated at 12.59%.",
      "drivers": [
        "+14.11% YTD",
        "P/E 20.19",
        "buy consensus (2.0)",
        "regulated utility stability"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "utilities",
      "from_group_name": "Utilities",
      "group_rank": 6
    },
    {
      "rank": 61,
      "ticker": "LOW",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "LOW rose +16.56% in 1M and +4.80% in 1W, with a P/E of 18.97 and a buy consensus, benefiting from steady housing demand and home improvement spending.",
      "drivers": [
        "+17% 1M",
        "P/E 19.0",
        "buy consensus",
        "housing demand"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 6
    },
    {
      "rank": 62,
      "ticker": "JKHY",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "Jack Henry & Associates gained +4% 1Y and +0.6% YTD, with a +9.2% 1M rebound, P/E 23.57, and a buy consensus; steady payment processing demand.",
      "drivers": [
        "+9.2% 1M",
        "buy consensus",
        "P/E 23.57",
        "stable fundamentals"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 7
    },
    {
      "rank": 63,
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
      "rank": 64,
      "ticker": "LYV",
      "signal": "buy",
      "confidence": 0.7,
      "rationale": "Buy analyst (score 1.64) with impressive YTD +26.37% and 1M +6.40%, 1W +4.16%.",
      "drivers": [
        "+26.37% YTD",
        "+6.40% 1M",
        "buy analyst",
        "beta 1.16"
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
      "rank": 65,
      "ticker": "AWK",
      "signal": "buy",
      "confidence": 0.68,
      "rationale": "American Water Works has +18.51% YTD, +6.78% 1-month, P/E 25.48, and a hold consensus (an_score 2.83). Strong YTD performance and water utility defensive growth, but high short interest 10.46% and elevated P/E.",
      "drivers": [
        "+18.51% YTD",
        "+6.78% 1-month",
        "defensive water utility",
        "hold consensus (2.83)"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "utilities",
      "from_group_name": "Utilities",
      "group_rank": 7
    },
    {
      "rank": 66,
      "ticker": "ROL",
      "signal": "buy",
      "confidence": 0.68,
      "rationale": "1M +10.8% after YTD -34.4%, P/E 35.0; pest control demand resilient; analyst buy; short interest 9.3% could squeeze.",
      "drivers": [
        "1M +10.8% reversal",
        "buy consensus",
        "pest control demand",
        "short squeeze potential"
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
      "rank": 67,
      "ticker": "TYL",
      "signal": "buy",
      "confidence": 0.68,
      "rationale": "TYL has strong recent momentum with +6.76% 1M and +0.75% 1W, low beta of 0.73, and a buy analyst consensus (score 1.61), despite a -5.36% YTD.",
      "drivers": [
        "+6.76% 1M",
        "low beta 0.73",
        "buy consensus",
        "analyst score 1.61"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "technology",
      "from_group_name": "Technology",
      "group_rank": 7
    },
    {
      "rank": 68,
      "ticker": "FISV",
      "signal": "buy",
      "confidence": 0.68,
      "rationale": "Fiserv surged +21.3% in 1M despite a -4% 1Y return; Tigress Financial reiterated Buy with a $95 PT (62% upside), and Q3 EPS beat estimates at $1.75 vs $1.72.",
      "drivers": [
        "+21.3% 1M",
        "Tigress $95 PT",
        "EPS beat",
        "buy consensus"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 8
    },
    {
      "rank": 69,
      "ticker": "DD",
      "signal": "buy",
      "confidence": 0.67,
      "rationale": "1M +10.6%, YTD +24.5%, P/E 52.7 elevated but strong momentum; analyst buy; diversified specialty chemicals exposure.",
      "drivers": [
        "1M +10.6%",
        "YTD +24.5%",
        "buy consensus",
        "diversified industrials"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "industrials",
      "from_group_name": "Industrials",
      "group_rank": 8
    },
    {
      "rank": 70,
      "ticker": "CLX",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "Q1 EPS beat ($1.55 vs $1.07), +24.9% 1M momentum, P/E 18.7, dividend yield 4.8%, ERP implementation largely behind, margins rebuilding.",
      "drivers": [
        "Earnings beat",
        "Strong 1M momentum",
        "Attractive P/E and yield",
        "Operational turnaround"
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
      "rank": 71,
      "ticker": "O",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "Realty Income offers a 5.61% dividend yield, +8.61% YTD, +4.68% 1-month momentum, and a low beta of 0.649, providing stable income from net-lease properties.",
      "drivers": [
        "5.61% dividend yield",
        "+8.61% YTD",
        "low beta 0.649",
        "stable net-lease income"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 6
    },
    {
      "rank": 72,
      "ticker": "TSCO",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "TSCO jumped +22.03% in 1M and +5.00% in 1D, with a P/E of 20.2 and a 2.56% dividend yield, reflecting strong demand in the rural and agricultural retail sector.",
      "drivers": [
        "+22% 1M",
        "P/E 20.2",
        "dividend 2.6%",
        "rural retail demand"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 7
    },
    {
      "rank": 73,
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
      "rank": 74,
      "ticker": "SHW",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "Buy consensus (an_score 2.07), +8.55% YTD, +5.43% 1M, P/E 32.15; steady recovery in specialty chemicals with positive near-term price action.",
      "drivers": [
        "+5.43% 1M",
        "buy consensus",
        "P/E 32.15",
        "specialty chemicals recovery"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "materials",
      "from_group_name": "Materials",
      "group_rank": 8
    },
    {
      "rank": 75,
      "ticker": "TPR",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "TPR advanced +16.25% in 1M and +1.48% in 1W, with a P/E of 16.28 and a buy consensus, driven by luxury accessories demand and brand strength.",
      "drivers": [
        "+16% 1M",
        "P/E 16.3",
        "buy consensus",
        "luxury demand"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 8
    },
    {
      "rank": 76,
      "ticker": "OMC",
      "signal": "buy",
      "confidence": 0.65,
      "rationale": "Buy analyst (score 2.08) with strong YTD +13.16% and 1M +11.78%, but high P/E 88.2.",
      "drivers": [
        "+13.16% YTD",
        "+11.78% 1M",
        "buy analyst",
        "dividend 3.66%"
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
      "rank": 77,
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
      "rank": 78,
      "ticker": "PCG",
      "signal": "buy",
      "confidence": 0.62,
      "rationale": "PG&E has -11.73% YTD but +10.66% 1-month, P/E 10.43, and a buy consensus (an_score 2.06). Low P/E and strong recent momentum, but negative YTD and regulatory overhang from California wildfire liabilities.",
      "drivers": [
        "P/E 10.43",
        "+10.66% 1-month",
        "buy consensus (2.06)",
        "low valuation"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "utilities",
      "from_group_name": "Utilities",
      "group_rank": 9
    },
    {
      "rank": 79,
      "ticker": "TSN",
      "signal": "buy",
      "confidence": 0.6,
      "rationale": "+12.5% 1M momentum, +15% 1Y return, P/E 49.2 but improving volume trends, dividend yield 3.3%, analyst hold but improving fundamentals.",
      "drivers": [
        "Strong 1M momentum",
        "Solid YTD return",
        "Dividend yield 3.3%",
        "Volume recovery"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 6
    },
    {
      "rank": 80,
      "ticker": "CBRE",
      "signal": "buy",
      "confidence": 0.6,
      "rationale": "CBRE Group shows strong short-term momentum with +8.63% 1-month and +3.17% 1-day gains, a buy consensus (score 1.54), and benefits from recovering commercial real estate transaction volumes.",
      "drivers": [
        "+8.63% 1M",
        "buy consensus 1.54",
        "recovering transaction volumes",
        "low short interest 1.48%"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 7
    },
    {
      "rank": 81,
      "ticker": "WY",
      "signal": "strong_buy",
      "confidence": 0.6,
      "rationale": "Weyerhaeuser has a strong_buy analyst consensus (score 1.5), +3.22% 1-month momentum, a 4.25% dividend yield, and benefits from timberland demand and housing market recovery.",
      "drivers": [
        "strong_buy consensus 1.5",
        "+3.22% 1M",
        "4.25% dividend yield",
        "timberland demand"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 8
    },
    {
      "rank": 82,
      "ticker": "WYNN",
      "signal": "strong_buy",
      "confidence": 0.6,
      "rationale": "WYNN has a strong_buy consensus (an_score 1.29) and gained +13.69% in 1M, with a P/E of 23.54, supported by Macau recovery and travel demand.",
      "drivers": [
        "strong_buy consensus",
        "+14% 1M",
        "Macau recovery",
        "travel demand"
      ],
      "pre_momentum_label": "strong_buy",
      "post_momentum_label": "strong_buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 9
    },
    {
      "rank": 83,
      "ticker": "ERIE",
      "signal": "buy",
      "confidence": 0.6,
      "rationale": "Erie Indemnity rose +9.8% in 1M and +1.7% YTD, with a P/E of 24.4; no analyst coverage but strong property-casualty niche and low beta of 0.22.",
      "drivers": [
        "+9.8% 1M",
        "low beta 0.22",
        "P/E 24.4",
        "niche insurer"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "financials",
      "from_group_name": "Financials",
      "group_rank": 10
    },
    {
      "rank": 84,
      "ticker": "HRL",
      "signal": "buy",
      "confidence": 0.55,
      "rationale": "+11.1% 1M momentum, +7% 1Y return, dividend yield 5.07%, P/E 37.2 but value brand strength, improving volume trends.",
      "drivers": [
        "Strong 1M momentum",
        "High dividend yield",
        "Brand strength",
        "Volume recovery"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 7
    },
    {
      "rank": 85,
      "ticker": "DG",
      "signal": "buy",
      "confidence": 0.55,
      "rationale": "+35% 1Y return, +8% 1M momentum, P/E 17.4, low beta 0.19, analyst buy consensus, dollar store resilience.",
      "drivers": [
        "Strong 1Y return",
        "Low P/E",
        "Analyst buy consensus",
        "Defensive retail"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-staples",
      "from_group_name": "Consumer Staples",
      "group_rank": 8
    },
    {
      "rank": 86,
      "ticker": "VICI",
      "signal": "buy",
      "confidence": 0.55,
      "rationale": "Vici Properties offers a high 7.62% dividend yield, a low P/E of 11.19, +3.12% 1-month momentum, and benefits from stable gaming and hospitality lease income.",
      "drivers": [
        "7.62% dividend yield",
        "P/E 11.19",
        "+3.12% 1M",
        "stable gaming leases"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "real-estate",
      "from_group_name": "Real Estate",
      "group_rank": 9
    },
    {
      "rank": 87,
      "ticker": "CVNA",
      "signal": "buy",
      "confidence": 0.55,
      "rationale": "CVNA surged +16.52% in 1M despite a high beta of 3.65 and short interest of 12.1%, with a buy consensus and P/E of 32.6, reflecting used-car market momentum.",
      "drivers": [
        "+17% 1M",
        "buy consensus",
        "used-car demand",
        "high momentum"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "consumer-discretionary",
      "from_group_name": "Consumer Discretionary",
      "group_rank": 10
    },
    {
      "rank": 88,
      "ticker": "MOS",
      "signal": "buy",
      "confidence": 0.55,
      "rationale": "Buy consensus (an_score 2.50), +11.12% 1M, dividend yield 4.38%; Q3 2026 results showed progress on cost reduction and sulfur contract settlement, positioning for improved free cash flow [mosaicco.com](https://investors.mosaicco.com/press-releases/news-details/2026/The-Mosaic-Company-Reports-Third-Quarter-2026-Results/default.aspx).",
      "drivers": [
        "+11.12% 1M",
        "dividend yield 4.38%",
        "cost reduction progress",
        "sulfur contract settlement"
      ],
      "pre_momentum_label": "buy",
      "post_momentum_label": "buy",
      "momentum_label": null,
      "momentum_score": null,
      "from_group": "materials",
      "from_group_name": "Materials",
      "group_rank": 10
    }
  ]
};
