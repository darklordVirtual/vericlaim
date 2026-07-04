// The claims LIBRARY: cross-project preservation and reuse of claim bundles.
//
// A bundle is the unit built by integrations/library/bundlefmt.py: claim +
// provenance + evidence/code/literature files, content-addressed by
// bundle_id = sha256(canonical MANIFEST). The Worker preserves bundles as:
//
//   - R2: every file at sha256/<hash> (the existing content-addressed vault)
//   - D1: library_bundles — an append-only, hash-chained registry of bundles
//   - Vectorize: one vector per bundle (metadata library="true") for search
//
// FAIL CLOSED ON INGEST: the server recomputes the bundle_id from the manifest
// and re-hashes every uploaded file against it; a mismatched byte rejects the
// bundle. Verified and candidate bundles are both preserved, but candidates
// are always labeled — search output must never let an unverified assertion
// masquerade as a gate-verified claim.
import { type Env, embed } from "./lib";
import { canonical, entryHash, sha256Hex } from "./hashchain";
import { putEvidence, verifyEvidence } from "./vault";

export interface BundleManifest {
  schema: string;
  status: string;
  files: Record<string, string>; // bundle-relative path -> sha256
}

export interface BundleIn {
  bundle_id: string;
  status: string;
  claim: Record<string, unknown>;
  manifest: BundleManifest;
  provenance: Record<string, unknown>;
  files?: Record<string, string>; // path -> base64 bytes
}

export interface BundleRow {
  seq: number; ts: string; bundle_id: string; status: string;
  source_repo: string; source_claim_id: string;
  claim: string; manifest: string; provenance: string;
  prev_hash: string; entry_hash: string;
}

