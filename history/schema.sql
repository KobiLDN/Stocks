-- History database (Cloudflare D1 = SQLite). Rebuild step 3, spec in issue #54.
-- D1 holds HISTORY ONLY and is never read by the site.
-- Bump SCHEMA_VERSION in history/db.py whenever this file changes.
-- Every statement must be idempotent (IF NOT EXISTS): it is re-applied on version bumps.
-- WITHOUT ROWID: the primary key is the table, so a write counts as one row
-- written on D1's free plan (100k/day), not two.

-- One row per bot run. Readers use only runs with status = 'complete'.
CREATE TABLE IF NOT EXISTS runs (
  run_id       TEXT PRIMARY KEY,
  bot          TEXT NOT NULL,
  status       TEXT NOT NULL CHECK (status IN ('running', 'complete', 'failed')),
  started_utc  TEXT NOT NULL,
  finished_utc TEXT,
  rows_offered INTEGER,
  git_sha      TEXT,
  gh_run       TEXT,
  note         TEXT
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
) WITHOUT ROWID;

-- Mirror of universe.yaml, re-synced when the file changes.
CREATE TABLE IF NOT EXISTS assets (
  asset_id    TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  exchange    TEXT NOT NULL,
  kind        TEXT NOT NULL CHECK (kind IN ('equity', 'crypto', 'benchmark')),
  yahoo       TEXT NOT NULL,
  special     TEXT,
  cmc_symbol  TEXT,
  cmc_id      INTEGER,
  coingecko   TEXT,
  updated_utc TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS asset_sectors (
  asset_id TEXT NOT NULL,
  sector   TEXT NOT NULL,
  category TEXT NOT NULL,
  position INTEGER NOT NULL,
  PRIMARY KEY (asset_id, sector)
) WITHOUT ROWID;

-- What the site showed: one row per asset per published sector update.
-- Written by the price bot. Keyed on the data's own timestamp, so re-ingesting
-- an unchanged sector file is a no-op.
CREATE TABLE IF NOT EXISTS price_snapshots (
  asset_id         TEXT NOT NULL,
  as_of_utc        TEXT NOT NULL,
  sector           TEXT NOT NULL,
  price_usd        REAL,
  price_gbp        REAL,
  change_1d_pct    REAL,
  market_cap_usd_b REAL,
  volume_1d        REAL,
  run_id           TEXT NOT NULL,
  PRIMARY KEY (asset_id, as_of_utc)
) WITHOUT ROWID;

-- End-of-day bars, RAW (not split- or dividend-adjusted), in the instrument's own
-- quote currency (GBp = pence). Keyed by Yahoo symbol = the instrument, so an asset
-- listed under two IDs (RR. / RR.L) is stored once. Only history/bars.py writes here.
-- Missing days stay missing (gaps are gaps).
CREATE TABLE IF NOT EXISTS daily_bars (
  symbol   TEXT NOT NULL,
  date     TEXT NOT NULL,
  open     REAL,
  high     REAL,
  low      REAL,
  close    REAL,
  volume   REAL,
  currency TEXT NOT NULL,
  run_id   TEXT NOT NULL,
  PRIMARY KEY (symbol, date)
) WITHOUT ROWID;

-- Splits (value = ratio, e.g. 10 for 10-for-1) and dividends (value = raw amount
-- per share in `currency`). Prices are adjusted from these when read.
CREATE TABLE IF NOT EXISTS corporate_actions (
  symbol   TEXT NOT NULL,
  date     TEXT NOT NULL,
  kind     TEXT NOT NULL CHECK (kind IN ('split', 'dividend')),
  value    REAL NOT NULL,
  currency TEXT,
  run_id   TEXT NOT NULL,
  PRIMARY KEY (symbol, date, kind)
) WITHOUT ROWID;

-- Data-quality flags, e.g. a day-over-day jump that looks like an unrecorded
-- split, or a pence/pound mismatch.
CREATE TABLE IF NOT EXISTS data_flags (
  symbol TEXT NOT NULL,
  date   TEXT NOT NULL,
  kind   TEXT NOT NULL,
  detail TEXT,
  run_id TEXT NOT NULL,
  PRIMARY KEY (symbol, date, kind)
) WITHOUT ROWID;

-- AI + momentum signals. Written once, never changed (INSERT OR IGNORE).
CREATE TABLE IF NOT EXISTS signal_runs (
  signal_run_id TEXT PRIMARY KEY,
  sector        TEXT NOT NULL,
  generated_utc TEXT NOT NULL,
  model         TEXT,
  provenance    TEXT NOT NULL CHECK (provenance IN ('live', 'backtest')),
  run_id        TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS signals (
  signal_run_id TEXT NOT NULL,
  kind          TEXT NOT NULL CHECK (kind IN ('ai', 'momentum')),
  asset_id      TEXT NOT NULL,
  rank          INTEGER,
  signal        TEXT NOT NULL,
  confidence    REAL,
  rationale     TEXT,
  drivers       TEXT,
  PRIMARY KEY (signal_run_id, kind, asset_id)
) WITHOUT ROWID;

-- SPY / QQQ / VIX and the regime, one row per published market.json.
CREATE TABLE IF NOT EXISTS market_snapshots (
  as_of_utc     TEXT PRIMARY KEY,
  spy           REAL,
  qqq           REAL,
  vix           REAL,
  market_regime TEXT,
  vix_signal    TEXT,
  payload       TEXT NOT NULL,
  run_id        TEXT NOT NULL
) WITHOUT ROWID;
