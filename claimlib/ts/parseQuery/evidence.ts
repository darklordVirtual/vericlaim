// SPDX-License-Identifier: Apache-2.0
// Evidence for CLAIM-LIB-PARSEQUERY-001. Exercises parseQuery / stringifyQuery
// over a fixed battery whose expected outcomes are written out independently:
//   (a) hand-written expected objects / strings,
//   (b) round-trip checks (parse -> stringify -> parse is stable),
//   (c) a cross-check of per-key decoding against the built-in URLSearchParams,
//       whose getAll() is an independent reference implementation.
// Prints the metrics JSON on stdout. Deterministic; `node evidence.ts` produces
// the same line every run.
import { parseQuery, stringifyQuery } from "./parseQuery.ts";

// [label, actual, expected] — expected values are hand-written / independent.
const cases: Array<[string, unknown, unknown]> = [
  // (a) hand-written parse expectations.
  ["repeated key -> ordered array", parseQuery("?a=1&b=2&a=3"), { a: ["1", "3"], b: "2" }],
  ["single key -> string", parseQuery("x=hello"), { x: "hello" }],
  ["leading ? stripped", parseQuery("?k=v"), { k: "v" }],
  ["no leading ? also fine", parseQuery("k=v"), { k: "v" }],
  ["empty string -> {}", parseQuery(""), {}],
  ["lone ? -> {}", parseQuery("?"), {}],
  ["key without = -> empty value", parseQuery("flag"), { flag: "" }],
  ["key with empty value", parseQuery("a="), { a: "" }],
  ["percent-decoded value", parseQuery("q=a%20b%26c"), { q: "a b&c" }],
  ["plus decodes to space", parseQuery("q=a+b"), { q: "a b" }],
  ["percent-decoded key", parseQuery("a%20b=1"), { "a b": "1" }],
  ["three repeats -> array of 3", parseQuery("t=1&t=2&t=3"), { t: ["1", "2", "3"] }],
  ["empty pairs skipped", parseQuery("a=1&&b=2&"), { a: "1", b: "2" }],
  ["value with = kept after first", parseQuery("eq=a=b=c"), { eq: "a=b=c" }],
  ["utf-8 percent value", parseQuery("name=%C3%A6%C3%B8%C3%A5"), { name: "æøå" }],

  // (a) hand-written stringify expectations (stable sorted key order).
  ["stringify sorts keys", stringifyQuery({ b: "2", a: "1" }), "a=1&b=2"],
  ["stringify expands array in order", stringifyQuery({ a: ["1", "3"], b: "2" }), "a=1&a=3&b=2"],
  ["stringify encodes space as +", stringifyQuery({ q: "a b" }), "q=a+b"],
  ["stringify percent-encodes special", stringifyQuery({ q: "a&b=c" }), "q=a%26b%3Dc"],
  ["stringify empty object -> ''", stringifyQuery({}), ""],
  ["stringify empty value", stringifyQuery({ a: "" }), "a="],

  // (b) round-trip: parse(stringify(parse(qs))) equals parse(qs).
  ["round-trip repeated keys", parseQuery(stringifyQuery(parseQuery("a=1&b=2&a=3"))), { a: ["1", "3"], b: "2" }],
  ["round-trip special chars", parseQuery(stringifyQuery(parseQuery("q=a%20b%26c&r=x%2By"))), { q: "a b&c", r: "x+y" }],
  ["round-trip utf-8", parseQuery(stringifyQuery(parseQuery("n=%C3%A6%C3%B8%C3%A5"))), { n: "æøå" }],
];

// (c) Cross-check per-key decoding against the built-in URLSearchParams (an
// independent implementation). For each query and key, our value normalized to
// an array must equal URLSearchParams.getAll(key). Expected is derived from the
// reference (URLSearchParams), NOT from our module.
const crossQueries = [
  "a=1&b=2&a=3",
  "q=a%20b%26c",
  "q=a+b",
  "name=%C3%A6%C3%B8%C3%A5",
  "t=1&t=2&t=3",
  "eq=a=b=c",
  "a=",
];
for (const q of crossQueries) {
  const parsed = parseQuery(q);
  const usp = new URLSearchParams(q);
  for (const key of Object.keys(parsed)) {
    const v = parsed[key];
    const ours = Array.isArray(v) ? v : [v];
    const ref = usp.getAll(key); // independent reference
    cases.push(["URLSearchParams cross-check " + q + " [" + key + "]", ours, ref]);
  }
}

let correct = 0;
for (const [, actual, expected] of cases) {
  if (JSON.stringify(actual) === JSON.stringify(expected)) correct++;
}

process.stdout.write(JSON.stringify({
  schema: "claimlib_parseQuery_v1",
  module: "parseQuery",
  n_cases: cases.length,
  correct,
  errors: cases.length - correct,
}) + "\n");
