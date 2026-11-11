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

test('signals: Mon/Wed/Fri 08:00 London with 60 min grace', () => {
  const s = { signals: STREAMS.signals };
  // Wed 08:45: inside the grace window for today's run -> Monday's data is still fine
  assert.equal(evaluate(Z('2026-11-11T08:45:00Z'), { signals: Z('2026-11-09T08:10:00Z') }, s).ok, true);
  // Wed 09:05: today's run is overdue -> stale if it never landed
  assert.equal(evaluate(Z('2026-11-11T09:05:00Z'), { signals: Z('2026-11-09T08:10:00Z') }, s).ok, false);
  assert.equal(evaluate(Z('2026-11-11T09:05:00Z'), { signals: Z('2026-11-11T08:09:00Z') }, s).ok, true);
  // Tuesday: last due run is Monday's
  assert.equal(lastDueSlot(STREAMS.signals, Z('2026-11-10T12:00:00Z')), Z('2026-11-09T08:00:00Z'));
});

test('export: 21:30 London; Saturday still expects Friday night', () => {
  assert.equal(lastDueSlot(STREAMS.export, Z('2026-11-14T10:00:00Z')), Z('2026-11-13T21:30:00Z'));
  // summer: 21:30 London = 20:30 UTC
  assert.equal(lastDueSlot(STREAMS.export, Z('2026-07-01T21:20:00Z')), Z('2026-07-01T20:30:00Z'));
});
