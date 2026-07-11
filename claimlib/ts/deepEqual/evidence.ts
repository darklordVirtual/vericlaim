// SPDX-License-Identifier: Apache-2.0
// Evidence for CLAIM-LIB-DEEPEQUAL-001. Runs deepEqual over a fixed battery of
// [a, b, expected] rows whose expected boolean is hand-written independently of
// the module (structural reasoning by inspection, not read back from deepEqual),
// and prints the metrics JSON on stdout. Deterministic; `node evidence.ts`
// produces the same line every run.
import { deepEqual } from "./deepEqual.ts";

// [label, a, b, expected] — expected is a hand-written known-good boolean.
const cases: Array<[string, unknown, unknown, boolean]> = [
  // Primitives
  ["equal numbers", 1, 1, true],
  ["different numbers", 1, 2, false],
  ["equal strings", "x", "x", true],
  ["different strings", "x", "y", false],
  ["true === true", true, true, true],
  ["true vs false", true, false, false],
  ["number vs string", 1, "1", false],
  ["zero vs false", 0, false, false],
  ["empty string vs zero", "", 0, false],

  // NaN handling
  ["NaN equals NaN", NaN, NaN, true],
  ["NaN vs number", NaN, 1, false],

  // null / undefined
  ["null equals null", null, null, true],
  ["undefined equals undefined", undefined, undefined, true],
  ["null distinct from undefined", null, undefined, false],
  ["null vs object", null, {}, false],
  ["undefined vs zero", undefined, 0, false],

  // Arrays
  ["equal arrays", [1, 2, 3], [1, 2, 3], true],
  ["arrays different length", [1, 2], [1, 2, 3], false],
  ["arrays different element", [1, 2, 3], [1, 9, 3], false],
  ["empty arrays equal", [], [], true],
  ["nested arrays equal", [[1], [2, 3]], [[1], [2, 3]], true],
  ["nested arrays differ", [[1], [2, 3]], [[1], [2, 4]], false],
  ["array vs object", [1, 2], { 0: 1, 1: 2 }, false],

  // Plain objects
  ["equal objects", { a: 1, b: 2 }, { a: 1, b: 2 }, true],
  ["objects key order irrelevant", { a: 1, b: 2 }, { b: 2, a: 1 }, true],
  ["objects different value", { a: 1, b: 2 }, { a: 1, b: 3 }, false],
  ["objects extra key", { a: 1 }, { a: 1, b: 2 }, false],
  ["objects missing key", { a: 1, b: 2 }, { a: 1 }, false],
  ["objects different key name", { a: 1 }, { b: 1 }, false],
  ["empty objects equal", {}, {}, true],
  ["nested objects equal", { a: { b: { c: 1 } } }, { a: { b: { c: 1 } } }, true],
  ["nested objects differ", { a: { b: { c: 1 } } }, { a: { b: { c: 2 } } }, false],
  ["object with array value equal", { xs: [1, 2] }, { xs: [1, 2] }, true],
  ["object with array value differ", { xs: [1, 2] }, { xs: [1, 3] }, false],
  ["key present with undefined vs absent", { a: undefined }, {}, false],

  // Dates
  ["equal dates", new Date(0), new Date(0), true],
  ["different dates", new Date(0), new Date(1000), false],
  ["date vs number", new Date(0), 0, false],
  ["date vs object", new Date(0), {}, false],
  ["dates same instant different construction", new Date("2020-01-01T00:00:00Z"), new Date(1577836800000), true],

  // Mixed / edge
  ["object vs primitive", { a: 1 }, 1, false],
  ["array vs primitive", [1], 1, false],
];

let correct = 0;
for (const [, a, b, expected] of cases) {
  if (deepEqual(a, b) === expected) correct++;
}

process.stdout.write(JSON.stringify({
  schema: "claimlib_deepEqual_v1",
  module: "deepEqual",
  n_cases: cases.length,
  correct,
  errors: cases.length - correct,
}) + "\n");
