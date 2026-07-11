// SPDX-License-Identifier: Apache-2.0
import { test } from "node:test";
import assert from "node:assert/strict";
import { groupBy } from "./groupBy.ts";

test("groups by parity preserving input order", () => {
  assert.deepEqual(
    groupBy([1, 2, 3, 4, 5, 6], (n) => (n % 2 === 0 ? "even" : "odd")),
    { odd: [1, 3, 5], even: [2, 4, 6] },
  );
});

test("empty input yields an empty object", () => {
  assert.deepEqual(groupBy([] as number[], (n) => String(n)), {});
});

test("all items sharing a key keep input order within the bucket", () => {
  assert.deepEqual(groupBy([3, 1, 2], () => "k"), { k: [3, 1, 2] });
});

test("groups objects by a field", () => {
  const rows = [
    { id: 1, team: "red" },
    { id: 2, team: "blue" },
    { id: 3, team: "red" },
  ];
  assert.deepEqual(groupBy(rows, (o) => o.team), {
    red: [
      { id: 1, team: "red" },
      { id: 3, team: "red" },
    ],
    blue: [{ id: 2, team: "blue" }],
  });
});

test("bucket key order follows first appearance, not sort", () => {
  const g = groupBy(["zebra", "apple", "zip", "ant"], (w) => w[0]);
  assert.deepEqual(Object.keys(g), ["z", "a"]);
});

test("a __proto__ data key becomes an ordinary bucket, not prototype pollution", () => {
  const g = groupBy(["a", "b", "a"], (s) => (s === "b" ? "__proto__" : "safe"));
  assert.deepEqual(g["__proto__"], ["b"]);
  assert.deepEqual(g["safe"], ["a", "a"]);
  // Object.prototype must be untouched: no stray key leaked onto it.
  assert.equal(({} as Record<string, unknown>)["safe"], undefined);
});

test("returned buckets are independent arrays (mutating one input group is local)", () => {
  const g = groupBy([1, 2, 3], (n) => (n === 2 ? "b" : "a"));
  g["a"].push(99);
  assert.deepEqual(g, { a: [1, 3, 99], b: [2] });
});
