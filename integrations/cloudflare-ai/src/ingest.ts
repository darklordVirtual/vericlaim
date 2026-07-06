// SPDX-License-Identifier: Apache-2.0
// The /index ingest body, extracted so it can run either directly (default) or
// serialized behind a single-writer Durable Object (opt-in, SINGLE_WRITER=true).
//
// ⚠️ DEPLOY-ONLY / NOT DEPLOY-TESTED: the IndexWriter Durable Object path below
// is written and type-checked but has NOT been exercised against real
// D1/R2/Vectorize bindings in this change (no Cloudflare env available). It is
// off by default; the tested, unchanged behavior is the direct path. Enable and
// verify it in a staging Worker before trusting it. See ROADMAP.md.
import { type Claim, type Env, b64ToBytes, indexClaims, reconcileClaims } from "./lib.ts";
import { appendClaim } from "./ledger.ts";
import { putEvidence } from "./vault.ts";
import type { IngestCounts } from "./snapshot.ts";

// A caller-facing (400) failure — bad base64 in a claim's artifact.
export class IngestError extends Error {}

// The actual write path: vault artifacts, append the ledger, (re)index the search
// surface, and — for a full snapshot — reconcile away withdrawn claims. This is
// the ONLY place these side effects live, so serializing it (below) serializes
// the whole write.
export async function ingestSnapshot(
  env: Env, claims: Claim[], reconcile: boolean, ts: string,
): Promise<IngestCounts> {
  let appended = 0, unchanged = 0, vaulted = 0;
  for (const c of claims) {
    let artifact_sha256: string | null = null;
    if (c.artifact_b64) {
      let bytes: Uint8Array;
      try { bytes = b64ToBytes(c.artifact_b64); }
      catch { throw new IngestError(`claim ${c.id}: artifact_b64 is not valid base64`); }
      artifact_sha256 = await putEvidence(env, bytes);
      vaulted++;
    }
    const r = await appendClaim(env, c, { git_commit: c.git_commit, artifact_sha256, ts });
    r === "appended" ? appended++ : unchanged++;
  }
  const indexed = await indexClaims(env, claims);
  const withdrawn = reconcile
    ? await reconcileClaims(env, new Set(claims.map((c) => c.id)))
    : [];
  return { indexed, ledger_appended: appended, ledger_unchanged: unchanged,
    vaulted, withdrawn: withdrawn.length };
}

// Single-writer serializer. All /index writes are routed to ONE named instance
// of this Durable Object; a DO instance processes requests serially, and
// blockConcurrencyWhile makes the critical section explicit — so two concurrent
// pushes can never interleave their ledger appends / reconciles (the "read tip →
// insert is not atomic" gap the ledger documents). No stored state is needed; the
// object exists only to serialize.
export class IndexWriter {
  constructor(private state: DurableObjectState, private env: Env) {}

  async fetch(req: Request): Promise<Response> {
    let body: { claims?: Claim[]; reconcile?: boolean; ts?: string };
    try { body = await req.json(); }
    catch { return jsonResp({ ok: false, error: "invalid JSON" }, 400); }
    const claims = body.claims ?? [];
    const ts = body.ts ?? new Date().toISOString();
    try {
      const counts = await this.state.blockConcurrencyWhile(
        () => ingestSnapshot(this.env, claims, body.reconcile !== false, ts));
      return jsonResp({ ok: true, counts });
    } catch (e) {
      if (e instanceof IngestError) return jsonResp({ ok: false, error: e.message }, 400);
      throw e;
    }
  }
}

function jsonResp(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status, headers: { "content-type": "application/json" },
  });
}
