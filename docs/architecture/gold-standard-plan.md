# Gold-standard implementation plan

**Purpose.** Map the work to lift `vericlaim` to a gold-standard reference
implementation of Claim-Oriented Programming, and record honestly which phases
are *implemented*, *scaffolded*, or *deferred* — so this document itself obeys
the product rule: no claim above its evidence.

> **Status note (point-in-time plan).** This table reflects the original 8-phase
> plan. Substantial work landed *after* it — an external security review's P0/P1
> fixes (MCP auth, bundle-download traversal, `/index` snapshot integrity + opt-in
> single-writer, request limits), the bounded self-improvement + autonomous-loop
> work, and Cloudflare auth/limit unit tests. For the *current* state, `CHANGELOG.md`
> and `implementation-report.md` are authoritative; this plan is not re-scored
> per commit.

**Scope.** The trusted core is the zero-dependency Python gate (`vericlaim/`).
Integrations (`integrations/cloudflare-ai/`, `integrations/library/`) are optional
product surfaces with their own threat models and are never part of the trusted
core. This plan preserves the intellectual core: *no claim without evidence; no
evidence without provenance; no drift; no claim above its earned level.*

## Status legend

- ✅ **implemented** — working code + tests, gate green.
- 🟡 **scaffolded** — machinery or docs landed; not yet fully dogfooded/enforced.
- ⏳ **deferred** — specified here as roadmap; not yet built. Tracked, not hidden.

## Phases

| Phase | Item | Status |
|-------|------|--------|
| 1.1 | Central path-validation utility (`vericlaim/pathsafe.py`) + adversarial tests; wired into the gate and bundle modules | ✅ |
| 1.2 | Declarative reproduce spec + isolated-workspace runner with pre-exec output removal (no-op detection); legacy shell allowed only under `adopt`, rejected under `strict` | ✅ |
| 2 | Schema-v2 typed structures + explicit metric bindings (JSON Pointer + comparators + Decimal); zero-dependency parser contract documented | 🟡 (key-based register↔artifact metric check ✅; JSON-Pointer/comparator bindings, typed-dataclass migration, and the parser contract ⏳ — see ROADMAP) |
| 3 | Policy profiles `adopt`/`strict`/`enterprise` in config + gate wiring | ✅ (adopt/strict ✅; enterprise controls 🟡/⏳) |
| 4 | Documentation architecture (architecture/security/operations/reference/tutorials/adr) + policy files | 🟡 (core pages + policy files ✅; full 21-doc set ⏳) |
| 5 | Mermaid diagram system + CI render validation | 🟡 (key diagrams + explanatory prose ✅; pinned mermaid-CLI CI render ⏳) |
| 6 | CI/release/supply-chain hardening (matrix, SBOM, signing, scanners) | 🟡 (zero-dep + optional-dep jobs, self-dogfood ✅; SBOM/signing/mutation ⏳) |
| 7 | Integration hardening — webfetch SSRF controls; Cloudflare scoped tokens/CORS/limits | 🟡 (done since: MCP generative-auth gate + central choke point, bundle-download traversal fix, request limits + paginated export, error redaction, snapshot-integrity guard, opt-in single-writer DO, 23 auth/limit/snapshot unit tests; ⏳ SSRF allowlist, scoped-token model, full Miniflare route tests — see CHANGELOG/ROADMAP) |
| 8 | Testing & strict self-dogfooding | 🟡 (path/reproduce/parser/schema tests ✅; full strict dogfood of the register ⏳) |

## Sequencing rationale

Security- and integrity-critical core first (1.1, 1.2), because they change what
the tool *guarantees*. Profiles (3) make new strictness opt-in and backwards
compatible — `adopt` keeps existing repos working, `strict` is the recommended
destination, `enterprise` is the regulated tier. Schema/metric bindings (2)
remove the last ambiguous inference in the core. Docs/diagrams/CI/integrations
(4–7) then package it for adoption. Everything stays **fail-closed** and
**secure-by-default under `strict`**; permissive behavior requires explicit opt-in.

## What this repository still does not prove

(Repeated verbatim in the final report and `docs/security/security-model.md`.)
vericlaim detects *specified classes* of drift and integrity failure between a
project's register, artifacts, provenance, docs, and code. It does **not** prove
semantic truth, real-world validity, production readiness, or external
validation unless the required evidence and attestation are explicitly present
and verified. Retrieval and the oracle are discovery aids, never proof.
