// SPDX-License-Identifier: Apache-2.0
// deepEqual — structural deep equality for TypeScript.
//
// A pre-verified claimlib code artifact: compares two values by structure rather
// than reference. Primitives are compared with a NaN-aware rule (NaN equals NaN),
// Dates by their timestamp, arrays element-by-element, and plain objects by an
// identical key-set with recursively equal values. null and undefined are
// distinct, and values of differing runtime shape are never equal. Zero
// dependencies, erasable-syntax-only (runs under `node <file>.ts`). The claim that
// it matches a battery of hand-written expected outcomes is backed by a committed
// evidence artifact; vendoring carries that claim with it.
//
// NOTE: cyclic structures are out of scope (a self-referential input will recurse
// until the stack overflows); callers must not pass cyclic graphs.

const isPlainObject = (v: unknown): v is Record<string, unknown> =>
  typeof v === "object" &&
  v !== null &&
  !Array.isArray(v) &&
  !(v instanceof Date);

/** Structural deep equality. Returns true iff a and b are the same by structure. */
export const deepEqual = (a: unknown, b: unknown): boolean => {
  // Fast path: identical reference or identical primitive (excludes NaN, since
  // NaN !== NaN — handled below).
  if (a === b) return true;

  // NaN is the only value not equal to itself; treat NaN as equal to NaN.
  if (typeof a === "number" && typeof b === "number") {
    return Number.isNaN(a) && Number.isNaN(b);
  }

  // From here any equality requires both sides to be non-null objects.
  if (typeof a !== "object" || typeof b !== "object" || a === null || b === null) {
    return false;
  }

  // Dates compare by timestamp.
  if (a instanceof Date || b instanceof Date) {
    return a instanceof Date && b instanceof Date && a.getTime() === b.getTime();
  }

  // Arrays compare by length then element-wise; an array is never equal to a
  // non-array object.
  if (Array.isArray(a) || Array.isArray(b)) {
    if (!Array.isArray(a) || !Array.isArray(b)) return false;
    if (a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) {
      if (!deepEqual(a[i], b[i])) return false;
    }
    return true;
  }

  // Plain objects: identical key-set and recursively equal values.
  if (isPlainObject(a) && isPlainObject(b)) {
    const ak = Object.keys(a);
    const bk = Object.keys(b);
    if (ak.length !== bk.length) return false;
    for (const k of ak) {
      if (!Object.prototype.hasOwnProperty.call(b, k)) return false;
      if (!deepEqual(a[k], b[k])) return false;
    }
    return true;
  }

  return false;
};
