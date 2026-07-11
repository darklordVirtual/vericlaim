// SPDX-License-Identifier: Apache-2.0
// Evidence for CLAIM-LIB-USESTEPPER-001. Exercises the pure stepper core over a
// fixed battery with independently hand-computed clamped state, and prints the
// metrics JSON. Deterministic under `node`.
import { stepper } from "./stepper.logic.ts";

type Case = [string, [number, number], Record<string, unknown>];

// [label, [stepCount, index], expected] — expected values written by hand,
// independent of the module (index clamped to [0, stepCount-1], progress =
// index/(stepCount-1) rounded to 4 dp, or 0 for a single step).
const cases: Case[] = [
  ["single step is both first and last", [1, 0],
    { index: 0, stepCount: 1, isFirst: true, isLast: true, progress: 0, nextIndex: 0, prevIndex: 0 }],
  ["first of five", [5, 0],
    { index: 0, stepCount: 5, isFirst: true, isLast: false, progress: 0, nextIndex: 1, prevIndex: 0 }],
  ["middle of five (half progress)", [5, 2],
    { index: 2, stepCount: 5, isFirst: false, isLast: false, progress: 0.5, nextIndex: 3, prevIndex: 1 }],
  ["last of five (full progress)", [5, 4],
    { index: 4, stepCount: 5, isFirst: false, isLast: true, progress: 1, nextIndex: 4, prevIndex: 3 }],
  ["index above range clamps to last", [5, 99],
    { index: 4, stepCount: 5, isFirst: false, isLast: true, progress: 1, nextIndex: 4, prevIndex: 3 }],
  ["index below range clamps to first", [5, -3],
    { index: 0, stepCount: 5, isFirst: true, isLast: false, progress: 0, nextIndex: 1, prevIndex: 0 }],
  ["two steps, first", [2, 0],
    { index: 0, stepCount: 2, isFirst: true, isLast: false, progress: 0, nextIndex: 1, prevIndex: 0 }],
  ["two steps, last", [2, 1],
    { index: 1, stepCount: 2, isFirst: false, isLast: true, progress: 1, nextIndex: 1, prevIndex: 0 }],
  ["three steps, middle (half)", [3, 1],
    { index: 1, stepCount: 3, isFirst: false, isLast: false, progress: 0.5, nextIndex: 2, prevIndex: 0 }],
  ["four steps, second (one third)", [4, 1],
    { index: 1, stepCount: 4, isFirst: false, isLast: false, progress: 0.3333, nextIndex: 2, prevIndex: 0 }],
  ["four steps, third (two thirds)", [4, 2],
    { index: 2, stepCount: 4, isFirst: false, isLast: false, progress: 0.6667, nextIndex: 3, prevIndex: 1 }],
];

let correct = 0;
for (const [, [stepCount, index], expected] of cases) {
  if (JSON.stringify(stepper(stepCount, index)) === JSON.stringify(expected)) correct++;
}

process.stdout.write(JSON.stringify({
  schema: "claimlib_usestepper_v1",
  module: "useStepper",
  n_cases: cases.length,
  correct,
  errors: cases.length - correct,
}) + "\n");
