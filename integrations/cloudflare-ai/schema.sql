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
