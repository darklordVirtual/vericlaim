// SPDX-License-Identifier: Apache-2.0
// useAsync.tsx — a drop-in React hook, a thin binding over the tested pure core
// in async.logic.ts. Vendor both files; the claim is on the core reducer.
import { useReducer, useCallback } from "react";
import {
  asyncReducer,
  idleState,
  type AsyncState,
  type AsyncAction,
} from "./async.logic.ts";

export interface UseAsync<T, E> extends AsyncState<T, E> {
  readonly isIdle: boolean;
  readonly isPending: boolean;
  readonly isSuccess: boolean;
  readonly isError: boolean;
  run: (task: () => Promise<T>) => Promise<void>;
}

/**
 * Runs an async task and tracks its state through the pure reducer core.
 * `run` dispatches `start`, awaits the task, then dispatches `resolve`/`reject`.
 * All state transitions are delegated to `asyncReducer`, so the status/data/error
 * bookkeeping is exactly the framework-agnostic behaviour proven in evidence.
 */
export function useAsync<T, E = unknown>(): UseAsync<T, E> {
  const [state, dispatch] = useReducer(
    asyncReducer as (s: AsyncState<T, E>, a: AsyncAction<T, E>) => AsyncState<T, E>,
    undefined,
    idleState<T, E>,
  );

  const run = useCallback(async (task: () => Promise<T>) => {
    dispatch({ type: "start" });
    try {
      const data = await task();
      dispatch({ type: "resolve", data });
    } catch (error) {
      dispatch({ type: "reject", error: error as E });
    }
  }, []);

  return {
    ...state,
    isIdle: state.status === "idle",
    isPending: state.status === "pending",
    isSuccess: state.status === "success",
    isError: state.status === "error",
    run,
  };
}
