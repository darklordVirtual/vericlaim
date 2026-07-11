# SPDX-License-Identifier: Apache-2.0
"""BGP AS-path parsing and ASN classification (RFC 6996 / 7300 / 5398 / 7607).

A pre-verified claimlib code artifact for the ISP routing control plane. It
parses an AS_SEQUENCE, measures its length, finds the origin AS, and classifies
an Autonomous System Number as private, reserved, or public per the IANA/RFC
allocations. That the classification matches the published ranges is registered
as a claim and proven by a committed evidence artifact.

Ranges (independently defined by the RFCs):
    private:  64512-65534 (RFC 6996) and 4200000000-4294967294 (RFC 6996)
    reserved: 0 (RFC 7607), 23456 AS_TRANS (RFC 6793), 65535 & 4294967295
              (RFC 7300), 64496-64511 & 65536-65551 documentation (RFC 5398)
    public:   any other valid 0..4294967295 ASN

Public API
----------
    parse(path: str) -> list[int]         # "65001 174 3356" -> [65001, 174, 3356]
    path_length(path) -> int
    origin(path) -> int                   # the originating (rightmost) AS
    is_private(asn: int) -> bool
    is_reserved(asn: int) -> bool
    is_public(asn: int) -> bool
    strip_private(path) -> list[int]

    >>> is_private(64512), is_reserved(65535), is_public(15169)
    (True, True, True)
"""
from __future__ import annotations

from collections.abc import Sequence

_ASN_MAX = (1 << 32) - 1


class ASPathError(ValueError):
    """The AS-path or ASN is malformed / out of the 0..4294967295 range."""


def _check_asn(asn: int) -> int:
    if not isinstance(asn, int) or isinstance(asn, bool) or not 0 <= asn <= _ASN_MAX:
        raise ASPathError(f"ASN must be 0..{_ASN_MAX}, got {asn!r}")
    return asn


def parse(path: str) -> list[int]:
    """Parse a whitespace-separated AS_SEQUENCE into a list of ASNs."""
    if not isinstance(path, str):
        raise ASPathError("expected a string")
    out = []
    for token in path.split():
        if not token.isdigit():
            raise ASPathError(f"non-numeric ASN {token!r}")
        out.append(_check_asn(int(token)))
    return out


def path_length(path: Sequence[int]) -> int:
    """Return the number of ASNs in the sequence (AS-path length)."""
    return len(path)


def origin(path: Sequence[int]) -> int:
    """Return the origin AS (the last / rightmost ASN in the sequence)."""
    if len(path) == 0:
        raise ASPathError("empty AS-path has no origin")
    return _check_asn(path[-1])


def is_private(asn: int) -> bool:
    """Return True iff *asn* is in an RFC 6996 private-use range."""
    _check_asn(asn)
    return 64512 <= asn <= 65534 or 4200000000 <= asn <= 4294967294


def is_reserved(asn: int) -> bool:
    """Return True iff *asn* is reserved (AS0, AS_TRANS, last-ASN, or doc)."""
    _check_asn(asn)
    return (asn in (0, 23456, 65535, 4294967295)
            or 64496 <= asn <= 64511
            or 65536 <= asn <= 65551)


def is_public(asn: int) -> bool:
    """Return True iff *asn* is a normal, globally-routable public ASN."""
    return not (is_private(asn) or is_reserved(asn))


def strip_private(path: Sequence[int]) -> list[int]:
    """Return *path* with all private ASNs removed (simple filter)."""
    return [asn for asn in path if not is_private(_check_asn(asn))]
