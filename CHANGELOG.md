# Changelog

All notable changes to the vericlaim core. Format follows
[Keep a Changelog](https://keepachangelog.com/); this project versions the core
from `vericlaim/__init__.py` (see `CLAIM-META-001`).

## [Unreleased] — gold-standard lift

### Added — theory-synergy round: three modules (99 → 102 modules, 116 → 119 works)
- **`learn_then_test`** (LTT — Angelopoulos, Bates, Candès, Jordan, Lei;
  arXiv 2021, Ann. Appl. Stat. 2025): risk control for ANY loss and grid by
  reframing calibration as multiple testing. The EXACT binomial-tail
  p-value in rational arithmetic, SUPER-UNIFORMITY enumerated at every
  achievable threshold, and FAMILY-WISE ERROR enumerated exactly as
  Fractions over all 343 joint outcomes of 3 independent nulls for both
  Bonferroni and fixed-sequence procedures (both <= delta) — 43/43 checks.
  Complements `conformal_risk` (one monotone loss → any loss).
- **`in_toto_layout`** (in-toto — Torres-Arias et al., USENIX Security
  2019): the seven-rule supply-chain artifact-flow engine (MATCH, CREATE,
  DELETE, MODIFY, ALLOW, DISALLOW, REQUIRE) with rule-order sensitivity, a
  canonical clone→build→package layout verified whole, and five independent
  tamperings each detected (unauthorized signer, below-threshold
  signatures, un-sourced product, cross-step hash mismatch, DISALLOW stray)
  — 20/20 checks. Signature verification is explicitly the caller's layer.
- **`datasheet`** (Datasheets for Datasets — Gebru et al., CACM 2021):
  seven-section lifecycle completeness scoring with the paper's own
  justified-N/A escape hatch (a section marked not-applicable WITH a reason
  counts; a bare N/A does not), proven by an INDEPENDENT direct count over
  ALL 2187 (= 3**7) assignments of {answered, justified-N/A, gap} — 2193/2193
  checks. Complements `model_card` (model → the dataset it learned from).
- Literature layer 116 → 119 works (`ltt-2021`, `in-toto-2019`,
  `datasheets-2018`, all web-verified against primary sources and
  hash-locked); the bibliography is now grouped by kind (Regulations,
  Standards, RFCs, Specifications, Frameworks, Papers, Books) with a
  contents index and per-section counts. Catalogue deep-seeding rose
  22 → 25; CLAIM-LIB-INDEX-001 (99 → 102 modules, 87 → 90 Python, 90 → 93
  cited, 127 → 133 references) and CLAIM-CATALOG-001 updated. Claimlib tests
  +48 (learn_then_test 19, in_toto_layout 17, datasheet 12); declarative
  reproduce covers all 102 claims.

### Added — three catalogue promotions (96 → 99 modules, 112 → 116 works)
- **`conformal_risk`** (CRC — Angelopoulos et al., ICLR 2024): the
  published lambdahat rule with the risk theorem ENUMERATED under its
  preconditions (exhaustive leave-one-out risk <= alpha as exact
  Fractions), honest refusal outside them, and the exact reduction to
  split conformal prediction verified against the quantile rule. Where the
  paper defaults to lambda_max when nothing qualifies, the module returns
  None — refusal over an unverifiable assumption.
- **`prov_dm`** (W3C PROV-DM core): three types + exactly seven relations
  with the Recommendation's signatures (Start/End correctly absent), all
  63 signature combinations enumerated, derivation/delegation cycle
  detection, an ML-pipeline exemplar, 8/8 corruptions caught.
- **`runtime_rules`** (AgentSpec ICSE 2026 + MI9): the four verified
  enforcement kinds encoded verbatim — the fact-verifier caught that
  'skip' (in the task hint) does NOT exist in the paper — with
  first-match-wins semantics proven by permutation, Decimal-exact
  boundaries, fail-closed missing attributes, trace halt at stop, and a
  7/7 mutation battery. An empty trace no longer bypasses rule validation
  (found by the module's own reject battery during authoring).
- Catalogue deep-seeding rose 18 → 22 (identical-id mapping);
  CLAIM-CATALOG-001 and the catalogue page updated. Claimlib tests
  816 → 864; declarative reproduce covers all 99 claims.

### Added — the AI-assurance literature catalogue, claim-bound
- **`CLAIM-CATALOG-001`**: the curated 231-work / 10-section reading map
  behind the AI areas is now a committed, mechanically validated artifact
  (`docs/reference/ai_assurance_literature_catalog_2026-07-14_enriched.csv`
  → `tools/ai_catalog_evidence.py` → `claims/ai_catalog.json`). Every row
  is validated fail-closed (unique ids, known vocabularies, sane years with
  a whitelist for versionless living specs, https URLs); 154 works are
  priority p0 and 18 are deep-seeded as cited claimlib literature via an
  explicit same-work alias table (a lineage relation is never an alias —
  one candidate alias was rejected on exactly that rule). Counts are bound
  with schema-v2 metric bindings and reproduced declaratively;
  `docs/reference/ai-assurance-catalog.md` documents the three honest
  seeding tiers (cataloged / deep-seeded / RAG-ingested) and maps sections
  to the modules they feed.

### Added — AI assurance & uncertainty (88 → 96 modules, 103 → 112 works)
- **Measurable assurance techniques**, each with a theorem-or-publication
  oracle: `conformal_split` (the split-conformal quantile rule and the
  coverage theorem ENUMERATED — exhaustive leave-one-out coverage inside
  [1−α, 1−α+1/n] as exact Fractions), `selective_risk` (Geifman/El-Yaniv
  coverage + selective risk + risk-coverage curve, exact), `shannon_entropy`
  (entropy/cross-entropy/KL/perplexity with Shannon's own worked example
  and Gibbs/chain identities), `gsn_case` (GSN Community Standard v3
  assurance-case structure validator — 12 adversarial mutations all caught,
  36-pair edge enumeration admitting exactly the 4 legal pairs),
  `tool_guard` (default-deny agent tool-call policy — fail-safe defaults
  enumerated, 20/20 mutations denied, Decimal-exact constraints).
- **Assurance taxonomies**, facts web-verified against primary sources by a
  dedicated workflow before encoding: `owasp_llm10` (the ten v2025 entries
  verified against the official PDF), `slsa_levels` (v1.1 Build track with
  all 16 capability subsets enumerated against an independent re-derivation
  of the cumulative rule), `zta_tenets` (the seven SP 800-207 tenets).
- Literature grew to 112 hash-locked works (Shannon 1948, Angelopoulos &
  Bates, Geifman & El-Yaniv, GSN Community Standard v3/SCSC-141C, OWASP LLM
  Top 10 2025, SLSA v1.1, NIST SP 800-207, Progent, Clymer et al. safety
  cases); 87 of 96 modules cite what they implement through 122 references.
  Claimlib tests 718 → 816; declarative reproduce covers all 96 claims.

### Added — schema v2 metric bindings (`vericlaim/binding.py`)
- **Explicit, typed, Decimal-safe metric bindings**: `metric_bindings` pin a
  register metric to an exact RFC 6901 JSON-Pointer location in a named
  artifact, with `type` (number/integer/string/boolean — booleans are never
  numbers) and comparators `exact` / `minimum` / `maximum` / `bounded`
  (+`tolerance`). Artifact JSON is parsed with `parse_float=Decimal` and
  register values via `Decimal(str(v))`, so comparisons are exact decimal
  arithmetic — closing the v1 limitation where an identically-named key
  anywhere in the JSON tree could satisfy the metric check. Bound metrics
  leave the v1 scan; every binding failure mode is a finding (pointer
  missing, type mismatch, ambiguous/unclaimed/unreadable artifact, missing
  tolerance, unknown comparator), and structurally malformed bindings raise
  `RegisterError` at load. The list-of-flat-maps YAML shape parses
  identically under the bundled parser and PyYAML.
- **Dogfooded end to end**: claimlib's build emits a binding for every
  register metric of all 88 modules (386 pointer bindings verified by the
  gate), and the root register binds CLAIM-EX-001 and CLAIM-LIB-INDEX-001.
  Reference doc: `docs/reference/claim-schema-v2.md`; 30 adversarial tests
  including the decoy-key attack the binding exists to stop.

### Security — fail-closed hardening (external review P0/high findings)
- **Declarative reproduce is no longer exempt from provenance or manifest
  coverage** (P0): `check_provenance` and `check_manifest_coverage` keyed on
  the legacy `reproduce` string only, so the recommended `reproduce_argv`
  form — the only one strict/enterprise accept, used by all 88 claimlib
  claims — bypassed both. A shared `_has_reproduce()` now covers both forms;
  claimlib's sidecars pass the newly-enforced check unchanged.
- **`reproduce_outputs` is now bound to the claim's `artifact` list** (P0):
  a declarative spec that reproduces an unrelated file while the claimed
  evidence is never produced now fails with the exact mismatch.
- **A configured manifest that is missing is a hard failure** (P0): deleting
  `claims/manifest.md` used to silently disable SHA-256 verification. The
  `manifest` key is now opt-in (unset = explicitly off, default changed from
  `claims/manifest.md` to unset), configured-but-absent fails, and
  strict/enterprise require a manifest whenever any claim is reproducible.
- **Strict refuses unestablishable metrics**: a register metric whose key
  does not appear in the claim's JSON artifact is a finding under
  strict/enterprise (adopt keeps the doc-only tolerance); the README now
  states the binding's honest semantics, and the any-depth key-match limit
  is documented (schema v2 closes it).
- **The register parser fails closed on malformed entries and wrong field
  types**: `claims: [oops]`, a bare-string entry, a non-string `id`, a
  mapping `artifact`, a string `reproduce_argv`, or a non-mapping
  `literature` entry now raise `RegisterError` instead of being silently
  dropped or crashing later.
- **The baseline can no longer absorb new occurrences of a baselined
  problem**: entries grandfather exactly `count` occurrences of their
  `error_id` (default 1); every further occurrence fails.
- **The reproduction runner walks the output directory recursively** and
  rejects symlinks: a file hidden in a subdirectory is an undeclared output.
- **CI gains a Windows job** (gate + both test suites on windows-latest) —
  the LF/pathsafe/process-group code paths are now exercised on the platform
  they special-case. 23 adversarial regression tests lock all of the above.

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
