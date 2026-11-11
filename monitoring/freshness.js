// Data-freshness rules for /health (functions/health.js) and its tests.
// A stream is stale when a scheduled run is due (slot time + grace has passed)
// but the stream's as_of is older than that slot.

export const STREAMS = {
  // All bots are started by cron-job.org in London time (jobs: cron-job-stocks*,
  // stocks-news, stocks-signals, stocks-export). Keep these slots in sync with it.
  // Grace covers run time plus queueing behind another bot (measured Nov 2026:
  // prices ~8 min, news up to 27 min, signals up to 22 min, export <1 min).
  prices:  { label: 'Prices',               tz: 'Europe/London', days: [1, 2, 3, 4, 5], times: ['07:30', '15:30', '20:30'], graceMin: 45 },
  market:  { label: 'Market (SPY/QQQ/VIX)', tz: 'Europe/London', days: [1, 2, 3, 4, 5], times: ['07:30', '15:30', '20:30'], graceMin: 45 },
  news:    { label: 'News feed',            tz: 'Europe/London', days: [1, 2, 3, 4, 5], times: ['08:35', '15:35', '20:35'], graceMin: 45 },
  signals: { label: 'AI signals',           tz: 'Europe/London', days: [1, 3, 5],       times: ['08:00'],                   graceMin: 60 },
  export:  { label: 'Daily export',         tz: 'Europe/London', days: [1, 2, 3, 4, 5], times: ['21:30'],                   graceMin: 45 },
};

function tzParts(ms, tz) {
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-GB', {
    timeZone: tz, hourCycle: 'h23', year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  }).formatToParts(new Date(ms)).map(x => [x.type, x.value]));
  return { y: +p.year, mo: +p.month, d: +p.day, h: +p.hour, mi: +p.minute, s: +p.second };
}

// Wall-clock time in `tz` -> epoch ms (handles BST/GMT changes).
export function zonedToUtc(y, mo, d, h, mi, tz) {
  const wall = Date.UTC(y, mo - 1, d, h, mi);
  if (tz === 'UTC') return wall;
  let guess = wall;
  for (let i = 0; i < 2; i++) {
    const p = tzParts(guess, tz);
    const offset = Date.UTC(p.y, p.mo - 1, p.d, p.h, p.mi, p.s) - guess;
    guess = wall - offset;
  }
  return guess;
}

// "YYYY-MM-DD HH:MM" (optionally followed by GMT/BST) in London time, or ISO 8601 with Z.
export function parseAsOf(value) {
  if (!value) return null;
  const s = String(value).trim();
  if (/T.*(Z|[+-]\d\d:?\d\d)$/.test(s)) {
    const ms = Date.parse(s);
    return Number.isNaN(ms) ? null : ms;
  }
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})/);
  return m ? zonedToUtc(+m[1], +m[2], +m[3], +m[4], +m[5], 'Europe/London') : null;
}

// Latest slot whose grace period has fully passed by `nowMs`.
export function lastDueSlot(stream, nowMs) {
  const graceMs = stream.graceMin * 60000;
  let best = null;
  for (let back = 0; back <= 9; back++) {
    const p = tzParts(nowMs - back * 86400000, stream.tz);
    const weekday = new Date(Date.UTC(p.y, p.mo - 1, p.d)).getUTCDay();
    if (!stream.days.includes(weekday)) continue;
    for (const t of stream.times) {
      const [h, mi] = t.split(':').map(Number);
      const slot = zonedToUtc(p.y, p.mo, p.d, h, mi, stream.tz);
      if (slot + graceMs <= nowMs && (best === null || slot > best)) best = slot;
    }
  }
  return best;
}

// asOf: { streamKey: epoch ms | null }. Returns the /health payload.
export function evaluate(nowMs, asOf, streams = STREAMS) {
  const iso = ms => (ms === null || ms === undefined ? null : new Date(ms).toISOString());
  const out = {};
  for (const [key, stream] of Object.entries(streams)) {
    const due = lastDueSlot(stream, nowMs);
    const as = asOf[key] ?? null;
    const stale = due !== null && (as === null || as < due);
    out[key] = { label: stream.label, as_of: iso(as), last_due_run: iso(due), grace_min: stream.graceMin, stale };
  }
  const ok = Object.values(out).every(s => !s.stale);
  return { ok, status: ok ? 'ok' : 'stale', checked_at: iso(nowMs), streams: out };
}
