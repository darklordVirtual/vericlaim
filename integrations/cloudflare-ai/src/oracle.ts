// The claim oracle: answer questions ONLY from registered claims — and refuse
// when none support an answer.
//
// This is the anti-overclaim discipline applied to generative AI itself. The
// pipeline: embed the question -> Vectorize retrieve -> rerank -> if nothing is
// relevant enough, REFUSE -> otherwise a grounded answer that cites claim ids,
// carries the caveats, and never invents a number. A vericlaim oracle that
// hallucinated a claim would defeat the entire purpose, so refusal is a feature.
import { type Env, type SearchHit, embed } from "./lib";

const RERANK_MODEL = "@cf/baai/bge-reranker-base";
const GEN_MODEL = "@cf/meta/llama-3.1-8b-instruct-fast";
const RETRIEVE_K = 8;
const USE_K = 4;
const REFUSE_COSINE = 0.42; // below this, no claim is relevant enough to ground an answer

export interface OracleAnswer {
  query: string;
  refused: boolean;
  answer: string;
  citations: string[];
  claims: SearchHit[];
}

async function retrieve(env: Env, query: string): Promise<SearchHit[]> {
  const [vector] = await embed(env, [query]);
  const res = await env.VECTORIZE.query(vector, { topK: RETRIEVE_K, returnMetadata: "all" });
  return res.matches.map((m) => ({
    id: m.id, score: m.score,
    statement: String(m.metadata?.statement ?? ""),
    evidence_level: String(m.metadata?.evidence_level ?? ""),
    caveat: String(m.metadata?.caveat ?? ""),
    artifact: String(m.metadata?.artifact ?? ""),
  }));
}

async function rerank(env: Env, query: string, hits: SearchHit[]): Promise<SearchHit[]> {
  if (hits.length <= 1) return hits;
  try {
    // The reranker needs { query, contexts }. This version of @cloudflare/
    // workers-types omits the `query` field from the input interface (a types
    // bug), so we bypass the overload check; the field is required at runtime.
    const run = env.AI.run.bind(env.AI) as (m: string, i: unknown) => Promise<unknown>;
    const out = (await run(RERANK_MODEL, {
      query, contexts: hits.map((h) => ({ text: h.statement })),
    })) as { response?: { id: number; score: number }[] };
    const ranked = out.response;
    if (Array.isArray(ranked) && ranked.length) {
      return ranked.map((r) => hits[r.id]).filter(Boolean);
    }
  } catch {
    // rerank is a best-effort refinement; fall back to cosine order
  }
  return hits;
}

const REFUSAL = "No registered claim supports an answer to this. " +
  "Register and back a claim first — the oracle only answers from verified claims.";

export async function ask(env: Env, query: string): Promise<OracleAnswer> {
  const retrieved = await retrieve(env, query);
  const relevant = retrieved.filter((h) => h.score >= REFUSE_COSINE);

  if (relevant.length === 0) {
    return { query, refused: true, answer: REFUSAL, citations: [], claims: [] };
  }

  const ordered = (await rerank(env, query, relevant)).slice(0, USE_K);
  const context = ordered.map((h, i) =>
    `[${i + 1}] ${h.id} (evidence: ${h.evidence_level})\n` +
    `    statement: ${h.statement.trim()}\n` +
    `    caveat: ${h.caveat.trim()}`).join("\n\n");

  const system =
    "You answer questions strictly and ONLY from the vericlaim CLAIMS provided. " +
    "Rules: (1) Use only facts stated in the claims; never invent or estimate a " +
    "number. (2) Cite the claim id in square brackets, e.g. [CLAIM-EX-001], after " +
    "each fact. (3) Always carry the claim's caveat when you state its result. " +
    "(4) If the claims do not actually answer the question, say so plainly and do " +
    "not guess. Be concise (2-4 sentences).";
  const user = `CLAIMS:\n${context}\n\nQUESTION: ${query}\n\nGrounded answer:`;

  let answer: string;
  try {
    const gen = (await env.AI.run(GEN_MODEL, {
      messages: [{ role: "system", content: system }, { role: "user", content: user }],
      max_tokens: 400, temperature: 0.1,
    })) as { response?: string };
    answer = (gen.response ?? "").trim() ||
      "The retrieved claims did not yield a grounded answer.";
  } catch {
    // If generation fails, degrade honestly to the retrieved claims themselves.
    answer = "Answer generation unavailable; the relevant registered claims are cited below.";
  }

  // Truthful citations: the claim ids the answer ACTUALLY cites, not merely the
  // ones retrieved. An anti-overclaim tool must not over-attribute either.
  const cited = ordered.filter((h) => answer.includes(h.id));
  return {
    query,
    refused: cited.length === 0, // grounded answer that cites nothing = a refusal
    answer,
    citations: cited.map((h) => h.id),
    claims: cited.length ? cited : ordered,
  };
}
