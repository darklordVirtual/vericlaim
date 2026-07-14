# SPDX-License-Identifier: Apache-2.0
"""JWS compact serialization with HS256 (RFC 7515) + JWT claims (RFC 7519).

A pre-verified code artifact from the VeriClaim claim library. The property
that makes it trustworthy — that it reproduces the RFC 7515 Appendix A.1
published HMAC-SHA-256 example byte-for-byte, agrees with the stdlib base64
oracle, and enforces the RFC 7519 exp/nbf boundary semantics exactly — is
registered as a claim and proven by a committed evidence artifact; vendoring
this module carries that claim (and its caveat) with it.

Scope and security posture
--------------------------
* HS256 ONLY. ``verify``/``decode`` reject any token whose header ``alg`` is
  not exactly ``"HS256"`` — including ``"none"`` — which forecloses the
  classic algorithm-confusion downgrade attacks.
* Tokens whose header carries a ``crit`` parameter are rejected (RFC 7515
  section 4.1.11: a receiver MUST reject extensions it does not implement).
* base64url is implemented from scratch per RFC 4648 section 5, UNPADDED as
  JWS requires (RFC 7515 section 2, Appendix C): '=' padding, non-alphabet
  characters, impossible lengths, and non-canonical trailing bits all fail
  closed. The MAC itself is the stdlib ``hmac``/``hashlib`` HMAC-SHA-256 —
  the claim here is about the JWS construction, not about reimplementing HMAC.
* NO CLOCK READS: exp/nbf validation takes an explicit ``now`` (seconds since
  the epoch, RFC 7519 NumericDate), so behaviour is deterministic and testable.

Public API
----------
    b64url_encode(data: bytes) -> str
    b64url_decode(s: str) -> bytes
    sign_bytes(header: bytes, payload: bytes, key: bytes) -> str
    sign_claims(claims: dict, key: bytes, header: dict | None = None) -> str
    verify(token: str, key: bytes) -> tuple[dict, bytes]
    validate_claims(claims: dict, now, *, leeway=0) -> None
    decode(token: str, key: bytes, *, now=None, leeway=0) -> dict

    >>> tok = sign_claims({"iss": "joe"}, b"secret")
    >>> decode(tok, b"secret")
    {'iss': 'joe'}
"""
from __future__ import annotations

import hashlib
import hmac
import json

__all__ = [
    "JWTError", "InvalidToken", "InvalidSignature", "ClaimValidationError",
    "b64url_encode", "b64url_decode", "sign_bytes", "sign_claims",
    "verify", "validate_claims", "decode",
]


class JWTError(ValueError):
    """Base error: malformed input, bad encoding, wrong types."""


class InvalidToken(JWTError):
    """The token is structurally invalid (parts, header, encoding)."""


class InvalidSignature(JWTError):
    """The HMAC-SHA-256 signature does not verify under the given key."""


class ClaimValidationError(JWTError):
    """A registered time claim (exp/nbf) rejects the token at ``now``."""


# ---------------------------------------------------------------- base64url
# RFC 4648 section 5 alphabet: standard base64 with '-' and '_' replacing
# '+' and '/'. JWS uses it WITHOUT '=' padding (RFC 7515 section 2).
_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
_REVERSE = {c: i for i, c in enumerate(_ALPHABET)}


def b64url_encode(data: bytes) -> str:
    """Encode *data* as unpadded base64url (RFC 4648 section 5)."""
    if not isinstance(data, (bytes, bytearray)):
        raise JWTError("b64url_encode expects bytes")
    data = bytes(data)
    out = []
    full = len(data) - len(data) % 3
    for i in range(0, full, 3):
        n = (data[i] << 16) | (data[i + 1] << 8) | data[i + 2]
        out.append(_ALPHABET[n >> 18])
        out.append(_ALPHABET[(n >> 12) & 0x3F])
        out.append(_ALPHABET[(n >> 6) & 0x3F])
        out.append(_ALPHABET[n & 0x3F])
    rem = len(data) - full
    if rem == 1:                       # 8 bits -> 2 symbols, 4 zero pad bits
        n = data[-1] << 4
        out.append(_ALPHABET[n >> 6])
        out.append(_ALPHABET[n & 0x3F])
    elif rem == 2:                     # 16 bits -> 3 symbols, 2 zero pad bits
        n = ((data[-2] << 8) | data[-1]) << 2
        out.append(_ALPHABET[n >> 12])
        out.append(_ALPHABET[(n >> 6) & 0x3F])
        out.append(_ALPHABET[n & 0x3F])
    return "".join(out)


