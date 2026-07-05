# Literature RAG Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Vectorize the canonical research literature (hybrid full-text/abstract, three honesty tiers) into a separate Cloudflare research layer with coverage checked against a machine-readable canon.

**Architecture:** The git-anchored `litindex` catalog stays the single source of truth; `canon.toml` is the coverage contract; new stdlib tools acquire, snapshot, chunk and push; the Worker gains a `/research/*` layer over a new Vectorize index `vericlaim-literature` plus D1 serving tables and the existing R2 vault.

**Tech Stack:** Python 3.11+ stdlib only (tools), TypeScript Cloudflare Worker (existing `integrations/cloudflare-ai`), Workers AI `@cf/baai/bge-base-en-v1.5` (768/cosine) + `@cf/baai/bge-reranker-base`.

## Global Constraints

- Zero runtime dependencies in Python tools; everything under `integrations/`, core untouched.
- Fail-closed everywhere: hash mismatch, missing metadata or unverifiable source ⇒ error/drop with reason, never a silent skip.
- Bibliographic metadata ONLY from registrar responses (litfetch anti-fabrication rule); tier-3 snapshots are `accredited=false`, `source="web-snapshot"`.
- First snapshot wins: stored texts and chunk manifests never mutate silently.
- All HTTP clients set an explicit User-Agent (edge 403s default urllib) and pause ≥3 s between arXiv calls.
- Verification ritual before every push: `python3 -m pytest tests/ -q && python3 -m vericlaim && python3 -m vericlaim reproduce && python3 -m ruff check .`
- Worker deploys ALWAYS with `--var ENABLE_MCP:true`.
- Commits with Stian's identity, no Claude co-author trailer.
- Numbers in README/docs only via registered claims + `<!-- v: -->` tokens.

---

### Task 1: canon.toml + canon.py loader

**Files:**
- Create: `integrations/library/research/canon.toml` (entries in Appendix A)
- Create: `integrations/library/canon.py`
- Test: `tests/test_canon.py`

**Interfaces:**
- Produces: `canon.load(path: Path) -> list[dict]` — validated entries, each
  `{id, collection, title, authors: list[str], year: int|None, kind, registrar, p0: bool, top15: bool}`;
  raises `ValueError` naming the entry id on any invalid/missing field.
  `canon.COLLECTIONS` — the 10 canonical collection names, ordered.

- [ ] **Step 1: Write failing tests** — valid load returns all entries with defaults applied; duplicate id raises; unknown collection raises; unknown kind raises; missing authors raises.

```python
# tests/test_canon.py
import textwrap
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "integrations" / "library"))
import canon  # noqa: E402

GOOD = textwrap.dedent("""
    [[work]]
    id = "shannon-1948"
    collection = "01_uncertainty_and_routing"
    title = "A Mathematical Theory of Communication"
    authors = ["Shannon"]
    year = 1948
    kind = "paper"
    registrar = "crossref"
    p0 = true
    top15 = false
""")

def _write(tmp_path, body):
    p = tmp_path / "canon.toml"
    p.write_text(body)
    return p

def test_load_valid(tmp_path):
    entries = canon.load(_write(tmp_path, GOOD))
    assert entries[0]["id"] == "shannon-1948"
    assert entries[0]["p0"] is True and entries[0]["top15"] is False

def test_duplicate_id_rejected(tmp_path):
    with pytest.raises(ValueError, match="shannon-1948"):
        canon.load(_write(tmp_path, GOOD + GOOD))

def test_unknown_collection_rejected(tmp_path):
    bad = GOOD.replace("01_uncertainty_and_routing", "99_nope")
    with pytest.raises(ValueError, match="99_nope"):
        canon.load(_write(tmp_path, bad))

def test_unknown_kind_rejected(tmp_path):
    with pytest.raises(ValueError, match="kind"):
        canon.load(_write(tmp_path, GOOD.replace('kind = "paper"', 'kind = "poem"')))

def test_real_canon_loads_and_is_big():
    root = Path(__file__).resolve().parents[1]
    entries = canon.load(root / "integrations/library/research/canon.toml")
    assert len(entries) >= 90
    assert sum(1 for e in entries if e["top15"]) >= 15
```

