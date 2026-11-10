import { test } from 'node:test';
import assert from 'node:assert/strict';
import { STREAMS, zonedToUtc, parseAsOf, lastDueSlot, evaluate } from './freshness.js';

const Z = s => Date.parse(s);

test('London wall clock converts across BST and GMT', () => {
  assert.equal(zonedToUtc(2026, 7, 1, 7, 30, 'Europe/London'), Z('2026-07-01T06:30:00Z'));
  assert.equal(zonedToUtc(2026, 11, 10, 7, 30, 'Europe/London'), Z('2026-11-10T07:30:00Z'));
  assert.equal(zonedToUtc(2026, 11, 10, 7, 30, 'UTC'), Z('2026-11-10T07:30:00Z'));
});

test('parses the formats the bots write', () => {
  assert.equal(parseAsOf('2026-07-01 20:55'), Z('2026-07-01T19:55:00Z'));       // prices.json, BST
  assert.equal(parseAsOf('2026-11-10 03:53 GMT'), Z('2026-11-10T03:53:00Z'));   // manifest
  assert.equal(parseAsOf('2026-11-10T23:06:32Z'), Z('2026-11-10T23:06:32Z'));   // news ISO
  assert.equal(parseAsOf(null), null);
  assert.equal(parseAsOf('garbage'), null);
});

test('prices: due slot is the last London slot past its 45 min grace', () => {
  assert.equal(lastDueSlot(STREAMS.prices, Z('2026-11-10T09:00:00Z')), Z('2026-11-10T07:30:00Z'));
  // 08:10 is inside the 07:30 grace window, so the previous evening slot is the one due
  assert.equal(lastDueSlot(STREAMS.prices, Z('2026-11-10T08:10:00Z')), Z('2026-11-09T20:30:00Z'));
  // summer: 07:30 London = 06:30 UTC
  assert.equal(lastDueSlot(STREAMS.prices, Z('2026-07-01T07:20:00Z')), Z('2026-07-01T06:30:00Z'));
});

test('weekends and Monday morning look back to Friday evening', () => {
  assert.equal(lastDueSlot(STREAMS.prices, Z('2026-11-14T12:00:00Z')), Z('2026-11-13T20:30:00Z')); // Sat
  assert.equal(lastDueSlot(STREAMS.prices, Z('2026-11-16T06:00:00Z')), Z('2026-11-13T20:30:00Z')); // Mon early
});

test('fresh, stale and missing as_of', () => {
  const now = Z('2026-11-10T09:00:00Z');
  assert.equal(evaluate(now, { prices: Z('2026-11-10T07:38:00Z') }, { prices: STREAMS.prices }).ok, true);
  const stale = evaluate(now, { prices: Z('2026-11-09T20:55:00Z') }, { prices: STREAMS.prices });
  assert.equal(stale.ok, false);
  assert.equal(stale.streams.prices.stale, true);
  assert.equal(evaluate(now, { prices: null }, { prices: STREAMS.prices }).ok, false);
});

test('signals allow for GitHub schedule delays', () => {
  const s = { signals: STREAMS.signals };
  // Wed 07:00 run: still inside the grace window at 18:00 Wed -> Monday's data is fine
  assert.equal(evaluate(Z('2026-11-11T18:00:00Z'), { signals: Z('2026-11-09T17:10:00Z') }, s).ok, true);
  // Thursday morning: Wednesday's run is now overdue -> stale if it never landed
  assert.equal(evaluate(Z('2026-11-12T09:00:00Z'), { signals: Z('2026-11-09T17:10:00Z') }, s).ok, false);
  assert.equal(evaluate(Z('2026-11-12T09:00:00Z'), { signals: Z('2026-11-11T12:00:00Z') }, s).ok, true);
});