def b64url_decode(s: str) -> bytes:
    """Decode unpadded base64url, failing closed on anything non-canonical.

    Rejects: non-str input, '=' padding (forbidden in JWS), characters
    outside the RFC 4648 section 5 alphabet, impossible lengths
    (len % 4 == 1), and non-zero trailing pad bits (non-canonical encodings
    that would let two distinct strings decode to the same bytes).
    """
    if not isinstance(s, str):
        raise JWTError("b64url_decode expects str")
    if "=" in s:
        raise JWTError("padding '=' is forbidden in unpadded base64url (JWS)")
    if len(s) % 4 == 1:
        raise JWTError("invalid base64url length")
    try:
        vals = [_REVERSE[c] for c in s]
    except KeyError as exc:
        raise JWTError(f"non-alphabet base64url character: {exc.args[0]!r}") from None
    out = bytearray()
    full = len(vals) - len(vals) % 4
    for i in range(0, full, 4):
        n = (vals[i] << 18) | (vals[i + 1] << 12) | (vals[i + 2] << 6) | vals[i + 3]
        out.append(n >> 16)
        out.append((n >> 8) & 0xFF)
        out.append(n & 0xFF)
    tail = vals[full:]
    if len(tail) == 2:                 # 12 bits -> 1 byte + 4 pad bits
        n = (tail[0] << 6) | tail[1]
        if n & 0x0F:
            raise JWTError("non-canonical base64url (trailing bits set)")
        out.append(n >> 4)
    elif len(tail) == 3:               # 18 bits -> 2 bytes + 2 pad bits
        n = (tail[0] << 12) | (tail[1] << 6) | tail[2]
        if n & 0x03:
            raise JWTError("non-canonical base64url (trailing bits set)")
        out.append(n >> 10)
        out.append((n >> 2) & 0xFF)
    return bytes(out)


# ------------------------------------------------------------------- JWS
def _hs256(key: bytes, msg: bytes) -> bytes:
    """HMAC-SHA-256 via the stdlib (RFC 2104 over FIPS 180-4 SHA-256)."""
    if not isinstance(key, (bytes, bytearray)):
        raise JWTError("key must be bytes")
    return hmac.new(bytes(key), msg, hashlib.sha256).digest()


