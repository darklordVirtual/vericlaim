// SPDX-License-Identifier: Apache-2.0
// Unit tests for the pure stepper core (the React binding is a thin wrapper).
import { test } from "node:test";
import assert from "node:assert/strict";
import { stepper, next, prev, goto } from "./stepper.logic.ts";

test("single step is both first and last with zero progress", () => {
  assert.deepEqual(stepper(1, 0), {
    index: 0, stepCount: 1, isFirst: true, isLast: true,
    progress: 0, nextIndex: 0, prevIndex: 0,
  });
});

test("progress spans 0..1 across the steps", () => {
  assert.equal(stepper(5, 0).progress, 0);
  assert.equal(stepper(5, 2).progress, 0.5);
  assert.equal(stepper(5, 4).progress, 1);
  assert.equal(stepper(4, 1).progress, 0.3333); // 1/3 rounded to 4 dp
});

test("index is clamped into range on both ends", () => {
  assert.equal(stepper(5, 99).index, 4);
  assert.equal(stepper(5, -3).index, 0);
  assert.equal(goto(5, 100), 4);
  assert.equal(goto(5, -100), 0);
});

test("next/prev clamp at the boundaries", () => {
  assert.equal(next(5, 4), 4); // cannot go past the last step
  assert.equal(next(5, 0), 1);
  assert.equal(prev(5, 0), 0); // cannot go before the first step
  assert.equal(prev(5, 4), 3);
});

test("isFirst/isLast track the boundaries", () => {
  assert.equal(stepper(3, 0).isFirst, true);
  assert.equal(stepper(3, 0).isLast, false);
  assert.equal(stepper(3, 2).isLast, true);
  assert.equal(stepper(3, 1).isFirst, false);
});

test("fails closed on invalid stepCount", () => {
  assert.throws(() => stepper(0, 0), RangeError);
  assert.throws(() => stepper(-2, 0), RangeError);
  assert.throws(() => goto(1.5, 0), RangeError);
});
