// SPDX-License-Identifier: Apache-2.0
// Evidence for CLAIM-LIB-GROUPBY-001. Exercises groupBy over a fixed battery
// whose expected records are hand-written independently of the module (never
// read back from groupBy itself), and prints the metrics JSON on stdout.
// Deterministic: `node claimlib/ts/groupBy/evidence.ts` prints the same line
// every run. Comparison is by JSON.stringify, so it also pins the key order
// (first-seen) and within-bucket input order that the spec requires.
import { groupBy } from "./groupBy.ts";

// Each case: [label, actual, expected].
// The `expected` literals are written out by hand from the input; keys appear
// in first-seen order and items within a bucket appear in input order, which is
// exactly what JSON.stringify then encodes and compares.
const cases: Array<[string, unknown, unknown]> = [
  [
    "parity of small integers",
    groupBy([1, 2, 3, 4, 5, 6], (n) => (n % 2 === 0 ? "even" : "odd")),
    { odd: [1, 3, 5], even: [2, 4, 6] },
  ],
  [
    "first letter of words preserves order",
    groupBy(["ant", "bee", "art", "bat", "cat"], (w) => w[0]),
    { a: ["ant", "art"], b: ["bee", "bat"], c: ["cat"] },
  ],
  [
    "empty input yields empty object",
    groupBy([] as number[], (n) => String(n)),
    {},
  ],
  [
    "single element single bucket",
    groupBy([42], (n) => "the-answer"),
    { "the-answer": [42] },
  ],
  [
    "all items same key keep order",
    groupBy([3, 1, 2], () => "k"),
    { k: [3, 1, 2] },
  ],
  [
    "every item distinct key",
    groupBy(["x", "y", "z"], (s) => s),
    { x: ["x"], y: ["y"], z: ["z"] },
  ],
  [
    "group objects by field",
    groupBy(
      [
        { id: 1, team: "red" },
        { id: 2, team: "blue" },
        { id: 3, team: "red" },
      ],
      (o) => o.team,
    ),
    {
      red: [
        { id: 1, team: "red" },
        { id: 3, team: "red" },
      ],
      blue: [{ id: 2, team: "blue" }],
    },
  ],
  [
    "numeric key coerced to string",
    groupBy([10, 20, 11, 21, 12], (n) => String(Math.floor(n / 10))),
    { "1": [10, 11, 12], "2": [20, 21] },
  ],
  [
    "key order follows first appearance not sort",
    groupBy(["zebra", "apple", "zip", "ant"], (w) => w[0]),
    { z: ["zebra", "zip"], a: ["apple", "ant"] },
  ],
  [
    "dangerous __proto__ key is a normal bucket",
    groupBy(["a", "b", "a"], (s) => (s === "b" ? "__proto__" : "safe")),
    // Computed key so this is a real own "__proto__" property, not a
    // prototype assignment (which a bare `__proto__:` literal would be).
    { safe: ["a", "a"], ["__proto__"]: ["b"] },
  ],
];

let correct = 0;
for (const [, actual, expected] of cases) {
  if (JSON.stringify(actual) === JSON.stringify(expected)) correct++;
}

process.stdout.write(
  JSON.stringify({
    schema: "claimlib_groupby_v1",
    module: "groupBy",
    n_cases: cases.length,
    correct,
    errors: cases.length - correct,
  }) + "\n",
);
