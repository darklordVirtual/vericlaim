// SPDX-License-Identifier: Apache-2.0
// parseQuery / stringifyQuery — URL query-string parse and serialize for TypeScript.
//
// A pre-verified claimlib code artifact. parseQuery turns a query string into a
// plain object, collapsing repeated keys into ordered arrays and URI-decoding
// keys and values; stringifyQuery is its serializer, emitting keys in a stable
// (sorted) order with URI-encoding. Zero dependencies, erasable-syntax-only
// (runs under `node <file>.ts`). The claim that these obey the expected outcomes
// is backed by a committed evidence artifact; vendoring carries that claim.

/** Decode one `application/x-www-form-urlencoded` component: '+' -> space, then percent-decode. */
const decodeComponent = (s: string): string => {
  try {
    return decodeURIComponent(s.replace(/\+/g, " "));
  } catch {
    // Malformed percent-escape: fall back to '+'-substituted raw text.
    return s.replace(/\+/g, " ");
  }
};

/** Encode one component: percent-encode, then render space as '+' (form style). */
const encodeComponent = (s: string): string =>
  encodeURIComponent(s).replace(/%20/g, "+");

/**
 * Parse a query string into an object. A leading "?" is allowed and stripped.
 * Repeated keys become an array of their values in first-seen order; a key that
 * appears exactly once maps to a string. Empty pairs are skipped; a key with no
 * "=" maps to the empty string. Keys and values are URI-decoded.
 */
export const parseQuery = (qs: string): Record<string, string | string[]> => {
  const out: Record<string, string | string[]> = {};
  let s = qs;
  if (s.startsWith("?")) s = s.slice(1);
  if (s === "") return out;
  for (const pair of s.split("&")) {
    if (pair === "") continue;
    const eq = pair.indexOf("=");
    const rawKey = eq === -1 ? pair : pair.slice(0, eq);
    const rawVal = eq === -1 ? "" : pair.slice(eq + 1);
    const key = decodeComponent(rawKey);
    const val = decodeComponent(rawVal);
    if (Object.prototype.hasOwnProperty.call(out, key)) {
      const existing = out[key];
      if (Array.isArray(existing)) {
        existing.push(val);
      } else {
        out[key] = [existing, val];
      }
    } else {
      out[key] = val;
    }
  }
  return out;
};

/**
 * Serialize an object to a query string with a stable key order (keys sorted
 * lexicographically). Array values expand to one `key=value` pair per element,
 * in array order. Keys and values are URI-encoded. No leading "?".
 */
export const stringifyQuery = (
  obj: Record<string, string | string[]>,
): string => {
  const parts: string[] = [];
  for (const key of Object.keys(obj).sort()) {
    const value = obj[key];
    const ek = encodeComponent(key);
    if (Array.isArray(value)) {
      for (const v of value) parts.push(ek + "=" + encodeComponent(v));
    } else {
      parts.push(ek + "=" + encodeComponent(value));
    }
  }
  return parts.join("&");
};
