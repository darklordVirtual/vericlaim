// SPDX-License-Identifier: Apache-2.0
// Evidence for CLAIM-LIB-USEPAGINATION-001. Exercises the pure pagination core
// over a fixed battery with independently hand-written expected windows, and
// prints the metrics JSON. Deterministic under `node`.
import { paginate } from "./pagination.logic.ts";

type Case = [string, [number, number, number], Record<string, unknown>];

// [label, [total, pageSize, page], expected] — expected written by hand.
const cases: Case[] = [
  ["empty list", [0, 10, 1],
    { page: 0, pageCount: 0, pageSize: 10, total: 0, startIndex: 0, endIndex: 0, itemsOnPage: 0, hasPrev: false, hasNext: false }],
  ["first of three pages", [25, 10, 1],
    { page: 1, pageCount: 3, pageSize: 10, total: 25, startIndex: 0, endIndex: 10, itemsOnPage: 10, hasPrev: false, hasNext: true }],
  ["middle page", [25, 10, 2],
    { page: 2, pageCount: 3, pageSize: 10, total: 25, startIndex: 10, endIndex: 20, itemsOnPage: 10, hasPrev: true, hasNext: true }],
  ["last partial page", [25, 10, 3],
    { page: 3, pageCount: 3, pageSize: 10, total: 25, startIndex: 20, endIndex: 25, itemsOnPage: 5, hasPrev: true, hasNext: false }],
  ["page above range clamps to last", [25, 10, 99],
    { page: 3, pageCount: 3, pageSize: 10, total: 25, startIndex: 20, endIndex: 25, itemsOnPage: 5, hasPrev: true, hasNext: false }],
  ["page below range clamps to first", [25, 10, 0],
    { page: 1, pageCount: 3, pageSize: 10, total: 25, startIndex: 0, endIndex: 10, itemsOnPage: 10, hasPrev: false, hasNext: true }],
  ["single full page", [10, 10, 1],
    { page: 1, pageCount: 1, pageSize: 10, total: 10, startIndex: 0, endIndex: 10, itemsOnPage: 10, hasPrev: false, hasNext: false }],
  ["exact multiple, last page full", [20, 10, 2],
    { page: 2, pageCount: 2, pageSize: 10, total: 20, startIndex: 10, endIndex: 20, itemsOnPage: 10, hasPrev: true, hasNext: false }],
];

let correct = 0;
let throwsCorrect = 0;
for (const [, [total, size, page], expected] of cases) {
  if (JSON.stringify(paginate(total, size, page)) === JSON.stringify(expected)) correct++;
}
// Fail-closed checks: bad sizing must throw.
for (const bad of [[-1, 10, 1], [10, 0, 1], [10, -5, 1], [1.5, 10, 1]] as Array<[number, number, number]>) {
  try { paginate(bad[0], bad[1], bad[2]); } catch { throwsCorrect++; }
}

process.stdout.write(JSON.stringify({
  schema: "claimlib_usepagination_v1",
  module: "usePagination",
  n_cases: cases.length,
  correct,
  errors: cases.length - correct,
  invalid_inputs_rejected: throwsCorrect,
}) + "\n");
