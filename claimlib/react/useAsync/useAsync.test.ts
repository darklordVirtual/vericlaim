// SPDX-License-Identifier: Apache-2.0
// Unit tests for the pure async state machine (the React binding is a thin wrapper).
import { test } from "node:test";
import assert from "node:assert/strict";
import { asyncReducer, idleState } from "./async.logic.ts";

test("idle is the neutral starting state", () => {
  assert.deepEqual(idleState(), { status: "idle", data: undefined, error: undefined });
});

test("start moves to pending and clears any prior error", () => {
  const s = asyncReducer({ status: "error", data: undefined, error: "boom" }, { type: "start" });
  assert.equal(s.status, "pending");
  assert.equal(s.error, undefined);
});

test("start keeps stale data (stale-while-revalidate)", () => {
  const s = asyncReducer({ status: "success", data: 7, error: undefined }, { type: "start" });
  assert.deepEqual(s, { status: "pending", data: 7, error: undefined });
});

test("resolve moves to success, sets data, clears error", () => {
  const s = asyncReducer({ status: "error", data: undefined, error: "boom" }, { type: "resolve", data: "ok" });
  assert.deepEqual(s, { status: "success", data: "ok", error: undefined });
});

test("resolve accepts falsy data without confusion", () => {
  const s = asyncReducer({ status: "pending", data: undefined, error: undefined }, { type: "resolve", data: 0 });
  assert.deepEqual(s, { status: "success", data: 0, error: undefined });
});

test("reject moves to error, sets error, keeps stale data", () => {
  const s = asyncReducer({ status: "success", data: 5, error: undefined }, { type: "reject", error: "e2" });
  assert.deepEqual(s, { status: "error", data: 5, error: "e2" });
});

test("unknown actions leave the state unchanged", () => {
  const before = { status: "success", data: 1, error: undefined } as const;
  // deliberately cast an invalid action to exercise the total-reducer default branch
  const s = asyncReducer(before, { type: "nope" } as unknown as { type: "start" });
  assert.deepEqual(s, before);
});
