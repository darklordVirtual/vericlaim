// SPDX-License-Identifier: Apache-2.0
// Central authorization policy for the Worker — one place that decides who may
// call what. Pure and dependency-light so it is unit-testable without workerd.
//
// The security lesson this encodes (see the P0-1 review finding): any route that
// drives Workers AI MUST pass the same generative gate. /mcp exposes
// ask_claims / ask_research, so it belongs in `requiresGenerativeAuth` alongside
// /ask and /research/ask — otherwise setting READ_TOKEN protects /ask while
// leaving an open generative endpoint on /mcp.
import { type Env, timingSafeEqual } from "./lib.ts";

// Constant-time bearer check: compare the whole token, never short-circuit on the
// first mismatch (which would leak how many characters were right).
export function bearerMatches(req: Request, token: string | undefined): boolean {
  if (!token) return false; // fail closed
  const auth = req.headers.get("authorization") ?? "";
  return timingSafeEqual(auth, `Bearer ${token}`);
}

// Write access (rebuilding the index) always requires INDEX_TOKEN.
export function authorized(req: Request, env: Env): boolean {
  return bearerMatches(req, env.INDEX_TOKEN);
}

// Generative access: when READ_TOKEN is configured, generative routes require it
// (INDEX_TOKEN also satisfies it, so the CI pusher is fine). When it is unset they
// stay public — an explicit, backward-compatible opt-in.
export function generativeAllowed(req: Request, env: Env): boolean {
  if (!env.READ_TOKEN) return true; // reads are public unless a token is set
  return bearerMatches(req, env.READ_TOKEN) || bearerMatches(req, env.INDEX_TOKEN);
}

// The canonical set of routes that drive Workers AI and therefore require the
// generative gate. Keep this in sync with the handlers; the unit tests pin it so
// a new generative route cannot be added without appearing here.
export function requiresGenerativeAuth(pathname: string): boolean {
  return pathname === "/ask" || pathname === "/research/ask" || pathname === "/mcp";
}
