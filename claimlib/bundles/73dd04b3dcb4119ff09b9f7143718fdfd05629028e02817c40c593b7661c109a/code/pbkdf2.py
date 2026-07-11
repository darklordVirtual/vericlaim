# SPDX-License-Identifier: Apache-2.0
"""PBKDF2 password-based key derivation (RFC 8018 / PKCS#5), from scratch.

A pre-verified claimlib code artifact for password hashing / key stretching.
This module implements the PBKDF2 construction DIRECTLY -- the block function
T_i = U_1 XOR U_2 XOR ... XOR U_c where U_1 = PRF(password, salt || INT(i)) and
U_j = PRF(password, U_{j-1}) -- using an HMAC PRF from ``hmac``/``hashlib``. It
does NOT call ``hashlib.pbkdf2_hmac``, so cross-checking against it is a genuine
independent test. That it agrees with ``hashlib.pbkdf2_hmac`` and reproduces the
RFC 6070 vectors is registered as a claim and proven by a committed evidence
artifact.

Public API
----------
    pbkdf2_hmac(hash_name, password, salt, iterations, dklen=None) -> bytes

    >>> pbkdf2_hmac("sha1", b"password", b"salt", 1, 20).hex()
    '0c60c80f961f0e71f3a9b524af6012062fe037a6'
"""
from __future__ import annotations

import hashlib
import hmac


class PBKDF2Error(ValueError):
    """Invalid PBKDF2 argument (unknown hash, non-positive iterations, ...)."""


def pbkdf2_hmac(hash_name: str, password: bytes, salt: bytes,
                iterations: int, dklen: int | None = None) -> bytes:
    """Derive a key from *password* and *salt* with PBKDF2-HMAC (RFC 8018)."""
    try:
        prf = getattr(hashlib, hash_name)
        hlen = prf().digest_size
    except AttributeError:
        raise PBKDF2Error(f"unknown hash {hash_name!r}")
    if not isinstance(password, (bytes, bytearray)) or not isinstance(salt, (bytes, bytearray)):
        raise PBKDF2Error("password and salt must be bytes")
    if not isinstance(iterations, int) or isinstance(iterations, bool) or iterations < 1:
        raise PBKDF2Error("iterations must be a positive int")
    if dklen is None:
        dklen = hlen
    if not isinstance(dklen, int) or isinstance(dklen, bool) or dklen < 1:
        raise PBKDF2Error("dklen must be a positive int")

    password = bytes(password)
    derived = bytearray()
    block_index = 1
    while len(derived) < dklen:
        u = hmac.new(password, bytes(salt) + block_index.to_bytes(4, "big"), prf).digest()
        t = bytearray(u)
        for _ in range(iterations - 1):
            u = hmac.new(password, u, prf).digest()
            for k in range(hlen):
                t[k] ^= u[k]
        derived += t
        block_index += 1
    return bytes(derived[:dklen])
