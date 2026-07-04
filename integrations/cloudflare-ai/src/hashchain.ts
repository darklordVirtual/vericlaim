// Tamper-evident hashing for the claim ledger.
//
// Each ledger row carries entry_hash = sha256(prev_hash + canonical(row)). The
// chain means altering any past row changes its entry_hash, which breaks the
// prev_hash link of every row after it — so tampering is detectable by re-walking
// the chain (see verifyChain). This is the Certificate-Transparency / Rekor idea
// applied to a project's claims about itself.

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
