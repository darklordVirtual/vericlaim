// SPDX-License-Identifier: Apache-2.0
// Evidence for CLAIM-LIB-USEUNDOREDO-001. Drives the pure undo/redo core through
// a fixed action sequence and compares the resulting {present, canUndo, canRedo}
// after each step against independently hand-computed expected values (written
// by reasoning about undo/redo semantics, NOT by calling the module). Prints the
// metrics JSON on one line. Deterministic under `node`.
import {
  initHistory,
  push,
  undo,
  redo,
  canUndo,
  canRedo,
  type History,
} from "./undoredo.logic.ts";

type Op = { op: "set"; value: number } | { op: "undo" } | { op: "redo" };
// Expected snapshot after applying the op, hand-computed from present=0 start.
type Expect = { present: number; canUndo: boolean; canRedo: boolean };
type Case = [string, Op, Expect];

// Start: {past:[], present:0, future:[]}. Each row's expected value is derived by
// hand from the standard editor undo model (a new set() forks and clears redo).
const cases: Case[] = [
  ["set 1",            { op: "set", value: 1 }, { present: 1, canUndo: true,  canRedo: false }],
  ["set 2",            { op: "set", value: 2 }, { present: 2, canUndo: true,  canRedo: false }],
  ["set 3",            { op: "set", value: 3 }, { present: 3, canUndo: true,  canRedo: false }],
  ["undo -> 2",        { op: "undo" },          { present: 2, canUndo: true,  canRedo: true  }],
  ["undo -> 1",        { op: "undo" },          { present: 1, canUndo: true,  canRedo: true  }],
  ["redo -> 2",        { op: "redo" },          { present: 2, canUndo: true,  canRedo: true  }],
  ["set 9 clears redo",{ op: "set", value: 9 }, { present: 9, canUndo: true,  canRedo: false }],
  ["undo -> 2",        { op: "undo" },          { present: 2, canUndo: true,  canRedo: true  }],
  ["undo -> 1",        { op: "undo" },          { present: 1, canUndo: true,  canRedo: true  }],
  ["undo -> 0 (base)", { op: "undo" },          { present: 0, canUndo: false, canRedo: true  }],
  ["undo no-op at base",{ op: "undo" },         { present: 0, canUndo: false, canRedo: true  }],
  ["redo -> 1",        { op: "redo" },          { present: 1, canUndo: true,  canRedo: true  }],
];

const apply = (s: History<number>, op: Op): History<number> => {
  if (op.op === "set") return push(s, op.value);
  if (op.op === "undo") return undo(s);
  return redo(s);
};

let state = initHistory<number>(0);
let correct = 0;
for (const [, op, expected] of cases) {
  state = apply(state, op);
  const got: Expect = {
    present: state.present,
    canUndo: canUndo(state),
    canRedo: canRedo(state),
  };
  if (JSON.stringify(got) === JSON.stringify(expected)) correct++;
}

process.stdout.write(
  JSON.stringify({
    schema: "claimlib_useundoredo_v1",
    module: "useUndoRedo",
    n_cases: cases.length,
    correct,
    errors: cases.length - correct,
  }) + "\n",
);