function b64ToBytes(b64: string): Uint8Array {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

// Must mirror bundlefmt._bundle_id: sha256 of the canonical manifest object.
export async function computeBundleId(man: BundleManifest): Promise<string> {
  return sha256Hex(canonical({ schema: man.schema, status: man.status, files: man.files }));
}

async function lastRow(env: Env): Promise<BundleRow | null> {
  const r = await env.DB.prepare(
    "SELECT * FROM library_bundles ORDER BY seq DESC LIMIT 1").first();
  return (r as unknown as BundleRow) ?? null;
}

export async function getBundleRow(env: Env, bundleId: string): Promise<BundleRow | null> {
  const r = await env.DB.prepare(
    "SELECT * FROM library_bundles WHERE bundle_id = ? ORDER BY seq DESC LIMIT 1")
    .bind(bundleId).first();
  return (r as unknown as BundleRow) ?? null;
}

// --- DERIVED versioning: a bundle's identity is (source_repo,
// source_claim_id); a later row for the same identity supersedes earlier
// ones. Nothing is declared and no schema changes — the append-only
// registry IS the version chain, so hash chains and witnesses stay valid.

export async function latestBundleIds(env: Env): Promise<Set<string>> {
  const r = await env.DB.prepare(
    `SELECT lb.bundle_id FROM library_bundles lb
     JOIN (SELECT source_repo, source_claim_id, MAX(seq) AS mseq
             FROM library_bundles GROUP BY source_repo, source_claim_id) m
       ON lb.seq = m.mseq`).all();
  return new Set(((r.results ?? []) as { bundle_id: string }[])
    .map((row) => row.bundle_id));
}

export async function versionChain(env: Env, sourceRepo: string,
                                   sourceClaimId: string): Promise<BundleRow[]> {
  const r = await env.DB.prepare(
    `SELECT * FROM library_bundles
     WHERE source_repo = ? AND source_claim_id = ? ORDER BY seq ASC`)
    .bind(sourceRepo, sourceClaimId).all();
  return ((r.results ?? []) as unknown as BundleRow[]);
}

async function neighborsOf(env: Env, row: BundleRow): Promise<
  { supersedes: string | null; superseded_by: string | null }
> {
  const chain = await versionChain(env, row.source_repo, row.source_claim_id);
  const i = chain.findIndex((c) => c.bundle_id === row.bundle_id);
  return {
    supersedes: i > 0 ? chain[i - 1].bundle_id : null,
    superseded_by: i >= 0 && i < chain.length - 1 ? chain[i + 1].bundle_id : null,
  };
}

function bundleText(b: BundleIn): string {
  const c = b.claim as Record<string, string>;
  return [
    String(c.statement ?? ""),
    `evidence level: ${c.evidence_level ?? ""}`,
    c.caveat ? `caveat: ${c.caveat}` : "",
    `source: ${String(b.provenance?.source_repo ?? "")}`,
    b.status === "candidate" ? "UNVERIFIED CANDIDATE (quarantined)" : "",
  ].filter(Boolean).join("\n");
}

// Ingest bundles: verify -> vault files -> chain a registry row -> index.
export async function indexBundles(env: Env, bundles: BundleIn[], ts: string): Promise<{
  stored: number; unchanged: number; rejected: { bundle_id: string; error: string }[];
}> {
  let stored = 0, unchanged = 0;
  const rejected: { bundle_id: string; error: string }[] = [];
  for (const b of bundles) {
    try {
      const computed = await computeBundleId(b.manifest);
      if (computed !== b.bundle_id) {
        throw new Error(`bundle_id mismatch: claimed ${b.bundle_id.slice(0, 12)}, ` +
          `manifest hashes to ${computed.slice(0, 12)}`);
      }
      if ((b.manifest.status ?? "verified") !== b.status) {
        throw new Error("status differs between bundle and manifest");
      }
      if (await getBundleRow(env, b.bundle_id)) { unchanged++; continue; } // immutable

      // Every listed file must arrive and hash to its manifest entry.
      const files = b.files ?? {};
      for (const [rel, expected] of Object.entries(b.manifest.files)) {
        const b64 = files[rel];
        if (b64 === undefined) throw new Error(`file missing from upload: ${rel}`);
        const bytes = b64ToBytes(b64);
        const sha = await putEvidence(env, bytes); // content-addressed; idempotent
        if (sha !== expected) {
          throw new Error(`${rel}: uploaded bytes hash to ${sha.slice(0, 12)}, ` +
            `manifest says ${expected.slice(0, 12)}`);
        }
      }

      // Vector first (idempotent), THEN the chained registry row — so a
      // failed ingest leaves no partial, unsearchable ledger entry behind.
      // Vectorize ids are capped at 64 bytes; `lib:` + 48 hex chars (192
      // bits) stays unique, and metadata carries the full bundle_id.
      const [vector] = await embed(env, [bundleText(b)]);
      await env.VECTORIZE.upsert([{
        id: `lib:${b.bundle_id.slice(0, 48)}`,
        values: vector,
        metadata: {
          library: "true",
          status: b.status,
          bundle_id: b.bundle_id,
          claim_id: String((b.claim as Record<string, unknown>).id ?? ""),
          statement: String((b.claim as Record<string, unknown>).statement ?? ""),
          evidence_level: String((b.claim as Record<string, unknown>).evidence_level ?? ""),
          caveat: String((b.claim as Record<string, unknown>).caveat ?? ""),
          source_repo: String(b.provenance?.source_repo ?? ""),
        },
      }]);

      // If this identity already has a latest version, the new row will
      // supersede it: prune the OLD version's search vector so discovery
      // surfaces only the current version (history stays in D1 + R2).
      const repo = String(b.provenance?.source_repo ?? "");
      const scid = String(b.provenance?.source_claim_id ?? "");
      const priorChain = await versionChain(env, repo, scid);
      const prior = priorChain[priorChain.length - 1];

      const tip = await lastRow(env);
      const prev_hash = tip ? tip.entry_hash : "";
      const row = {
        ts,
        bundle_id: b.bundle_id,
        status: b.status,
        source_repo: repo,
        source_claim_id: scid,
        claim: canonical(b.claim),
        manifest: canonical(b.manifest),
        provenance: canonical(b.provenance),
      };
      const eh = await entryHash(prev_hash, row);
      await env.DB.prepare(
        `INSERT INTO library_bundles
         (ts, bundle_id, status, source_repo, source_claim_id, claim, manifest,
          provenance, prev_hash, entry_hash)
         VALUES (?,?,?,?,?,?,?,?,?,?)`)
        .bind(row.ts, row.bundle_id, row.status, row.source_repo,
          row.source_claim_id, row.claim, row.manifest, row.provenance,
          prev_hash, eh).run();
      if (prior) {
        await env.VECTORIZE.deleteByIds([`lib:${prior.bundle_id.slice(0, 48)}`]);
      }
      stored++;
    } catch (e) {
      rejected.push({ bundle_id: b.bundle_id ?? "?", error: String((e as Error).message ?? e) });
    }
  }
  return { stored, unchanged, rejected };
}

export interface LibraryHit {
  bundle_id: string; claim_id: string; score: number; status: string;
  statement: string; evidence_level: string; caveat: string; source_repo: string;
}

export async function searchLibrary(env: Env, query: string, topK = 5): Promise<LibraryHit[]> {
  const [vector] = await embed(env, [query]);
  const res = await env.VECTORIZE.query(vector, { topK: Math.min(20, topK * 4), returnMetadata: "all" });
  // Belt and braces: ingest prunes superseded vectors, and this filter
  // drops any that predate the pruning — search shows CURRENT versions only.
  const latest = await latestBundleIds(env);
  return res.matches
    .filter((m) => String(m.metadata?.library ?? "") === "true")
    .filter((m) => latest.has(String(m.metadata?.bundle_id ?? "")))
    .slice(0, topK)
    .map((m) => ({
      bundle_id: String(m.metadata?.bundle_id ?? ""),
      claim_id: String(m.metadata?.claim_id ?? ""),
      score: m.score,
      status: String(m.metadata?.status ?? ""),
      statement: String(m.metadata?.statement ?? ""),
      evidence_level: String(m.metadata?.evidence_level ?? ""),
      caveat: String(m.metadata?.caveat ?? ""),
      source_repo: String(m.metadata?.source_repo ?? ""),
    }));
}

export async function getBundle(env: Env, bundleId: string): Promise<Record<string, unknown> | null> {
  const row = await getBundleRow(env, bundleId);
  if (!row) return null;
  const nb = await neighborsOf(env, row);
  return {
    bundle_id: row.bundle_id,
    status: row.status,
    ts: row.ts,
    source_repo: row.source_repo,
    source_claim_id: row.source_claim_id,
    supersedes: nb.supersedes,
    superseded_by: nb.superseded_by,
    is_current: nb.superseded_by === null,
    claim: JSON.parse(row.claim),
    manifest: JSON.parse(row.manifest),
    provenance: JSON.parse(row.provenance),
    note: "Fetch files by hash at /library/file/<sha256>; verify locally with " +
      "bundlefmt.verify_bundle — the library is distribution, not truth." +
      (nb.superseded_by ? " NOTE: a newer version of this claim exists (" +
        "superseded_by) — prefer it unless you are auditing history." : ""),
  };
}

// One-off / maintenance: prune search vectors of ALL superseded versions
// (history in D1 + R2 is untouched — this only cleans discovery).
export async function pruneSuperseded(env: Env): Promise<
  { total_rows: number; current: number; vectors_pruned: number }
> {
  const latest = await latestBundleIds(env);
  const r = await env.DB.prepare(
    "SELECT bundle_id FROM library_bundles ORDER BY seq ASC").all();
  const all = ((r.results ?? []) as { bundle_id: string }[])
    .map((row) => row.bundle_id);
  const stale = all.filter((id) => !latest.has(id));
  const BATCH = 50;
  for (let i = 0; i < stale.length; i += BATCH) {
    await env.VECTORIZE.deleteByIds(
      stale.slice(i, i + BATCH).map((id) => `lib:${id.slice(0, 48)}`));
  }
  return { total_rows: all.length, current: latest.size,
           vectors_pruned: stale.length };
}

// Verify a stored bundle: manifest still hashes to the id, every file is in
// the vault and re-hashes correctly, and the registry chain is intact.
export async function verifyBundle(env: Env, bundleId: string): Promise<Record<string, unknown>> {
  const row = await getBundleRow(env, bundleId);
  if (!row) return { found: false };
  const man = JSON.parse(row.manifest) as BundleManifest;
  const computed = await computeBundleId(man);
  const filesOk: Record<string, boolean> = {};
  let allFiles = true;
  for (const [rel, sha] of Object.entries(man.files)) {
    const v = await verifyEvidence(env, sha);
    filesOk[rel] = v.present && v.matches;
    if (!filesOk[rel]) allFiles = false;
  }
  const chain = await verifyLibraryChain(env);
  return {
    found: true,
    bundle_id: bundleId,
    status: row.status,
    manifest_matches_id: computed === bundleId,
    files_ok: filesOk,
    all_files_ok: allFiles,
    registry_chain_intact: chain.ok,
    ok: computed === bundleId && allFiles && chain.ok,
  };
}

export async function verifyLibraryChain(env: Env): Promise<
  { ok: boolean; entries: number; brokenAt: number | null }
> {
  const r = await env.DB.prepare("SELECT * FROM library_bundles ORDER BY seq ASC").all();
  const rows = (r.results as unknown as BundleRow[]) ?? [];
  let prev = "";
  for (const row of rows) {
    if (row.prev_hash !== prev) return { ok: false, entries: rows.length, brokenAt: row.seq };
    const recomputed = await entryHash(prev, {
      ts: row.ts, bundle_id: row.bundle_id, status: row.status,
      source_repo: row.source_repo, source_claim_id: row.source_claim_id,
      claim: row.claim, manifest: row.manifest, provenance: row.provenance,
    });
    if (recomputed !== row.entry_hash) return { ok: false, entries: rows.length, brokenAt: row.seq };
    prev = row.entry_hash;
  }
  return { ok: true, entries: rows.length, brokenAt: null };
}

export async function librarySummary(env: Env): Promise<Record<string, unknown>> {
  const r = await env.DB.prepare(
    "SELECT status, COUNT(*) AS c FROM library_bundles GROUP BY status").all();
  const by_status: Record<string, number> = {};
  for (const row of (r.results as { status: string; c: number }[]) ?? []) {
    by_status[row.status] = Number(row.c);
  }
  const latest = await latestBundleIds(env);
  const total = Object.values(by_status).reduce((a, b) => a + b, 0);
  return {
    current_claims: latest.size,
    bundle_versions_total: total,
    superseded_versions: total - latest.size,
    by_status,
    note: "search surfaces current versions only; superseded versions " +
      "remain in the ledger and vault as auditable history (/library/versions).",
  };
}