- [ ] **Step 2:** `pytest tests/test_canon.py -q` — FAIL (no module `canon`).
- [ ] **Step 3: Implement `canon.py`** — `tomllib` parse; validate id uniqueness, collection ∈ COLLECTIONS, kind ∈ {paper, book, standard, spec, report}, registrar ∈ {arxiv, crossref, doi, web}, authors non-empty; defaults `p0=false`, `top15=false`, `year=None` allowed only for kind ∈ {standard, spec}.
- [ ] **Step 4: Author `research/canon.toml`** from Appendix A (every row one `[[work]]` entry).
- [ ] **Step 5:** `pytest tests/test_canon.py -q` — PASS. `ruff check .` clean.
- [ ] **Step 6:** Commit `feat(library): machine-readable canonical research map + loader`.

### Task 2: coverage.py

**Files:**
- Create: `integrations/library/coverage.py`
- Create: `integrations/library/research/drops.toml` (starts empty: `drop = []`)
- Test: `tests/test_coverage.py`

**Interfaces:**
- Consumes: `canon.load`, `litindex._load_works`, `biblio_curate.titles_agree`.
- Produces: `coverage.match(entry: dict, works: dict[str, dict]) -> str | None` (work_id or None; guard = titles_agree(title, work title) AND any canon surname in work authors AND (year is None or |Δyear| ≤ 1)); `coverage.report(root: Path, canon_path: Path, drops_path: Path, push_manifest: Path | None) -> dict` with per-entry status `{verified, text, fulltext, chunked, vectorized, claim_linked, dropped_reason}`; CLI `--check` exits 1 if any entry is neither matched nor in drops.toml (with reason), `--md` renders the report table.

- [ ] **Step 1: Write failing tests** — match by title+author+year guard; near-title imitation rejected (reuse the Guo-2017 lesson: same words different year/authors fails); report marks unmatched entry as gap; `--check` semantics via `check(report) -> list[str]` returning failures; drop with reason silences the gap but is listed under `drops`.

```python
# tests/test_coverage.py (core cases)
def test_match_requires_author_and_year():
    entry = {"id": "guo-2017", "title": "On Calibration of Modern Neural Networks",
             "authors": ["Guo"], "year": 2017, "kind": "paper"}
    works = {"doi:10.1/x": {"work_id": "doi:10.1/x",
             "title": "On calibration of modern neural networks",
             "authors": ["Chuan Guo", "Geoff Pleiss"], "year": 2017}}
    assert coverage.match(entry, works) == "doi:10.1/x"
    works["doi:10.1/x"]["year"] = 1989
    assert coverage.match(entry, works) is None

def test_unmatched_entry_is_visible_gap(tmp_path):
    rep = coverage.report(...)   # catalog without the work
    assert rep["entries"]["guo-2017"]["verified"] is False
    assert "guo-2017" in coverage.check(rep)

def test_documented_drop_is_not_a_failure(tmp_path):
    # drops.toml: [[drop]] id="iso-42001" reason="no registrar record; paywalled standard"
    assert "iso-42001" not in coverage.check(rep)
    assert rep["drops"]["iso-42001"].startswith("no registrar")
```

- [ ] **Step 2:** run — FAIL. **Step 3:** implement (chunked = manifest exists in `literature/chunks/`, fulltext = `fulltext_sha256` in work record, vectorized = all manifest shas present in push manifest, claim_linked = any link in links.jsonl). **Step 4:** run — PASS; ruff clean. **Step 5:** Commit `feat(library): coverage — canon vs catalog, fail-closed check`.

### Task 3: webfetch.py (tier 2/3 snapshots)

**Files:**
- Create: `integrations/library/webfetch.py`
- Test: `tests/test_webfetch.py`

**Interfaces:**
- Consumes: `litindex.add_work`.
- Produces: `webfetch.snapshot_work(root: Path, *, work_id: str, url: str, title: str, publisher: str, year: int | None, html: bytes, fetched_at: str) -> str` — strips HTML to text (shared `strip_html(html: bytes) -> str` used later by fulltext), builds a work record with `registrar="web-snapshot"`, `source_type="web-snapshot"`, `accredited=False`, and calls `add_work` with retrieval `{method: "web-snapshot", url, fetched_at, content_sha256}`; CLI `--url --work-id --title --publisher [--year]` does the fetch (UA set) then calls `snapshot_work`. `strip_html` drops `<script>/<style>/<nav>/<header>/<footer>/<math>` subtrees, renders `h1-h3` as `## <text>` lines, collapses whitespace.

