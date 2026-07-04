# Design: the vericlaim claims library

*Approved by Stian 2026-07-04 (conversation). Scope extended on approval:
generic extraction from arbitrary repos, literature-gap detection, evidence
scaffolding.*

## Goal

A cross-project, Cloudflare-backed library of **curated, provenance-locked
claim bundles** — claims + evidence artifacts + code extracts + hash-verified
literature — harvested from gate-verified repos (first: REMORA-research),
searchable and reusable in any new project via offline, hash-verified import.

## The unit: content-addressed claim bundles

```
bundle/
  claim.yaml          # the claim in vericlaim schema (mapped level, extended caveat)
  MANIFEST.json       # sha256 per file; bundle_id = sha256(canonical manifest)
  artifacts/          # byte-exact evidence copies from the source repo
  code/               # generating scripts (auto-identified from `reproduce`) + curated modules
  literature/         # hash-verified extracts/notes + source citations
  provenance.json     # source repo+commit, source gate status, level-mapping decision
```

Immutable: any change is a new bundle_id; the D1 ledger records the chain.

## Honesty contract

- Level mapping is explicit config and **never upgrades** (REMORA:
  externally_benchmarked→externally_validated, internal_benchmark→benchmarked,
  regression_tested→benchmarked+caveat, internal_simulation→measured,
  theoretical→theoretical).
- Caveats are *extended* with harvest provenance, never trimmed. Negative
  results ship with the bundle. Withdrawn material (REMORA MaxEnt) is excluded
  by denylist in the mapping config.
- Harvest **refuses** if the source repo's own gate fails at harvest time.
- Bundles from repos **without** a register (generic extraction) are
  `status: candidate` — quarantined, never importable as verified claims, and
  labeled as candidates in search/oracle. A candidate becomes verified only by
  producing evidence (scaffolded script, run, registered) in a gated repo.
- The library proves a reused claim is **intact and traceable** to its source
  gate at harvest time — not that it holds in the new project's context.

## Components

1. `integrations/library/bundlefmt.py` — canonical manifest, build, verify
   (stdlib, offline).
2. `integrations/library/harvest.py` — register adapters (vericlaim-native;
   mapping-config for foreign taxonomies like REMORA's), source-gate check,
   code-extract identification from `reproduce` commands, bundle build.
3. `integrations/library/extract_candidates.py` — generic mode for arbitrary
   repos: scan docs/code for numeric/capability assertions → candidate claims
   (quarantined), each with a scaffolded evidence script
   (`scaffold_evidence`) that a curator completes and runs — the tool never
   fabricates results.
4. `integrations/library/gaps.py` — curation worklist: claims missing
   literature, missing reproduce, candidates pending evidence.
5. `integrations/library/import_bundle.py` — fetch (Worker or local path),
   verify all hashes offline, vendor under `claims/imported/<id>/`, emit a
   register entry with literature pointers + extended caveat. Target repo's
   gate stays zero-dep and offline.
6. Worker extension (existing vericlaim-claims Worker): D1 `library_bundles`
   (hash-chained), R2 files under the existing `sha256/<hash>` vault scheme,
   Vectorize entries with `library=true` metadata; endpoints
   `POST /library/index` (bearer), `GET /library/search|bundle/:id|verify/:id`;
   additive MCP tools `search_library`, `get_bundle`. Deploy with
   `--var ENABLE_MCP:true`.

## Round 1 harvest

All 11 REMORA claims (mapped), literature entries for the clearly-sourced ones
(AgentHarm, external datasets, confidence sequences) as hash-locked extracts,
code extracts from `reproduce` scripts, NEGATIVE_RESULTS.md attached. Gaps
report drives the next curation round.

## Acceptance

- Round-trip: harvest REMORA → import one bundle into a fresh tmp project →
  `vericlaim` gate green there with provenance intact.
- `verify_bundle` detects any tampered byte.
- Live: `/library/search` returns REMORA bundles; `/library/verify/:id` green;
  MCP `search_library` works in Claude Code.
- All tooling TDD'd, stdlib-only outside the Worker.
