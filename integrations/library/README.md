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

# 5. PROGRAM with the claim behind you: vendor the bundle's code byte-exact
#    (the code you run IS the code that produced the evidence) plus a
#    generated binding test — editing the vendored code fails your own suite,
#    so forking is an explicit decision.
python3 integrations/library/use_code.py \
    --bundle build/fetched/<bundle_id> --target .
```

## Versioning (derived supersession)

Bundles are immutable, so re-enriching a repo at a new commit creates new
bundle versions. A bundle's *identity* is `(source_repo, source_claim_id)`,
and supersession is **derived** from the append-only registry — the latest
row per identity is current; nothing is declared, no schema changes, hash
chains and witnesses stay valid. Consequences:

- **search** surfaces current versions only (ingest prunes the previous
  version's vector; a query-time filter catches stragglers);
- `GET /library/bundle/:id` reports `supersedes` / `superseded_by` /
  `is_current`, and `fetch_bundle.py` warns when fetching a superseded
  version;
- `GET /library/versions?repo=..&claim=..` lists the full immutable chain —
  history is never deleted, only de-emphasized in discovery;
- `POST /library/prune` (bearer) is the idempotent maintenance/backfill.

## The research layer (literature RAG)

The claims library answers *"what has been proven?"*. The research layer
answers *"what does the literature actually say?"* — with the same honesty
rules. A machine-readable **canonical research map**
(`research/canon.toml`, 10 collections from uncertainty/conformal through
assurance cases) is the coverage contract; `litcoverage.py --check` fails
closed on any canon entry that is neither verified in the catalog nor a
documented drop (`research/drops.toml`, reason required).

Acquisition has three honesty tiers, all ending in the hash-locked catalog:

1. **registrar** (`acquire_canon.py`): arXiv/Crossref/DOI, title+author+year
   guard; optional DOI fields in the canon are *seeds* — searched, never
   trusted.
2. **official document**: DOI-carrying institutional docs (NIST, EUR-Lex).
3. **web snapshot** (`webfetch.py`): specs with no registrar record (SLSA,
   PROV-DM, C4…) — sha256-locked page text, always `accredited=false`,
   curator supplies the URL explicitly.

`fulltext.py` fetches arXiv HTML full text (ar5iv fallback, honest
abstract-only fallback recorded); `chunker.py` splits deterministically into
content-addressed, section-aware chunks (manifests refuse silent re-chunks);
`push_literature.py` re-verifies every hash before the wire and pushes
idempotently to the Worker's `/research/*` layer (separate Vectorize index,
D1 mirror, shared R2 vault). `/research/ask` — and the MCP tools
`search_literature_rag` / `ask_research` — answer ONLY from retrieved
excerpts and **refuse** otherwise. Retrieval, never evidence: a hit proves
the text was cataloged and hash-locked, not that it is true.

## External anchoring

The Worker's hash chains are witnessed in this repo's public git history
(`claims/witness.jsonl`). `integrations/cloudflare-ai/witness.py --verify`
re-walks the full `/ledger/export` client-side — never trusting the Worker's
own verify — and requires today's chains to extend every witnessed head, so a
rebuilt or truncated history fails against any prior witness. Record a new
witness (`--record`) after each push, then commit and push the witness file.

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
