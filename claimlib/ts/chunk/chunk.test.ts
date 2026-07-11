// SPDX-License-Identifier: Apache-2.0
import { test } from "node:test";
import assert from "node:assert/strict";
import { chunk } from "./chunk.ts";

test("splits 7 items into chunks of 3 with a short final chunk", () => {
  assert.deepEqual(chunk([1, 2, 3, 4, 5, 6, 7], 3), [[1, 2, 3], [4, 5, 6], [7]]);
});

test("empty array yields no chunks", () => {
  assert.deepEqual(chunk([] as number[], 3), []);
});

test("exact multiples produce equal chunks", () => {
  assert.deepEqual(chunk([1, 2, 3, 4], 2), [[1, 2], [3, 4]]);
});

test("size 1 yields singletons", () => {
  assert.deepEqual(chunk(["a", "b", "c"], 1), [["a"], ["b"], ["c"]]);
});

test("size larger than length yields one chunk", () => {
  assert.deepEqual(chunk([1, 2], 5), [[1, 2]]);
});

test("does not mutate the input array", () => {
  const input = [1, 2, 3, 4];
  chunk(input, 2);
  assert.deepEqual(input, [1, 2, 3, 4]);
});

test("size below 1 throws RangeError", () => {
  assert.throws(() => chunk([1, 2, 3], 0), RangeError);
  assert.throws(() => chunk([1, 2, 3], -1), RangeError);
});

test("non-integer size throws RangeError", () => {
  assert.throws(() => chunk([1, 2, 3], 1.5), RangeError);
});
