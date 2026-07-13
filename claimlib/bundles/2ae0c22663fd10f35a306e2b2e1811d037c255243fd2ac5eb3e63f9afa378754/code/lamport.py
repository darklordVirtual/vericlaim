# SPDX-License-Identifier: Apache-2.0
"""Lamport one-time signatures -- a hash-based, quantum-resistant signature.

A pre-verified claimlib code artifact. A Lamport signature builds a digital
signature from nothing but a hash function: the private key is 2x256 random
secrets, the public key is their hashes, and signing a 256-bit message digest
reveals, for each message bit, the secret at that bit position. Its security
rests ONLY on the preimage resistance of the hash (here SHA-256), so -- unlike
RSA/ECDSA -- it is not broken by Shor's algorithm and is post-quantum. That
signing then verifying succeeds and that any tampering is rejected is registered
as a claim and proven by a committed evidence artifact.

Public API
----------
    keygen(seed: bytes) -> tuple[list, list]     # (private_key, public_key)
    sign(message: bytes, private_key) -> list[bytes]
    verify(message: bytes, signature, public_key) -> bool
    public_key_bytes(public_key) -> bytes        # 2*256*32 = 16384 bytes

    >>> sk, pk = keygen(b"seed")
    >>> verify(b"hello", sign(b"hello", sk), pk)
    True
"""
from __future__ import annotations

import hashlib

_N = 256           # message digest bits (SHA-256)
_HLEN = 32         # secret / hash length in bytes


class LamportError(ValueError):
    """A malformed key, signature, or non-bytes message."""


def _h(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def keygen(seed: bytes) -> tuple[list, list]:
    """Deterministically derive a Lamport key pair from *seed*.

    Real use needs a cryptographically random seed kept secret; the deterministic
    derivation here makes the evidence reproducible.
    """
    if not isinstance(seed, (bytes, bytearray)):
        raise LamportError("seed must be bytes")
    seed = bytes(seed)
    private = [[_h(seed + bytes([b]) + i.to_bytes(4, "big")) for i in range(_N)]
               for b in range(2)]
    public = [[_h(private[b][i]) for i in range(_N)] for b in range(2)]
    return private, public


def _message_bits(message: bytes) -> list[int]:
    if not isinstance(message, (bytes, bytearray)):
        raise LamportError("message must be bytes")
    digest = _h(bytes(message))
    return [(digest[i // 8] >> (7 - (i % 8))) & 1 for i in range(_N)]


def sign(message: bytes, private_key) -> list[bytes]:
    """Sign *message* with a Lamport *private_key*. USE THE KEY ONLY ONCE."""
    bits = _message_bits(message)
    return [private_key[bits[i]][i] for i in range(_N)]


def verify(message: bytes, signature, public_key) -> bool:
    """Return True iff *signature* is a valid Lamport signature of *message*."""
    try:
        bits = _message_bits(message)
    except LamportError:
        return False
    if not isinstance(signature, (list, tuple)) or len(signature) != _N:
        return False
    for i in range(_N):
        element = signature[i]
        if not isinstance(element, (bytes, bytearray)) or len(element) != _HLEN:
            return False
        if _h(bytes(element)) != public_key[bits[i]][i]:
            return False
    return True


def public_key_bytes(public_key) -> bytes:
    """Serialize a public key to its concatenated 2*256*32-byte form."""
    return b"".join(public_key[b][i] for b in range(2) for i in range(_N))
