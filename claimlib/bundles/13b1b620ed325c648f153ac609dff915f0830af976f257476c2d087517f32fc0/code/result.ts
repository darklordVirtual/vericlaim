// SPDX-License-Identifier: Apache-2.0
// Result<T, E> — typed, exception-free error handling for TypeScript.
//
// A pre-verified claimlib code artifact: a value is either Ok<T> or Err<E>, and
// you thread it through map / mapErr / andThen instead of throwing. Zero
// dependencies, erasable-syntax-only (runs under `node <file>.ts`). The claim
// that its combinators obey the expected outcomes is backed by a committed
// evidence artifact; vendoring carries that claim with it.

export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

/** Wrap a success value. */
export const ok = <T, E = never>(value: T): Result<T, E> => ({ ok: true, value });

/** Wrap a failure value. */
export const err = <E, T = never>(error: E): Result<T, E> => ({ ok: false, error });

export const isOk = <T, E>(r: Result<T, E>): boolean => r.ok;
export const isErr = <T, E>(r: Result<T, E>): boolean => !r.ok;

/** Transform the success value; an Err passes through untouched. */
export const map = <T, U, E>(r: Result<T, E>, f: (t: T) => U): Result<U, E> =>
  r.ok ? ok(f(r.value)) : r;

/** Transform the error value; an Ok passes through untouched. */
export const mapErr = <T, E, F>(r: Result<T, E>, f: (e: E) => F): Result<T, F> =>
  r.ok ? r : err(f(r.error));

/** Chain a fallible step; short-circuits on the first Err (monadic bind). */
export const andThen = <T, U, E>(
  r: Result<T, E>,
  f: (t: T) => Result<U, E>,
): Result<U, E> => (r.ok ? f(r.value) : r);

/** Extract the value or fall back to a default on Err. */
export const unwrapOr = <T, E>(r: Result<T, E>, fallback: T): T =>
  r.ok ? r.value : fallback;

/** Run a throwing function and capture the outcome as a Result. */
export const fromThrowing = <T>(f: () => T): Result<T, unknown> => {
  try {
    return ok(f());
  } catch (e) {
    return err(e);
  }
};
