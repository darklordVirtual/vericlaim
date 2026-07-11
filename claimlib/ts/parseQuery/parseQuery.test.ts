// SPDX-License-Identifier: Apache-2.0
import { test } from "node:test";
import assert from "node:assert/strict";
import { parseQuery, stringifyQuery } from "./parseQuery.ts";

test("parses simple pairs", () => {
  assert.deepEqual(parseQuery("a=1&b=2"), { a: "1", b: "2" });
});

test("repeated keys collapse to ordered arrays", () => {
  assert.deepEqual(parseQuery("?a=1&b=2&a=3"), { a: ["1", "3"], b: "2" });
  assert.deepEqual(parseQuery("t=1&t=2&t=3"), { t: ["1", "2", "3"] });
});

test("leading ? is optional", () => {
  assert.deepEqual(parseQuery("?k=v"), { k: "v" });
  assert.deepEqual(parseQuery("k=v"), { k: "v" });
});

test("empty and lone-? queries yield {}", () => {
  assert.deepEqual(parseQuery(""), {});
  assert.deepEqual(parseQuery("?"), {});
});

test("URI-decodes keys and values", () => {
  assert.deepEqual(parseQuery("q=a%20b%26c"), { q: "a b&c" });
  assert.deepEqual(parseQuery("a%20b=1"), { "a b": "1" });
  assert.deepEqual(parseQuery("q=a+b"), { q: "a b" });
});

test("key without = maps to empty string; extra = kept in value", () => {
  assert.deepEqual(parseQuery("flag"), { flag: "" });
  assert.deepEqual(parseQuery("eq=a=b=c"), { eq: "a=b=c" });
});

test("empty pairs are skipped", () => {
  assert.deepEqual(parseQuery("a=1&&b=2&"), { a: "1", b: "2" });
});

test("stringify uses stable sorted key order", () => {
  assert.equal(stringifyQuery({ b: "2", a: "1" }), "a=1&b=2");
});

test("stringify expands arrays in order", () => {
  assert.equal(stringifyQuery({ a: ["1", "3"], b: "2" }), "a=1&a=3&b=2");
});

test("stringify URI-encodes and uses + for space", () => {
  assert.equal(stringifyQuery({ q: "a b" }), "q=a+b");
  assert.equal(stringifyQuery({ q: "a&b=c" }), "q=a%26b%3Dc");
});

test("round-trips through stringify then parse", () => {
  for (const qs of ["a=1&b=2&a=3", "q=a%20b%26c", "n=%C3%A6%C3%B8%C3%A5"]) {
    const once = parseQuery(qs);
    assert.deepEqual(parseQuery(stringifyQuery(once)), once);
  }
});

test("agrees with URLSearchParams.getAll on per-key decoding", () => {
  const q = "a=1&b=2&a=3&q=a%20b%26c&t=1&t=2";
  const parsed = parseQuery(q);
  const usp = new URLSearchParams(q);
  for (const key of Object.keys(parsed)) {
    const v = parsed[key];
    const ours = Array.isArray(v) ? v : [v];
    assert.deepEqual(ours, usp.getAll(key));
  }
});
