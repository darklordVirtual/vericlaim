// SPDX-License-Identifier: Apache-2.0
// cx — a dependency-free classnames combiner for TypeScript.
//
// A pre-verified claimlib code artifact: join truthy class tokens from a mix of
// strings, numbers, nested arrays, and { className: boolean } objects into one
// space-separated string, skipping every falsy input. Zero dependencies,
// erasable-syntax-only (runs under `node <file>.ts`). Document order is
// preserved and de-duplication is intentionally NOT performed. The claim that
// it produces the expected string is backed by a committed evidence artifact;
// vendoring carries that claim with it.

/**
 * Combine class tokens into a single space-separated string.
 *
 * Accepts strings, numbers, nested arrays (recursively flattened), and plain
 * objects whose keys are emitted when their value is truthy. Falsy values
 * (false, null, undefined, 0, NaN, "") are skipped. A numeric 0 as a bare token
 * is falsy and skipped; a non-zero number is stringified and included. Order is
 * preserved; duplicates are NOT removed.
 */
export const cx = (...inputs: unknown[]): string => {
  const out: string[] = [];
  push(inputs, out);
  return out.join(" ");
};

const push = (input: unknown, out: string[]): void => {
  if (input === null || input === undefined) return;
  const t = typeof input;
  if (t === "string") {
    if (input !== "") out.push(input as string);
    return;
  }
  if (t === "number") {
    // Falsy numbers (0, NaN) are skipped; everything else is stringified.
    if (input && Number.isFinite(input as number)) out.push(String(input));
    return;
  }
  if (t === "boolean") return; // true/false never contribute a token
  if (Array.isArray(input)) {
    for (const item of input) push(item, out);
    return;
  }
  if (t === "object") {
    for (const key of Object.keys(input as Record<string, unknown>)) {
      if ((input as Record<string, unknown>)[key]) out.push(key);
    }
    return;
  }
  // Any other type (function, symbol, bigint) contributes nothing.
};
