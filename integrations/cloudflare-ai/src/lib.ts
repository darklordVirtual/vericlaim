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
// Shared Workers-AI model ids (used by both the claims and research oracles).
export const RERANK_MODEL = "@cf/baai/bge-reranker-base";
export const GEN_MODEL = "@cf/meta/llama-3.1-8b-instruct-fast";

// Decode base64 to bytes. Throws on malformed input (atob) — callers on request
// paths must guard it so a bad payload becomes a 400, not an unhandled 500.
export function b64ToBytes(b64: string): Uint8Array {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

// Constant-time string comparison for bearer tokens: compare every character so
// the time taken does not leak how many leading characters matched. Both the
// length and the content are folded into one accumulator.
export function timingSafeEqual(a: string, b: string): boolean {
  let diff = a.length ^ b.length;
  for (let i = 0; i < a.length; i++) {
    diff |= a.charCodeAt(i) ^ b.charCodeAt(i % b.length);
  }
  return diff === 0;
}

export interface Env {
  AI: Ai;
  VECTORIZE: VectorizeIndex;
  VECTORIZE_LIT: VectorizeIndex; // chunk-level literature index (research layer)
  DB: D1Database; // the tamper-evident claim ledger
  EVIDENCE: R2Bucket; // the content-addressed evidence vault
  INDEX_TOKEN?: string; // bearer token required to (re)build the index
  ENABLE_MCP?: string; // "true" to expose the /mcp endpoint
  // Optional: when set, the generative endpoints (/ask, /research/ask) require
  // this bearer token — a guard against anonymous, unbounded Workers-AI cost.
  // Unset = reads stay public (the passport/search/badge remain open).
  READ_TOKEN?: string;
  // Optional: an HMAC key (a secret NOT stored in D1) used to sign the ledger
  // head at /ledger/head. A witness holding this key can then confirm a head
  // was endorsed by the operator, not merely recomputed by anyone with D1
  // write access — the gap plain hash-chaining leaves open.
  LEDGER_HMAC_KEY?: string;
  VERICLAIM_MCP: DurableObjectNamespace; // backing store for the MCP agent
  // Optional single-writer serializer for POST /index. When SINGLE_WRITER==="true"
  // AND this binding exists, /index is routed through one IndexWriter instance so
  // concurrent pushes cannot interleave. Off by default (direct path). DEPLOY-ONLY:
  // add the binding + migration in wrangler.toml and verify in staging first.
  INDEX_WRITER?: DurableObjectNamespace;
  SINGLE_WRITER?: string; // "true" to route /index through INDEX_WRITER
}

export interface Claim {
  id: string;
  statement: string;
  evidence_level: string;
  artifact?: string[] | string;
  caveat?: string;
  metrics?: Record<string, unknown>;
  git_commit?: string; // best-effort, from the exporter
  artifact_b64?: string; // base64 of the primary artifact's bytes (optional)
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
        // Positive marker so search can exclude library bundles (`lib:*`),
        // which share this index and now outnumber project claims — a metadata
        // index on `kind` makes the exclusion exact at any library size.
        kind: "claim",
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

// Reconcile the search surface to the pushed snapshot. `export_claims` sends the
// FULL current register, so any claim id in the ledger that is absent from the
// push has been withdrawn or deleted: remove its vector so /search and /ask can
// never surface a claim the project no longer stands behind. History is kept —
// claim_events is append-only and untouched; only the live index is pruned.
// This is what lets the Worker be described as a CURRENT truth layer.
export async function reconcileClaims(
  env: Env, receivedIds: Set<string>,
): Promise<string[]> {
  const rows = await env.DB.prepare(
    "SELECT DISTINCT claim_id FROM claim_events").all();
  const known = (rows.results ?? [])
    .map((r) => String((r as { claim_id: string }).claim_id));
  const withdrawn = known.filter((id) => !receivedIds.has(id));
  for (let i = 0; i < withdrawn.length; i += 100) {
    // deleteByIds is idempotent — re-deleting an already-gone id is a no-op.
    await env.VECTORIZE.deleteByIds(withdrawn.slice(i, i + 100));
  }
  return withdrawn;
}

export async function searchClaims(
  env: Env, query: string, topK = 5,
): Promise<SearchHit[]> {
  const [vector] = await embed(env, [query]);
  // Library bundles (`lib:*`) share this index and now outnumber project
  // claims heavily, so a plain nearest-neighbour query can come back
  // all-library. Filter to kind="claim" at query time (exact, via a metadata
  // index) — this scales no matter how large the library grows.
  const hit = (m: { id: string; score: number; metadata?: Record<string, unknown> }): SearchHit => {
    const md = m.metadata ?? {};
    return {
      id: m.id, score: m.score,
      statement: String(md.statement ?? ""),
      evidence_level: String(md.evidence_level ?? ""),
      caveat: String(md.caveat ?? ""),
      artifact: String(md.artifact ?? ""),
    };
  };
  const res = await env.VECTORIZE.query(vector, {
    topK: 20, returnMetadata: "all", filter: { kind: "claim" },
  });
  if (res.matches?.length) return res.matches.slice(0, topK).map(hit);

  // Fallback for claim vectors written before the metadata index existed:
  // wide id-only query, drop `lib:*` by prefix, fetch metadata for survivors.
  const wide = await env.VECTORIZE.query(vector, { topK: 100 });
  const kept = wide.matches.filter((m) => !m.id.startsWith("lib:")).slice(0, topK);
  if (!kept.length) return [];
  const byId = new Map(
    (await env.VECTORIZE.getByIds(kept.map((m) => m.id)))
      .map((v) => [v.id, v.metadata ?? {}] as const));
  return kept.map((m) => hit({ id: m.id, score: m.score, metadata: byId.get(m.id) }));
}
