// SPDX-License-Identifier: Apache-2.0
// undoredo.logic.ts — the framework-agnostic core of the useUndoRedo hook.
//
// The entire undo/redo history model lives here as pure, immutable functions so
// it can be tested deterministically (run under `node`) without a DOM or React.
// The React binding (useUndoRedo.tsx) is a thin useReducer over this — vendor both.

/** Undo/redo history: a stack of past states, the present, and a redo stack. */
export interface History<T> {
  readonly past: readonly T[];
  readonly present: T;
  readonly future: readonly T[];
}

/** Seed a fresh history whose present is `present` and whose stacks are empty. */
export const initHistory = <T>(present: T): History<T> => ({
  past: [],
  present,
  future: [],
});

/** True when there is at least one earlier state to undo to. */
export const canUndo = <T>(state: History<T>): boolean => state.past.length > 0;

/** True when there is at least one undone state to redo to. */
export const canRedo = <T>(state: History<T>): boolean => state.future.length > 0;

/**
 * Commit a new present value. The old present is pushed onto `past` and the
 * redo stack (`future`) is cleared — a new edit forks history, discarding any
 * previously-undone branch. This is the standard editor undo model.
 */
export const push = <T>(state: History<T>, next: T): History<T> => ({
  past: [...state.past, state.present],
  present: next,
  future: [],
});

/**
 * Step back one state. The present moves to the front of `future`, and the most
 * recent past state becomes the present. A no-op (returns the same state) when
 * there is nothing to undo, so callers never fall off the end of history.
 */
export const undo = <T>(state: History<T>): History<T> => {
  if (state.past.length === 0) return state;
  const previous = state.past[state.past.length - 1];
  return {
    past: state.past.slice(0, -1),
    present: previous,
    future: [state.present, ...state.future],
  };
};

/**
 * Step forward one state, inverting `undo`. The present is pushed onto `past`
 * and the first `future` entry becomes the present. A no-op when there is
 * nothing to redo.
 */
export const redo = <T>(state: History<T>): History<T> => {
  if (state.future.length === 0) return state;
  const next = state.future[0];
  return {
    past: [...state.past, state.present],
    present: next,
    future: state.future.slice(1),
  };
};
