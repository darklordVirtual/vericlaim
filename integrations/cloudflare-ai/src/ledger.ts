// The claim ledger: an append-only, hash-chained history in D1.
//
// append() records a new event for a claim only when its content changed since
// the last event for that claim id, so the ledger is a true timeline. Every row
// chains the previous row's entry_hash, so a PARTIAL edit is detectable by
// re-walking (verifyChain). See hashchain.ts for the honest limit (a full
// rewrite by a D1 writer is not detectable by verifyChain alone).
//
// SINGLE-WRITER MODEL: appendClaim does read-tip-then-insert, which is NOT
// atomic. The deployment assumes ONE trusted writer — the CI pusher holding
// INDEX_TOKEN — calling /index serially. Two concurrent /index calls could read
// the same tip and insert rows with the same prev_hash, which verifyChain would
// then report as a break (a self-inflicted false alarm, not a security hole).
// Do not fan /index out across concurrent callers; a true multi-writer setup
// needs a single-writer serializer (e.g. a Durable Object) in front of D1.
import { type Claim, type Env } from "./lib";
import { contentHash, entryHash } from "./hashchain";

export interface LedgerEvent {
  seq: number; ts: string; claim_id: string; statement: string;
  evidence_level: string; metrics: string; caveat: string; artifact: string;
  artifact_sha256: string | null; git_commit: string | null;
  content_hash: string; prev_hash: string; entry_hash: string;
}

async function lastRow(env: Env): Promise<LedgerEvent | null> {
  const r = await env.DB.prepare(
    "SELECT * FROM claim_events ORDER BY seq DESC LIMIT 1").first();
  return (r as unknown as LedgerEvent) ?? null;
}

async function lastForClaim(env: Env, id: string): Promise<LedgerEvent | null> {
  const r = await env.DB.prepare(
    "SELECT * FROM claim_events WHERE claim_id = ? ORDER BY seq DESC LIMIT 1")
    .bind(id).first();
  return (r as unknown as LedgerEvent) ?? null;
}

// Append one claim if it is new or changed. Returns "appended" | "unchanged".
export async function appendClaim(
  env: Env, claim: Claim, opts: { git_commit?: string; artifact_sha256?: string | null; ts: string },
): Promise<"appended" | "unchanged"> {
  const ch = await contentHash({
    claim_id: claim.id, statement: claim.statement,
    evidence_level: claim.evidence_level, metrics: claim.metrics,
    caveat: claim.caveat, artifact: claim.artifact,
    artifact_sha256: opts.artifact_sha256 ?? null,
  });
  const prevForClaim = await lastForClaim(env, claim.id);
  if (prevForClaim && prevForClaim.content_hash === ch) return "unchanged";

  const tip = await lastRow(env);
  const prev_hash = tip ? tip.entry_hash : "";
  const row = {
    ts: opts.ts,
    claim_id: claim.id,
    statement: claim.statement ?? "",
    evidence_level: claim.evidence_level ?? "",
    metrics: JSON.stringify(claim.metrics ?? null),
    caveat: claim.caveat ?? "",
    artifact: JSON.stringify(Array.isArray(claim.artifact) ? claim.artifact
      : claim.artifact ? [claim.artifact] : []),
    artifact_sha256: opts.artifact_sha256 ?? null,
    git_commit: opts.git_commit ?? null,
    content_hash: ch,
  };
  const eh = await entryHash(prev_hash, row);
  await env.DB.prepare(
    `INSERT INTO claim_events
     (ts, claim_id, statement, evidence_level, metrics, caveat, artifact,
      artifact_sha256, git_commit, content_hash, prev_hash, entry_hash)
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`)
    .bind(row.ts, row.claim_id, row.statement, row.evidence_level, row.metrics,
      row.caveat, row.artifact, row.artifact_sha256, row.git_commit,
      row.content_hash, prev_hash, eh).run();
  return "appended";
}

