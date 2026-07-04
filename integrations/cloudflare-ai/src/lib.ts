// Shared helpers for the vericlaim Cloudflare AI add-on.
//
// A "claim" here is exactly the record vericlaim registers: id, statement,
// evidence_level, artifact(s), caveat and optional metrics. We embed the
// statement (plus a little context) so the register becomes semantically
// searchable — a discovery aid over what a project has proven about itself.
//
// SCOPE: this add-on indexes and searches claims. It does NOT change what the
// vericlaim gate proves. A claim is trustworthy because the gate verified its
// artifact, provenance and doc-binding — not because it turned up in a search.

export const EMBED_MODEL = "@cf/baai/bge-base-en-v1.5"; // 768 dims, cosine

export interface Env {
  AI: Ai;
  VECTORIZE: VectorizeIndex;
  INDEX_TOKEN?: string; // bearer token required to (re)build the index
  ENABLE_MCP?: string; // "true" to expose the /mcp endpoint
  VERICLAIM_MCP: DurableObjectNamespace; // backing store for the MCP agent
}

export interface Claim {
  id: string;
  statement: string;
  evidence_level: string;
  artifact?: string[] | string;
  caveat?: string;
  metrics?: Record<string, unknown>;
}

export interface SearchHit {
  id: string;
  score: number;
  statement: string;
  evidence_level: string;
  caveat: string;
  artifact: string;
}

// Text we embed for a claim: the statement is the signal; evidence level and
// caveat add a little grounding so "reproduced benchmark" queries rank well.
function claimText(c: Claim): string {
  const arts = Array.isArray(c.artifact) ? c.artifact.join(", ") : c.artifact ?? "";
  return [
    c.statement,
    `evidence level: ${c.evidence_level}`,
    c.caveat ? `caveat: ${c.caveat}` : "",
    arts ? `artifact: ${arts}` : "",
  ].filter(Boolean).join("\n");
}

export async function embed(env: Env, texts: string[]): Promise<number[][]> {
  const res = (await env.AI.run(EMBED_MODEL, { text: texts })) as { data: number[][] };
  return res.data;
}

// (Re)build the vector index from a full set of claims. Idempotent: uses the
// claim id as the vector id, so re-indexing upserts in place.
export async function indexClaims(env: Env, claims: Claim[]): Promise<number> {
  if (claims.length === 0) return 0;
  const BATCH = 100; // Workers AI + Vectorize both accept batches
  let count = 0;
  for (let i = 0; i < claims.length; i += BATCH) {
    const slice = claims.slice(i, i + BATCH);
    const vectors = await embed(env, slice.map(claimText));
    const rows = slice.map((c, j) => ({
      id: c.id,
      values: vectors[j],
      metadata: {
        statement: c.statement,
        evidence_level: c.evidence_level,
        caveat: c.caveat ?? "",
        artifact: Array.isArray(c.artifact) ? c.artifact.join(", ") : c.artifact ?? "",
      },
    }));
    await env.VECTORIZE.upsert(rows);
    count += rows.length;
  }
  return count;
}

export async function searchClaims(
  env: Env, query: string, topK = 5,
): Promise<SearchHit[]> {
  const [vector] = await embed(env, [query]);
  const res = await env.VECTORIZE.query(vector, { topK, returnMetadata: "all" });
  return res.matches.map((m) => ({
    id: m.id,
    score: m.score,
    statement: String(m.metadata?.statement ?? ""),
    evidence_level: String(m.metadata?.evidence_level ?? ""),
    caveat: String(m.metadata?.caveat ?? ""),
    artifact: String(m.metadata?.artifact ?? ""),
  }));
}
