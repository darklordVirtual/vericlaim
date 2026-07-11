// SPDX-License-Identifier: Apache-2.0
// chunk — split an array into fixed-size chunks.
//
// A pre-verified claimlib code artifact: `chunk(arr, size)` partitions `arr`
// into consecutive sub-arrays of length `size`, with a final shorter chunk when
// the length is not an exact multiple. A `size` below 1 is rejected with a
// RangeError rather than looping forever or silently misbehaving. Zero
// dependencies, erasable-syntax-only (runs under `node <file>.ts`). The claim
// that it produces the expected partitions is backed by a committed evidence
// artifact; vendoring carries that claim with it.

/** Split `arr` into consecutive chunks of length `size` (last chunk may be shorter). Throws RangeError if size < 1. */
export const chunk = <T>(arr: T[], size: number): T[][] => {
  if (!Number.isInteger(size) || size < 1) {
    throw new RangeError(`chunk size must be an integer >= 1, got ${size}`);
  }
  const out: T[][] = [];
  for (let i = 0; i < arr.length; i += size) {
    out.push(arr.slice(i, i + size));
  }
  return out;
};
