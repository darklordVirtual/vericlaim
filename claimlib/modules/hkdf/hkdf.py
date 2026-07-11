# SPDX-License-Identifier: Apache-2.0
"""HKDF -- HMAC-based key derivation function (RFC 5869).

A pre-verified claimlib code artifact for key derivation (the KDF used by TLS 1.3
and the Signal protocol). HKDF is a two-step extract-then-expand construction:
Extract computes a pseudorandom key PRK = HMAC(salt, IKM); Expand stretches PRK
into output keying material via T(i) = HMAC(PRK, T(i-1) || info || i). This
module implements both steps over an HMAC PRF from ``hmac``/``hashlib``, and that
it reproduces the published RFC 5869 test vectors is registered as a claim and
proven by a committed evidence artifact.

Public API
----------
    extract(salt: bytes, ikm: bytes, hash_name="sha256") -> bytes         # PRK
    expand(prk: bytes, info: bytes, length: int, hash_name="sha256") -> bytes
    hkdf(salt, ikm, info, length, hash_name="sha256") -> bytes            # OKM

    >>> hkdf(bytes.fromhex("000102030405060708090a0b0c"),
    ...      b"\\x0b" * 22, bytes.fromhex("f0f1f2f3f4f5f6f7f8f9"), 42).hex()[:16]
    '3cb25f25faacd57a'
"""
from __future__ import annotations

import hashlib
import hmac


class HKDFError(ValueError):
    """Invalid HKDF argument (unknown hash, bad length, ...)."""


def _prf(hash_name: str):
    try:
        prf = getattr(hashlib, hash_name)
        prf().digest_size
    except AttributeError:
        raise HKDFError(f"unknown hash {hash_name!r}")
    return prf


def extract(salt: bytes, ikm: bytes, hash_name: str = "sha256") -> bytes:
    """HKDF-Extract: return PRK = HMAC-Hash(salt, IKM). Empty salt -> all zeros."""
    prf = _prf(hash_name)
    if not isinstance(ikm, (bytes, bytearray)) or not isinstance(salt, (bytes, bytearray)):
        raise HKDFError("salt and ikm must be bytes")
    if len(salt) == 0:
        salt = b"\x00" * prf().digest_size
    return hmac.new(bytes(salt), bytes(ikm), prf).digest()


def expand(prk: bytes, info: bytes, length: int, hash_name: str = "sha256") -> bytes:
    """HKDF-Expand: stretch *prk* into *length* bytes of output keying material."""
    prf = _prf(hash_name)
    hlen = prf().digest_size
    if not isinstance(prk, (bytes, bytearray)) or not isinstance(info, (bytes, bytearray)):
        raise HKDFError("prk and info must be bytes")
    if not isinstance(length, int) or isinstance(length, bool) or length < 1:
        raise HKDFError("length must be a positive int")
    if length > 255 * hlen:
        raise HKDFError(f"length must be <= {255 * hlen} for {hash_name}")
    okm = bytearray()
    block = b""
    counter = 1
    while len(okm) < length:
        block = hmac.new(bytes(prk), block + bytes(info) + bytes([counter]), prf).digest()
        okm += block
        counter += 1
    return bytes(okm[:length])


def hkdf(salt: bytes, ikm: bytes, info: bytes, length: int,
         hash_name: str = "sha256") -> bytes:
    """Full HKDF: extract a PRK from (salt, ikm) then expand to *length* bytes."""
    return expand(extract(salt, ikm, hash_name), info, length, hash_name)
