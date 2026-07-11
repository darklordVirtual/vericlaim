# SPDX-License-Identifier: Apache-2.0
"""TOTP -- time-based one-time passwords (RFC 6238).

A pre-verified claimlib code artifact for two-factor authentication. TOTP is
HOTP driven by a time counter: floor((now - T0) / time_step). This module
computes it (with selectable SHA-1/256/512 and digit count) and its reproduction
of the published RFC 6238 Appendix B test vectors is registered as a claim and
proven by a committed evidence artifact.

Public API
----------
    totp(secret, timestamp, *, time_step=30, t0=0, digits=6, algorithm="sha1") -> str

    >>> totp(b"12345678901234567890", 59, digits=8)
    '94287082'
"""
from __future__ import annotations

import hashlib
import hmac

_ALGORITHMS = {"sha1": hashlib.sha1, "sha256": hashlib.sha256, "sha512": hashlib.sha512}


class TOTPError(ValueError):
    """Invalid TOTP argument (bad secret, time_step, digits, or algorithm)."""


def totp(secret: bytes, timestamp: int, *, time_step: int = 30, t0: int = 0,
         digits: int = 6, algorithm: str = "sha1") -> str:
    """Return the TOTP for *secret* at Unix *timestamp* (RFC 6238)."""
    if not isinstance(secret, (bytes, bytearray)):
        raise TOTPError("secret must be bytes")
    if not isinstance(time_step, int) or isinstance(time_step, bool) or time_step <= 0:
        raise TOTPError("time_step must be a positive int")
    if not isinstance(digits, int) or isinstance(digits, bool) or not 1 <= digits <= 10:
        raise TOTPError("digits must be an int in 1..10")
    if algorithm not in _ALGORITHMS:
        raise TOTPError(f"algorithm must be one of {sorted(_ALGORITHMS)}")
    counter = (int(timestamp) - t0) // time_step
    if counter < 0:
        raise TOTPError("timestamp is before t0")
    mac = hmac.new(bytes(secret), counter.to_bytes(8, "big"), _ALGORITHMS[algorithm]).digest()
    offset = mac[-1] & 0x0F
    truncated = ((mac[offset] & 0x7F) << 24
                 | mac[offset + 1] << 16
                 | mac[offset + 2] << 8
                 | mac[offset + 3])
    return str(truncated % (10 ** digits)).zfill(digits)
