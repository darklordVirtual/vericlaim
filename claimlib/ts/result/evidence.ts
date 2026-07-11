// SPDX-License-Identifier: Apache-2.0
// Evidence for CLAIM-LIB-RESULT-001. Exercises the Result combinators over a
// fixed battery whose expected outcomes are written out independently (not read
// back from the module), and prints the metrics JSON on stdout. Deterministic;
// `node claimlib/ts/result/evidence.ts` produces the same line every run.
import { ok, err, map, mapErr, andThen, unwrapOr, isOk, isErr, fromThrowing } from "./result.ts";

// [label, actual, expected] — expected values are hand-written references.
const cases: Array<[string, unknown, unknown]> = [
  ["map over ok doubles", map(ok<number>(21), (x) => x * 2), { ok: true, value: 42 }],
  ["map over err passes through", map(err<string, number>("boom"), (x: number) => x * 2), { ok: false, error: "boom" }],
  ["mapErr transforms error", mapErr(err<number, number>(2), (e) => e * 10), { ok: false, error: 20 }],
  ["mapErr leaves ok", mapErr(ok<number, number>(5), (e) => e * 10), { ok: true, value: 5 }],
  ["andThen chains ok", andThen(ok<number>(2), (x) => ok(x + 1)), { ok: true, value: 3 }],
  ["andThen short-circuits err", andThen(err<string, number>("x"), (x: number) => ok(x + 1)), { ok: false, error: "x" }],
  ["unwrapOr returns value on ok", unwrapOr(ok<number>(3), 7), 3],
  ["unwrapOr returns fallback on err", unwrapOr(err<string, number>("e"), 7), 7],
  ["isOk true for ok", isOk(ok(1)), true],
  ["isErr true for err", isErr(err("e")), true],
  ["fromThrowing captures success", fromThrowing(() => 10), { ok: true, value: 10 }],
  ["fromThrowing captures throw", (() => { const r = fromThrowing(() => { throw new Error("nope"); }); return r.ok; })(), false],
];

let correct = 0;
for (const [, actual, expected] of cases) {
  if (JSON.stringify(actual) === JSON.stringify(expected)) correct++;
}

process.stdout.write(JSON.stringify({
  schema: "claimlib_result_v1",
  module: "result",
  n_cases: cases.length,
  correct,
  errors: cases.length - correct,
}) + "\n");
