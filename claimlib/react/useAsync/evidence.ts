// SPDX-License-Identifier: Apache-2.0
// Evidence for CLAIM-LIB-USEASYNC-001. Exercises the pure async state machine
// (async.logic.ts) over a fixed transition table with independently hand-written
// expected next-states, and prints the metrics JSON. Deterministic under `node`.
import { asyncReducer, type AsyncState, type AsyncAction } from "./async.logic.ts";

type S = AsyncState<unknown, unknown>;
type A = AsyncAction<unknown, unknown>;
type Case = [string, S, A, S]; // [label, fromState, action, expectedNextState]

// Expected next-states written BY HAND from the documented transition rules,
// independently of the reducer under test (never expected = asyncReducer(...)).
const cases: Case[] = [
  ["idle + start -> pending (error cleared)",
    { status: "idle", data: undefined, error: undefined },
    { type: "start" },
    { status: "pending", data: undefined, error: undefined }],

  ["pending + resolve -> success (sets data)",
    { status: "pending", data: undefined, error: undefined },
    { type: "resolve", data: 42 },
    { status: "success", data: 42, error: undefined }],

  ["pending + reject -> error (sets error)",
    { status: "pending", data: undefined, error: undefined },
    { type: "reject", error: "boom" },
    { status: "error", data: undefined, error: "boom" }],

  ["error + start -> pending (clears prior error)",
    { status: "error", data: undefined, error: "boom" },
    { type: "start" },
    { status: "pending", data: undefined, error: undefined }],

  ["success + start -> pending (keeps stale data, clears error)",
    { status: "success", data: 7, error: undefined },
    { type: "start" },
    { status: "pending", data: 7, error: undefined }],

  ["error + resolve -> success (error cleared, data set)",
    { status: "error", data: undefined, error: "boom" },
    { type: "resolve", data: "ok" },
    { status: "success", data: "ok", error: undefined }],

  ["success + reject -> error (keeps stale data)",
    { status: "success", data: 5, error: undefined },
    { type: "reject", error: "e2" },
    { status: "error", data: 5, error: "e2" }],

  ["pending + resolve of falsy data -> success (data = 0)",
    { status: "pending", data: undefined, error: undefined },
    { type: "resolve", data: 0 },
    { status: "success", data: 0, error: undefined }],

  ["idle + reject -> error (error before any data)",
    { status: "idle", data: undefined, error: undefined },
    { type: "reject", error: "early" },
    { status: "error", data: undefined, error: "early" }],
];

let correct = 0;
for (const [, from, action, expected] of cases) {
  const next = asyncReducer(from, action);
  if (JSON.stringify(next) === JSON.stringify(expected)) correct++;
}

process.stdout.write(JSON.stringify({
  schema: "claimlib_useasync_v1",
  module: "useAsync",
  n_cases: cases.length,
  correct,
  errors: cases.length - correct,
}) + "\n");