- [ ] **Step 1: failing tests** — `strip_html` on a fixture with nav/script/math keeps body text + `##` headings and drops noise; `snapshot_work` writes a work whose `text_sha256` matches the stored text and whose record says `accredited=False`; a second snapshot of the same work_id does not change the stored text (first wins).
- [ ] **Step 2:** FAIL. **Step 3:** implement with `html.parser.HTMLParser` subclass (stack of skipped tags; heading buffer). **Step 4:** PASS + ruff. **Step 5:** Commit `feat(library): tier-3 web snapshots — hash-locked, honestly non-accredited`.

### Task 4: fulltext.py

**Files:**
- Create: `integrations/library/fulltext.py`
- Modify: `integrations/library/litindex.py` (add `add_fulltext`)
- Test: `tests/test_fulltext.py`

**Interfaces:**
- Consumes: `webfetch.strip_html`.
- Produces: `litindex.add_fulltext(root: Path, work_id: str, text: str, retrieval: dict) -> str` — stores content-addressed in `texts/`, sets `fulltext_sha256` + `fulltext_retrieval` on the work record only if absent (first wins), returns sha; `fulltext.fetch_arxiv_html(arxiv_id: str, opener=urllib.request.urlopen) -> tuple[str, str]` — tries `https://arxiv.org/html/<id>` then `https://ar5iv.labs.arxiv.org/html/<id>`, returns `(text, source_url)`, raises `LookupError` if both fail; CLI `--all` walks catalog works with `work_id` starting `arxiv:` and no `fulltext_sha256`, ≥3 s between fetches, prints per-work `fetched|fallback-abstract-only|already`.

- [ ] **Step 1: failing tests** — `add_fulltext` first-wins + verify() still green after adding; `fetch_arxiv_html` with a fake opener: first URL 404 ⇒ falls to ar5iv; both fail ⇒ `LookupError`; stripping produces `## ` sections from fixture HTML.
- [ ] **Step 2:** FAIL. **Step 3:** implement; extend `litindex.verify` to also hash-check `fulltext_sha256` when present. **Step 4:** PASS + ruff. **Step 5:** Commit `feat(library): arXiv full text — content-addressed, first snapshot wins`.

### Task 5: chunker.py

**Files:**
- Create: `integrations/library/chunker.py`
- Test: `tests/test_chunker.py`

**Interfaces:**
- Produces: `chunker.chunk(text: str, *, target: int = 1200, overlap: int = 200) -> list[dict]` — each `{seq, section, text, sha256}`; section = most recent `## ` heading ("" before the first); sentences never split when avoidable (split on `(?<=[.!?])\s+`, a sentence longer than 2×target is hard-wrapped); consecutive chunks share ~overlap chars (whole trailing sentences of the previous chunk). `chunker.write_manifest(root: Path, fsid: str, source_sha: str, chunks: list[dict]) -> Path` — writes `literature/chunks/<fsid>.jsonl`: first line `{"fsid","source_sha256","target","overlap","n"}` then one line per chunk (text NOT in the manifest — chunk texts go content-addressed into `texts/`); refuses to overwrite a manifest with a different `source_sha256` unless `--refresh`. CLI `--all` chunks fulltext when present else abstract+extract text.
- Consumes: nothing new.

- [ ] **Step 1: failing tests** — determinism (same text twice ⇒ identical shas); section labels follow `##` headings; every chunk ≤ 2×target; overlap present between consecutive chunks in the same section; `write_manifest` round-trips and refuses silent source change.
- [ ] **Step 2:** FAIL. **Step 3:** implement. **Step 4:** PASS + ruff. **Step 5:** Commit `feat(library): deterministic section-aware chunking, content-addressed manifests`.

### Task 6: Acquisition run (tiers 1–3) — operational

**Files:**
- Create: `integrations/library/acquire_canon.py` (thin driver)
- Modify: `integrations/library/research/drops.toml` (honest drops as found)

**Interfaces:**
- Consumes: `canon.load`, `coverage.match/report`, `litfetch.search_arxiv/search_crossref/lookup_doi` (whatever exists — check `litfetch` for the author-qualified Crossref search used for Shannon-1948, reuse it), `webfetch.snapshot_work`, `biblio_curate.titles_agree`.
- Produces: catalog works for every canon entry or a documented drop. Driver logic per unmatched entry: registrar=arxiv ⇒ arXiv `ti:"<title>"` phrase search (NOT `all:` — phrase search is the working trick); registrar=crossref/doi ⇒ author-qualified Crossref title search, guard title+author+year; registrar=web ⇒ print the entry for manual `webfetch` invocation (tier 3 is curator-invoked with an explicit URL — the driver never guesses URLs).

