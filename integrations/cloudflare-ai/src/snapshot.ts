// SPDX-License-Identifier: Apache-2.0
// Snapshot integrity for POST /index (P1 review finding). A "full snapshot" push
// reconciles the live search index down to exactly the claims it carries — so a
// DEFECTIVE export (truncated to one claim, wrong file) could prune everything
// else. The exporter therefore declares what it is sending; we refuse to
// reconcile unless what arrived matches. Pure + unit-testable (no bindings).

export interface SnapshotMeta {
  full_snapshot?: boolean;        // explicit intent to reconcile to this set
  expected_claim_count?: number;  // the exporter's own count of valid claims
  register_sha256?: string;       // integrity tag of the source register
  snapshot_id?: string;           // opaque id echoed back in the receipt
}

export interface SnapshotCheck { ok: boolean; error?: string; }

const SHA256_HEX = /^[0-9a-f]{64}$/;

// Validate BEFORE any prune. The load-bearing check: when the exporter declares
// expected_claim_count, the number of VALID claims actually received must equal
// it — an off-by-N truncation or a one-claim defect is refused, not applied.
export function validateSnapshot(
  validClaimCount: number, meta: SnapshotMeta, isReconcile: boolean,
): SnapshotCheck {
  if (meta.expected_claim_count !== undefined) {
    if (!Number.isInteger(meta.expected_claim_count) || meta.expected_claim_count < 0) {
      return { ok: false, error: "expected_claim_count must be a non-negative integer" };
    }
    if (meta.expected_claim_count !== validClaimCount) {
      return {
        ok: false,
        error: `snapshot count mismatch: exporter declared ${meta.expected_claim_count} ` +
          `but ${validClaimCount} valid claim(s) arrived — refusing to reconcile a ` +
          `possibly-truncated snapshot (fix the export, or drop expected_claim_count)`,
      };
    }
  }
  if (meta.register_sha256 !== undefined && !SHA256_HEX.test(meta.register_sha256)) {
    return { ok: false, error: "register_sha256 must be a lowercase sha256 hex string" };
  }
  // full_snapshot=true asserting an empty reconcile is still gated by the caller's
  // allow_empty guard; we only validate consistency here.
  if (meta.full_snapshot === true && !isReconcile) {
    return { ok: false, error: "full_snapshot=true conflicts with reconcile=0 (a delta is not a full snapshot)" };
  }
  return { ok: true };
}

export interface IngestCounts {
  indexed: number; ledger_appended: number; ledger_unchanged: number;
  vaulted: number; withdrawn: number;
}

// A verifiable receipt: what the writer accepted and what it changed.
export function buildReceipt(
  meta: SnapshotMeta, counts: IngestCounts, claim_count: number, ingested_at: string,
) {
  return {
    receipt: {
      snapshot_id: meta.snapshot_id ?? null,
      register_sha256: meta.register_sha256 ?? null,
      claim_count,
      full_snapshot: meta.full_snapshot === true,
      ingested_at,
      ...counts,
    },
  };
}
