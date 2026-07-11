# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-VARINT-001 -- varint reproduces the published LEB128
reference vectors and round-trips losslessly.

Two references:
  1. Published LEB128 vectors (Protocol Buffers / Wikipedia "LEB128"): 0 -> 00,
     1 -> 01, 127 -> 7f, 128 -> 8001, 255 -> ff01, 300 -> ac02, and the classic
     624485 -> e58e26. Each expected byte string is hand-written from the spec.
  2. Round-trip: over a wide range of unsigned values (incl. powers of two and
     64-bit boundaries) decode_uvarint(encode_uvarint(x)) == x, and over a range
     of signed values decode_varint(encode_varint(x)) == x with the documented
     ZigZag mapping (0->0, -1->1, 1->2, -2->3, 2->4). Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (varint.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from varint import (  # noqa: E402
    encode_uvarint, decode_uvarint, encode_varint, decode_varint,
    zigzag_encode, zigzag_decode)
from _util import emit  # noqa: E402

# Published LEB128 vectors (value, hex).
PUBLISHED = [
    (0, "00"), (1, "01"), (127, "7f"), (128, "8001"),
    (255, "ff01"), (300, "ac02"), (624485, "e58e26"),
]
# Published ZigZag mappings (signed, unsigned).
ZIGZAG = [(0, 0), (-1, 1), (1, 2), (-2, 3), (2, 4), (-64, 127), (63, 126)]


def run() -> dict:
    published_ok = 0
    for value, expected in PUBLISHED:
        got = encode_uvarint(value).hex()
        rt = decode_uvarint(bytes.fromhex(expected)) == (value, len(expected) // 2)
        published_ok += int(got == expected and rt)

    zigzag_ok = 0
    for signed, unsigned in ZIGZAG:
        zigzag_ok += int(zigzag_encode(signed) == unsigned
                         and zigzag_decode(unsigned) == signed)

    unsigned_values = ([0, 1, 2, 127, 128, 255, 256, 16383, 16384, 300, 624485]
                       + [2 ** k for k in range(0, 64)]
                       + [2 ** 64 - 1])
    unsigned_rt = sum(decode_uvarint(encode_uvarint(x)) == (x, len(encode_uvarint(x)))
                      for x in unsigned_values)

    signed_values = list(range(-500, 500)) + [2 ** 31, -(2 ** 31), 2 ** 62, -(2 ** 62)]
    signed_rt = sum(decode_varint(encode_varint(x))[0] == x for x in signed_values)

    return {
        "schema": "claimlib_varint_v1",
        "module": "varint",
        "published_vectors": len(PUBLISHED),
        "published_matched": published_ok,
        "zigzag_vectors": len(ZIGZAG),
        "zigzag_matched": zigzag_ok,
        "unsigned_roundtrip_total": len(unsigned_values),
        "unsigned_roundtrip_ok": unsigned_rt,
        "signed_roundtrip_total": len(signed_values),
        "signed_roundtrip_ok": signed_rt,
        "reference_vectors": len(PUBLISHED) + len(ZIGZAG),
        "reference_vectors_matched": published_ok + zigzag_ok,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "varint.json", obj,
         script="python3 claimlib/modules/varint/evidence.py")
    # claim:CLAIM-LIB-VARINT-001 reference_vectors_matched
    # All 7 LEB128 vectors and 7 ZigZag mappings reproduce, so
    # reference_vectors_matched = 14 and every round-trip holds.
    print(f"varint: {obj['reference_vectors_matched']}/{obj['reference_vectors']} "
          f"reference vectors reproduced; unsigned round-trip "
          f"{obj['unsigned_roundtrip_ok']}/{obj['unsigned_roundtrip_total']}, "
          f"signed {obj['signed_roundtrip_ok']}/{obj['signed_roundtrip_total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
