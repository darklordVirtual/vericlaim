# SPDX-License-Identifier: Apache-2.0
"""IEEE 802.1Q VLAN ID validation and compact range parsing.

A pre-verified claimlib code artifact for switch / ISP L2 management. An 802.1Q
VLAN ID is a 12-bit field, but only 1..4094 are assignable: 0 marks a
priority-tagged (untagged) frame and 4095 is reserved. This module validates VIDs
and parses / formats the compact ``"1,10-12,4094"`` range notation used in switch
configs. That its validity rule matches the 802.1Q reservations and that range
parse/format round-trips is registered as a claim and proven by a committed
evidence artifact.

Public API
----------
    is_valid(vid: int) -> bool                 # True iff 1 <= vid <= 4094
    parse_range(text: str) -> list[int]        # "1,10-12" -> [1, 10, 11, 12]
    format_range(vids: Iterable[int]) -> str   # [1,10,11,12] -> "1,10-12"

    >>> parse_range("1,10-12,4094")
    [1, 10, 11, 12, 4094]
    >>> format_range([1, 10, 11, 12, 4094])
    '1,10-12,4094'
"""
from __future__ import annotations

from collections.abc import Iterable

VID_MIN = 1
VID_MAX = 4094


class VLANError(ValueError):
    """A VLAN ID or range string outside the assignable 1..4094 space."""


def is_valid(vid: int) -> bool:
    """Return True iff *vid* is an assignable 802.1Q VLAN ID (1..4094)."""
    return isinstance(vid, int) and not isinstance(vid, bool) and VID_MIN <= vid <= VID_MAX


def parse_range(text: str) -> list[int]:
    """Parse a ``"a,b-c,d"`` VLAN range list into a sorted, de-duplicated list."""
    if not isinstance(text, str):
        raise VLANError("expected a string")
    vids: set[int] = set()
    for token in text.split(","):
        token = token.strip()
        if not token:
            raise VLANError("empty range token")
        if "-" in token:
            lo_s, _, hi_s = token.partition("-")
            if not (lo_s.isdigit() and hi_s.isdigit()):
                raise VLANError(f"bad range {token!r}")
            lo, hi = int(lo_s), int(hi_s)
            if lo > hi:
                raise VLANError(f"descending range {token!r}")
            for vid in range(lo, hi + 1):
                if not is_valid(vid):
                    raise VLANError(f"VLAN {vid} out of range in {token!r}")
                vids.add(vid)
        else:
            if not token.isdigit():
                raise VLANError(f"bad VLAN {token!r}")
            vid = int(token)
            if not is_valid(vid):
                raise VLANError(f"VLAN {vid} out of range")
            vids.add(vid)
    return sorted(vids)


def format_range(vids: Iterable[int]) -> str:
    """Render a set of VIDs as a compact ``"a,b-c"`` range list (runs collapsed)."""
    ordered = sorted(set(vids))
    for vid in ordered:
        if not is_valid(vid):
            raise VLANError(f"VLAN {vid} out of range")
    parts = []
    i = 0
    while i < len(ordered):
        j = i
        while j + 1 < len(ordered) and ordered[j + 1] == ordered[j] + 1:
            j += 1
        if j > i:
            parts.append(f"{ordered[i]}-{ordered[j]}")
        else:
            parts.append(str(ordered[i]))
        i = j + 1
    return ",".join(parts)