- [ ] **Step 1:** `python3 integrations/library/acquire_canon.py --dry-run` — list unmatched entries per tier.
- [ ] **Step 2:** run tier 1+2 acquisition; watch guard rejections; re-run `coverage.py --md`.
- [ ] **Step 3:** for each `registrar="web"` entry run `webfetch.py` with the curated URL (SLSA levels page, in-toto spec, W3C PROV-DM TR, c4model.com, Rules of ML, GSN standard, EUR-Lex CELEX 32024R1689 English HTML, Anthropic monosemanticity page, MemGPT if needed, event-sourcing page).
- [ ] **Step 4:** entries still unmatched (paywalled books, ISO 42001…) get `[[drop]]` with reason. `coverage.py --check` must exit 0.
- [ ] **Step 5:** `litindex.py verify` green; full ritual; Commit `feat(library): canon acquisition — works verified or honestly dropped`.

### Task 7: Full text + chunk the catalog — operational

- [ ] **Step 1:** `python3 integrations/library/fulltext.py --all` (arXiv works; polite pacing; expect some `fallback-abstract-only`).
- [ ] **Step 2:** `python3 integrations/library/chunker.py --all`.
- [ ] **Step 3:** `litindex.py verify` + `coverage.py --md` — fulltext/chunked columns populated; ritual; Commit `feat(library): full text + chunks for the catalog`.

### Task 8: Worker research layer

**Files:**
- Create: `integrations/cloudflare-ai/src/research.ts`
- Modify: `integrations/cloudflare-ai/src/index.ts` (routes), `src/lib.ts` (Env: `VECTORIZE_LIT: VectorizeIndex`), `wrangler.toml` (second `[[vectorize]]` binding `VECTORIZE_LIT` → `vericlaim-literature`), `schema.sql` (new tables)
- Test: `integrations/cloudflare-ai/test/live_test.py` (extended in Task 11 — Worker repo has live tests only, per existing convention)

**Interfaces:**
- Consumes: `embed(env, texts)`, `json()` helper, `authorized()`, oracle's rerank pattern (`@cf/baai/bge-reranker-base`), vault `putEvidence/getEvidence`.
- Produces (route contracts push_literature.py and MCP rely on):
  - `POST /research/index` (bearer) body `{works: [{fsid, work_id, title, authors, year, venue, kind, tier, accredited, url, linked_claims}], chunks: [{sha, fsid, seq, section, text}]}` → per-item `{sha, status: "indexed"|"skipped"|"rejected", reason?}`; rejects when sha256(text) ≠ sha; skips when sha already in D1.
  - `GET /research/search?q=&topK=` → `{hits: [{score, sha, fsid, work_id, title, section, snippet, accredited, tier, linked_claims}]}`.
  - `GET /research/ask?q=` → grounded `{answer, citations: [{work_id, sha, section}]}` or `{refused: true, reason}` — same refusal bar pattern as `oracle.ask`.
  - `GET /research/work/:fsid` → work row + ordered chunk list.
  - `GET /research/summary` → `{works, chunks, by_tier, by_collection?}` (works/chunks counts from D1).

```sql
-- schema.sql additions
CREATE TABLE IF NOT EXISTS literature_works (
  fsid TEXT PRIMARY KEY, work_id TEXT NOT NULL, title TEXT NOT NULL,
  authors TEXT NOT NULL, year INTEGER, venue TEXT, kind TEXT NOT NULL,
  tier TEXT NOT NULL, accredited INTEGER NOT NULL, url TEXT,
  linked_claims TEXT NOT NULL DEFAULT '[]', updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS literature_chunks (
  sha TEXT PRIMARY KEY, fsid TEXT NOT NULL, seq INTEGER NOT NULL,
  section TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_lit_chunks_fsid ON literature_chunks(fsid, seq);
```

Ingest core (research.ts): verify sha with WebCrypto (`crypto.subtle.digest`), batch-embed only novel chunks (batch ≤ 20), vector id `"lit:" + sha.slice(0, 48)`, metadata `{fsid, work_id, section, seq, snippet: text.slice(0, 300), accredited, tier}`, `putEvidence` full text to R2, D1 insert. Search: embed query → `VECTORIZE_LIT.query(vector, {topK, returnMetadata: "all"})` → join `literature_works`. Ask: top 8 → rerank vs query → threshold as in oracle → generate with the same model oracle uses, context = chunk texts fetched from R2, instructed to cite `[work_id]` only.

