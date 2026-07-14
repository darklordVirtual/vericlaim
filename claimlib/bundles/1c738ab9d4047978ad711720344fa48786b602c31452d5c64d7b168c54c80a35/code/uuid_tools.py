# SPDX-License-Identifier: Apache-2.0
"""UUID parse / format / inspect + deterministic v3 (MD5) and v5 (SHA-1)
name-based generation per RFC 9562 — a reusable, stdlib-only building block.

A pre-verified code artifact from the VeriClaim claim library. The property
that makes it trustworthy — that name-based generation reproduces the RFC 9562
Appendix A example vectors exactly and agrees with Python's independent stdlib
``uuid`` implementation over a fixed battery — is registered as a claim and
proven by a committed evidence artifact; vendoring this module carries that
claim (and its caveat) with it.

RFC 9562 (May 2024, obsoletes RFC 4122) defines the UUID: a 128-bit
identifier written as 32 lowercase hexadecimal digits in five hyphen-separated
groups (8-4-4-4-12). The version field is the most significant 4 bits of
octet 6; the variant field is the most significant bits of octet 8 (0b10 for
the variant RFC 9562 itself defines). Name-based UUIDs (v3: MD5, v5: SHA-1)
hash a namespace UUID's 16 bytes concatenated with the name's octets, then
overwrite the version and variant bits — so the same (namespace, name) pair
always yields the same UUID, which is exactly what makes them useful for
deterministic, coordination-free identifier derivation.

This module is implemented from scratch (no ``uuid`` import), so the stdlib
remains available as a genuinely independent oracle for the evidence.

Public API
----------
    parse(text: str) -> bytes            # canonical / urn:uuid: / {braced} -> 16 bytes
    format_uuid(raw: bytes) -> str       # 16 bytes -> canonical lowercase string
    version(u) -> int | None             # RFC-variant UUIDs only, else None
    variant(u) -> str                    # "ncs" | "rfc9562" | "microsoft" | "future"
    inspect(u) -> dict                   # version/variant/hex/urn/is_nil/is_max
    uuid3(namespace, name) -> str        # deterministic MD5 name-based UUID
    uuid5(namespace, name) -> str        # deterministic SHA-1 name-based UUID
    NAMESPACE_DNS / NAMESPACE_URL / NAMESPACE_OID / NAMESPACE_X500
    NIL_UUID / MAX_UUID

    >>> uuid5(NAMESPACE_DNS, "www.example.com")
    '2ed6657d-e927-568b-95e1-2665a8aea6a2'
"""
from __future__ import annotations

import hashlib

# Well-known namespace IDs, RFC 9562 section 6.6 (unchanged from RFC 4122).
NAMESPACE_DNS = "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
NAMESPACE_URL = "6ba7b811-9dad-11d1-80b4-00c04fd430c8"
NAMESPACE_OID = "6ba7b812-9dad-11d1-80b4-00c04fd430c8"
NAMESPACE_X500 = "6ba7b814-9dad-11d1-80b4-00c04fd430c8"

# Special UUIDs, RFC 9562 sections 5.9 (Nil) and 5.10 (Max).
NIL_UUID = "00000000-0000-0000-0000-000000000000"
MAX_UUID = "ffffffff-ffff-ffff-ffff-ffffffffffff"

_GROUP_LENGTHS = (8, 4, 4, 4, 12)
_HEX_DIGITS = frozenset("0123456789abcdef")


class UUIDError(ValueError):
    """The input is not a syntactically valid UUID."""


def parse(text: str) -> bytes:
    """Parse a UUID string to its 16 raw bytes (big-endian field order).

    Accepts the canonical hyphenated form (``8-4-4-4-12`` hex digits,
    RFC 9562 section 4), case-insensitively, optionally wrapped in braces
    (``{...}``, the historical Microsoft registry format) or prefixed with
    ``urn:uuid:`` (RFC 9562 section 8 URN namespace). Anything else —
    wrong group lengths, missing hyphens, non-hex characters, surrounding
    whitespace — raises UUIDError (fail closed).
    """
    if not isinstance(text, str):
        raise UUIDError(f"expected a string, got {type(text).__name__}")
    s = text.lower()
    if s.startswith("urn:uuid:"):
        s = s[len("urn:uuid:"):]
    elif s.startswith("{") and s.endswith("}"):
        s = s[1:-1]
    groups = s.split("-")
    if len(groups) != 5 or tuple(len(g) for g in groups) != _GROUP_LENGTHS:
        raise UUIDError(f"not a canonical 8-4-4-4-12 UUID string: {text!r}")
    hexstr = "".join(groups)
    if not all(c in _HEX_DIGITS for c in hexstr):
        raise UUIDError(f"non-hex character in UUID string: {text!r}")
    return bytes.fromhex(hexstr)


