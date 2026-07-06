# Changelog

All notable changes to the vericlaim core. Format follows
[Keep a Changelog](https://keepachangelog.com/); this project versions the core
from `vericlaim/__init__.py` (see `CLAIM-META-001`).

## [Unreleased] — gold-standard lift

### Added
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
- Closed the bundle traversal-write vector (read + write side).
- Closed drift-past-the-gate vectors (unbalanced fence, unverified provenance
  hash, unchecked register metrics).
- See the security findings table in the implementation report.

### Deferred
- See [`ROADMAP.md`](ROADMAP.md). Notably: full strict-reproduce dogfooding
  (parser-blocked), schema-v2 metric bindings, sandboxed runner, signed
  attestation, SSRF controls, full CI render/scan pipeline.
