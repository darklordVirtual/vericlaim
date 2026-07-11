// SPDX-License-Identifier: Apache-2.0
// groupBy — partition an array into buckets keyed by a projection function.
//
// A pre-verified claimlib code artifact: each item is placed into the bucket
// named by key(item), and within every bucket the items keep their original
// input order (a stable partition). Zero dependencies, erasable-syntax-only
// (runs under `node <file>.ts`). The claim that it groups correctly and
// order-preservingly is backed by a committed evidence artifact; vendoring
// carries that claim with it.

/**
 * Group `items` by the string key produced by `key`.
 *
 * Returns an ordinary object mapping each distinct key to the array of items
 * that produced it. Insertion order within each bucket matches input order, so
 * the grouping is stable, and buckets appear in first-seen key order.
 *
 * Items are accumulated in a Map (safe for every string key, including
 * "__proto__") and then materialised onto the result with defineProperty, so a
 * data-driven key such as "__proto__" becomes an ordinary own bucket instead of
 * mutating the prototype chain — no prototype-pollution footgun.
 */
export const groupBy = <T>(items: T[], key: (t: T) => string): Record<string, T[]> => {
  const buckets = new Map<string, T[]>();
  for (const item of items) {
    const k = key(item);
    const bucket = buckets.get(k);
    if (bucket === undefined) {
      buckets.set(k, [item]);
    } else {
      bucket.push(item);
    }
  }
  const out: Record<string, T[]> = {};
  for (const [k, v] of buckets) {
    Object.defineProperty(out, k, {
      value: v,
      writable: true,
      enumerable: true,
      configurable: true,
    });
  }
  return out;
};
