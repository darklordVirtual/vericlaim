// SPDX-License-Identifier: Apache-2.0
// useUndoRedo.tsx — a drop-in React hook, a thin binding over the tested pure
// core in undoredo.logic.ts. Vendor both files; the claim is on the core.
import { useReducer, useMemo, useCallback } from "react";
import {
  initHistory,
  push,
  undo,
  redo,
  canUndo,
  canRedo,
  type History,
} from "./undoredo.logic.ts";

type Action<T> = { type: "set"; value: T } | { type: "undo" } | { type: "redo" };

function reducer<T>(state: History<T>, action: Action<T>): History<T> {
  switch (action.type) {
    case "set":
      return push(state, action.value);
    case "undo":
      return undo(state);
    case "redo":
      return redo(state);
    default:
      return state;
  }
}

export interface UseUndoRedo<T> {
  state: T;
  set: (value: T) => void;
  undo: () => void;
  redo: () => void;
  canUndo: boolean;
  canRedo: boolean;
}

/**
 * Undo/redo state for a single `initial` value. `set` commits a new value (and
 * clears the redo stack); `undo`/`redo` walk history. All transitions are
 * delegated to the pure core, so the reducer here holds no logic of its own.
 */
export function useUndoRedo<T>(initial: T): UseUndoRedo<T> {
  const [history, dispatch] = useReducer(reducer<T>, initial, initHistory);
  const set = useCallback((value: T) => dispatch({ type: "set", value }), []);
  const undoFn = useCallback(() => dispatch({ type: "undo" }), []);
  const redoFn = useCallback(() => dispatch({ type: "redo" }), []);
  return useMemo(
    () => ({
      state: history.present,
      set,
      undo: undoFn,
      redo: redoFn,
      canUndo: canUndo(history),
      canRedo: canRedo(history),
    }),
    [history, set, undoFn, redoFn],
  );
}
