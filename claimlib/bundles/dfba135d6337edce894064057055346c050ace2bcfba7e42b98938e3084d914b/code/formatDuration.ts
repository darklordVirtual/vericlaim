// SPDX-License-Identifier: Apache-2.0
// formatDuration — human-readable compact duration formatting for TypeScript.
//
// A pre-verified claimlib code artifact: given a non-negative millisecond count,
// render it as a compact string like "0s", "1m 1s", "1h 1m 1s" or
// "1d 1h 1m 1s". Zero-valued units are dropped (except the whole value 0, which
// renders "0s"); sub-second remainders are truncated; a negative input throws a
// RangeError. Zero dependencies, erasable-syntax-only (runs under `node
// <file>.ts`). The claim that its output matches a hand-written reference table
// is backed by a committed evidence artifact; vendoring carries that claim.

/**
 * Format a duration given in milliseconds as a compact human-readable string.
 *
 * Units: d (day = 86400s), h (hour = 3600s), m (minute = 60s), s (second).
 * Leading/trailing zero units are dropped; the value 0 renders "0s".
 * Sub-second remainders are truncated (floored to whole seconds).
 *
 * @throws RangeError if ms is negative (or not a finite number).
 */
export const formatDuration = (ms: number): string => {
  if (typeof ms !== "number" || !Number.isFinite(ms)) {
    throw new RangeError("formatDuration: ms must be a finite number");
  }
  if (ms < 0) {
    throw new RangeError("formatDuration: ms must be non-negative");
  }

  const totalSeconds = Math.floor(ms / 1000);
  if (totalSeconds === 0) {
    return "0s";
  }

  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  const parts: string[] = [];
  if (days > 0) parts.push(days + "d");
  if (hours > 0) parts.push(hours + "h");
  if (minutes > 0) parts.push(minutes + "m");
  if (seconds > 0) parts.push(seconds + "s");

  return parts.join(" ");
};
