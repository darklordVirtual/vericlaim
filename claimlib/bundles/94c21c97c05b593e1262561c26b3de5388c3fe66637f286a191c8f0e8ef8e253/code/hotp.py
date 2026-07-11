# SPDX-License-Identifier: Apache-2.0
"""HOTP -- HMAC-based one-time passwords (RFC 4226).

A pre-verified claimlib code artifact for authentication. HOTP derives a short
numeric one-time password from a shared secret and a moving counter: HMAC-SHA1
of the counter, then RFC 4226 "dynamic truncation" to a 31-bit number reduced
modulo 10**digits. That it reproduces the published RFC 4226 Appendix D test
vectors is registered as a claim and proven by a committed evidence artifact.

Public API
----------
    hotp(secret: bytes, counter: int, digits: int = 6) -> str

    >>> hotp(b"12345678901234567890", 0)
    '755224'
    >>> hotp(b"12345678901234567890", 1)
    '287082'
"""
from __future__ import annotations

import hashlib
import hmac


class HOTPError(ValueError):
    """Invalid HOTP argument (bad secret, negative counter, or bad digits)."""


def hotp(secret: bytes, counter: int, digits: int = 6) -> str:
    """Return the *digits*-length HOTP for *secret* at *counter* (RFC 4226)."""
    if not isinstance(secret, (bytes, bytearray)):
        raise HOTPError("secret must be bytes")
    if not isinstance(counter, int) or isinstance(counter, bool) or counter < 0:
        raise HOTPError("counter must be a non-negative int")
    if not isinstance(digits, int) or isinstance(digits, bool) or not 1 <= digits <= 10:
        raise HOTPError("digits must be an int in 1..10")
    mac = hmac.new(bytes(secret), counter.to_bytes(8, "big"), hashlib.sha1).digest()
    offset = mac[-1] & 0x0F                       # low nibble of the last byte
    truncated = ((mac[offset] & 0x7F) << 24
                 | mac[offset + 1] << 16
                 | mac[offset + 2] << 8
                 | mac[offset + 3])               # 31-bit dynamic truncation
    return str(truncated % (10 ** digits)).zfill(digits)
