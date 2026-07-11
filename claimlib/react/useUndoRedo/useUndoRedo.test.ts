// SPDX-License-Identifier: Apache-2.0
// Unit tests for the pure undo/redo core (the React binding is a thin wrapper).
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  initHistory,
  push,
  undo,
  redo,
  canUndo,
  canRedo,
} from "./undoredo.logic.ts";

test("fresh history has empty stacks and no undo/redo", () => {
  const s = initHistory(0);
  assert.deepEqual(s, { past: [], present: 0, future: [] });
  assert.equal(canUndo(s), false);
  assert.equal(canRedo(s), false);
});

test("push records the old present and clears the redo stack", () => {
  let s = initHistory(0);
  s = push(s, 1);
  s = push(s, 2);
  assert.deepEqual(s, { past: [0, 1], present: 2, future: [] });
  assert.equal(canUndo(s), true);
  assert.equal(canRedo(s), false);
});

test("undo then redo returns to the same present (round-trip)", () => {
  let s = initHistory(0);
  s = push(s, 1);
  s = push(s, 2);
  const back = undo(s);
  assert.equal(back.present, 1);
  assert.equal(canRedo(back), true);
  const forward = redo(back);
  assert.deepEqual(forward, s);
});

test("a new set() after undo forks history and drops the redo branch", () => {
  let s = initHistory(0);
  s = push(s, 1);
  s = push(s, 2); // history: 0,1 -> 2
  s = undo(s); // present 1, future [2]
  assert.equal(canRedo(s), true);
  s = push(s, 9); // fork
  assert.deepEqual(s, { past: [0, 1], present: 9, future: [] });
  assert.equal(canRedo(s), false); // redo branch discarded
});

test("undo at base and redo at tip are no-ops (fail closed)", () => {
  let s = initHistory(0);
  s = push(s, 1);
  s = undo(s); // back to base 0
  assert.equal(s.present, 0);
  assert.equal(canUndo(s), false);
  const same = undo(s);
  assert.equal(same, s); // no-op returns the same object
  s = redo(s); // back to 1
  assert.equal(s.present, 1);
  assert.equal(canRedo(s), false);
  assert.equal(redo(s), s); // no-op at the tip
});

test("input state is never mutated by an operation", () => {
  const s = initHistory(0);
  const pushed = push(s, 1);
  assert.deepEqual(s, { past: [], present: 0, future: [] });
  assert.notEqual(pushed, s);
});
