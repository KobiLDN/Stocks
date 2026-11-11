/* asset-links.js — GENERATED from universe.yaml by `python universe.py --write-links`.
   Do not edit by hand; CI fails if it is out of date. */
const ASSET_COINGECKO = {"ADA": "cardano", "AGIX": "singularitynet", "AIOZ": "aioz-network", "ALGO": "algorand", "ALT": "altlayer", "ARKM": "arkham", "AVAX": "avalanche-2", "BNB": "binancecoin", "BTC": "bitcoin", "DOGE": "dogecoin", "DOT": "polkadot", "ETH": "ethereum", "FET": "fetch-ai", "GRT": "the-graph", "HBAR": "hedera-hashgraph", "ICP": "internet-computer", "KAITO": "kaito", "LINK": "chainlink", "MATIC": "matic-network", "MINA": "mina-protocol", "NEAR": "near", "NMR": "numeraire", "OCEAN": "ocean-protocol", "PEPE": "pepe", "POL": "polygon-ecosystem-token", "RNDR": "render-token", "SOL": "solana", "SUI": "sui", "TAO": "bittensor", "TON": "the-open-network", "TRX": "tron", "VIRTUAL": "virtual-protocol", "WLD": "worldcoin-wld", "XLM": "stellar", "XRP": "ripple"};
const ASSET_YAHOO = {"285A": "285A.T", "AZN": "AZN.L", "GSK": "GSK.L", "RR.": "RR.L"};
function assetUrl(t) {
  if (ASSET_COINGECKO[t]) return 'https://www.coingecko.com/en/coins/' + ASSET_COINGECKO[t];
  return 'https://finance.yahoo.com/quote/' + encodeURIComponent(ASSET_YAHOO[t] || t) + '/';
}
