# SPDX-License-Identifier: Apache-2.0
"""ChaCha20 stream cipher (RFC 8439) implemented from scratch -- reusable,
claim-bound.

A pre-verified claimlib code artifact. This module computes the ChaCha20 block
function and stream encryption DIRECTLY (the 4x4 32-bit state, the
add/xor/rotate quarter round, 20 rounds as 10 column/diagonal double rounds,
little-endian serialization, and per-block counter increment) using nothing but
pure integer arithmetic -- no cryptography libraries. That it reproduces the
published RFC 8439 test vectors (the section 2.1.1/2.2.1 quarter-round vectors,
the section 2.3.2 block-function keystream, the section 2.4.2 "sunscreen"
ciphertext, and all Appendix A.1/A.2 vectors) is registered as a claim and
proven by a committed evidence artifact. Vendoring carries that claim (and its
caveat) with it.

ChaCha20 (D. J. Bernstein's ChaCha with the IETF 96-bit-nonce / 32-bit-counter
layout of RFC 8439) is the stream cipher used by TLS 1.3, WireGuard, OpenSSH
and age. Encryption and decryption are the same operation: XOR the message
with the keystream generated from (key, counter, nonce).

SECURITY: ChaCha20 alone provides confidentiality ONLY -- no integrity. An
attacker can flip any ciphertext bit and flip the same plaintext bit. Use an
AEAD (ChaCha20-Poly1305) for real protocols, and NEVER reuse a (key, nonce)
pair: two messages encrypted under the same key and nonce leak their XOR.

Public API
----------
    quarter_round(a, b, c, d) -> (a, b, c, d)   # RFC 8439 section 2.1
    chacha20_block(key, counter, nonce) -> bytes    # 64-byte keystream block
    chacha20_encrypt(key, counter, nonce, plaintext) -> bytes
    chacha20_decrypt(key, counter, nonce, ciphertext) -> bytes

    key is exactly 32 bytes, nonce exactly 12 bytes, counter a 32-bit int.

    >>> chacha20_block(bytes(32), 0, bytes(12))[:8].hex()
    '76b8e0ada0f13d90'
"""
from __future__ import annotations

_MASK = 0xFFFFFFFF

# "expand 32-byte k" as four little-endian 32-bit words (RFC 8439 section 2.3).
_CONSTANTS = (0x61707865, 0x3320646E, 0x79622D32, 0x6B206574)


class ChaCha20Error(ValueError):
    """Invalid key / nonce / counter / message input (fail closed)."""


def _rotl(value: int, bits: int) -> int:
    return ((value << bits) & _MASK) | (value >> (32 - bits))


def _qr(s: list, ia: int, ib: int, ic: int, id_: int) -> None:
    """One quarter round on state words ia, ib, ic, id_ (in place)."""
    a, b, c, d = s[ia], s[ib], s[ic], s[id_]
    a = (a + b) & _MASK
    d = _rotl(d ^ a, 16)
    c = (c + d) & _MASK
    b = _rotl(b ^ c, 12)
    a = (a + b) & _MASK
    d = _rotl(d ^ a, 8)
    c = (c + d) & _MASK
    b = _rotl(b ^ c, 7)
    s[ia], s[ib], s[ic], s[id_] = a, b, c, d


def quarter_round(a: int, b: int, c: int, d: int) -> tuple:
    """The ChaCha quarter round (RFC 8439 section 2.1) on four 32-bit words.

    a += b; d ^= a; d <<<= 16;
    c += d; b ^= c; b <<<= 12;
    a += b; d ^= a; d <<<= 8;
    c += d; b ^= c; b <<<= 7;
    """
    for word in (a, b, c, d):
        if not isinstance(word, int) or isinstance(word, bool) \
                or not 0 <= word <= _MASK:
            raise ChaCha20Error("quarter-round words must be ints in "
                                "[0, 2**32 - 1]")
    s = [a, b, c, d]
    _qr(s, 0, 1, 2, 3)
    return tuple(s)


def _check_inputs(key: bytes, counter: int, nonce: bytes) -> None:
    if not isinstance(key, (bytes, bytearray)) or len(key) != 32:
        raise ChaCha20Error("key must be exactly 32 bytes")
    if not isinstance(nonce, (bytes, bytearray)) or len(nonce) != 12:
        raise ChaCha20Error("nonce must be exactly 12 bytes (the IETF "
                            "RFC 8439 layout, not the original 8-byte one)")
    if not isinstance(counter, int) or isinstance(counter, bool) \
            or not 0 <= counter <= _MASK:
        raise ChaCha20Error("counter must be an int in [0, 2**32 - 1]")


def chacha20_block(key: bytes, counter: int, nonce: bytes) -> bytes:
    """Return one 64-byte keystream block (RFC 8439 section 2.3).

    State layout (16 little-endian 32-bit words):
      words 0-3   the constants "expand 32-byte k"
      words 4-11  the 256-bit key
      word  12    the 32-bit block counter
      words 13-15 the 96-bit nonce
    20 rounds (10 column + 10 diagonal, interleaved), then the original state
    is added word-wise and the result serialized little-endian.
    """
    _check_inputs(key, counter, nonce)
    state = [
        _CONSTANTS[0], _CONSTANTS[1], _CONSTANTS[2], _CONSTANTS[3],
        *(int.from_bytes(key[i:i + 4], "little") for i in range(0, 32, 4)),
        counter,
        *(int.from_bytes(nonce[i:i + 4], "little") for i in range(0, 12, 4)),
    ]
    w = list(state)
    for _ in range(10):
        _qr(w, 0, 4, 8, 12)     # column rounds
        _qr(w, 1, 5, 9, 13)
        _qr(w, 2, 6, 10, 14)
        _qr(w, 3, 7, 11, 15)
        _qr(w, 0, 5, 10, 15)    # diagonal rounds
        _qr(w, 1, 6, 11, 12)
        _qr(w, 2, 7, 8, 13)
        _qr(w, 3, 4, 9, 14)
    return b"".join(((w[i] + state[i]) & _MASK).to_bytes(4, "little")
                    for i in range(16))


def chacha20_encrypt(key: bytes, counter: int, nonce: bytes,
                     plaintext: bytes) -> bytes:
    """Encrypt *plaintext* with the ChaCha20 keystream (RFC 8439 section 2.4).

    Block j is XORed with chacha20_block(key, counter + j, nonce); the last
    (possibly partial) block discards unused keystream. The 32-bit block
    counter is NOT allowed to wrap: a message that would need a block counter
    above 2**32 - 1 raises ChaCha20Error (RFC 8439 defines no wrap semantics).
    """
    _check_inputs(key, counter, nonce)
    if not isinstance(plaintext, (bytes, bytearray)):
        raise ChaCha20Error("plaintext must be bytes or bytearray")
    n_blocks = (len(plaintext) + 63) // 64
    if n_blocks and counter + n_blocks - 1 > _MASK:
        raise ChaCha20Error("message too long for this initial counter: the "
                            "32-bit block counter would overflow")
    out = bytearray()
    for j in range(n_blocks):
        keystream = chacha20_block(key, counter + j, nonce)
        block = plaintext[j * 64:(j + 1) * 64]
        out += bytes(p ^ k for p, k in zip(bytes(block), keystream))
    return bytes(out)


def chacha20_decrypt(key: bytes, counter: int, nonce: bytes,
                     ciphertext: bytes) -> bytes:
    """Decrypt: the identical keystream-XOR operation (RFC 8439 section 2.4)."""
    return chacha20_encrypt(key, counter, nonce, ciphertext)
