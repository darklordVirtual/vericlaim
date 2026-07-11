// SPDX-License-Identifier: Apache-2.0
// useDebouncedValue.tsx — a drop-in React hook, a thin binding over the trailing
// debounce timing model that is unit-tested in debounce.logic.ts. Vendor both
// files; the claim is on the core simulator, not on React rendering.
import { useState, useEffect } from "react";

/**
 * Returns a debounced copy of `value` that only updates after `value` has
 * stopped changing for `delayMs`. On every change a fresh setTimeout(delayMs)
 * is scheduled and the previous one is cleared, so rapid updates collapse to
 * the last value — exactly the trailing-debounce model proven in
 * debounce.logic.ts (each render's value plays the role of one timed event).
 */
export function useDebouncedValue<V>(value: V, delayMs: number): V {
  const [debounced, setDebounced] = useState<V>(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(id);
  }, [value, delayMs]);
  return debounced;
}
