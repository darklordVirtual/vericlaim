// SPDX-License-Identifier: Apache-2.0
// Request limits — bound cost and abuse on the public surface (P1 review finding:
// "Innfør maks query-lengde, body-size ... antall requests"). Pure and
// dependency-light so it is unit-testable without workerd. These are cheap,
// in-app guards; hard per-client rate limiting still belongs at the edge
// (Cloudflare rate-limit / WAF) and per-token quotas are a tracked follow-up.

export const MAX_QUERY_LEN = 4096;        // chars in a ?q= search/ask query
export const MAX_BODY_BYTES = 2_000_000;  // declared content-length for POST bodies
export const LEDGER_PAGE_DEFAULT = 500;   // /ledger/export rows per page
export const LEDGER_PAGE_MAX = 2000;

// A query longer than this drives needless embedding / generation cost.
export function queryTooLong(q: string, max: number = MAX_QUERY_LEN): boolean {
  return q.length > max;
}

// Reject an oversized POST before buffering it. We trust the declared
// Content-Length only to fail fast; a missing/lying header still hits the normal
// parse path (Workers caps request size independently). Fail closed on a header
// that parses to more than the limit.
export function declaredBodyTooLarge(req: Request, max: number = MAX_BODY_BYTES): boolean {
  const len = Number(req.headers.get("content-length"));
  return Number.isFinite(len) && len > max;
}

// Clamp a caller-supplied page size into [1, max].
export function clampLimit(raw: string | null, def: number, max: number): number {
  const n = Number(raw);
  if (!Number.isFinite(n) || n < 1) return def;
  return Math.min(Math.floor(n), max);
}

// Parse a non-negative cursor (e.g. ?after_seq=). Anything invalid -> 0 (start).
export function parseCursor(raw: string | null): number {
  const n = Number(raw);
  return Number.isFinite(n) && n > 0 ? Math.floor(n) : 0;
}
