// SPDX-License-Identifier: Apache-2.0
// Regression tests for the Worker authorization policy — the P0-1 fix (MCP
// generative-auth bypass) and the constant-time bearer/base64 helpers. Run with
// Node's built-in test runner (no workerd needed):
//     node --test test/authz.test.ts
// Full Miniflare route tests (real bindings end-to-end) remain a tracked
// follow-up; these lock the security-critical DECISION logic.
import { test } from "node:test";
import assert from "node:assert";

import {
  authorized,
  bearerMatches,
  generativeAllowed,
  requiresGenerativeAuth,
  routeAuthError,
} from "../src/authz.ts";
import { b64ToBytes, timingSafeEqual } from "../src/lib.ts";

function req(token?: string): Request {
  const h = new Headers();
  if (token !== undefined) h.set("authorization", `Bearer ${token}`);
  return new Request("https://x/", { headers: h });
}

// ── the P0-1 policy: /mcp is a generative route ─────────────────────────────

test("/mcp requires the generative gate (it exposes ask_claims/ask_research)", () => {
  assert.equal(requiresGenerativeAuth("/mcp"), true);
  assert.equal(requiresGenerativeAuth("/ask"), true);
  assert.equal(requiresGenerativeAuth("/research/ask"), true);
});

test("cheap reads are NOT behind the generative gate", () => {
  for (const p of ["/search", "/passport", "/badge.svg", "/", "/ledger/verify"]) {
    assert.equal(requiresGenerativeAuth(p), false, p);
  }
});

// ── generativeAllowed: public only when READ_TOKEN is unset ──────────────────

test("generative routes are public when READ_TOKEN is unset", () => {
  const env = {} as any;
  assert.equal(generativeAllowed(req(), env), true);
  assert.equal(generativeAllowed(req("anything"), env), true);
});

test("generative routes require the token once READ_TOKEN is set", () => {
  const env = { READ_TOKEN: "s3cret", INDEX_TOKEN: "idx" } as any;
  assert.equal(generativeAllowed(req(), env), false, "no token -> denied");
  assert.equal(generativeAllowed(req("wrong"), env), false, "wrong token -> denied");
  assert.equal(generativeAllowed(req("s3cret"), env), true, "READ_TOKEN -> allowed");
  assert.equal(generativeAllowed(req("idx"), env), true, "INDEX_TOKEN also satisfies");
});

// This is the exact bypass the review caught: with READ_TOKEN set, an
// unauthenticated caller must NOT be able to reach a generative route — and /mcp
// is a generative route, so the same denial applies to it.
test("READ_TOKEN set + no bearer -> a generative route (incl. /mcp) is denied", () => {
  const env = { READ_TOKEN: "s3cret" } as any;
  assert.equal(requiresGenerativeAuth("/mcp") && !generativeAllowed(req(), env), true);
});

// ── write access ────────────────────────────────────────────────────────────

test("authorized() requires INDEX_TOKEN exactly", () => {
  const env = { INDEX_TOKEN: "idx", READ_TOKEN: "read" } as any;
  assert.equal(authorized(req(), env), false);
  assert.equal(authorized(req("read"), env), false, "READ_TOKEN must not grant write");
  assert.equal(authorized(req("idx"), env), true);
});

// ── constant-time compare + base64 (base64 -> 400 path) ─────────────────────

test("timingSafeEqual: equal true, unequal/length-mismatch false", () => {
  assert.equal(timingSafeEqual("abc", "abc"), true);
  assert.equal(timingSafeEqual("abc", "abd"), false);
  assert.equal(timingSafeEqual("abc", "abcd"), false);
});

test("bearerMatches fails closed on an unset token", () => {
  assert.equal(bearerMatches(req("x"), undefined), false);
});

test("b64ToBytes decodes valid base64 and throws on invalid", () => {
  assert.deepEqual(Array.from(b64ToBytes("aGk=")), [104, 105]); // "hi"
  assert.throws(() => b64ToBytes("!!!not base64!!!"));
});

// ── the central choke point the router actually calls ───────────────────────

test("routeAuthError: generative paths (incl. /mcp) are gated when READ_TOKEN set", () => {
  const env = { READ_TOKEN: "s3cret" } as any;
  for (const p of ["/ask", "/research/ask", "/mcp"]) {
    assert.deepEqual(routeAuthError(p, req(), env), { status: 401, error: "unauthorized" }, `${p} no token`);
    assert.equal(routeAuthError(p, req("s3cret"), env), null, `${p} with token`);
  }
});

test("routeAuthError: cheap reads and writes are never blocked by the generative gate", () => {
  const env = { READ_TOKEN: "s3cret" } as any;
  for (const p of ["/search", "/passport", "/badge.svg", "/", "/index", "/ledger/verify"]) {
    assert.equal(routeAuthError(p, req(), env), null, p);
  }
});

test("routeAuthError: generative paths stay open when no READ_TOKEN is set", () => {
  assert.equal(routeAuthError("/mcp", req(), {} as any), null);
});