export async function history(env: Env, claimId: string): Promise<LedgerEvent[]> {
  const r = await env.DB.prepare(
    "SELECT * FROM claim_events WHERE claim_id = ? ORDER BY seq ASC").bind(claimId).all();
  return (r.results as unknown as LedgerEvent[]) ?? [];
}

// Re-walk the whole chain and confirm every entry_hash still matches. Returns
// the first sequence number where the chain breaks, if any.
export async function verifyChain(env: Env): Promise<
  { ok: boolean; entries: number; brokenAt: number | null }
> {
  const r = await env.DB.prepare("SELECT * FROM claim_events ORDER BY seq ASC").all();
  const rows = (r.results as unknown as LedgerEvent[]) ?? [];
  let prev = "";
  for (const row of rows) {
    if (row.prev_hash !== prev) return { ok: false, entries: rows.length, brokenAt: row.seq };
    const recomputed = await entryHash(prev, {
      ts: row.ts, claim_id: row.claim_id, statement: row.statement,
      evidence_level: row.evidence_level, metrics: row.metrics, caveat: row.caveat,
      artifact: row.artifact, artifact_sha256: row.artifact_sha256,
      git_commit: row.git_commit, content_hash: row.content_hash,
    });
    if (recomputed !== row.entry_hash) return { ok: false, entries: rows.length, brokenAt: row.seq };
    prev = row.entry_hash;
  }
  return { ok: true, entries: rows.length, brokenAt: null };
}

// verifyChain is O(n) crypto over the whole ledger. The health page, passport,
// and badge render it on every hit — so cache the last-verified result keyed by
// the tip (count + head hash), which is a single cheap row. When nothing has
// been appended, the cached verdict is returned without re-walking. Correctness
// is preserved: any append changes the tip and invalidates the cache. The cache
// lives per Worker isolate (module scope), so a cold isolate simply recomputes.
let _chainCache: { entries: number; head: string;
  result: { ok: boolean; entries: number; brokenAt: number | null } } | null = null;

export async function verifyChainCached(env: Env): Promise<
  { ok: boolean; entries: number; brokenAt: number | null }
> {
  const tip = await env.DB.prepare(
    "SELECT seq, entry_hash FROM claim_events ORDER BY seq DESC LIMIT 1").first() as
    { entry_hash: string } | null;
  const countRow = await env.DB.prepare(
    "SELECT COUNT(*) AS c FROM claim_events").first() as { c: number } | null;
  const entries = Number(countRow?.c ?? 0);
  const head = tip?.entry_hash ?? "";
  if (_chainCache && _chainCache.entries === entries && _chainCache.head === head) {
    return _chainCache.result;
  }
  const result = await verifyChain(env);
  _chainCache = { entries, head, result };
  return result;
}

export async function summary(env: Env): Promise<{
  claims: number; events: number; by_level: Record<string, number>;
  latest: { claim_id: string; evidence_level: string; ts: string; artifact_sha256: string | null }[];
}> {
  // latest event per claim
  const r = await env.DB.prepare(
    `SELECT e.* FROM claim_events e
     JOIN (SELECT claim_id, MAX(seq) AS mseq FROM claim_events GROUP BY claim_id) m
       ON e.claim_id = m.claim_id AND e.seq = m.mseq
     ORDER BY e.claim_id ASC`).all();
  const latest = (r.results as unknown as LedgerEvent[]) ?? [];
  const by_level: Record<string, number> = {};
  for (const e of latest) by_level[e.evidence_level] = (by_level[e.evidence_level] ?? 0) + 1;
  const ev = await env.DB.prepare("SELECT COUNT(*) AS c FROM claim_events").first();
  return {
    claims: latest.length,
    events: Number((ev as { c: number })?.c ?? 0),
    by_level,
    latest: latest.map((e) => ({
      claim_id: e.claim_id, evidence_level: e.evidence_level, ts: e.ts,
      artifact_sha256: e.artifact_sha256,
    })),
  };
}
