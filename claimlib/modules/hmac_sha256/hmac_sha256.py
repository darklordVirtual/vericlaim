# SPDX-License-Identifier: Apache-2.0
"""HMAC-SHA256 (RFC 2104) -- keyed message authentication, from scratch.

A pre-verified claimlib code artifact. This module implements the HMAC
construction DIRECTLY -- key normalization, the inner/outer ipad/opad padding,
and the two-pass hash -- over ``hashlib.sha256`` as the underlying hash. It does
NOT call the stdlib ``hmac`` module, so cross-checking against ``hmac`` is a
genuine independent test of the construction. That it agrees with stdlib
``hmac`` over the RFC 4231 test inputs and a fixed battery is registered as a
claim and proven by a committed evidence artifact.

Public API
----------
    hmac_sha256(key: bytes, message: bytes) -> bytes    # 32-byte tag
    hexdigest(key: bytes, message: bytes) -> str
    verify(key: bytes, message: bytes, tag: bytes) -> bool   # constant-time

    >>> hexdigest(b"key", b"The quick brown fox jumps over the lazy dog")
    'f7bc83f430538424b13298e6aa6fb143ef4d59a14946175997479dbc2d1a3cd8'
"""
from __future__ import annotations

import hashlib

_BLOCK_SIZE = 64  # SHA-256 block size in bytes


class HMACError(ValueError):
    """A key, message, or tag argument was not bytes."""


def _digest(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def hmac_sha256(key: bytes, message: bytes) -> bytes:
    """Return the 32-byte HMAC-SHA256 tag of *message* under *key* (RFC 2104)."""
    if not isinstance(key, (bytes, bytearray)) or not isinstance(message, (bytes, bytearray)):
        raise HMACError("key and message must be bytes")
    key = bytes(key)
    if len(key) > _BLOCK_SIZE:
        key = _digest(key)                       # long keys are hashed down first
    key = key.ljust(_BLOCK_SIZE, b"\x00")        # then zero-padded to the block
    inner = bytes(b ^ 0x36 for b in key)         # ipad
    outer = bytes(b ^ 0x5C for b in key)         # opad
    return _digest(outer + _digest(inner + bytes(message)))


def hexdigest(key: bytes, message: bytes) -> str:
    """Return the HMAC-SHA256 tag as 64 lowercase hex characters."""
    return hmac_sha256(key, message).hex()


def verify(key: bytes, message: bytes, tag: bytes) -> bool:
    """Return True iff *tag* is the correct HMAC-SHA256 of *message*.

    The comparison is constant-time in the length of the tag (it does not
    short-circuit on the first differing byte).
    """
    if not isinstance(tag, (bytes, bytearray)):
        raise HMACError("tag must be bytes")
    expected = hmac_sha256(key, message)
    if len(expected) != len(tag):
        return False
    diff = 0
    for x, y in zip(expected, tag):
        diff |= x ^ y
    return diff == 0
