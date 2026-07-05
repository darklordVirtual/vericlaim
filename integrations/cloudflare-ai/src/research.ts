// The research layer — vectorized literature with the same honesty rules.
//
// The git-anchored catalog (integrations/library/literature/) is the source
// of truth; this layer is DERIVED serving state: chunk vectors in a separate
// Vectorize index (`vericlaim-literature`), chunk texts content-addressed in
// the existing R2 vault, work/chunk metadata mirrored into D1.
//
// SCOPE: retrieval, never evidence. A work being searchable proves it was
// registrar-verified (or honestly snapshotted, tier "web-snapshot") and
// hash-locked — not that its contents are true. Tier travels with every hit,
// and the research oracle REFUSES when no chunk clears the relevance bar.
import { type Env, embed } from "./lib";
import { getEvidence, putEvidence } from "./vault";
import { searchLibrary } from "./library";

const RERANK_MODEL = "@cf/baai/bge-reranker-base";
const GEN_MODEL = "@cf/meta/llama-3.1-8b-instruct-fast";
// Retrieve wide (composite questions often find their answering excerpt
// outside the top few cosine hits — the reranker decides), use narrow.
// Note: returnMetadata caps Vectorize topK at 20.
const RETRIEVE_K = 16;
const USE_K = 4;
// Two-stage refusal bar. Cosine over a 5k-chunk corpus is a weak
// discriminator (off-corpus queries still hit ~0.66), so the reranker's
// relevance score decides; cosine is only the cheap floor. When the
// reranker is unavailable we fall back to a STRICT cosine bar — this
// oracle prefers a false refusal over a fluent overclaim.
const REFUSE_COSINE_FLOOR = 0.55;
// Measured margins (live, 2026-07-05): on-corpus answers rerank 0.4–0.99;
// vocabulary-shifted but answerable questions land ~0.15; every measured
// off-corpus query lands <= 0.03. 0.1 keeps 3x margin to the worst
// off-corpus observation while admitting honest vocabulary shifts.
const REFUSE_RERANK = 0.1;
const REFUSE_COSINE_FALLBACK = 0.78;
const EMBED_BATCH = 20;

export interface WorkIn {
  fsid: string;
  work_id: string;
  title: string;
  authors: string[];
  year?: number | null;
  venue?: string;
  kind: string;
  tier: string; // registrar | doi | web-snapshot | …
  accredited: boolean;
  url?: string;
  linked_claims?: string[];
}

export interface ChunkIn {
  sha: string; // sha256 of text, hex
  fsid: string;
  seq: number;
  section: string;
  text: string;
}

export interface ResearchHit {
  score: number;
  sha: string;
  fsid: string;
  work_id: string;
  title: string;
  section: string;
  snippet: string;
  accredited: boolean;
  tier: string;
  linked_claims: string[];
}

