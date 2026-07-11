// SPDX-License-Identifier: Apache-2.0
// Unit tests for the pure trailing-debounce core (the React binding is a thin
// setTimeout wrapper). Expected emissions are hand-derived from the debounce
// definition, independent of the implementation.
import { test } from "node:test";
import assert from "node:assert/strict";
import { emitDebounced } from "./debounce.logic.ts";

test("empty trace emits nothing", () => {
  assert.deepEqual(emitDebounced([], 100), []);
});

test("a single event fires exactly delay later", () => {
  assert.deepEqual(emitDebounced([[50, "x"]], 100), [[150, "x"]]);
});

test("a rapid burst collapses to the last value", () => {
  assert.deepEqual(
    emitDebounced([[0, "a"], [10, "b"], [20, "c"]], 100),
    [[120, "c"]],
  );
});

test("events spaced at least delay apart each emit", () => {
  assert.deepEqual(
    emitDebounced([[0, "a"], [200, "b"], [400, "c"]], 100),
    [[100, "a"], [300, "b"], [500, "c"]],
  );
});

test("gap exactly equal to delay counts as fired; one below coalesces", () => {
  assert.deepEqual(emitDebounced([[0, "a"], [100, "b"]], 100), [[100, "a"], [200, "b"]]);
  assert.deepEqual(emitDebounced([[0, "a"], [99, "b"]], 100), [[199, "b"]]);
});

test("only the last event ever survives a burst; emission time is lastEvent + delay", () => {
  const trace: Array<[number, string]> = [[0, "h"], [50, "he"], [90, "hel"], [130, "hell"], [170, "hello"]];
  assert.deepEqual(emitDebounced(trace, 200), [[370, "hello"]]);
});

test("fails closed on invalid delay and unsorted input", () => {
  assert.throws(() => emitDebounced([[0, "a"]], 0), RangeError);
  assert.throws(() => emitDebounced([[0, "a"]], -5), RangeError);
  assert.throws(() => emitDebounced([[0, "a"]], 1.5), RangeError);
  assert.throws(() => emitDebounced([[10, "a"], [5, "b"]], 100), RangeError);
});
