# Changelog

All notable changes to the vericlaim core. Format follows
[Keep a Changelog](https://keepachangelog.com/); this project versions the core
from `vericlaim/__init__.py` (see `CLAIM-META-001`).

## [Unreleased] — gold-standard lift

### Added
- **AI-governance architecture for enterprise environments (80 → 88
  modules, 94 → 103 works)**: a dedicated subject area pairing the four
  load-bearing frameworks with the measurements that make governance
  quantitative. Frameworks — `eu_ai_act` (Regulation (EU) 2024/1689:
  13/113/13 structure, the eight Art. 5(1) prohibitions and eight Annex III
  high-risk areas, verified mechanically against CELEX 32024R1689; the
  module also documents that the popular "minimal risk" tier label does not
  occur in the enacted text), `nist_ai_rmf` (AI 100-1 Core: 19 categories /
  72 subcategories / 7 trustworthy-AI characteristics, verified identifier
  by identifier), `iso_42001` (AIMS clauses 4-10 + Annex A's 38 controls in
  9 objectives with fail-closed SoA accounting), `dora_eu` (9 chapters
  partitioning 64 articles, five resilience pillars — the enterprise frame
  around AI in finance). Measurements — `fairness_metrics` (demographic
  parity, EEOC four-fifths, Hardt equalized odds; 73 exact-Fraction
  checks), `calibration_ece` (Guo/Naeini ECE+MCE with an independent
  re-derivation oracle), `dp_composition` (Dwork-Roth composition + a
  fail-closed privacy-budget accountant), `model_card` (Mitchell et al.'s
  nine sections, completeness gate). All framework facts were web-verified
  against primary sources by a dedicated workflow before encoding;
  declarative reproduce covers all 88 claims. Claimlib tests 595 → 718.
- **16 new claimlib modules — deep domain coverage (64 → 80)**: `chacha20`
  (RFC 8439 vectors byte-exact) and `jwt_hs256` (RFC 7515 A.1 + alg-confusion
  rejection) in security; `punycode` (all 19 RFC 3492 samples + stdlib
  oracle), `dns_name` (RFC 1035/1123 boundaries) and `erlang_b` (exact-
  rational closed form + published traffic tables) in telecom; `kid`
  (Norwegian OCR giro MOD10/MOD11, 859 095 tamperings caught exhaustively)
  and `annuity` (integer-øre schedules, the $599.55 textbook payment) in
  finance; `bloom_filter`, `uuid_tools` (RFC 9562), `base58` in data;
  `pt100` (IEC 60751, table points re-derived at 50-digit precision) in
  industrial; `slo_burnrate` (SRE Workbook table) and `ewma` (Roberts/NIST)
  in observability; `cis_controls` (v8.1: 18/153/56-130-153) and `gdpr`
  (11 chapters partitioning 99 articles, verified exhaustively) in
  compliance; `mus_sampling` (top-stratum guarantee over all 500 000 starts)
  in audit. Literature grew 76 → 94 hash-locked works (Erlang 1917, Bloom
  1970, Roberts 1959, Kellison, the SRE Workbook, Nets OCR giro, IEC 60751,
  CIS v8.1, GDPR, RFCs 1035/1123/3492/7515/7519/8439/9562, …); 71 of 80
  modules now cite what they implement through 103 references. Claimlib
  tests 338 → 595.
- **Full literature coverage for the knowledge register**: claimlib's
  hash-locked bibliography grew from 24 to 76 works (RFCs, ISO/IEEE/ITU
  standards, classic papers from Hamming 1950 to Haber–Stornetta 1991, and
  books down to Pacioli's 1494 *Summa*); 55 of 64 modules now cite the
  literature they implement through 80 resolved references, and the 9 generic
  utilities are documented as intentionally uncited — a stretched citation is
  worse than none. Every entry was drafted and adversarially fact-checked
  against the primary sources.
- **`CLAIM-LIB-INDEX-001`** (`tools/claimlib_index_evidence.py` →
  `claims/claimlib_index.json`): the knowledge register's size and citation
  coverage counted from `MODULES.py`/`SOURCES.py` and bound into the README —
  adding a module or work without regenerating the evidence fails the gate.
- **README restructured around the two halves**: the gate and the knowledge
  register, with a table of contents, a categorized directory of all 64
  library modules, the claim→program pipeline (literature → claim → evidence
  → artifact → bundle), and the scaffolder documented as the generative path.
- **`seed/` corpora generators committed** (`seed/generate.py`,
  `seed/enterprise/{generate.py,domains.py}`): deterministic stress-test
  workspaces — 300 artifact-backed claims at scale and 30 claims across 16
  enterprise domains — regenerable byte-identically; the generated corpus is
  gitignored by design (`seed/README.md`).
- **Central path-safety policy** (`vericlaim/pathsafe.py`): one fail-closed,
  adversarially-tested definition of a safe path, used by the gate, manifest,
  literature, and bundle tooling. Rejects absolute paths, `..`/`.`/empty/
  non-canonical segments, backslashes, Windows drives, NUL/control bytes, and
  symlink escapes; validates `bundle_id` as strict sha256 hex.
- **Declarative reproduction oracle** (`vericlaim/repro.py`): runs a declarative
  spec (`argv` + `outputs`) in an isolated empty output directory so every
  declared output must be created **from scratch** — a no-op now fails. Process-
  group timeout kill; bounded output capture; machine-readable `ReproductionResult`.
- **Policy profiles** `adopt` / `strict` / `enterprise` with `--profile`. strict/
  enterprise are secure-by-default (provenance + git-tracking forced on, legacy
  shell reproduction rejected).
- **Register↔evidence metric check**, unbalanced-fence guard, provenance-hash
  verification, non-numeric-metric crash fix, and bundled-parser inline-comment
  parity (earlier in this cycle).
- **Five applied domain modules** under `domains/` (eval-harness, evidence-graph,
  multi-tenant, ontologies, cost-routing), each a reproduce-backed claim.
- **Bounded self-improvement** (`vericlaim/selfimprove.py`, `vericlaim improve`):
  a defensible, propose-only take on recursive self-improvement. A non-weakening
  safety envelope (`check_non_weakening`) refuses any self-proposed change that
  removes a claim, demotes evidence, shrinks tests, grows the baseline, edits the
  verifier core, or fails the gate; an advisory proposer suggests honest,
  evidence-backed improvements and edits nothing; a kill-switch sentinel disables
  it. Dogfooded as `CLAIM-RSI-001`. See `docs/architecture/self-improvement.md`.
- Documentation architecture, `SECURITY.md`, `ROADMAP.md`, `CODE_OF_CONDUCT.md`,
  `SUPPORT.md`, and diagram sources with explanatory prose.

### Changed
- The gate's path resolution now delegates to the central `pathsafe` policy.
- Cloudflare integration: constant-time auth, CORS preflight + error boundary,
  cached ledger verify on hot paths, reconcile-wipe guard, honest ledger/oracle
  wording, optional read-token and HMAC-signed head.
- Honest wording fixes across README, evidence-levels, governance editions
  (EN+NO), and the library caveats (the two-180s / registrar false-match).

### Security
- Closed the bundle traversal-write vector on ALL three surfaces: `verify_bundle`
  (read), `import_bundle` (vendor write), and now `fetch_bundle` (network
  download) — the download path staged in a private temp dir, safe-joins every
  manifest path before writing, verifies, then atomically moves into place
  (P0-2). Adversarial tests for `../`, absolute, backslash, and Windows-drive
  manifest paths.
- Closed the MCP generative-auth bypass: `/mcp` now passes the same
  `generativeAllowed()` gate as `/ask`, because it exposes `ask_claims` /
  `ask_research` (Workers AI). Setting `READ_TOKEN` no longer leaves an open
  generative endpoint on `/mcp` (P0-1).
- Stopped leaking internal `err.message` to clients from the Worker error
  boundary — logged server-side, generic 500 returned (P1).
- Extracted Worker auth into one central, unit-tested policy (`src/authz.ts`) and
  added request limits (`src/limits.ts`): `?q=` length cap, POST body-size cap,
  and paginated `/ledger/export` so it cannot be forced into an unbounded dump
  (P1). Regression tests run on Node's built-in test runner and in CI.
- `/index` snapshot integrity (`src/snapshot.ts`, unit-tested): a push may declare
  `expected_claim_count` / `register_sha256` / `full_snapshot`; the writer refuses
  to reconcile on a mismatch, so a truncated export cannot prune the index, and
  returns a verifiable ingest receipt (P1). Plus an **opt-in** single-writer
  `IndexWriter` Durable Object (`src/ingest.ts`, `SINGLE_WRITER=true`) that
  serializes `/index` — type-checked, bundles clean via `wrangler --dry-run`, but
  runtime behavior is not deploy-tested (off by default).
- Closed drift-past-the-gate vectors (unbalanced fence, unverified provenance
  hash, unchecked register metrics).
- See the security findings table in the implementation report.

### Self-review hardening
Fixes from an adversarial self-review of this cycle's own work:
- **Declarative reproduce is now dogfooded.** Parser-friendly flat fields
  (`reproduce_argv` / `reproduce_outputs`, identical under the bundled parser and
  PyYAML) let real claims use the isolated-workspace runner; CLAIM-RSI-001/002 are
  converted and verified "re-created from scratch and byte-identical" — so CI's
  `reproduce` now exercises the declarative path, not only legacy shell.
- **Self-improvement envelope now diffs the whole `vericlaim/` tree** (added /
  removed / modified), not a hardcoded file list — a self-proposed change can no
  longer add or delete a core module undetected.
- **Central generative-auth choke point** (`routeAuthError`): every Workers-AI
  route incl. `/mcp` passes one gate up front; removes the dead `requiresGenerativeAuth`
  and the per-route duplicates. +3 tests.
- **`fetch_bundle` now stages inside `out_root`** so the final move is a true
  atomic rename, not a cross-filesystem copy.
- Honesty: the envelope's docstring/doc now state it is a pure comparator that
  trusts the captured snapshot (not an autonomous gatekeeper); the loop no longer
  says "applied nothing" (reproduce rewrites artifacts byte-identically); stale
  hard-coded counts removed from the implementation report; the gold-standard plan
  is marked a point-in-time snapshot.

### Deferred
- See [`ROADMAP.md`](ROADMAP.md). Notably: converting the remaining 13 legacy
  reproduce commands to declarative (strict-reproduce across the whole register),
  schema-v2 metric bindings, sandboxed runner, signed attestation, SSRF controls,
  full Miniflare route tests, CI render/scan pipeline.
