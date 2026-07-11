// SPDX-License-Identifier: Apache-2.0
import { test } from "node:test";
import assert from "node:assert/strict";
import { ok, err, map, mapErr, andThen, unwrapOr, isOk, isErr, fromThrowing } from "./result.ts";

test("ok / err constructors", () => {
  assert.deepEqual(ok(1), { ok: true, value: 1 });
  assert.deepEqual(err("e"), { ok: false, error: "e" });
});

test("map only touches the ok branch", () => {
  assert.deepEqual(map(ok<number>(21), (x) => x * 2), { ok: true, value: 42 });
  assert.deepEqual(map(err<string, number>("boom"), (x: number) => x * 2), { ok: false, error: "boom" });
});

test("mapErr only touches the err branch", () => {
  assert.deepEqual(mapErr(err<number, number>(2), (e) => e * 10), { ok: false, error: 20 });
  assert.deepEqual(mapErr(ok<number, number>(5), (e) => e * 10), { ok: true, value: 5 });
});

test("andThen chains and short-circuits", () => {
  assert.deepEqual(andThen(ok<number>(2), (x) => ok(x + 1)), { ok: true, value: 3 });
  assert.deepEqual(andThen(err<string, number>("x"), (x: number) => ok(x + 1)), { ok: false, error: "x" });
});

test("unwrapOr falls back on err", () => {
  assert.equal(unwrapOr(ok<number>(3), 7), 3);
  assert.equal(unwrapOr(err<string, number>("e"), 7), 7);
});

test("isOk / isErr", () => {
  assert.equal(isOk(ok(1)), true);
  assert.equal(isErr(err("e")), true);
});

test("fromThrowing captures both outcomes", () => {
  assert.deepEqual(fromThrowing(() => 10), { ok: true, value: 10 });
  const thrown = fromThrowing(() => { throw new Error("nope"); });
  assert.equal(thrown.ok, false);
});
