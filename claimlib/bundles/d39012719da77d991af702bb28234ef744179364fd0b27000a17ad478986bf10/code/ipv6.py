# SPDX-License-Identifier: Apache-2.0
"""IPv6 address parsing, RFC 5952 canonical compression, and prefix math.

A pre-verified claimlib code artifact: a reusable, stdlib-only building block
that parses IPv6 and produces the RFC 5952 canonical text form DIRECTLY (it does
NOT import :mod:`ipaddress`), so it is a genuine second implementation. The
property that makes it trustworthy -- that its parse/compress/explode and prefix
math agree with Python's stdlib ``ipaddress`` over a fixed battery -- is
registered as a claim and proven by a committed evidence artifact.

RFC 5952 canonical form: lowercase hex, no leading zeros in a group, and the
single longest run of consecutive all-zero groups (length >= 2, leftmost on a
tie) replaced by ``::`` (a single zero group is never shortened to ``::``).

Public API
----------
    parse(s: str) -> int                    # IPv6 text -> 128-bit int
    compress(value: int) -> str             # 128-bit int -> RFC 5952 text
    explode(value: int) -> str              # full 8x4 hex form
    parse_cidr(s: str) -> tuple[int, int]   # "addr/prefix" -> (network_int, prefix)
    network_address(value: int, prefix: int) -> int
    num_addresses(prefix: int) -> int

    >>> compress(parse("2001:0db8:0000:0000:0000:ff00:0042:8329"))
    '2001:db8::ff00:42:8329'
"""
from __future__ import annotations

_U128 = (1 << 128) - 1


class IPv6Error(ValueError):
    """The input is not a valid (non-dotted) IPv6 address, prefix, or CIDR."""


def _groups_to_int(groups: list[str]) -> int:
    if len(groups) != 8:
        raise IPv6Error("IPv6 must resolve to 8 groups")
    value = 0
    for g in groups:
        if not (1 <= len(g) <= 4):
            raise IPv6Error(f"bad group {g!r}")
        try:
            part = int(g, 16)
        except ValueError:
            raise IPv6Error(f"non-hex group {g!r}")
        value = (value << 16) | part
    return value


def parse(value: str) -> int:
    """Parse an IPv6 string (with optional ``::``) into a 128-bit integer.

    Dotted-quad IPv4 embedding (e.g. ``::ffff:192.0.2.1``) is out of scope.
    """
    if not isinstance(value, str) or value == "":
        raise IPv6Error("expected a non-empty string")
    if "." in value:
        raise IPv6Error("dotted IPv4-embedded IPv6 is out of scope")
    if value.count("::") > 1:
        raise IPv6Error("'::' may appear at most once")
    if "::" in value:
        left, _, right = value.partition("::")
        lg = left.split(":") if left else []
        rg = right.split(":") if right else []
        if len(lg) + len(rg) > 7:
            raise IPv6Error("'::' must elide at least one group")
        groups = lg + ["0"] * (8 - len(lg) - len(rg)) + rg
    else:
        groups = value.split(":")
    return _groups_to_int(groups)


def _to_groups(value: int) -> list[int]:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= _U128:
        raise IPv6Error("value must be a 128-bit unsigned integer")
    return [(value >> shift) & 0xFFFF for shift in range(112, -1, -16)]


def compress(value: int) -> str:
    """Return the RFC 5952 canonical compressed text form of *value*."""
    groups = _to_groups(value)
    hexs = [format(g, "x") for g in groups]
    best_start, best_len = -1, 0
    i = 0
    while i < 8:
        if groups[i] == 0:
            j = i
            while j < 8 and groups[j] == 0:
                j += 1
            if j - i > best_len:                 # strict '>' keeps the leftmost tie
                best_start, best_len = i, j - i
            i = j
        else:
            i += 1
    if best_len >= 2:
        left = ":".join(hexs[:best_start])
        right = ":".join(hexs[best_start + best_len:])
        return f"{left}::{right}"
    return ":".join(hexs)


def explode(value: int) -> str:
    """Return the fully-expanded 8-group, 4-hex-digit form of *value*."""
    return ":".join(format(g, "04x") for g in _to_groups(value))


def _check_prefix(prefix: int) -> int:
    if not isinstance(prefix, int) or isinstance(prefix, bool) or not 0 <= prefix <= 128:
        raise IPv6Error(f"IPv6 prefix must be 0..128, got {prefix!r}")
    return prefix


def parse_cidr(value: str) -> tuple[int, int]:
    """Parse ``"addr/prefix"`` into ``(network_int, prefix)`` (host bits masked)."""
    if not isinstance(value, str) or value.count("/") != 1:
        raise IPv6Error(f"expected 'addr/prefix', got {value!r}")
    addr, _, pfx = value.partition("/")
    if not pfx.isdigit():
        raise IPv6Error(f"bad prefix in {value!r}")
    prefix = _check_prefix(int(pfx))
    return network_address(parse(addr), prefix), prefix


def network_address(value: int, prefix: int) -> int:
    """Return the network address (host bits cleared) for *value* under *prefix*."""
    _check_prefix(prefix)
    mask = (_U128 << (128 - prefix)) & _U128 if prefix else 0
    return value & mask


def num_addresses(prefix: int) -> int:
    """Total addresses in the block (2 ** (128 - prefix))."""
    _check_prefix(prefix)
    return 1 << (128 - prefix)
