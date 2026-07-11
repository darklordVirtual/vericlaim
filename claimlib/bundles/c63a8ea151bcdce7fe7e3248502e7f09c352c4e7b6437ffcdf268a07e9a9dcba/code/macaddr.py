# SPDX-License-Identifier: Apache-2.0
"""MAC / EUI-48 address parsing, normalization, and IEEE 802 bit flags.

A pre-verified claimlib code artifact: a reusable, stdlib-only building block for
the L2 management plane. It parses the common MAC notations (colon, hyphen,
Cisco dotted, and bare hex), renders the canonical lowercase colon form, and
decodes the two IEEE 802 low bits of the first octet -- the I/G (multicast) and
U/L (locally administered) bits. That its flag decoding matches the IEEE
definitions and that all four notations parse to the same value is registered as
a claim and proven by a committed evidence artifact.

Public API
----------
    parse(s: str) -> int                       # any notation -> 48-bit int
    format_mac(value: int, sep: str = ":") -> str
    is_multicast(value: int) -> bool           # I/G bit (bit 0 of first octet)
    is_unicast(value: int) -> bool
    is_locally_administered(value: int) -> bool # U/L bit (bit 1 of first octet)
    is_broadcast(value: int) -> bool           # all ones
    oui(value: int) -> int                     # top 24 bits (vendor prefix)

    >>> is_multicast(parse("01:00:5e:00:00:fb"))
    True
    >>> format_mac(parse("aabb.ccdd.eeff"))
    'aa:bb:cc:dd:ee:ff'
"""
from __future__ import annotations

_U48 = (1 << 48) - 1
_HEX = set("0123456789abcdef")


class MACError(ValueError):
    """The input is not a recognizable 48-bit MAC address."""


def parse(value: str) -> int:
    """Parse a MAC in colon, hyphen, Cisco-dotted, or bare-hex notation."""
    if not isinstance(value, str):
        raise MACError("expected a string")
    text = value.strip().lower()
    if ":" in text:
        groups, width = text.split(":"), 2
    elif "-" in text:
        groups, width = text.split("-"), 2
    elif "." in text:
        groups, width = text.split("."), 4
    else:
        groups, width = [text], 12
    expected_groups = 12 // width
    if len(groups) != expected_groups:
        raise MACError(f"expected {expected_groups} groups in {value!r}")
    digits = ""
    for g in groups:
        if len(g) != width or any(c not in _HEX for c in g):
            raise MACError(f"bad group {g!r} in {value!r}")
        digits += g
    return int(digits, 16)


def _check(value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= _U48:
        raise MACError("value must be a 48-bit unsigned integer")
    return value


def format_mac(value: int, sep: str = ":") -> str:
    """Render *value* as a canonical lowercase MAC with *sep* between octets."""
    _check(value)
    octets = [f"{(value >> shift) & 0xFF:02x}" for shift in range(40, -1, -8)]
    return sep.join(octets)


def _first_octet(value: int) -> int:
    return (_check(value) >> 40) & 0xFF


def is_multicast(value: int) -> bool:
    """Return True iff the I/G (group) bit is set -- a multicast/broadcast MAC."""
    return bool(_first_octet(value) & 0x01)


def is_unicast(value: int) -> bool:
    """Return True iff the address is unicast (I/G bit clear)."""
    return not is_multicast(value)


def is_locally_administered(value: int) -> bool:
    """Return True iff the U/L bit is set -- a locally administered address."""
    return bool(_first_octet(value) & 0x02)


def is_broadcast(value: int) -> bool:
    """Return True iff the address is the L2 broadcast ff:ff:ff:ff:ff:ff."""
    return _check(value) == _U48


def oui(value: int) -> int:
    """Return the 24-bit Organizationally Unique Identifier (vendor prefix)."""
    return (_check(value) >> 24) & 0xFFFFFF
