// SPDX-License-Identifier: Apache-2.0
// async.logic.ts — the framework-agnostic core of the useAsync hook.
//
// The async request state machine lives here as a pure reducer, so it can be
// tested deterministically (run under `node`) without a DOM or React. The React
// binding (useAsync.tsx) is a thin wrapper over this — vendor both.

export type AsyncStatus = "idle" | "pending" | "success" | "error";

export interface AsyncState<T, E> {
  readonly status: AsyncStatus;
  readonly data: T | undefined;
  readonly error: E | undefined;
}

// Discriminated action union: start a request, resolve it with data, or reject
// it with an error. Erasable-syntax friendly (no enum/namespace).
export type AsyncAction<T, E> =
  | { readonly type: "start" }
  | { readonly type: "resolve"; readonly data: T }
  | { readonly type: "reject"; readonly error: E };

/** The neutral starting state before any request has begun. */
export const idleState = <T, E>(): AsyncState<T, E> => ({
  status: "idle",
  data: undefined,
  error: undefined,
});

/**
 * Pure async state machine. Transitions:
 *   start   -> pending, ALWAYS clears error (keeps prior data: stale-while-revalidate).
 *   resolve -> success, sets data, clears error.
 *   reject  -> error,   sets error (keeps prior data so callers can show stale content).
 * Unknown actions leave the state unchanged (defensive; keeps the reducer total).
 */
export const asyncReducer = <T, E>(
  state: AsyncState<T, E>,
  action: AsyncAction<T, E>,
): AsyncState<T, E> => {
  switch (action.type) {
    case "start":
      return { status: "pending", data: state.data, error: undefined };
    case "resolve":
      return { status: "success", data: action.data, error: undefined };
    case "reject":
      return { status: "error", data: state.data, error: action.error };
    default:
      return state;
  }
};