def sign_bytes(header: bytes, payload: bytes, key: bytes) -> str:
    """Build a JWS compact serialization over EXACT header/payload octets.

    RFC 7515 section 5.1: the signing input is
    ASCII(BASE64URL(header) || '.' || BASE64URL(payload)) and the token is
    signing-input || '.' || BASE64URL(HMAC-SHA-256(key, signing-input)).
    Octets pass through untouched, so published vectors (whose JSON contains
    specific line-break octets) are reproducible byte-for-byte.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise JWTError("payload must be bytes")
    h_b64 = b64url_encode(header)
    p_b64 = b64url_encode(bytes(payload))
    signing_input = (h_b64 + "." + p_b64).encode("ascii")
    sig_b64 = b64url_encode(_hs256(key, signing_input))
    return h_b64 + "." + p_b64 + "." + sig_b64


def sign_claims(claims: dict, key: bytes, header: dict | None = None) -> str:
    """Sign a JWT claims set (RFC 7519) with HS256, deterministically.

    Header defaults to ``{"alg": "HS256", "typ": "JWT"}``; a supplied header
    must still declare ``alg == "HS256"``. JSON is serialized with sorted
    keys and compact separators so the same claims always yield the same
    token bytes.
    """
    if not isinstance(claims, dict):
        raise JWTError("claims must be a dict (JWT Claims Set is a JSON object)")
    if header is None:
        header = {"alg": "HS256", "typ": "JWT"}
    if not isinstance(header, dict) or header.get("alg") != "HS256":
        raise JWTError('header must be a dict with alg == "HS256"')
    h_bytes = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    p_bytes = json.dumps(claims, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return sign_bytes(h_bytes, p_bytes, key)


def verify(token: str, key: bytes) -> tuple[dict, bytes]:
    """Verify a JWS compact serialization; return (header, payload_bytes).

    Fails closed on: wrong part count, bad base64url, non-JSON-object
    header, any ``alg`` other than exactly ``"HS256"`` (including
    ``"none"``), a ``crit`` header parameter, wrong signature length, or a
    signature mismatch (compared with ``hmac.compare_digest``).
    """
    if not isinstance(token, str):
        raise InvalidToken("token must be str")
    parts = token.split(".")
    if len(parts) != 3:
        raise InvalidToken(f"expected 3 dot-separated parts, got {len(parts)}")
    h_b64, p_b64, s_b64 = parts
    try:
        header_bytes = b64url_decode(h_b64)
        payload = b64url_decode(p_b64)
        sig = b64url_decode(s_b64)
    except JWTError as exc:
        raise InvalidToken(str(exc)) from None
    try:
        header = json.loads(header_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise InvalidToken("header is not valid UTF-8 JSON") from None
    if not isinstance(header, dict):
        raise InvalidToken("header must be a JSON object")
    if header.get("alg") != "HS256":
        raise InvalidToken(f"alg not allowed: {header.get('alg')!r} (HS256 only)")
    if "crit" in header:
        raise InvalidToken("crit header extensions are not supported (RFC 7515 s4.1.11)")
    if len(sig) != 32:
        raise InvalidSignature("HS256 signature must be exactly 32 bytes")
    expected = _hs256(key, (h_b64 + "." + p_b64).encode("ascii"))
    if not hmac.compare_digest(expected, sig):
        raise InvalidSignature("HMAC-SHA-256 signature mismatch")
    return header, payload


def validate_claims(claims: dict, now, *, leeway=0) -> None:
    """Validate exp/nbf (RFC 7519 sections 4.1.4 / 4.1.5) at explicit *now*.

    * ``exp``: the token MUST NOT be accepted on or after exp — valid iff
      ``now < exp + leeway``.
    * ``nbf``: the token MUST NOT be accepted before nbf; acceptance at
      exactly nbf is allowed ("after or equal") — valid iff
      ``now >= nbf - leeway``.

    ``now`` is a NumericDate (seconds since 1970-01-01T00:00:00Z, leap
    seconds ignored) supplied by the CALLER — this function never reads a
    clock. Absent claims pass; present claims of a non-numeric type fail
    closed. ``leeway`` (seconds, >= 0) absorbs clock skew.
    """
    if not isinstance(claims, dict):
        raise JWTError("claims must be a dict")
    if isinstance(now, bool) or not isinstance(now, (int, float)):
        raise JWTError("now must be a number (NumericDate seconds)")
    if isinstance(leeway, bool) or not isinstance(leeway, (int, float)) or leeway < 0:
        raise JWTError("leeway must be a non-negative number")
    if "exp" in claims:
        exp = claims["exp"]
        if isinstance(exp, bool) or not isinstance(exp, (int, float)):
            raise ClaimValidationError("exp must be a NumericDate number")
        if not now < exp + leeway:
            raise ClaimValidationError(f"token expired: now={now} >= exp={exp} (+leeway={leeway})")
    if "nbf" in claims:
        nbf = claims["nbf"]
        if isinstance(nbf, bool) or not isinstance(nbf, (int, float)):
            raise ClaimValidationError("nbf must be a NumericDate number")
        if not now >= nbf - leeway:
            raise ClaimValidationError(f"token not yet valid: now={now} < nbf={nbf} (-leeway={leeway})")


def decode(token: str, key: bytes, *, now=None, leeway=0) -> dict:
    """Verify signature, parse the claims set, optionally validate exp/nbf.

    Returns the claims dict. If *now* is given (explicit NumericDate — this
    module never reads the clock), exp/nbf are enforced with *leeway*.
    """
    _header, payload = verify(token, key)
    try:
        claims = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise InvalidToken("payload is not valid UTF-8 JSON") from None
    if not isinstance(claims, dict):
        raise InvalidToken("JWT claims set must be a JSON object")
    if now is not None:
        validate_claims(claims, now, leeway=leeway)
    return claims
