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

const RERANK_MODEL = "@cf/baai/bge-reranker-base";
const GEN_MODEL = "@cf/meta/llama-3.1-8b-instruct-fast";
const RETRIEVE_K = 8;
const USE_K = 4;
const REFUSE_COSINE = 0.42;
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
    for (const c of slice) {
      await putEvidence(env, new TextEncoder().encode(c.text));
      await env.DB.prepare(
        `INSERT OR IGNORE INTO literature_chunks (sha, fsid, seq, section, created_at)
         VALUES (?1,?2,?3,?4,?5)`,
      ).bind(c.sha, c.fsid, c.seq, c.section ?? "", ts).run();
      indexed++;
    }
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
}

const REFUSAL = "No cataloged literature supports an answer to this. The " +
  "research layer only answers from hash-locked, registrar-verified or " +
  "honestly-snapshotted works — it does not fill gaps from model memory.";

export async function askResearch(env: Env, query: string): Promise<ResearchAnswer> {
  const [vector] = await embed(env, [query]);
  const res = await env.VECTORIZE_LIT.query(vector, {
    topK: RETRIEVE_K, returnMetadata: "all",
  });
  const relevant = res.matches.filter((m) => m.score >= REFUSE_COSINE);
  if (!relevant.length) {
    return { query, refused: true, answer: REFUSAL, citations: [] };
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
  try {
    const run = env.AI.run.bind(env.AI) as (m: string, i: unknown) => Promise<unknown>;
    const out = (await run(RERANK_MODEL, {
      query, contexts: withText.map((c) => ({ text: c.text.slice(0, 1800) })),
    })) as { response?: { id: number; score: number }[] };
    if (Array.isArray(out.response) && out.response.length) {
      ordered = out.response.map((r) => withText[r.id]).filter(Boolean);
    }
  } catch { /* rerank is best-effort; cosine order stands */ }
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
  const user = `EXCERPTS:\n${context}\n\nQUESTION: ${query}\n\nGrounded answer:`;

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

  return {
    query, refused: false, answer,
    citations: ordered.map((c) => ({
      work_id: c.hit.work_id, sha: c.hit.sha, section: c.hit.section,
    })),
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
