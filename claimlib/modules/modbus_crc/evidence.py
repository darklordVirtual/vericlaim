# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-MODBUS-CRC-001 -- the CRC-16/MODBUS implementation
reproduces the published catalogue check value AND agrees with an independent
table-driven implementation.

Two independent references:

  1. Published check value: the CRC catalogue (reveng / "CRC-16/MODBUS")
     defines check == 0x4B37 for the ASCII bytes b"123456789". This constant is
     hand-written from the catalogue, not produced by the module.
  2. Independent implementation: a table-driven CRC (a different code path from
     the module's bit-by-bit loop) is computed here from scratch, and every
     byte string in a fixed battery must produce the SAME value under both --
     including empty, single bytes, all-zero / all-0xFF runs, a Modbus read
     frame, and every single byte value 0..255.

Each reference that matches its independent expected value counts toward
reference_vectors_matched. Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (modbus_crc.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from modbus_crc import crc16_modbus, append_crc, check_frame  # noqa: E402
from _util import emit  # noqa: E402

_POLY = 0xA001


def _build_table() -> list[int]:
    table = []
    for i in range(256):
        crc = i
        for _ in range(8):
            crc = (crc >> 1) ^ _POLY if crc & 1 else crc >> 1
        table.append(crc & 0xFFFF)
    return table


_TABLE = _build_table()


def crc_table(data: bytes) -> int:
    """Independent table-driven CRC-16/MODBUS (different code path)."""
    crc = 0xFFFF
    for byte in data:
        crc = (crc >> 8) ^ _TABLE[(crc ^ byte) & 0xFF]
    return crc & 0xFFFF

# Published catalogue check: CRC-16/MODBUS of b"123456789" == 0x4B37.
PUBLISHED = [(b"123456789", 0x4B37)]

# Byte strings whose CRC must agree between the module (bitwise) and the
# independent table implementation.
CROSSCHECK = [
    b"",
    b"\x00",
    b"\xff",
    b"A",
    b"123456789",
    b"\x01\x03\x00\x00\x00\x0a",   # a Modbus "read 10 holding registers" frame
    b"\x00" * 16,
    b"\xff" * 16,
    b"\xde\xad\xbe\xef" * 8,
    bytes(range(256)),
]
CROSSCHECK += [bytes([b]) for b in range(256)]


def run() -> dict:
    published_rows = []
    matched = 0
    for data, expected in PUBLISHED:
        got = crc16_modbus(data)
        ok = (got == expected)
        matched += int(ok)
        published_rows.append({"input": data.decode("latin-1"),
                               "expected": expected, "computed": got, "match": ok})

    cross_matched = 0
    for data in CROSSCHECK:
        got = crc16_modbus(data)
        oracle = crc_table(data)
        ok = (got == oracle)
        matched += int(ok)
        cross_matched += int(ok)

    # append_crc / check_frame round-trip (self-consistency).
    frame = b"\x11\x03\x00\x6b\x00\x03"
    roundtrip_ok = check_frame(append_crc(frame)) and not check_frame(
        append_crc(frame)[:-1] + bytes([(append_crc(frame)[-1] ^ 0x01)]))

    reference_vectors = len(PUBLISHED) + len(CROSSCHECK)
    return {
        "schema": "claimlib_modbus_crc_v1",
        "module": "modbus_crc",
        "reference_vectors": reference_vectors,
        "reference_vectors_matched": matched,
        "mismatches": reference_vectors - matched,
        "published_vectors": len(PUBLISHED),
        "crosscheck_vectors": len(CROSSCHECK),
        "crosscheck_matched": cross_matched,
        "roundtrip_ok": bool(roundtrip_ok),
        "published_detail": published_rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "modbus_crc.json", obj,
         script="python3 claimlib/modules/modbus_crc/evidence.py")
    # claim:CLAIM-LIB-MODBUS-CRC-001 reference_vectors_matched
    # The published 0x4B37 check plus 266 table-cross-checked vectors all
    # reproduce, so reference_vectors_matched = 267 and mismatches = 0.
    print(f"modbus_crc: {obj['reference_vectors_matched']}/{obj['reference_vectors']} "
          f"reference vectors reproduced ({obj['mismatches']} mismatches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
