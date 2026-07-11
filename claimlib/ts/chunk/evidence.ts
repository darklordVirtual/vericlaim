// SPDX-License-Identifier: Apache-2.0
// Evidence for CLAIM-LIB-CHUNK-001. Exercises chunk() over a fixed battery whose
// expected partitions are hand-written independently of the module (not read
// back from chunk itself), plus a set of invalid sizes that must throw
// RangeError. Prints the metrics JSON on stdout. Deterministic;
// `node claimlib/ts/chunk/evidence.ts` produces the same line every run.
import { chunk } from "./chunk.ts";

// [label, actual, expected] — expected values are hand-written references.
const cases: Array<[string, unknown, unknown]> = [
  ["7 items into 3s", chunk([1, 2, 3, 4, 5, 6, 7], 3), [[1, 2, 3], [4, 5, 6], [7]]],
  ["empty array", chunk([] as number[], 3), []],
  ["exact multiple", chunk([1, 2, 3, 4], 2), [[1, 2], [3, 4]]],
  ["size 1 is singletons", chunk(["a", "b", "c"], 1), [["a"], ["b"], ["c"]]],
  ["size larger than length", chunk([1, 2], 5), [[1, 2]]],
  ["size equals length", chunk([1, 2, 3], 3), [[1, 2, 3]]],
  ["single element", chunk([9], 3), [[9]]],
  ["strings into 2s with remainder", chunk(["a", "b", "c", "d", "e"], 2), [["a", "b"], ["c", "d"], ["e"]]],
];

let correct = 0;
for (const [, actual, expected] of cases) {
  if (JSON.stringify(actual) === JSON.stringify(expected)) correct++;
}

// Invalid sizes that must be rejected with a RangeError.
const invalidSizes = [0, -1, -5, 1.5];
let invalidRejected = 0;
for (const s of invalidSizes) {
  try {
    chunk([1, 2, 3], s);
  } catch (e) {
    if (e instanceof RangeError) invalidRejected++;
  }
}

process.stdout.write(JSON.stringify({
  schema: "claimlib_chunk_v1",
  module: "chunk",
  n_cases: cases.length,
  correct,
  errors: cases.length - correct,
  invalid_inputs_rejected: invalidRejected,
}) + "\n");
