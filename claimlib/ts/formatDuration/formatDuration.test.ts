// SPDX-License-Identifier: Apache-2.0
import { test } from "node:test";
import assert from "node:assert/strict";
import { formatDuration } from "./formatDuration.ts";

test("zero and sub-second render 0s", () => {
  assert.equal(formatDuration(0), "0s");
  assert.equal(formatDuration(999), "0s");
});

test("seconds truncate and drop higher units", () => {
  assert.equal(formatDuration(1000), "1s");
  assert.equal(formatDuration(1500), "1s");
  assert.equal(formatDuration(59000), "59s");
});

test("minutes drop zero seconds", () => {
  assert.equal(formatDuration(60000), "1m");
  assert.equal(formatDuration(61000), "1m 1s");
  assert.equal(formatDuration(119000), "1m 59s");
});

test("hours drop interior zero units", () => {
  assert.equal(formatDuration(3600000), "1h");
  assert.equal(formatDuration(3601000), "1h 1s");
  assert.equal(formatDuration(3660000), "1h 1m");
  assert.equal(formatDuration(3661000), "1h 1m 1s");
});

test("days compose all units", () => {
  assert.equal(formatDuration(86400000), "1d");
  assert.equal(formatDuration(86461000), "1d 1m 1s");
  assert.equal(formatDuration(90061000), "1d 1h 1m 1s");
  assert.equal(formatDuration(93784000), "1d 2h 3m 4s");
});

test("negative input throws RangeError", () => {
  assert.throws(() => formatDuration(-1), RangeError);
  assert.throws(() => formatDuration(-90061000), RangeError);
});

test("non-finite input throws RangeError", () => {
  assert.throws(() => formatDuration(NaN), RangeError);
  assert.throws(() => formatDuration(Infinity), RangeError);
});
