# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-CRC32-001 — the CRC-32 implementation reproduces the
published reference values AND agrees with Python's stdlib ``zlib.crc32``.

Runs the reusable ``crc32`` module over two independent references:

  1. Published CRC-32 (IEEE 802.3) check values — crc32(b"") == 0,
     crc32(b"123456789") == 0xCBF43926, and the classic pangram — whose
     expected values are hand-written from the specification, not produced by
     this module.
  2. A fixed set of byte strings cross-checked for exact equality against
     ``zlib.crc32`` (a different, independent implementation in the standard
     library). ``zlib`` masks its result to unsigned, matching this module's
     contract.

Every reference case that matches its independent expected value counts toward
``reference_vectors_matched``. Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (crc32.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from crc32 import crc32  # noqa: E402
from _util import emit  # noqa: E402

# (data, published CRC-32). Independently-known IEEE 802.3 CRC-32 check values,
# NOT produced by this module:
#   * b""                 -> 0            (empty message, init^final cancels)
#   * b"123456789"        -> 0xCBF43926  (the canonical CRC "check" string,
#                                          published in the CRC catalogue for
#                                          CRC-32/ISO-HDLC == zip/gzip CRC-32)
#   * the lazy-dog pangram -> 0x414FA339 (widely published CRC-32 test vector)
PUBLISHED = [
    (b"", 0x00000000),
    (b"123456789", 0xCBF43926),
    (b"The quick brown fox jumps over the lazy dog", 0x414FA339),
]

# Byte strings whose CRC-32 is defined by the independent oracle zlib.crc32.
# Covers empty, single byte, all-zero and all-0xFF runs, repeated patterns,
# incremental lengths, and every single byte value 0..255 as a payload.
CROSSCHECK = [
    b"",
    b"\x00",
    b"\xff",
    b"a",
    b"abc",
    b"message digest",
    b"abcdefghijklmnopqrstuvwxyz",
    b"\x00" * 32,
    b"\xff" * 32,
    b"\xde\xad\xbe\xef" * 16,
    bytes(range(256)),
    b"The quick brown fox jumps over the lazy dog.",
]
CROSSCHECK += [bytes([b]) for b in range(256)]      # 256 single-byte payloads
CROSSCHECK += [b"\x01\x02\x03" * n for n in range(20)]  # incremental lengths


def run() -> dict:
    published_rows = []
    matched = 0
    for data, expected in PUBLISHED:
        got = crc32(data)
        ok = (got == expected)
        matched += int(ok)
        published_rows.append({
            "input_hex": data.hex(),
            "length": len(data),
            "expected": expected,
            "computed": got,
            "match": ok,
        })

    cross_matched = 0
    cross_mismatch = 0
    for data in CROSSCHECK:
        got = crc32(data)
        oracle = zlib.crc32(data) & 0xFFFFFFFF
        ok = (got == oracle)
        matched += int(ok)
        cross_matched += int(ok)
        cross_mismatch += int(not ok)

    reference_vectors = len(PUBLISHED) + len(CROSSCHECK)
    mismatches = reference_vectors - matched
    return {
        "schema": "claimlib_crc32_v1",
        "module": "crc32",
        "reference_vectors": reference_vectors,
        "reference_vectors_matched": matched,
        "mismatches": mismatches,
        "published_vectors": len(PUBLISHED),
        "crosscheck_vectors": len(CROSSCHECK),
        "crosscheck_matched": cross_matched,
        "crosscheck_mismatched": cross_mismatch,
        "published_detail": published_rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "crc32.json", obj,
         script="python3 claimlib/modules/crc32/evidence.py")
    # claim:CLAIM-LIB-CRC32-001 reference_vectors_matched
    # All 291 published + zlib-cross-checked reference vectors reproduce exactly,
    # so reference_vectors_matched = 291 and mismatches = 0.
    print(f"crc32: {obj['reference_vectors_matched']}/{obj['reference_vectors']} "
          f"reference vectors reproduced ({obj['mismatches']} mismatches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
