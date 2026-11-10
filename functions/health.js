// GET /health — data freshness per stream. 200 when everything is fresh, 503 when
// any stream missed its last scheduled run (rules in monitoring/freshness.js).
// An external uptime monitor polls this and emails when it returns 503.
import { evaluate, parseAsOf } from '../monitoring/freshness.js';

const SECTORS = ['AI', 'Biotech', 'Defence', 'Tech', 'Crypto', 'Energy', 'MegaCap'];

export async function onRequestGet({ request, env }) {
  const getJson = async path => {
    try {
      const r = await env.ASSETS.fetch(new URL(path, request.url));
      return r.ok ? await r.json() : null;
    } catch { return null; }
  };
  // Oldest sector wins: one sector failing to update must show as stale.
  const oldest = values => {
    const ms = values.map(parseAsOf);
    return ms.some(v => v === null) ? null : Math.min(...ms);
  };

  const [prices, signals, market, news, manifest] = await Promise.all([
    Promise.all(SECTORS.map(s => getJson(`/${s}/prices.json`))),
    Promise.all(SECTORS.map(s => getJson(`/${s}/signals-local.json`))),
    getJson('/market.json'),
    getJson('/News/news-feed.json'),
    getJson('/exports/manifest.json'),
  ]);

  const result = evaluate(Date.now(), {
    prices:  oldest(prices.map(d => d && d.updated)),
    signals: oldest(signals.map(d => d && d.updated)),
    market:  parseAsOf(market && market.updated),
    news:    parseAsOf(news && news.generated_utc),
    export:  parseAsOf(manifest && manifest.snapshots && manifest.snapshots[0] && manifest.snapshots[0].generated),
  });

  return new Response(JSON.stringify(result, null, 2), {
    status: result.ok ? 200 : 503,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });
}
