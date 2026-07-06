// Tamper-evident hashing for the claim ledger.
//
// Each ledger row carries entry_hash = sha256(prev_hash + canonical(row)). The
// chain means altering any past row changes its entry_hash, which breaks the
// prev_hash link of every row after it — so a PARTIAL edit is detectable by
// re-walking the chain (see verifyChain). This is the Certificate-Transparency /
// Rekor idea applied to a project's claims about itself.
//
// HONEST LIMIT: the hash is unkeyed, so an actor who can write the whole D1
// table can rewrite history AND recompute every entry_hash from genesis — then
// verifyChain passes. Internal consistency is not proof against a full rewrite.
// Two things raise the bar: (1) external witnesses re-walk /ledger/export and
// check the chain still EXTENDS a previously-seen head (length + head pinned
// off-box); (2) the optional HMAC head signature (hmacHex, keyed by a secret
// not in D1) that only the operator can produce. Use one or both when the D1
// writer is not fully trusted.

// Deterministic JSON: object keys sorted recursively, so the same logical value
// always hashes the same regardless of field order.
export function canonical(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map(canonical).join(",") + "]";
  const obj = value as Record<string, unknown>;
  const keys = Object.keys(obj).sort();
  return "{" + keys.map((k) => JSON.stringify(k) + ":" + canonical(obj[k])).join(",") + "}";
}

export async function sha256Hex(data: string | ArrayBuffer | Uint8Array): Promise<string> {
  const bytes = typeof data === "string" ? new TextEncoder().encode(data)
    : data instanceof Uint8Array ? data : new Uint8Array(data);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// The content hash of a claim: identity of what it asserts + what backs it.
// Two ledger events with the same content hash are the same claim state, so we
// only append when this changes.
export async function contentHash(claim: {
  claim_id: string; statement?: string; evidence_level?: string;
  metrics?: unknown; caveat?: string; artifact?: unknown; artifact_sha256?: string | null;
}): Promise<string> {
  return sha256Hex(canonical({
    claim_id: claim.claim_id,
    statement: claim.statement ?? "",
    evidence_level: claim.evidence_level ?? "",
    metrics: claim.metrics ?? null,
    caveat: claim.caveat ?? "",
    artifact: claim.artifact ?? [],
    artifact_sha256: claim.artifact_sha256 ?? "",
  }));
}

// entry_hash for a row given the previous entry_hash. The row object here must
// exclude entry_hash/prev_hash themselves.
export async function entryHash(prevHash: string, row: Record<string, unknown>): Promise<string> {
  return sha256Hex(prevHash + "\n" + canonical(row));
}

// HMAC-SHA256 of a message under a secret key, hex-encoded. Used to sign the
// ledger head: unlike the unkeyed chain, a valid signature cannot be produced
// by an attacker who only has D1 write access — they lack the key.
export async function hmacHex(key: string, message: string): Promise<string> {
  const cryptoKey = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(key),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", cryptoKey, new TextEncoder().encode(message));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
