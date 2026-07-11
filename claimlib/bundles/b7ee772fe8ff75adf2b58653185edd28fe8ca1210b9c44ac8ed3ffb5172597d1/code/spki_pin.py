# SPDX-License-Identifier: Apache-2.0
"""SPKI public-key pins (RFC 7469) -- certificate pinning for TLS / mutual TLS.

A pre-verified claimlib code artifact. A pin is the base64 of the SHA-256 digest
of a certificate's Subject Public Key Info (SPKI). A client stores one or more
pins (a live key plus a backup) and rejects any chain that presents no matching
pinned key -- defeating a mis-issued certificate from an otherwise-trusted CA.
This module computes and verifies pins; that a pin equals base64(sha256(spki))
and that matching accepts a pinned key and rejects an unpinned one is registered
as a claim and proven by a committed evidence artifact.

Public API
----------
    pin_sha256(spki_der: bytes) -> str            # base64(sha256(spki))
    pin_directive(spki_der: bytes) -> str         # pin-sha256="<pin>"
    matches(spki_der: bytes, pins: Iterable[str]) -> bool   # constant-time

    >>> pin = pin_sha256(b"public-key-info")
    >>> matches(b"public-key-info", [pin])
    True
"""
from __future__ import annotations

import base64
import hashlib
from collections.abc import Iterable


class SPKIPinError(ValueError):
    """The SPKI or pin argument is not bytes / a valid base64 SHA-256 pin."""


def pin_sha256(spki_der: bytes) -> str:
    """Return the RFC 7469 pin: base64 of SHA-256 of the SPKI DER."""
    if not isinstance(spki_der, (bytes, bytearray)):
        raise SPKIPinError("spki_der must be bytes")
    return base64.b64encode(hashlib.sha256(bytes(spki_der)).digest()).decode("ascii")


def pin_directive(spki_der: bytes) -> str:
    """Return the HPKP header directive form: pin-sha256=\"<pin>\"."""
    return f'pin-sha256="{pin_sha256(spki_der)}"'


def _ct_equal(a: str, b: str) -> bool:
    """Constant-time string comparison (no early return on first mismatch)."""
    if len(a) != len(b):
        return False
    diff = 0
    for x, y in zip(a.encode(), b.encode()):
        diff |= x ^ y
    return diff == 0


def matches(spki_der: bytes, pins: Iterable[str]) -> bool:
    """Return True iff the SPKI's pin is present in *pins* (constant-time compare)."""
    computed = pin_sha256(spki_der)
    found = False
    for pin in pins:
        if not isinstance(pin, str):
            raise SPKIPinError("each pin must be a base64 string")
        found |= _ct_equal(computed, pin)      # scan all pins, no early exit
    return found
