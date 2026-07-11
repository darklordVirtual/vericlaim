// SPDX-License-Identifier: Apache-2.0
import { test } from "node:test";
import assert from "node:assert/strict";
import { cx } from "./cx.ts";

test("spec example combines mixed inputs", () => {
  assert.equal(cx("a", false, ["b", { c: true, d: false }], undefined, 0, "e"), "a b c e");
});

test("plain strings join with single spaces", () => {
  assert.equal(cx("a", "b", "c"), "a b c");
});

test("all falsy inputs yield empty string", () => {
  assert.equal(cx(false, null, undefined, 0, "", NaN), "");
  assert.equal(cx(), "");
});

test("objects include keys with truthy values only", () => {
  assert.equal(cx({ foo: true, bar: false, baz: 1 }), "foo baz");
  assert.equal(cx({ active: "yes", hidden: "" }), "active");
});

test("arrays flatten recursively", () => {
  assert.equal(cx(["a", ["b", ["c"]]], "d"), "a b c d");
  assert.equal(cx(["a", [false, "b", [null, "c"]]]), "a b c");
});

test("numbers: nonzero stringified, zero and NaN dropped", () => {
  assert.equal(cx(1, 0, 2, "n"), "1 2 n");
});

test("duplicates are preserved (no de-dup)", () => {
  assert.equal(cx("a", "a", { a: true }), "a a a");
});

test("booleans never contribute a token", () => {
  assert.equal(cx(true, "a", true), "a");
});

test("document order is preserved across kinds", () => {
  assert.equal(cx("first", ["second"], { third: true }), "first second third");
});
