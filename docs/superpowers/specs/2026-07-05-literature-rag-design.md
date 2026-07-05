# Literature RAG — the vetted research layer

Date: 2026-07-05. Approved by Stian (hybrid content, standalone works, separate
index — all three confirmed).

## Problem

The claims library answers "what have we verified?" but the RAG stops at claim
statements. The system needs intelligence *beyond* claims: the literature
itself — the canonical research map (10 collections, ~120 works spanning
uncertainty/routing, agents, evaluation, agent security, governance, MLOps,
provenance/supply-chain, formal methods, fairness/privacy, assurance cases) —
vectorized and queryable with the same provenance discipline as everything
else. Claim-Oriented Programming should let a Claude skill answer with
precision because every assertion links down through claims to hash-locked
source chunks.

## Non-goals

- No new truth tier. The literature layer is *retrieval*, never evidence:
  a work being in the catalog proves it was registrar-verified and snapshotted,
  not that its contents are true.
- No full-text for works we cannot legally fetch (books, paywalled papers,
  most standards). They get registrar metadata + abstract + our hash-locked
  extract, honestly marked.
- Core stays untouched. Everything lives under `integrations/`, stdlib-only.

## Decisions (with the user)

1. **Hybrid content**: full text chunked for open arXiv works; abstract +
   curated extract for everything else. All content-addressed.
2. **Works stand alone**: the catalog is first-class; claims link to works
   when links exist. Coverage reports works without claims as honest gaps —
   it never blocks a verified work from being searchable.
3. **Separate serving layer**: new Vectorize index `vericlaim-literature`,
   `/research/*` endpoints, new MCP tools. Claim search is untouched.

## Architecture

### 1. Canonical research map — `integrations/library/research/canon.toml`

The user's research map made machine-readable: 10 collections
(`01_uncertainty_and_routing` … `10_assurance_cases_and_runtime_verification`),
each entry with `title`, `authors` (surnames), `year`, `kind`
(paper|book|standard|spec), `priority` (`p0` flag, `top15` flag), `registrar`
hint (arxiv|crossref|doi|web). This file is the coverage *contract*.

### 2. Coverage — `integrations/library/coverage.py`

Matches canon entries against the catalog (`literature/works/`) using the
existing title+author+year guard, and against library claims via
`links.jsonl`. Per entry it reports: verified? text stored? chunked?
vectorized (present in the push manifest)? claim-linked? Plus honest drops
with reasons. Output is a deterministic report artifact; the headline numbers
land in README via `<!-- v: -->` value tokens so they cannot drift. Fail-closed:
`coverage.py --check` exits nonzero if any canon entry is neither
verified-in-catalog nor an explicit documented drop.

### 3. Acquisition — three honesty tiers

- **Tier 1 registrar** (existing `litfetch`): arXiv Atom + Crossref REST,
  title+author+year guard, `accredited` only for peer-reviewed Crossref types.
- **Tier 2 official document**: DOI-carrying institutional docs (NIST AI RMF,
  SP 800-207/218) via Crossref/DataCite DOI lookup; EU AI Act by CELEX id from
  EUR-Lex with a snapshot.
- **Tier 3 web snapshot** (`webfetch.py`): SLSA, in-toto, W3C PROV-DM, C4,
  Rules of ML, TUF spec… No registrar record exists; store URL + fetch date +
  sha256-locked snapshot, `accredited=false`, `source="web-snapshot"`. Never
  dressed up as peer-reviewed. First snapshot wins.

All tiers end in the same `litindex.add_work` path; work records carry the
tier in `retrieval`.

### 4. Full text + chunks

- `fulltext.py`: for arXiv works, fetch `https://arxiv.org/html/<id>`
  (fallback `ar5iv.labs.arxiv.org/html/<id>`), strip to plain text with
  stdlib `html.parser`, drop nav/math-noise, keep section headings. Stored
  content-addressed in `literature/texts/` like abstracts; the work record
  gains `fulltext_sha256` + retrieval provenance. Failure → honest fallback
  to abstract-only (recorded, not hidden). Politeness: ≥3 s between fetches;
  explicit User-Agent (the edge 403s default urllib).
- `chunker.py`: deterministic, section-aware splitting (~1200 chars target,
  200 overlap, never split mid-sentence when avoidable). Each chunk sha256'd;
  per-work manifest `literature/chunks/<fsid>.jsonl` with ordered chunk
  hashes + section labels. Chunks never mutate silently; re-chunking a
  changed text is a new manifest generation (old one superseded in git
  history, catalog stays append-honest).

### 5. Worker research layer (`integrations/cloudflare-ai`)

- New Vectorize index `vericlaim-literature` (768/cosine, same
  `@cf/baai/bge-base-en-v1.5`). Vector id `lit:<48 hex of chunk sha>`
  (64-byte id limit). Metadata: work_id, fsid, section, seq, kind, tier,
  accredited.
- New D1 table `literature_works` (serving metadata mirror; git catalog is
  the anchor — no second hash chain).
- R2 vault reused: chunk texts at `sha256/<hash>`.
- Endpoints:
  - `POST /research/index` (bearer `INDEX_TOKEN`): accepts work records +
    chunk batches, embeds server-side, upserts vectors, vaults texts,
    upserts D1 rows. Idempotent by sha.
  - `GET /research/search?q=`: embed → topK over literature index → hits
    with work metadata, section, snippet, and any linked claims (bridge via
    links pushed with the works).
  - `GET /research/ask?q=`: same oracle discipline as `/ask` — retrieve,
    rerank (`@cf/baai/bge-reranker-base`), **refuse** when nothing clears
    the relevance bar, answer grounded with work_id + chunk citations only.
  - `GET /research/work/:fsid`, `GET /research/summary`.
- MCP: two new tools `search_literature_rag` (chunk-level retrieval) and
  `ask_research` (grounded/refusing oracle). Existing tools untouched.
- `push_literature.py` (stdlib): reads catalog + chunk manifests, pushes in
  batches. Dedupe is server-side: `/research/index` treats already-present
  shas as no-ops and reports them as `skipped`, so re-pushing the whole
  catalog is always safe. Records a push manifest locally for coverage.

### 6. Claims ↔ literature bridge

`links.jsonl` entries are pushed with works; `/research/search` hits include
`linked_claims`. Future (out of scope now): `/ask` escalating to the research
layer when no claim matches.

## Error handling

- Every fetch tool: fail-closed on hash mismatch, explicit drops with
  reasons, never silent skips.
- Worker ingest: rejects chunks whose sha doesn't match content; partial
  batches report per-item status.
- `/research/ask` refuses rather than hallucinating — same bar as `/ask`.

## Testing

- TDD (pytest, stdlib) for canon parsing, coverage matching, chunker
  determinism (golden manifests), fulltext HTML stripping (fixture pages),
  push idempotency (fake transport).
- Worker: extend existing test suite for new routes (mock AI/Vectorize/D1
  bindings as done today).
- Live verification (phase 5): round-trip search over a known chunk;
  `/research/ask` answers a supported question and refuses an unsupported
  one; coverage `--check` green; verification ritual
  (`pytest && vericlaim && reproduce && ruff`) before every push; deploy
  with `--var ENABLE_MCP:true`.

## Phases

1. `canon.toml` + `coverage.py` (contract first — coverage is red and honest).
2. Acquisition of missing works, tiers 1→3; documented drops.
3. `fulltext.py` + `chunker.py`; chunk all catalog works.
4. Worker research layer + `push_literature.py`.
5. Full ingest, live round-trip, coverage green (or honestly red with named
   gaps), claims about the library registered with v-tokens, witness pushed,
   README consequence-first, release tag.
