// SPDX-License-Identifier: Apache-2.0
// debounce.logic.ts — the framework-agnostic core of the useDebouncedValue hook.
//
// The trailing-debounce timing model lives here as a PURE, deterministic
// simulator, so it can be unit-tested under `node` with no DOM, no React, and
// no real timers. The React binding (useDebouncedValue.tsx) is a thin wrapper
// over the same model built on setTimeout — vendor both.

export type DebounceEvent<V> = readonly [timeMs: number, value: V];

/**
 * Pure trailing-debounce simulator.
 *
 * Given a chronologically ordered trace of `events` (each `[timeMs, value]`)
 * and a `delayMs` quiet window, returns the emissions a trailing debounce
 * would produce: an event's value is emitted `delayMs` after that event ONLY
 * if no further event arrives within the window (i.e. the timer is not reset).
 *
 * Model: each incoming event (re)starts a timer for `delayMs`. If the next
 * event arrives strictly sooner than `delayMs` later, the pending timer is
 * cancelled and replaced, so that value is dropped. Otherwise the timer fires
 * at `eventTime + delayMs`, emitting that value, before the next window opens.
 * The final event always fires (nothing follows it). A gap of exactly `delayMs`
 * counts as fired (the timer elapses at the boundary): `nextTime - time >=
 * delayMs` emits. Rapid bursts therefore collapse to their last value; events
 * spaced at least `delayMs` apart each emit.
 *
 * The input is assumed sorted by time ascending. Fails closed on bad sizing.
 */
export const emitDebounced = <V>(
  events: ReadonlyArray<DebounceEvent<V>>,
  delayMs: number,
): Array<[number, V]> => {
  if (!Number.isInteger(delayMs) || delayMs < 1) {
    throw new RangeError(`delayMs must be a positive integer, got ${delayMs}`);
  }
  const out: Array<[number, V]> = [];
  for (let i = 0; i < events.length; i++) {
    const [time, value] = events[i];
    if (!Number.isFinite(time)) {
      throw new RangeError(`event time must be finite, got ${time} at index ${i}`);
    }
    if (i > 0 && time < events[i - 1][0]) {
      throw new RangeError(`events must be sorted by time; index ${i} goes backwards`);
    }
    const isLast = i === events.length - 1;
    // The timer fires (emits) iff nothing arrives before it elapses.
    if (isLast || events[i + 1][0] - time >= delayMs) {
      out.push([time + delayMs, value]);
    }
  }
  return out;
};
