# Roadmap

**Purpose.** Track work that is *designed but not yet implemented*, so the
documentation never presents roadmap as shipped. Items here are **not** current
guarantees. Implemented capabilities live in the README and are gate-bound.

Status: 🟡 partially implemented · ⏳ designed, not built.

## Near-term

- ⏳ **Declarative reproduce for the whole register.** The declarative runner
  (`vericlaim/repro.py`) is implemented and tested, but the repo's own claims are
  still legacy string commands. Converting them (and making `reproduce --profile
  strict` pass across the register) is **blocked** by the zero-dependency parser:
  it cannot represent the nested `reproduce:` map without PyYAML. Resolving this
  is coupled to the parser-contract decision below.
- 🟡 **Schema v2 (typed structures + explicit metric bindings).** Today metric
  values are matched against JSON artifacts by key (`check_metrics_match_artifact`).
  v2 adds explicit bindings — `{value, artifact, pointer, type, unit, comparator}`
  with JSON Pointer and Decimal-safe comparators (`exact`/`bounded`/`minimum`/…),
  replacing key-scanning. Design: `docs/reference/claim-schema-v2.md`.
- ⏳ **Zero-dependency parser contract.** Either (A) a documented restricted YAML
  grammar with exact errors, or (B) a canonical stdlib format (JSON/TOML) with
  YAML as compat import. Required so nested specs parse identically with and
  without PyYAML. Currently unsupported syntax must not be silently read as a
  scalar (partly addressed: inline comments are stripped).

## Reproduction & supply chain

- ⏳ **True sandboxed runner** (containers / seccomp / network namespaces) so
  `network: disabled` is *enforced*, not merely requested. Until then
  `network_enforced` is always false.
- ⏳ **Signed provenance / attestation** (DSSE, Sigstore, GitHub OIDC) for the
  enterprise profile; SBOM generation; dependency lock with hashes.
- ⏳ **Baseline metadata** (owner, reason, created, expiry, ticket) enforced under
  strict; zero-expired-baseline gate under enterprise.

## CI & docs

- 🟡 **CI hardening.** SHA-pinned actions and a version-locked toolchain exist;
  still to add: Python matrix breadth, mutation testing, SBOM, secret/license/
  vuln scanning, and pinned Mermaid render validation.
- 🟡 **Diagram render validation** in CI (pinned mermaid-CLI + lockfile), stale-SVG
  detection, and a check that architecture docs only reference existing diagrams.
- ⏳ **Full 21-document set** per the gold-standard plan
  (`docs/architecture/gold-standard-plan.md`).

## Integrations

- ⏳ **SSRF controls** for `webfetch.py` (HTTPS-only, host allowlist, block
  loopback/RFC1918/link-local/metadata, redirect validation, size caps).
- ⏳ **Cloudflare scoped-token model** (separate tokens for index / read /
  ledger-export / evidence-download / admin), per-token quotas/rate limits, and
  exact CORS allowlist for authenticated endpoints. (Done: refusal integrity,
  read-token guard on generative endpoints INCLUDING `/mcp` — the P0-1 bypass —
  HMAC head, CORS preflight, error boundary + no message leak, reconcile-wipe
  guard, central `authz.ts` policy, request limits + paginated `/ledger/export`,
  auth/limits unit tests in CI.)
- 🟡 **`/index` atomicity + single-writer.** Done: snapshot-integrity guard
  (`expected_claim_count` / `register_sha256` / `full_snapshot`, unit-tested) so a
  truncated export cannot prune the index, a verifiable ingest receipt, and an
  **opt-in** `IndexWriter` Durable Object (`SINGLE_WRITER=true`) that serializes
  writes — type-checked and it bundles cleanly (`wrangler deploy --dry-run`), but
  its runtime concurrency behavior is NOT deploy-tested. Still ⏳: Vectorize
  staging-namespace + atomic active-snapshot swap (a mid-ingest failure can still
  leave the search index partial); needs a real Cloudflare env to verify.
- ⏳ **Full Miniflare route tests** (real D1/R2/Vectorize/AI bindings end-to-end).
  Auth + limit *decision* logic is now unit-tested; binding-level route tests
  need the workerd harness.

Nothing here is claimed as a current capability. See
[`docs/security/security-model.md`](docs/security/security-model.md) for what the
tool proves today.
