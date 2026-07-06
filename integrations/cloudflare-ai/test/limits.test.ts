// SPDX-License-Identifier: Apache-2.0
// Regression tests for the request-limit helpers (P1: bound query length, body
// size, and ledger-export pagination). Node's built-in test runner, no deps.
import { test } from "node:test";
import assert from "node:assert";

import {
  LEDGER_PAGE_MAX,
  MAX_BODY_BYTES,
  MAX_QUERY_LEN,
  clampLimit,
  declaredBodyTooLarge,
  parseCursor,
  queryTooLong,
} from "../src/limits.ts";

test("queryTooLong: at the limit is OK, over is not", () => {
  assert.equal(queryTooLong("a".repeat(MAX_QUERY_LEN)), false);
  assert.equal(queryTooLong("a".repeat(MAX_QUERY_LEN + 1)), true);
  assert.equal(queryTooLong(""), false);
});

function reqWithLength(len?: string): Request {
  const h = new Headers();
  if (len !== undefined) h.set("content-length", len);
  return new Request("https://x/", { method: "POST", headers: h });
}

test("declaredBodyTooLarge: only when the declared length exceeds the max", () => {
  assert.equal(declaredBodyTooLarge(reqWithLength(String(MAX_BODY_BYTES))), false);
  assert.equal(declaredBodyTooLarge(reqWithLength(String(MAX_BODY_BYTES + 1))), true);
  assert.equal(declaredBodyTooLarge(reqWithLength()), false, "no header -> not blocked (parse path caps it)");
  assert.equal(declaredBodyTooLarge(reqWithLength("garbage")), false, "unparseable -> not blocked");
});

test("clampLimit: default on junk, clamps into [1, max]", () => {
  assert.equal(clampLimit(null, 500, LEDGER_PAGE_MAX), 500);
  assert.equal(clampLimit("0", 500, LEDGER_PAGE_MAX), 500);
  assert.equal(clampLimit("-5", 500, LEDGER_PAGE_MAX), 500);
  assert.equal(clampLimit("abc", 500, LEDGER_PAGE_MAX), 500);
  assert.equal(clampLimit("10", 500, LEDGER_PAGE_MAX), 10);
  assert.equal(clampLimit(String(LEDGER_PAGE_MAX + 1000), 500, LEDGER_PAGE_MAX), LEDGER_PAGE_MAX);
});

test("parseCursor: non-negative integer, junk -> 0", () => {
  assert.equal(parseCursor(null), 0);
  assert.equal(parseCursor("-3"), 0);
  assert.equal(parseCursor("abc"), 0);
  assert.equal(parseCursor("42"), 42);
  assert.equal(parseCursor("42.9"), 42);
});
