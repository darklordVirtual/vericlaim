# The claims library — cross-project preservation and reuse

Curated, provenance-locked **claim bundles** — claims + evidence artifacts +
generating code + hash-verified literature — harvested from gate-verified
repos, preserved on Cloudflare (D1 hash-chained registry + R2 content-addressed
vault + Vectorize search), and reusable in any project via offline-verified
import. Design: `docs/superpowers/specs/2026-07-04-claims-library-design.md`.

**The library is distribution, never truth.** Trust comes from (1) the source
repo's own gate being green at harvest, (2) every hash verifying locally at
import, and (3) the target repo's own gate hash-locking the vendored content.

## The loop

```bash
# 1. HARVEST a gate-verified repo (refuses if its gate is red)
python3 integrations/library/harvest.py --source ~/REMORA-research \
    --config integrations/library/mappings/remora.toml --out build/library

# 2. PUSH to the Worker (server re-hashes everything on ingest)
python3 integrations/library/push_bundles.py --library build/library \
    --url "$WORKER_URL" --token "$INDEX_TOKEN"

# 3. DISCOVER from any project (HTTP or MCP search_library/get_bundle)
curl "$WORKER_URL/library/search?q=anytime-valid+monitoring"

# 4. FETCH + verify locally, then IMPORT into a fresh project
python3 integrations/library/fetch_bundle.py --url "$WORKER_URL" \
    --bundle <bundle_id> --out build/fetched
python3 integrations/library/import_bundle.py \
    --bundle build/fetched/<bundle_id> --target .
vericlaim   # the target's own gate is green, offline, tamper-guarded
```

## Arbitrary repos (no register)

`extract_candidates.py` mines assertion-like statements from any repo — but
everything lands as `status: candidate`: quarantined, unimportable, labeled in
search. `scaffold_evidence` writes an evidence-script template that fails until
a curator implements the real measurement. `gaps.py` prints the curation
worklist (candidates pending evidence, bundles missing literature/code).

## Honesty invariants (enforced, not aspirational)

- bundle_id = sha256(canonical manifest) — bundles are immutable; any change
  is a new bundle, chained in the D1 registry.
- Level mapping is explicit config (`mappings/*.toml`), never inferred, never
  an upgrade; caveats are extended with harvest provenance, never trimmed.
- Ingest is fail-closed server-side: mismatched bytes or a wrong bundle_id are
  rejected.
- Import refuses candidates, verifies every hash offline, and registers the
  vendored provenance as hash-locked `literature` entries — so the target
  repo's gate catches post-import tampering with no network involved.