def format_uuid(raw: bytes) -> str:
    """Format 16 raw bytes as the canonical lowercase hyphenated string.

    RFC 9562 section 4: each field is encoded most significant byte first,
    and the hexadecimal output is lowercase.
    """
    if not isinstance(raw, (bytes, bytearray)) or len(raw) != 16:
        raise UUIDError("expected exactly 16 bytes")
    h = bytes(raw).hex()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def _as_bytes(u: str | bytes) -> bytes:
    """Coerce a UUID given as string or 16 raw bytes to raw bytes."""
    if isinstance(u, (bytes, bytearray)):
        if len(u) != 16:
            raise UUIDError("expected exactly 16 bytes")
        return bytes(u)
    return parse(u)


def variant(u: str | bytes) -> str:
    """Return the variant per RFC 9562 section 4.1 (Table 1).

    Determined by the most significant bits of octet 8:
    ``0xx`` -> "ncs" (reserved, NCS backward compatibility),
    ``10x`` -> "rfc9562" (the variant defined by RFC 9562 / RFC 4122),
    ``110`` -> "microsoft" (reserved, Microsoft backward compatibility),
    ``111`` -> "future" (reserved for future definition).
    """
    octet8 = _as_bytes(u)[8]
    if octet8 & 0x80 == 0x00:
        return "ncs"
    if octet8 & 0xC0 == 0x80:
        return "rfc9562"
    if octet8 & 0xE0 == 0xC0:
        return "microsoft"
    return "future"


def version(u: str | bytes) -> int | None:
    """Return the version (0-15), or None if the variant is not rfc9562.

    RFC 9562 section 4.2: the version is the most significant 4 bits of
    octet 6, and is only meaningful for the 0b10 variant (mirroring the
    semantics of the stdlib ``uuid.UUID.version`` property).
    """
    raw = _as_bytes(u)
    if variant(raw) != "rfc9562":
        return None
    return raw[6] >> 4


def inspect(u: str | bytes) -> dict:
    """Return a summary dict for a UUID: hex, urn, version, variant, flags."""
    raw = _as_bytes(u)
    canonical = format_uuid(raw)
    return {
        "hex": raw.hex(),
        "canonical": canonical,
        "urn": "urn:uuid:" + canonical,
        "version": version(raw),
        "variant": variant(raw),
        "is_nil": raw == b"\x00" * 16,
        "is_max": raw == b"\xff" * 16,
    }


def _name_bytes(name: str | bytes) -> bytes:
    """Canonical octets of *name*: UTF-8 for str (stdlib convention)."""
    if isinstance(name, (bytes, bytearray)):
        return bytes(name)
    if isinstance(name, str):
        return name.encode("utf-8")
    raise UUIDError(f"name must be str or bytes, got {type(name).__name__}")


def _assemble(digest16: bytes, ver: int) -> str:
    """Overwrite version/variant bits of a 16-byte digest (RFC 9562 4.1/4.2)."""
    b = bytearray(digest16)
    b[6] = (b[6] & 0x0F) | (ver << 4)   # ver: high nibble of octet 6
    b[8] = (b[8] & 0x3F) | 0x80         # var: top two bits of octet 8 = 0b10
    return format_uuid(bytes(b))


def uuid3(namespace: str | bytes, name: str | bytes) -> str:
    """Deterministic MD5 name-based UUID (RFC 9562 section 5.3).

    MD5 over the namespace UUID's 16 bytes concatenated with the name's
    octets; the version (3) and variant (0b10) bits then replace the
    corresponding digest bits. Prefer :func:`uuid5` where possible
    (RFC 9562 recommends v5 in lieu of v3; MD5 is cryptographically broken).
    """
    data = _as_bytes(namespace) + _name_bytes(name)
    try:
        digest = hashlib.md5(data, usedforsecurity=False).digest()
    except TypeError:  # pragma: no cover - very old interpreters
        digest = hashlib.md5(data).digest()
    return _assemble(digest, 3)


def uuid5(namespace: str | bytes, name: str | bytes) -> str:
    """Deterministic SHA-1 name-based UUID (RFC 9562 section 5.5).

    SHA-1 over the namespace UUID's 16 bytes concatenated with the name's
    octets, truncated to the leftmost 128 bits; the version (5) and variant
    (0b10) bits then replace the corresponding digest bits.
    """
    data = _as_bytes(namespace) + _name_bytes(name)
    digest = hashlib.sha1(data).digest()
    return _assemble(digest[:16], 5)