- [ ] **Step 1:** write `research.ts` + routes + Env + wrangler binding + schema.
- [ ] **Step 2:** `npx tsc --noEmit` (or the repo's existing check) passes; `npx wrangler deploy --dry-run` bundles.
- [ ] **Step 3:** Commit `feat(cloudflare): /research layer — literature index, grounded ask that refuses`.

### Task 9: MCP tools

**Files:**
- Modify: `integrations/cloudflare-ai/src/mcp.ts`

**Interfaces:**
- Produces: MCP tools `search_literature_rag {query, topK?}` → same shape as `/research/search`; `ask_research {question}` → same shape as `/research/ask`. Both call the research.ts functions directly (as existing tools do for library.ts).

- [ ] **Step 1:** add the two tools following the existing `search_library`/`ask_claims` registration pattern. **Step 2:** typecheck + dry-run bundle. **Step 3:** Commit `feat(cloudflare): MCP tools search_literature_rag + ask_research`.

### Task 10: push_literature.py

**Files:**
- Create: `integrations/library/push_literature.py`
- Test: `tests/test_push_literature.py`

**Interfaces:**
- Consumes: catalog layout, chunk manifests, `/research/index` contract, token file `~/.vericlaim_index_token`.
- Produces: `build_batches(root: Path, batch_chunks: int = 30) -> list[dict]` (pure, testable: request bodies with works + chunk texts loaded from `texts/`); CLI `--push <url> [--token-file ~/.vericlaim_index_token]` posts batches (explicit UA), prints indexed/skipped/rejected tallies, fails nonzero on any rejected, appends `{sha, pushed_at}` lines to `research/push_manifest.jsonl` for indexed+skipped.

- [ ] **Step 1: failing tests** — `build_batches` includes every manifest chunk exactly once with correct text (sha re-verified locally before sending; mismatch raises); batch size respected; work record fields mapped (tier from retrieval method, fsid from filename).
- [ ] **Step 2:** FAIL. **Step 3:** implement. **Step 4:** PASS + ruff. **Step 5:** Commit `feat(library): idempotent literature push`.

### Task 11: Deploy + full ingest + live verification

- [ ] **Step 1:** `npx wrangler vectorize create vericlaim-literature --dimensions=768 --metric=cosine`; apply schema: `npx wrangler d1 execute vericlaim-ledger --remote --file=schema.sql`.
- [ ] **Step 2:** `npx wrangler deploy --var ENABLE_MCP:true`.
- [ ] **Step 3:** `python3 integrations/library/push_literature.py --push https://vericlaim-claims.razorsharp.workers.dev` (token from `~/.vericlaim_index_token`). Wait ~30 s (Vectorize indexing lag).
- [ ] **Step 4:** extend `test/live_test.py`: `/research/summary` counts > 0; `/research/search?q=conformal risk control` returns an Angelopoulos hit; `/research/ask` answers a supported question WITH citations and refuses an off-corpus question (e.g. "What does the canon say about quantum gravity?"); `search_literature_rag` reachable over MCP after reconnect.
- [ ] **Step 5:** run live tests; re-run `coverage.py --check` with push manifest — vectorized column true for all chunked works. Commit `test(cloudflare): research layer live verification`.

### Task 12: Claims, README, witness, release

- [ ] **Step 1:** invoke the repo's claim-oriented-programming skill; register claims for the headline numbers (canon size, works verified, drops, chunks vectorized, live round-trip) with artifacts = coverage report + push manifest + live test output; wire `<!-- v: -->` tokens into README section "The research layer".
- [ ] **Step 2:** README: consequence-first paragraph (pain: RAG that answers beyond its evidence; consequence: this one refuses; demo: one `ask_research` transcript).
- [ ] **Step 3:** full ritual green; commit; `witness.py --record` + commit + push (public anchor).
- [ ] **Step 4:** tag `v0.4.0`, GitHub release notes.

---

## Appendix A: canon.toml entries

Format per row: `id | collection | title | authors | year | kind | registrar | p0 | top15`. Collections: 01_uncertainty_and_routing, 02_llm_and_agent_architectures, 03_evaluation_and_calibration, 04_agent_security, 05_ai_governance, 06_mlops_and_enterprise_architecture, 07_provenance_and_supply_chain, 08_formal_methods, 09_fairness_privacy_and_human_impact, 10_assurance_cases_and_runtime_verification.

```
shannon-1948            |01|A Mathematical Theory of Communication|Shannon|1948|paper|crossref|p0|
bayes-1763              |01|An Essay towards solving a Problem in the Doctrine of Chances|Bayes|1763|paper|crossref|p0|
valiant-pac-1984        |01|A Theory of the Learnable|Valiant|1984|paper|crossref|p0|
vc-1971                 |01|On the Uniform Convergence of Relative Frequencies of Events to Their Probabilities|Vapnik,Chervonenkis|1971|paper|crossref|p0|
nfl-opt-1997            |01|No Free Lunch Theorems for Optimization|Wolpert,Macready|1997|paper|crossref|p0|
guo-calibration-2017    |01|On Calibration of Modern Neural Networks|Guo|2017|paper|arxiv|p0|
selective-2017          |01|Selective Classification for Deep Neural Networks|Geifman,El-Yaniv|2017|paper|arxiv|p0|
gentle-conformal-2021   |01|A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification|Angelopoulos,Bates|2021|paper|arxiv|p0|
conformal-risk-2022     |01|Conformal Risk Control|Angelopoulos|2022|paper|arxiv|p0|top15
confidence-seq-2021     |01|Time-uniform, nonparametric, nonasymptotic confidence sequences|Howard|2021|paper|arxiv|p0|
attention-2017          |02|Attention Is All You Need|Vaswani|2017|paper|arxiv|p0|
scaling-laws-2020       |02|Scaling Laws for Neural Language Models|Kaplan|2020|paper|arxiv|p0|
chinchilla-2022         |02|Training Compute-Optimal Large Language Models|Hoffmann|2022|paper|arxiv|p0|
instructgpt-2022        |02|Training language models to follow instructions with human feedback|Ouyang|2022|paper|arxiv|p0|
constitutional-ai-2022  |02|Constitutional AI: Harmlessness from AI Feedback|Bai|2022|paper|arxiv|p0|
dpo-2023                |02|Direct Preference Optimization: Your Language Model is Secretly a Reward Model|Rafailov|2023|paper|arxiv|p0|
superposition-2022      |02|Toy Models of Superposition|Elhage|2022|paper|arxiv|p0|
monosemanticity-2023    |02|Towards Monosemanticity: Decomposing Language Models With Dictionary Learning|Bricken|2023|report|web|p0|
rag-2020                |02|Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks|Lewis|2020|paper|arxiv|p0|top15
cot-2022                |02|Chain-of-Thought Prompting Elicits Reasoning in Large Language Models|Wei|2022|paper|arxiv|p0|
react-2022              |02|ReAct: Synergizing Reasoning and Acting in Language Models|Yao|2022|paper|arxiv|p0|top15
toolformer-2023         |02|Toolformer: Language Models Can Teach Themselves to Use Tools|Schick|2023|paper|arxiv|p0|top15
reflexion-2023          |02|Reflexion: Language Agents with Verbal Reinforcement Learning|Shinn|2023|paper|arxiv|p0|
tree-of-thoughts-2023   |02|Tree of Thoughts: Deliberate Problem Solving with Large Language Models|Yao|2023|paper|arxiv|p0|
self-rag-2023           |02|Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection|Asai|2023|paper|arxiv|p0|
memgpt-2023             |02|MemGPT: Towards LLMs as Operating Systems|Packer|2023|paper|arxiv|p0|
truthfulqa-2021         |03|TruthfulQA: Measuring How Models Mimic Human Falsehoods|Lin|2021|paper|arxiv|p0|top15
mmlu-2020               |03|Measuring Massive Multitask Language Understanding|Hendrycks|2020|paper|arxiv|p0|
big-bench-2022          |03|Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models|Srivastava|2022|paper|arxiv|p0|
helm-2022               |03|Holistic Evaluation of Language Models|Liang|2022|paper|arxiv|p0|top15
humaneval-2021          |03|Evaluating Large Language Models Trained on Code|Chen|2021|paper|arxiv|p0|
swe-bench-2023          |03|SWE-bench: Can Language Models Resolve Real-World GitHub Issues?|Jimenez|2023|paper|arxiv|p0|
agentharm-2024          |03|AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents|Andriushchenko|2024|paper|arxiv|p0|
agentdojo-2024          |03|AgentDojo: A Dynamic Environment to Evaluate Attacks and Defenses for LLM Agents|Debenedetti|2024|paper|arxiv|p0|
tau-bench-2024          |03|tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains|Yao|2024|paper|arxiv|p0|
prompt-injection-2023   |04|Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection|Greshake|2023|paper|arxiv|p0|top15
injecagent-2024         |04|InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents|Zhan|2024|paper|arxiv|p0|top15
anderson-monitor-1972   |04|Computer Security Technology Planning Study|Anderson|1972|report|web|p0|
capabilities-1966       |04|Programming Semantics for Multiprogrammed Computations|Dennis,Van Horn|1966|paper|crossref|p0|
saltzer-schroeder-1975  |04|The Protection of Information in Computer Systems|Saltzer,Schroeder|1975|paper|crossref|p0|
intriguing-2013         |04|Intriguing properties of neural networks|Szegedy|2013|paper|arxiv||
adversarial-2014        |04|Explaining and Harnessing Adversarial Examples|Goodfellow|2014|paper|arxiv|p0|
carlini-wagner-2017     |04|Towards Evaluating the Robustness of Neural Networks|Carlini,Wagner|2017|paper|arxiv|p0|
model-extraction-2016   |04|Stealing Machine Learning Models via Prediction APIs|Tramer|2016|paper|arxiv|p0|
universal-attacks-2023  |04|Universal and Transferable Adversarial Attacks on Aligned Language Models|Zou|2023|paper|arxiv||
extracting-training-2020|04|Extracting Training Data from Large Language Models|Carlini|2020|paper|arxiv||
mirai-2017              |04|Understanding the Mirai Botnet|Antonakakis|2017|paper|web||
nist-ai-rmf-2023        |05|Artificial Intelligence Risk Management Framework (AI RMF 1.0)|NIST|2023|standard|doi|p0|top15
nist-genai-2024         |05|Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile|NIST|2024|standard|doi|p0|
eu-ai-act-2024          |05|Regulation (EU) 2024/1689 (Artificial Intelligence Act)|European Parliament,Council|2024|standard|web|p0|top15
iso-42001-2023          |05|ISO/IEC 42001:2023 Artificial intelligence management system|ISO|2023|standard|web|p0|top15
model-cards-2019        |05|Model Cards for Model Reporting|Mitchell|2019|paper|arxiv|p0|top15
datasheets-2018         |05|Datasheets for Datasets|Gebru|2018|paper|arxiv|p0|top15
factsheets-2019         |05|FactSheets: Increasing trust in AI services through supplier's declarations of conformity|Arnold|2019|paper|crossref|p0|
aia-2018                |05|Algorithmic Impact Assessments: A Practical Framework for Public Agency Accountability|Reisman|2018|report|web|p0|
verifiable-claims-2020  |05|Toward Trustworthy AI Development: Mechanisms for Supporting Verifiable Claims|Brundage|2020|paper|arxiv||
sculley-debt-2015       |06|Hidden Technical Debt in Machine Learning Systems|Sculley|2015|paper|web|p0|top15
ml-test-score-2017      |06|The ML Test Score: A Rubric for ML Production Readiness and Technical Debt Reduction|Breck|2017|paper|crossref|p0|
rules-of-ml             |06|Rules of Machine Learning: Best Practices for ML Engineering|Zinkevich|None|spec|web|p0|
data-cascades-2021      |06|"Everyone wants to do the model work, not the data work": Data Cascades in High-Stakes AI|Sambasivan|2021|paper|crossref|p0|
dataset-shift-2009      |06|Dataset Shift in Machine Learning|Quionero-Candela|2009|book|crossref|p0|
cap-2002                |06|Brewer's conjecture and the feasibility of consistent, available, partition-tolerant web services|Gilbert,Lynch|2002|paper|crossref|p0|
raft-2014               |06|In Search of an Understandable Consensus Algorithm|Ongaro,Ousterhout|2014|paper|web|p0|
event-sourcing          |06|Event Sourcing|Fowler|None|spec|web||
ddd-2003                |06|Domain-Driven Design: Tackling Complexity in the Heart of Software|Evans|2003|book|crossref|p0|
c4-model                |06|The C4 model for visualising software architecture|Brown|None|spec|web||
prov-dm-2013            |07|PROV-DM: The PROV Data Model|W3C|2013|standard|web|p0|top15
slsa-v1                 |07|SLSA: Supply-chain Levels for Software Artifacts|SLSA|None|spec|web|p0|top15
in-toto-2019            |07|in-toto: Providing farm-to-table guarantees for bits and bytes|Torres-Arias|2019|paper|web|p0|top15
sigstore-2022           |07|Sigstore: Software Signing for Everybody|Newman|2022|paper|crossref|p0|
tuf-2010                |07|Survivable Key Compromise in Software Update Systems|Samuel|2010|paper|crossref|p0|
nist-ssdf-2022          |07|Secure Software Development Framework (SSDF) Version 1.1|NIST|2022|standard|doi|p0|
nist-zta-2020           |07|Zero Trust Architecture|NIST|2020|standard|doi|p0|
pcc-1997                |07|Proof-Carrying Code|Necula|1997|paper|crossref|p0|
dbc-1992                |07|Applying "Design by Contract"|Meyer|1992|paper|crossref|p0|
trusting-trust-1984     |07|Reflections on Trusting Trust|Thompson|1984|paper|crossref||
tla-1994                |08|The Temporal Logic of Actions|Lamport|1994|paper|crossref|p0|
model-checking-1981     |08|Design and Synthesis of Synchronization Skeletons Using Branching Time Temporal Logic|Clarke,Emerson|1981|paper|crossref|p0|
z3-2008                 |08|Z3: An Efficient SMT Solver|de Moura,Bjorner|2008|paper|crossref|p0|
lean4-2021              |08|The Lean 4 Theorem Prover and Programming Language|de Moura,Ullrich|2021|paper|crossref|p0|
isabelle-2002           |08|Isabelle/HOL: A Proof Assistant for Higher-Order Logic|Nipkow,Paulson,Wenzel|2002|book|crossref|p0|
quickcheck-2000         |08|QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs|Claessen,Hughes|2000|paper|crossref|p0|
metamorphic-2018        |08|Metamorphic Testing: A Review of Challenges and Opportunities|Chen|2018|paper|crossref|p0|
fairness-awareness-2012 |09|Fairness Through Awareness|Dwork|2012|paper|crossref|p0|
equality-opportunity-2016|09|Equality of Opportunity in Supervised Learning|Hardt,Price,Srebro|2016|paper|arxiv|p0|
gender-shades-2018      |09|Gender Shades: Intersectional Accuracy Disparities in Commercial Gender Classification|Buolamwini,Gebru|2018|paper|crossref|p0|
fairness-abstraction-2019|09|Fairness and Abstraction in Sociotechnical Systems|Selbst|2019|paper|crossref|p0|
membership-inference-2017|09|Membership Inference Attacks Against Machine Learning Models|Shokri|2017|paper|arxiv|p0|
dp-sgd-2016             |09|Deep Learning with Differential Privacy|Abadi|2016|paper|arxiv|p0|
calibrating-noise-2006  |09|Calibrating Noise to Sensitivity in Private Data Analysis|Dwork|2006|paper|crossref|p0|
runtime-verification-2009|10|A brief account of runtime verification|Leucker,Schallhart|2009|paper|crossref|p0|
gsn-standard            |10|Goal Structuring Notation Community Standard|SCSC|None|standard|web|p0|
assurance-cases-2010    |10|Safety and Assurance Cases: Past, Present and Possible Future|Bloomfield,Bishop|2010|paper|crossref|p0|
```

(93 entries; the test floor in Task 1 is 90 to leave room for honest merges. top15 count reaches 15 via conformal-risk, rag, react, toolformer, prompt-injection, injecagent, truthfulqa, helm, nist-ai-rmf, eu-ai-act, iso-42001, model-cards, datasheets, prov-dm, slsa, in-toto — SLSA+in-toto+PROV-DM were one top-15 slot in the source list, so ≥15 holds.)

## Self-review notes

- Spec coverage: canon (T1), coverage (T2), tiers 1–3 (T3+T6), fulltext/chunks (T4,T5,T7), Worker layer (T8), MCP (T9), push (T10), live+ingest (T11), claims/README/witness/release (T12). Bridge (spec §6): linked_claims travel with works in T10/T8 and surface in search hits — covered.
- Types consistent: chunk record `{sha, fsid, seq, section, text}` identical in T5 manifests, T8 ingest body, T10 batches.
- Worker has no unit-test harness (live_test.py only) — plan follows repo convention; typecheck + dry-run bundle gate T8/T9.