async function sha256hex(text: string): Promise<string> {
  const digest = await crypto.subtle.digest(
    "SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(digest)]
    .map((b) => b.toString(16).padStart(2, "0")).join("");
}

function chunkEmbedText(work: { title: string } | undefined, c: ChunkIn): string {
  // Title + section ground the chunk so "what does the SLSA spec say about
  // provenance" ranks the right work, not just any provenance sentence.
  const head = [work?.title ?? "", c.section].filter(Boolean).join(" — ");
  return head ? `${head}\n${c.text}` : c.text;
}

export async function ingestLiterature(
  env: Env, works: WorkIn[], chunks: ChunkIn[], ts: string,
): Promise<{
  works_upserted: number; indexed: number; skipped: number;
  rejected: { sha: string; reason: string }[];
}> {
  // Works first: chunks reference them.
  const workByFsid = new Map<string, WorkIn>();
  for (const w of works) {
    if (!w.fsid || !w.work_id || !w.title) continue;
    workByFsid.set(w.fsid, w);
    await env.DB.prepare(
      `INSERT INTO literature_works
         (fsid, work_id, title, authors, year, venue, kind, tier, accredited,
          url, linked_claims, updated_at)
       VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12)
       ON CONFLICT(fsid) DO UPDATE SET
         work_id=?2, title=?3, authors=?4, year=?5, venue=?6, kind=?7,
         tier=?8, accredited=?9, url=?10, linked_claims=?11, updated_at=?12`,
    ).bind(
      w.fsid, w.work_id, w.title, JSON.stringify(w.authors ?? []),
      w.year ?? null, w.venue ?? "", w.kind, w.tier, w.accredited ? 1 : 0,
      w.url ?? "", JSON.stringify(w.linked_claims ?? []), ts,
    ).run();
  }

  const rejected: { sha: string; reason: string }[] = [];
  let indexed = 0, skipped = 0;

  // Which shas exist already? (Dedupe server-side: re-pushing is a no-op.)
  const existing = new Set<string>();
  for (let i = 0; i < chunks.length; i += 50) {
    const slice = chunks.slice(i, i + 50);
    const marks = slice.map((_, j) => `?${j + 1}`).join(",");
    const rows = await env.DB.prepare(
      `SELECT sha FROM literature_chunks WHERE sha IN (${marks})`,
    ).bind(...slice.map((c) => c.sha)).all();
    for (const r of rows.results ?? []) existing.add(String((r as { sha: string }).sha));
  }

  const novel: ChunkIn[] = [];
  for (const c of chunks) {
    if (!/^[0-9a-f]{64}$/.test(c.sha ?? "")) {
      rejected.push({ sha: c.sha ?? "?", reason: "malformed sha256" });
      continue;
    }
    if (existing.has(c.sha)) { skipped++; continue; }
    const actual = await sha256hex(c.text ?? "");
    if (actual !== c.sha) {
      // fail-closed: a chunk whose bytes don't match its address never enters
      rejected.push({ sha: c.sha, reason: "text does not hash to sha" });
      continue;
    }
    novel.push(c);
  }

  for (let i = 0; i < novel.length; i += EMBED_BATCH) {
    const slice = novel.slice(i, i + EMBED_BATCH);
    const vectors = await embed(
      env, slice.map((c) => chunkEmbedText(workByFsid.get(c.fsid), c)));
    const rows = slice.map((c, j) => {
      const w = workByFsid.get(c.fsid);
      return {
        id: "lit:" + c.sha.slice(0, 48),
        values: vectors[j],
        metadata: {
          sha: c.sha, fsid: c.fsid, section: c.section ?? "",
          seq: c.seq, snippet: c.text.slice(0, 300),
          tier: w?.tier ?? "", accredited: String(w?.accredited ?? false),
        },
      };
    });
    await env.VECTORIZE_LIT.upsert(rows);
    await Promise.all(
      slice.map((c) => putEvidence(env, new TextEncoder().encode(c.text))));
    const stmt = env.DB.prepare(
      `INSERT OR IGNORE INTO literature_chunks (sha, fsid, seq, section, created_at)
       VALUES (?1,?2,?3,?4,?5)`);
    await env.DB.batch(
      slice.map((c) => stmt.bind(c.sha, c.fsid, c.seq, c.section ?? "", ts)));
    indexed += slice.length;
  }

  return { works_upserted: workByFsid.size, indexed, skipped, rejected };
}

async function workRows(env: Env, fsids: string[]): Promise<Map<string, Record<string, unknown>>> {
  const out = new Map<string, Record<string, unknown>>();
  if (!fsids.length) return out;
  const marks = fsids.map((_, j) => `?${j + 1}`).join(",");
  const rows = await env.DB.prepare(
    `SELECT * FROM literature_works WHERE fsid IN (${marks})`,
  ).bind(...fsids).all();
  for (const r of rows.results ?? []) out.set(String((r as { fsid: string }).fsid), r as Record<string, unknown>);
  return out;
}

function toHit(m: { score: number; metadata?: Record<string, unknown> },
               w: Record<string, unknown> | undefined): ResearchHit {
  return {
    score: m.score,
    sha: String(m.metadata?.sha ?? ""),
    fsid: String(m.metadata?.fsid ?? ""),
    work_id: String(w?.work_id ?? ""),
    title: String(w?.title ?? ""),
    section: String(m.metadata?.section ?? ""),
    snippet: String(m.metadata?.snippet ?? ""),
    accredited: String(m.metadata?.accredited ?? "") === "true",
    tier: String(m.metadata?.tier ?? ""),
    linked_claims: JSON.parse(String(w?.linked_claims ?? "[]")) as string[],
  };
}

export async function searchResearch(
  env: Env, query: string, topK = 5,
): Promise<ResearchHit[]> {
  const [vector] = await embed(env, [query]);
  const res = await env.VECTORIZE_LIT.query(vector, {
    topK: Math.min(20, topK), returnMetadata: "all",
  });
  const fsids = [...new Set(res.matches.map((m) => String(m.metadata?.fsid ?? "")))];
  const works = await workRows(env, fsids.filter(Boolean));
  return res.matches.map((m) => toHit(m, works.get(String(m.metadata?.fsid ?? ""))));
}

export interface ResearchAnswer {
  query: string;
  refused: boolean;
  answer: string;
  citations: { work_id: string; sha: string; section: string }[];
  // Verified claims from the claims LIBRARY that speak to the same question
  // — a separate truth tier, located with the same expanded phrasings. A
  // related claim is gate-verified evidence; the literature above is not.
  related_verified_claims?: {
    claim_id: string; evidence_level: string; statement: string;
    source_repo: string; score: number;
  }[];
  diagnostics?: {
    top_cosine: number; top_rerank: number | null;
    variants?: string[]; // how Workers AI located the literature
  };
}

const REFUSAL = "No cataloged literature supports an answer to this. The " +
  "research layer only answers from hash-locked, registrar-verified or " +
  "honestly-snapshotted works — it does not fill gaps from model memory.";

// Retrieval-side query expansion. The corpus is English research prose;
// questions arrive in any language and any vocabulary ("selective routing"
// vs the literature's "selective classification"), and an embedding of the
// user's phrasing can miss the very section that answers it. The expansion
// ONLY widens retrieval — the reranker still gates the refusal against a
// faithful rendering of the question, so this cannot manufacture relevance.
async function expandQuery(env: Env, query: string): Promise<string[]> {
  try {
    const gen = (await env.AI.run(GEN_MODEL, {
      messages: [{
        role: "system",
        content: "You rewrite research questions for literature retrieval " +
          "over an ENGLISH research corpus. Output ONLY a JSON array of " +
          "exactly 3 ENGLISH strings (translate if the question is not in " +
          "English): first a faithful English rendering of the question, " +
          "then 2 rephrasings that REPLACE non-standard or invented terms " +
          "with the research field's canonical vocabulary (e.g. 'selective " +
          "routing' -> 'selective classification' / 'abstention' / " +
          "'prediction sets'; 'AI gatekeeper' -> 'risk control' / " +
          "'selective prediction'). Every string must be in English. " +
          "No commentary, no markdown.",
      }, { role: "user", content: query }],
      max_tokens: 250, temperature: 0,
    })) as { response?: unknown };
    // Workers AI may hand back the model's JSON already parsed (an array)
    // or as text — accept both.
    let arr: unknown = null;
    if (Array.isArray(gen.response)) {
      arr = gen.response;
    } else if (typeof gen.response === "string") {
      const m = gen.response.match(/\[[\s\S]*\]/);
      if (m) arr = JSON.parse(m[0]);
    }
    if (!Array.isArray(arr)) return [];
    return arr.filter((s): s is string => typeof s === "string" && !!s.trim())
      .slice(0, 3);
  } catch {
    return []; // expansion is best-effort; the original query still runs
  }
}

export async function askResearch(env: Env, query: string): Promise<ResearchAnswer> {
  const variants = [query, ...(await expandQuery(env, query))];
  const vectors = await embed(env, variants);
  // Union retrieval across all phrasings; a chunk keeps its best score.
  const byId = new Map<string, { score: number; metadata?: Record<string, unknown> }>();
  for (const v of vectors) {
    const res = await env.VECTORIZE_LIT.query(v, {
      topK: RETRIEVE_K, returnMetadata: "all",
    });
    for (const m of res.matches) {
      const prev = byId.get(m.id);
      if (!prev || m.score > prev.score) {
        byId.set(m.id, { score: m.score, metadata: m.metadata as Record<string, unknown> });
      }
    }
  }
  const matches = [...byId.values()].sort((a, b) => b.score - a.score);
  const topCosine = matches[0]?.score ?? 0;
  // Union of 4 phrasings x 16 hits can hold ~64 candidates; the reranker is
  // cheap and is the real judge, so give it a wide window — a chunk that
  // answers is often outside the top few by raw cosine.
  const relevant = matches
    .filter((m) => m.score >= REFUSE_COSINE_FLOOR).slice(0, 32);
  // The refusal gate judges relevance against a faithful English rendering
  // of the question (variants[1]) — the corpus and reranker are English.
  const gateQuery = variants[1] ?? query;
  if (!relevant.length) {
    return {
      query, refused: true, answer: REFUSAL, citations: [],
      diagnostics: { top_cosine: topCosine, top_rerank: null, variants },
    };
  }

  // Full chunk texts from the vault for reranking + grounding.
  const fsids = [...new Set(relevant.map((m) => String(m.metadata?.fsid ?? "")))];
  const works = await workRows(env, fsids.filter(Boolean));
  const withText = [] as { hit: ResearchHit; text: string }[];
  for (const m of relevant) {
    const hit = toHit(m, works.get(String(m.metadata?.fsid ?? "")));
    const bytes = await getEvidence(env, hit.sha);
    withText.push({
      hit, text: bytes ? new TextDecoder().decode(bytes) : hit.snippet,
    });
  }

  let ordered = withText;
  let topRerank: number | null = null;
  let bestVariant = gateQuery;
  let bestVariantScore = -1;
  try {
    const run = env.AI.run.bind(env.AI) as (m: string, i: unknown) => Promise<unknown>;
    // Gate on the BEST rerank score across all phrasings: the user's words
    // and the canonical-vocabulary rewrites are the same question, and a
    // chunk that answers any faithful phrasing grounds the answer. Scores
    // are combined per chunk by element-wise max.
    const combined = new Array<number>(withText.length).fill(-1);
    for (const gq of variants.slice(0, 4)) {
      const out = (await run(RERANK_MODEL, {
        query: gq,
        contexts: withText.map((c) => ({ text: c.text.slice(0, 1800) })),
      })) as { response?: { id: number; score: number }[] };
      for (const r of out.response ?? []) {
        if (r.id >= 0 && r.id < combined.length) {
          if (r.score > combined[r.id]) combined[r.id] = r.score;
          if (r.score > bestVariantScore) {
            bestVariantScore = r.score;
            bestVariant = gq;
          }
        }
      }
    }
    if (combined.some((s) => s >= 0)) {
      const order = combined.map((s, i) => ({ s, i }))
        .sort((a, b) => b.s - a.s);
      ordered = order.map((o) => withText[o.i]);
      topRerank = order[0].s;
    }
  } catch { /* rerank unavailable; the strict cosine fallback decides below */ }

  // The refusal decision: reranker when we have it, strict cosine otherwise.
  const refuse = topRerank !== null
    ? topRerank < REFUSE_RERANK
    : topCosine < REFUSE_COSINE_FALLBACK;
  if (refuse) {
    return {
      query, refused: true, answer: REFUSAL, citations: [],
      diagnostics: { top_cosine: topCosine, top_rerank: topRerank, variants },
    };
  }
  ordered = ordered.slice(0, USE_K);

  const context = ordered.map((c, i) =>
    `[${i + 1}] ${c.hit.work_id} (${c.hit.tier}${c.hit.accredited ? ", peer-reviewed venue" : ""})` +
    `${c.hit.section ? ` — section: ${c.hit.section}` : ""}\n${c.text.trim()}`).join("\n\n");

  const system =
    "You answer strictly and ONLY from the literature EXCERPTS provided. " +
    "Rules: (1) Use only what the excerpts state; never add facts, numbers or " +
    "results from memory. (2) Cite the work id in square brackets, e.g. " +
    "[arxiv:2208.02814], after each fact. (3) Excerpts marked web-snapshot are " +
    "NOT peer-reviewed — say so if you rely on them. (4) If the excerpts do " +
    "not answer the question, say so plainly. Be concise (2-5 sentences).";
  const phrasingNote = bestVariant !== query
    ? `\n(The literature's vocabulary for this question: "${bestVariant}" — ` +
      "treat it as the same question, and name the literature's term when " +
      "the user's term differs.)"
    : "";
  const user = `EXCERPTS:\n${context}\n\nQUESTION: ${query}${phrasingNote}\n\nGrounded answer:`;

  let answer: string;
  try {
    const gen = (await env.AI.run(GEN_MODEL, {
      messages: [{ role: "system", content: system }, { role: "user", content: user }],
      max_tokens: 500, temperature: 0.1,
    })) as { response?: string };
    answer = (gen.response ?? "").trim() ||
      "The retrieved excerpts did not yield a grounded answer.";
  } catch {
    answer = "Answer generation unavailable; the relevant excerpts are cited below.";
  }

  // Locate verified claims for the same question (best-effort; the claims
  // library is a different truth tier and its absence never blocks the
  // literature answer).
  let related: ResearchAnswer["related_verified_claims"];
  try {
    const hits = await searchLibrary(env, bestVariant, 3);
    related = hits
      .filter((h) => h.status === "verified" && h.score >= 0.55)
      .map((h) => ({
        claim_id: h.claim_id, evidence_level: h.evidence_level,
        statement: h.statement, source_repo: h.source_repo, score: h.score,
      }));
  } catch { /* library lookup is additive only */ }

  return {
    query, refused: false, answer,
    citations: ordered.map((c) => ({
      work_id: c.hit.work_id, sha: c.hit.sha, section: c.hit.section,
    })),
    related_verified_claims: related,
    diagnostics: { top_cosine: topCosine, top_rerank: topRerank, variants },
  };
}

export async function getWork(env: Env, fsid: string): Promise<Record<string, unknown> | null> {
  const w = await env.DB.prepare(
    "SELECT * FROM literature_works WHERE fsid = ?1").bind(fsid).first();
  if (!w) return null;
  const chunks = await env.DB.prepare(
    "SELECT sha, seq, section FROM literature_chunks WHERE fsid = ?1 ORDER BY seq",
  ).bind(fsid).all();
  return { ...(w as Record<string, unknown>), chunks: chunks.results ?? [] };
}

export async function researchSummary(env: Env): Promise<Record<string, unknown>> {
  const works = await env.DB.prepare(
    "SELECT COUNT(*) AS c FROM literature_works").first();
  const chunks = await env.DB.prepare(
    "SELECT COUNT(*) AS c FROM literature_chunks").first();
  const byTier = await env.DB.prepare(
    "SELECT tier, COUNT(*) AS c FROM literature_works GROUP BY tier ORDER BY tier",
  ).all();
  return {
    works: Number((works as { c: number } | null)?.c ?? 0),
    chunks: Number((chunks as { c: number } | null)?.c ?? 0),
    by_tier: Object.fromEntries((byTier.results ?? []).map(
      (r) => [String((r as { tier: string }).tier), Number((r as { c: number }).c)])),
    note: "Retrieval, never evidence: a hit proves the text was hash-locked " +
          "and its metadata registrar-verified (or honestly web-snapshotted).",
  };
}
