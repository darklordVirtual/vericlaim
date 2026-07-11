# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-IPCHECKSUM-001 -- the Internet checksum reproduces the
published IPv4-header value and agrees with an independent implementation.

Two independent references:
  1. Published: the worked IPv4 header checksum example (Wikipedia "IPv4 header
     checksum") -- header 4500 0073 0000 4000 4011 0000 c0a8 0001 c0a8 00c7 (the
     checksum field zeroed) has checksum 0xb861. Inserting 0xb861 into the field
     must then verify (checksum over the whole header == 0). This constant is
     hand-written from the reference, not produced by the module.
  2. Independent implementation: a from-scratch struct-based checksum (a
     different code path from the module's byte loop) must agree with the module
     on every byte string in a fixed battery -- empty, odd and even lengths,
     all-zero and all-0xFF, and every single byte value 0..255.

Every reference that matches its independent expected value counts toward
reference_vectors_matched. Deterministic: same artifact on every run.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (ipchecksum.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from ipchecksum import checksum, checksum_bytes, verify  # noqa: E402
from _util import emit  # noqa: E402


def checksum_oracle(data: bytes) -> int:
    """Independent RFC 1071 checksum via struct (different code path)."""
    if len(data) & 1:
        data = data + b"\x00"
    total = sum(struct.unpack(f">{len(data) // 2}H", data)) if data else 0
    total = (total & 0xFFFF) + (total >> 16)
    total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


IPV4_HEADER_NO_CKSUM = bytes.fromhex(
    "45000073000040004011" "0000c0a80001c0a800c7")
PUBLISHED_CHECKSUM = 0xB861

CROSSCHECK = [
    b"",
    b"\x00",
    b"\xff",
    b"a",
    b"abc",
    b"abcd",
    b"\x00" * 20,
    b"\xff" * 20,
    IPV4_HEADER_NO_CKSUM,
    bytes(range(256)),
]
CROSSCHECK += [bytes([b]) for b in range(256)]


def run() -> dict:
    matched = 0
    # 1. Published IPv4 header checksum.
    published_ok = (checksum(IPV4_HEADER_NO_CKSUM) == PUBLISHED_CHECKSUM)
    matched += int(published_ok)
    # Inserting the checksum makes the full header verify.
    full_header = (IPV4_HEADER_NO_CKSUM[:10] + checksum_bytes(IPV4_HEADER_NO_CKSUM)
                   + IPV4_HEADER_NO_CKSUM[12:])
    verify_ok = verify(full_header)
    matched += int(verify_ok)

    # 2. Agreement with the independent oracle.
    cross_matched = 0
    for data in CROSSCHECK:
        if checksum(data) == checksum_oracle(data):
            cross_matched += 1
    matched += cross_matched

    reference_vectors = 2 + len(CROSSCHECK)   # published value + verify + crosschecks
    return {
        "schema": "claimlib_ipchecksum_v1",
        "module": "ipchecksum",
        "reference_vectors": reference_vectors,
        "reference_vectors_matched": matched,
        "mismatches": reference_vectors - matched,
        "published_checksum": PUBLISHED_CHECKSUM,
        "published_ok": published_ok,
        "verify_ok": verify_ok,
        "crosscheck_vectors": len(CROSSCHECK),
        "crosscheck_matched": cross_matched,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "ipchecksum.json", obj,
         script="python3 claimlib/modules/ipchecksum/evidence.py")
    # claim:CLAIM-LIB-IPCHECKSUM-001 reference_vectors_matched
    # The published 0xb861 value, the verify round-trip, and 266 oracle
    # cross-checks all match, so reference_vectors_matched = 268, mismatches = 0.
    print(f"ipchecksum: {obj['reference_vectors_matched']}/{obj['reference_vectors']} "
          f"reference vectors reproduced ({obj['mismatches']} mismatches); "
          f"published 0xb861 ok={obj['published_ok']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
