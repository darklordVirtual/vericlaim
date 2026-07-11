// SPDX-License-Identifier: Apache-2.0
// Evidence for CLAIM-LIB-CX-001. Exercises the cx classnames combiner over a
// fixed battery whose expected output strings are hand-written references
// (independent of the module, not read back from it), and prints the metrics
// JSON on stdout. Deterministic; `node claimlib/ts/cx/evidence.ts` produces the
// same line every run.
import { cx } from "./cx.ts";

// [label, actual, expected] — expected strings are hand-written literals.
const cases: Array<[string, string, string]> = [
  ["spec example (mixed)", cx("a", false, ["b", { c: true, d: false }], undefined, 0, "e"), "a b c e"],
  ["plain strings", cx("a", "b", "c"), "a b c"],
  ["all falsy -> empty", cx(false, null, undefined, 0, "", NaN), ""],
  ["no args -> empty", cx(), ""],
  ["object include truthy keys", cx({ foo: true, bar: false, baz: 1 }), "foo baz"],
  ["nested arrays flatten", cx(["a", ["b", ["c"]]], "d"), "a b c d"],
  ["array with objects", cx([{ x: true }, { y: false, z: true }]), "x z"],
  ["numbers: nonzero kept, zero dropped", cx(1, 0, 2, "n"), "1 2 n"],
  ["duplicates preserved (no de-dup)", cx("a", "a", { a: true }), "a a a"],
  ["boolean true contributes nothing", cx(true, "a", true), "a"],
  ["empty strings skipped", cx("", "a", "", "b"), "a b"],
  ["order preserved across kinds", cx("first", ["second"], { third: true }), "first second third"],
  ["object with truthy string value", cx({ active: "yes", hidden: "" }), "active"],
  ["deeply nested with falsy holes", cx(["a", [false, "b", [null, "c"]]]), "a b c"],
];

let correct = 0;
for (const [, actual, expected] of cases) {
  if (actual === expected) correct++;
}

process.stdout.write(JSON.stringify({
  schema: "claimlib_cx_v1",
  module: "cx",
  n_cases: cases.length,
  correct,
  errors: cases.length - correct,
}) + "\n");
