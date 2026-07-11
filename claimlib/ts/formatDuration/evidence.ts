// SPDX-License-Identifier: Apache-2.0
// Evidence for CLAIM-LIB-FORMATDURATION-001. Exercises formatDuration over a
// fixed battery whose expected strings are hand-written references computed by
// eye from the unit definitions (d=86400s, h=3600s, m=60s, s), NOT read back
// from the module. Negative inputs are expected to throw RangeError (encoded as
// the sentinel "RangeError"). Prints the metrics JSON on stdout. Deterministic;
// `node claimlib/ts/formatDuration/evidence.ts` produces the same line every run.
import { formatDuration } from "./formatDuration.ts";

// Run formatDuration, mapping a thrown RangeError to the sentinel string so the
// throw contract can be checked in the same table as the formatting contract.
const run = (ms: number): string => {
  try {
    return formatDuration(ms);
  } catch (e) {
    if (e instanceof RangeError) return "RangeError";
    return "OtherError";
  }
};

// [label, inputMs, expected] — expected values are hand-written references.
const cases: Array<[string, number, string]> = [
  ["zero renders 0s", 0, "0s"],
  ["sub-second truncates to 0s", 999, "0s"],
  ["exactly one second", 1000, "1s"],
  ["1.5s truncates to 1s", 1500, "1s"],
  ["59 seconds", 59000, "59s"],
  ["one minute drops zero seconds", 60000, "1m"],
  ["one minute one second", 61000, "1m 1s"],
  ["1m 59s", 119000, "1m 59s"],
  ["59m 59s", 3599000, "59m 59s"],
  ["one hour drops zero m/s", 3600000, "1h"],
  ["1h 0m 1s drops zero minute", 3601000, "1h 1s"],
  ["1h 1m 0s drops zero second", 3660000, "1h 1m"],
  ["1h 1m 1s full", 3661000, "1h 1m 1s"],
  ["two hours", 7200000, "2h"],
  ["one day drops zero h/m/s", 86400000, "1d"],
  ["1d 0h 1m 1s drops zero hour", 86461000, "1d 1m 1s"],
  ["1d 1h 1m 1s full", 90061000, "1d 1h 1m 1s"],
  ["1d 2h 3m 4s", 93784000, "1d 2h 3m 4s"],
  ["two days", 172800000, "2d"],
  ["negative throws RangeError", -1, "RangeError"],
  ["large negative throws RangeError", -90061000, "RangeError"],
];

let correct = 0;
for (const [, input, expected] of cases) {
  if (run(input) === expected) correct++;
}

process.stdout.write(JSON.stringify({
  schema: "claimlib_formatDuration_v1",
  module: "formatDuration",
  n_cases: cases.length,
  correct,
  errors: cases.length - correct,
}) + "\n");
