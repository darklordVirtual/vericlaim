# SPDX-License-Identifier: Apache-2.0
"""IPv4 CIDR / subnet math -- the core of ISP IP address management (IPAM).

A pre-verified claimlib code artifact: a reusable, stdlib-only building block
that implements IPv4 addressing arithmetic DIRECTLY on the 32-bit integer (it
does NOT import :mod:`ipaddress`), so it is a genuine second implementation. The
property that makes it trustworthy -- that its parsing, network/broadcast, host
count, membership and range agree with Python's stdlib ``ipaddress`` over a
fixed battery -- is registered as a claim and proven by a committed evidence
artifact. Vendoring carries that claim (and its caveat).

This is the everyday management-plane primitive on routers and ISP gear: given
``192.0.2.0/24`` decide the network, the broadcast, how many usable hosts, and
whether a given address falls inside.

Public API
----------
    parse_ip(s: str) -> int                 # dotted-quad -> 32-bit int
    ip_to_str(value: int) -> str            # 32-bit int -> dotted-quad
    parse_cidr(s: str) -> tuple[int, int]   # "a.b.c.d/p" -> (network_int, prefix)
    netmask(prefix: int) -> int
    network_address(ip: int, prefix: int) -> int
    broadcast_address(ip: int, prefix: int) -> int
    num_addresses(prefix: int) -> int
    num_usable_hosts(prefix: int) -> int
    host_range(ip: int, prefix: int) -> tuple[int, int]
    contains(network_ip: int, prefix: int, ip: int) -> bool

    >>> ip_to_str(broadcast_address(parse_ip("192.0.2.10"), 24))
    '192.0.2.255'
    >>> num_usable_hosts(24)
    254
"""
from __future__ import annotations

_U32 = 0xFFFFFFFF


class CIDRError(ValueError):
    """The input is not a valid IPv4 address, prefix, or CIDR string."""


def parse_ip(s: str) -> int:
    """Parse a dotted-quad IPv4 string into a 32-bit integer (fail closed)."""
    if not isinstance(s, str):
        raise CIDRError("expected a string")
    parts = s.split(".")
    if len(parts) != 4:
        raise CIDRError(f"IPv4 address needs 4 octets: {s!r}")
    value = 0
    for part in parts:
        if not part.isdigit() or (len(part) > 1 and part[0] == "0"):
            # reject empty, non-digit, and leading-zero octets (ambiguous/octal)
            raise CIDRError(f"bad octet {part!r} in {s!r}")
        octet = int(part)
        if octet > 255:
            raise CIDRError(f"octet out of range {octet} in {s!r}")
        value = (value << 8) | octet
    return value


def ip_to_str(value: int) -> str:
    """Render a 32-bit integer as a dotted-quad IPv4 string."""
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= _U32:
        raise CIDRError("value must be a 32-bit unsigned integer")
    return ".".join(str((value >> shift) & 0xFF) for shift in (24, 16, 8, 0))


def _check_prefix(prefix: int) -> int:
    if not isinstance(prefix, int) or isinstance(prefix, bool) or not 0 <= prefix <= 32:
        raise CIDRError(f"IPv4 prefix must be 0..32, got {prefix!r}")
    return prefix


def parse_cidr(s: str) -> tuple[int, int]:
    """Parse ``"a.b.c.d/p"`` into ``(network_int, prefix)`` (host bits masked)."""
    if not isinstance(s, str) or s.count("/") != 1:
        raise CIDRError(f"expected 'a.b.c.d/prefix', got {s!r}")
    addr, _, pfx = s.partition("/")
    if not pfx.isdigit():
        raise CIDRError(f"bad prefix in {s!r}")
    prefix = _check_prefix(int(pfx))
    return network_address(parse_ip(addr), prefix), prefix


def netmask(prefix: int) -> int:
    """Return the 32-bit subnet mask for *prefix* (e.g. 24 -> 255.255.255.0)."""
    _check_prefix(prefix)
    return (_U32 << (32 - prefix)) & _U32 if prefix else 0


def network_address(ip: int, prefix: int) -> int:
    """Return the network address (host bits cleared)."""
    return ip & netmask(prefix)


def broadcast_address(ip: int, prefix: int) -> int:
    """Return the directed broadcast address (host bits set)."""
    return network_address(ip, prefix) | (~netmask(prefix) & _U32)


def num_addresses(prefix: int) -> int:
    """Total addresses in the block, including network and broadcast."""
    _check_prefix(prefix)
    return 1 << (32 - prefix)


def num_usable_hosts(prefix: int) -> int:
    """Usable host addresses: block size minus network+broadcast for /0../30.

    /31 (RFC 3021 point-to-point) has 2 usable; /32 has 1 (a single host).
    """
    _check_prefix(prefix)
    if prefix == 32:
        return 1
    if prefix == 31:
        return 2
    return (1 << (32 - prefix)) - 2


def host_range(ip: int, prefix: int) -> tuple[int, int]:
    """Return (first_usable, last_usable) host address in the block."""
    net = network_address(ip, prefix)
    bcast = broadcast_address(ip, prefix)
    if prefix >= 31:
        return net, bcast
    return net + 1, bcast - 1


def contains(network_ip: int, prefix: int, ip: int) -> bool:
    """Return True iff *ip* lies within the block defined by (network_ip, prefix)."""
    return network_address(ip, prefix) == network_address(network_ip, prefix)
