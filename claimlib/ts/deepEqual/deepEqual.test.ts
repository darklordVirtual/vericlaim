// SPDX-License-Identifier: Apache-2.0
import { test } from "node:test";
import assert from "node:assert/strict";
import { deepEqual } from "./deepEqual.ts";

test("primitives", () => {
  assert.equal(deepEqual(1, 1), true);
  assert.equal(deepEqual(1, 2), false);
  assert.equal(deepEqual("x", "x"), true);
  assert.equal(deepEqual("x", "y"), false);
  assert.equal(deepEqual(true, true), true);
  assert.equal(deepEqual(true, false), false);
  assert.equal(deepEqual(1, "1"), false);
  assert.equal(deepEqual(0, false), false);
});

test("NaN equals NaN", () => {
  assert.equal(deepEqual(NaN, NaN), true);
  assert.equal(deepEqual(NaN, 1), false);
});

test("null vs undefined are distinct", () => {
  assert.equal(deepEqual(null, null), true);
  assert.equal(deepEqual(undefined, undefined), true);
  assert.equal(deepEqual(null, undefined), false);
  assert.equal(deepEqual(null, {}), false);
});

test("arrays", () => {
  assert.equal(deepEqual([1, 2, 3], [1, 2, 3]), true);
  assert.equal(deepEqual([1, 2], [1, 2, 3]), false);
  assert.equal(deepEqual([1, 2, 3], [1, 9, 3]), false);
  assert.equal(deepEqual([[1], [2, 3]], [[1], [2, 3]]), true);
  assert.equal(deepEqual([1, 2], { 0: 1, 1: 2 }), false);
});

test("plain objects compare by key-set and values", () => {
  assert.equal(deepEqual({ a: 1, b: 2 }, { a: 1, b: 2 }), true);
  assert.equal(deepEqual({ a: 1, b: 2 }, { b: 2, a: 1 }), true);
  assert.equal(deepEqual({ a: 1, b: 2 }, { a: 1, b: 3 }), false);
  assert.equal(deepEqual({ a: 1 }, { a: 1, b: 2 }), false);
  assert.equal(deepEqual({ a: undefined }, {}), false);
  assert.equal(deepEqual({ a: { b: { c: 1 } } }, { a: { b: { c: 1 } } }), true);
  assert.equal(deepEqual({ a: { b: { c: 1 } } }, { a: { b: { c: 2 } } }), false);
});

test("dates compare by getTime", () => {
  assert.equal(deepEqual(new Date(0), new Date(0)), true);
  assert.equal(deepEqual(new Date(0), new Date(1000)), false);
  assert.equal(deepEqual(new Date(0), 0), false);
  assert.equal(deepEqual(new Date("2020-01-01T00:00:00Z"), new Date(1577836800000)), true);
});

test("different types are never equal", () => {
  assert.equal(deepEqual({ a: 1 }, 1), false);
  assert.equal(deepEqual([1], 1), false);
  assert.equal(deepEqual(new Date(0), {}), false);
});
