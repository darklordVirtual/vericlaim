// SPDX-License-Identifier: Apache-2.0
// Unit tests for the pure pagination core (the React binding is a thin wrapper).
import { test } from "node:test";
import assert from "node:assert/strict";
import { paginate } from "./pagination.logic.ts";

test("empty list yields a zero window", () => {
  assert.deepEqual(paginate(0, 10, 1), {
    page: 0, pageCount: 0, pageSize: 10, total: 0,
    startIndex: 0, endIndex: 0, itemsOnPage: 0, hasPrev: false, hasNext: false,
  });
});

test("last page is partial and has no next", () => {
  const p = paginate(25, 10, 3);
  assert.equal(p.itemsOnPage, 5);
  assert.equal(p.startIndex, 20);
  assert.equal(p.endIndex, 25);
  assert.equal(p.hasNext, false);
  assert.equal(p.hasPrev, true);
});

test("page is clamped into range on both ends", () => {
  assert.equal(paginate(25, 10, 99).page, 3);
  assert.equal(paginate(25, 10, 0).page, 1);
  assert.equal(paginate(25, 10, -100).page, 1);
});

test("slice indices tile the list without gaps or overlap", () => {
  const size = 7, total = 30;
  const count = paginate(total, size, 1).pageCount;
  let covered = 0;
  for (let pg = 1; pg <= count; pg++) {
    const p = paginate(total, size, pg);
    assert.equal(p.startIndex, covered);
    covered = p.endIndex;
  }
  assert.equal(covered, total); // every item covered exactly once
});

test("fails closed on invalid sizing", () => {
  assert.throws(() => paginate(-1, 10, 1), RangeError);
  assert.throws(() => paginate(10, 0, 1), RangeError);
  assert.throws(() => paginate(1.5, 10, 1), RangeError);
});
