# SPDX-License-Identifier: Apache-2.0
"""Punycode (RFC 3492) — Bootstring encoding for Internationalized Domain Names.

A pre-verified code artifact from the VeriClaim claim library. The property
that makes it trustworthy — that it reproduces every published sample string
of RFC 3492 section 7.1 exactly, in both directions, and agrees with Python's
independent stdlib ``punycode`` codec — is registered as a claim and proven by
a committed evidence artifact; vendoring this module carries that claim (and
its caveat) with it.

Punycode is the Bootstring algorithm instantiated with the DNS parameters
(RFC 3492 section 5): base 36, tmin 1, tmax 26, skew 38, damp 700,
initial_bias 72, initial_n 128, delimiter "-". It maps any Unicode string to
a unique ASCII string and back, and is the encoding underneath IDNA's
"xn--" A-labels (this module handles the raw Punycode transform only — it
does NOT add or strip the "xn--" ACE prefix and performs no IDNA
normalization).

Per RFC 3492 section 5 the encoder emits only lowercase digit letters, and
the decoder accepts digits in either case (mixed-case annotation, appendix A,
is intentionally not implemented — IDNA does not use it).

Public API
----------
    encode(text: str) -> str   # Unicode -> Punycode (no "xn--" prefix)
    decode(text: str) -> str   # Punycode -> Unicode

    >>> encode("bücher")
    'bcher-kva'
    >>> decode("bcher-kva")
    'bücher'
"""
from __future__ import annotations

# Bootstring parameter values for Punycode (RFC 3492 section 5).
BASE = 36
TMIN = 1
TMAX = 26
SKEW = 38
DAMP = 700
INITIAL_BIAS = 72
INITIAL_N = 128            # 0x80: first non-basic code point
DELIMITER = "-"

# Python ints are unbounded, so "fail on overflow" (RFC 3492 section 6.4)
# needs an explicit ceiling. The reference implementation in appendix C uses
# an unsigned 32-bit punycode_uint; we adopt the same maxint.
_MAXINT = 2**32 - 1
_MAX_CODEPOINT = 0x10FFFF  # highest Unicode code point


class PunycodeError(ValueError):
    """The input cannot be encoded/decoded as RFC 3492 Punycode."""


def _adapt(delta: int, numpoints: int, firsttime: bool) -> int:
    """Bias adaptation function (RFC 3492 section 6.1)."""
    delta = delta // DAMP if firsttime else delta // 2
    delta += delta // numpoints
    k = 0
    while delta > ((BASE - TMIN) * TMAX) // 2:
        delta //= BASE - TMIN
        k += BASE
    return k + ((BASE - TMIN + 1) * delta) // (delta + SKEW)


def _encode_digit(d: int) -> str:
    """Digit value 0..35 -> lowercase basic code point (RFC 3492 section 5)."""
    if 0 <= d <= 25:
        return chr(d + 0x61)       # 0..25  -> 'a'..'z'
    if 26 <= d <= 35:
        return chr(d - 26 + 0x30)  # 26..35 -> '0'..'9'
    raise PunycodeError(f"digit value out of range: {d}")


def _digit_value(ch: str) -> int:
    """Basic code point -> digit value; both letter cases accepted."""
    c = ord(ch)
    if 0x41 <= c <= 0x5A:          # 'A'..'Z' -> 0..25
        return c - 0x41
    if 0x61 <= c <= 0x7A:          # 'a'..'z' -> 0..25
        return c - 0x61
    if 0x30 <= c <= 0x39:          # '0'..'9' -> 26..35
        return c - 0x30 + 26
    raise PunycodeError(f"invalid Punycode digit: {ch!r}")


def encode(text: str) -> str:
    """Encode a Unicode string as Punycode (RFC 3492 section 6.3).

    Basic code points (U+0000..U+007F) are copied literally, followed by the
    "-" delimiter iff at least one basic code point was present, followed by
    the delta-encoded non-basic code points using lowercase digits.
    """
    if not isinstance(text, str):
        raise PunycodeError("expected a str to encode")
    cps = [ord(c) for c in text]
    output = [c for c in text if ord(c) < INITIAL_N]
    b = h = len(output)
    if b > 0:
        output.append(DELIMITER)
    n = INITIAL_N
    delta = 0
    bias = INITIAL_BIAS
    while h < len(cps):
        m = min(c for c in cps if c >= n)
        delta += (m - n) * (h + 1)   # cannot overflow: Python ints unbounded
        n = m
        for c in cps:
            if c < n:
                delta += 1
            elif c == n:
                q = delta
                k = BASE
                while True:
                    if k <= bias:
                        t = TMIN
                    elif k >= bias + TMAX:
                        t = TMAX
                    else:
                        t = k - bias
                    if q < t:
                        break
                    output.append(_encode_digit(t + (q - t) % (BASE - t)))
                    q = (q - t) // (BASE - t)
                    k += BASE
                output.append(_encode_digit(q))
                bias = _adapt(delta, h + 1, h == b)
                delta = 0
                h += 1
        delta += 1
        n += 1
    return "".join(output)


def decode(text: str) -> str:
    """Decode a Punycode string to Unicode (RFC 3492 section 6.2).

    The basic string is everything before the LAST delimiter, consumed only
    if it is non-empty (so an input whose only delimiter is its first
    character fails, exactly like the appendix C reference decoder). Digits
    are accepted in either letter case. Fails closed (PunycodeError) on
    non-ASCII input, invalid digits, truncated deltas, arithmetic overflow
    (unsigned 32-bit, as in appendix C) and code points beyond U+10FFFF.
    """
    if not isinstance(text, str):
        raise PunycodeError("expected a str to decode")
    if any(ord(c) >= INITIAL_N for c in text):
        raise PunycodeError("Punycode input must be ASCII (basic code points)")
    d = text.rfind(DELIMITER)
    if d > 0:
        basic, ext = text[:d], text[d + 1:]
    else:
        # No delimiter, or the last delimiter is the first character: zero
        # basic code points were consumed, so the delimiter (if any) is NOT
        # consumed and must decode as a digit (which fails, per appendix C).
        basic, ext = "", text
    output = list(basic)
    n = INITIAL_N
    i = 0
    bias = INITIAL_BIAS
    pos = 0
    while pos < len(ext):
        oldi = i
        w = 1
        k = BASE
        while True:
            if pos >= len(ext):
                raise PunycodeError("truncated Punycode input (incomplete delta)")
            digit = _digit_value(ext[pos])
            pos += 1
            i += digit * w
            if i > _MAXINT:
                raise PunycodeError("overflow decoding delta")
            if k <= bias:
                t = TMIN
            elif k >= bias + TMAX:
                t = TMAX
            else:
                t = k - bias
            if digit < t:
                break
            w *= BASE - t
            if w > _MAXINT:
                raise PunycodeError("overflow decoding delta")
            k += BASE
        npoints = len(output) + 1
        bias = _adapt(i - oldi, npoints, oldi == 0)
        n += i // npoints
        i %= npoints
        if n > _MAX_CODEPOINT:
            raise PunycodeError(f"decoded code point out of range: {n:#x}")
        output.insert(i, chr(n))
        i += 1
    return "".join(output)
