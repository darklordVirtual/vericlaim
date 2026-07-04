// The evidence vault: content-addressed artifact storage in R2.
//
// Artifacts are stored under `sha256/<hex>`, so the storage key IS the hash of
// the bytes. You can always retrieve the exact evidence that backed a claim at
// a point in time, and prove it is unchanged by re-hashing what you get back —
// even if the repository later rewrote its history.
import { type Env } from "./lib";
import { sha256Hex } from "./hashchain";

const KEY = (sha: string) => `sha256/${sha}`;

// Store bytes, returning their sha256. Idempotent: same bytes -> same key.
export async function putEvidence(env: Env, bytes: Uint8Array): Promise<string> {
  const sha = await sha256Hex(bytes);
  const key = KEY(sha);
  // Only write if absent — the content address guarantees identical bytes.
  const head = await env.EVIDENCE.head(key);
  if (!head) {
    await env.EVIDENCE.put(key, bytes, {
      httpMetadata: { contentType: "application/octet-stream" },
    });
  }
  return sha;
}

export async function getEvidence(env: Env, sha: string): Promise<Uint8Array | null> {
  const obj = await env.EVIDENCE.get(KEY(sha));
  if (!obj) return null;
  return new Uint8Array(await obj.arrayBuffer());
}

// Verify: fetch by the claimed hash and confirm the stored bytes really hash to
// it (defence in depth against a corrupted store).
export async function verifyEvidence(env: Env, sha: string): Promise<
  { present: boolean; matches: boolean; size: number }
> {
  const bytes = await getEvidence(env, sha);
  if (!bytes) return { present: false, matches: false, size: 0 };
  const actual = await sha256Hex(bytes);
  return { present: true, matches: actual === sha, size: bytes.length };
}
