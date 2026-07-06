// SPDX-License-Identifier: Apache-2.0
// Regression tests for the /index snapshot-integrity guard (P1): a declared
// count/hash must match before a full snapshot is allowed to prune the index.
import { test } from "node:test";
import assert from "node:assert";

import { buildReceipt, validateSnapshot } from "../src/snapshot.ts";

test("no declared metadata -> accepted (backward compatible)", () => {
  assert.equal(validateSnapshot(5, {}, true).ok, true);
});

test("matching expected_claim_count -> accepted", () => {
  assert.equal(validateSnapshot(5, { expected_claim_count: 5 }, true).ok, true);
});

// The core fix: a truncated/defective export is refused, not applied.
test("mismatched expected_claim_count -> refused before prune", () => {
  const r = validateSnapshot(1, { expected_claim_count: 42 }, true);
  assert.equal(r.ok, false);
  assert.match(r.error!, /count mismatch/);
});

test("negative / non-integer expected_claim_count -> refused", () => {
  assert.equal(validateSnapshot(5, { expected_claim_count: -1 }, true).ok, false);
  assert.equal(validateSnapshot(5, { expected_claim_count: 2.5 }, true).ok, false);
});

test("register_sha256 must be sha256 hex", () => {
  assert.equal(validateSnapshot(5, { register_sha256: "a".repeat(64) }, true).ok, true);
  assert.equal(validateSnapshot(5, { register_sha256: "nothex" }, true).ok, false);
  assert.equal(validateSnapshot(5, { register_sha256: "A".repeat(64) }, true).ok, false);
});

test("full_snapshot=true conflicts with a delta (reconcile=0)", () => {
  assert.equal(validateSnapshot(5, { full_snapshot: true }, false).ok, false);
  assert.equal(validateSnapshot(5, { full_snapshot: true }, true).ok, true);
});

test("buildReceipt echoes id/hash/count and folds in the change counts", () => {
  const counts = { indexed: 3, ledger_appended: 1, ledger_unchanged: 2, vaulted: 0, withdrawn: 1 };
  const { receipt } = buildReceipt(
    { snapshot_id: "snap-1", register_sha256: "b".repeat(64), full_snapshot: true },
    counts, 3, "2026-07-06T00:00:00Z");
  assert.equal(receipt.snapshot_id, "snap-1");
  assert.equal(receipt.claim_count, 3);
  assert.equal(receipt.full_snapshot, true);
  assert.equal(receipt.withdrawn, 1);
  assert.equal(receipt.ingested_at, "2026-07-06T00:00:00Z");
});
