-- vericlaim claim ledger (D1) — an append-only, hash-chained history of every
-- claim a project registers. Tamper-evident: each row's entry_hash chains the
-- previous one, so altering any past row breaks every hash after it.
--
-- One row is appended per claim ONLY when the claim's content changes, so the
-- ledger is a true timeline of what a project has claimed about itself.

CREATE TABLE IF NOT EXISTS claim_events (
  seq             INTEGER PRIMARY KEY AUTOINCREMENT,
  ts              TEXT    NOT NULL,   -- ISO 8601, set server-side
  claim_id        TEXT    NOT NULL,
  statement       TEXT,
  evidence_level  TEXT,
  metrics         TEXT,               -- JSON object
  caveat          TEXT,
  artifact        TEXT,               -- JSON array of paths
  artifact_sha256 TEXT,               -- content address of the primary artifact in R2
  git_commit      TEXT,              -- best-effort, from the exporter
  content_hash    TEXT    NOT NULL,   -- sha256 of the claim's canonical content
  prev_hash       TEXT    NOT NULL,   -- entry_hash of the previous ledger row ('' for genesis)
  entry_hash      TEXT    NOT NULL    -- sha256(prev_hash + canonical(this row without hashes))
);

CREATE INDEX IF NOT EXISTS idx_claim_events_claim ON claim_events (claim_id, seq);

-- The claims LIBRARY: an append-only, hash-chained registry of cross-project
-- claim bundles (see integrations/library/). Bundles are immutable —
-- bundle_id = sha256(canonical manifest) — so one row per bundle, chained the
-- same way as claim_events. `status` is 'verified' (harvested from a repo
-- whose own gate passed) or 'candidate' (extracted assertion, quarantined).
CREATE TABLE IF NOT EXISTS library_bundles (
  seq             INTEGER PRIMARY KEY AUTOINCREMENT,
  ts              TEXT    NOT NULL,
  bundle_id       TEXT    NOT NULL UNIQUE,
  status          TEXT    NOT NULL,
  source_repo     TEXT    NOT NULL,
  source_claim_id TEXT    NOT NULL,
  claim           TEXT    NOT NULL,   -- canonical JSON of the bundled claim
  manifest        TEXT    NOT NULL,   -- canonical JSON: {schema, status, files}
  provenance      TEXT    NOT NULL,   -- canonical JSON of harvest provenance
  prev_hash       TEXT    NOT NULL,
  entry_hash      TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_library_bundles_claim
  ON library_bundles (source_claim_id, seq);

-- The RESEARCH layer: literature works + chunks (serving mirror of the
-- git-anchored catalog in integrations/library/literature/ — the catalog is
-- the anchor, so these tables carry no hash chain of their own).
CREATE TABLE IF NOT EXISTS literature_works (
  fsid          TEXT PRIMARY KEY,
  work_id       TEXT NOT NULL,
  title         TEXT NOT NULL,
  authors       TEXT NOT NULL,      -- JSON array
  year          INTEGER,
  venue         TEXT,
  kind          TEXT NOT NULL,      -- paper | book | standard | spec | report
  tier          TEXT NOT NULL,      -- registrar method or 'web-snapshot'
  accredited    INTEGER NOT NULL,   -- 1 only for peer-reviewed venue types
  url           TEXT,
  linked_claims TEXT NOT NULL DEFAULT '[]',  -- JSON array of claim ids
  updated_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS literature_chunks (
  sha        TEXT PRIMARY KEY,      -- sha256 of the chunk text (content address)
  fsid       TEXT NOT NULL,
  seq        INTEGER NOT NULL,
  section    TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_lit_chunks_fsid ON literature_chunks (fsid, seq);
