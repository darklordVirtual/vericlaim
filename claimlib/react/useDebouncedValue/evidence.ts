// SPDX-License-Identifier: Apache-2.0
// Evidence for CLAIM-LIB-USEDEBOUNCED-001. Exercises the pure trailing-debounce
// core over a fixed battery of event traces whose expected emissions are
// hand-computed from the trailing-debounce definition (a value emits delayMs
// after an event iff no further event arrives within the window) — computed
// INDEPENDENTLY of the module, never from emitDebounced itself. Deterministic
// under `node`; prints exactly one line of metrics JSON.
import { emitDebounced, type DebounceEvent } from "./debounce.logic.ts";

type Case = [string, ReadonlyArray<DebounceEvent<string>>, number, Array<[number, string]>];

// [label, events, delayMs, expectedEmissions] — expected written by hand.
const cases: Case[] = [
  ["empty trace emits nothing", [], 100, []],
  ["single event fires after delay", [[50, "x"]], 100, [[150, "x"]]],
  ["rapid burst collapses to last value",
    [[0, "a"], [10, "b"], [20, "c"]], 100, [[120, "c"]]],
  ["events spaced >= delay each emit",
    [[0, "a"], [200, "b"], [400, "c"]], 100, [[100, "a"], [300, "b"], [500, "c"]]],
  ["burst then long gap: dropped, kept, final",
    [[0, "a"], [10, "b"], [500, "c"]], 100, [[110, "b"], [600, "c"]]],
  ["gap exactly delay counts as fired",
    [[0, "a"], [100, "b"]], 100, [[100, "a"], [200, "b"]]],
  ["gap one below delay is coalesced",
    [[0, "a"], [99, "b"]], 100, [[199, "b"]]],
  ["typing keystrokes collapse to final word",
    [[0, "h"], [50, "he"], [90, "hel"], [130, "hell"], [170, "hello"]], 200, [[370, "hello"]]],
  ["two separate bursts each emit their last",
    [[0, "a"], [20, "b"], [300, "c"], [320, "d"]], 100, [[120, "b"], [420, "d"]]],
];

let correct = 0;
for (const [, events, delayMs, expected] of cases) {
  const got = emitDebounced(events, delayMs);
  if (JSON.stringify(got) === JSON.stringify(expected)) correct++;
}

process.stdout.write(JSON.stringify({
  schema: "claimlib_usedebounced_v1",
  module: "useDebouncedValue",
  n_cases: cases.length,
  correct,
  errors: cases.length - correct,
}) + "\n");
