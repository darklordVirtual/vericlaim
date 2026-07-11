# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-VLAN-001 -- VLAN-ID validity matches the 802.1Q
reservations and range parse/format round-trips.

Each validity row's expected label is INDEPENDENTLY KNOWN from IEEE 802.1Q: VID 0
is priority-tagged (not assignable), 1..4094 are assignable, and 4095 is
reserved. The battery pins every boundary. A second battery parses compact range
strings to explicit lists and checks that formatting the result reproduces the
canonical range text (round-trip). Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (vlan.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from vlan import is_valid, parse_range, format_range  # noqa: E402
from _util import emit  # noqa: E402

# (vid, expected_valid) from the 802.1Q reservations.
VALIDITY = [
    (0, False), (1, True), (2, True), (100, True), (1000, True),
    (4094, True), (4095, False), (4096, False), (-1, False),
]

# (input_range, expected_list, canonical_form).
RANGES = [
    ("1", [1], "1"),
    ("1,10-12,4094", [1, 10, 11, 12, 4094], "1,10-12,4094"),
    ("10-11", [10, 11], "10-11"),
    ("3,2,1", [1, 2, 3], "1-3"),                     # reorders + collapses
    ("5,5,6,6,7", [5, 6, 7], "5-7"),                  # de-duplicates
    ("1,3,5,7", [1, 3, 5, 7], "1,3,5,7"),             # no collapse
]


def run() -> dict:
    validity_correct = 0
    for vid, expected in VALIDITY:
        if is_valid(vid) == expected:
            validity_correct += 1

    range_correct = 0
    round_trip_correct = 0
    for text, expected_list, canonical in RANGES:
        parsed = parse_range(text)
        if parsed == expected_list:
            range_correct += 1
        if format_range(parsed) == canonical:
            round_trip_correct += 1

    return {
        "schema": "claimlib_vlan_v1",
        "module": "vlan",
        "n_cases": len(VALIDITY),
        "correct": validity_correct,
        "errors": len(VALIDITY) - validity_correct,
        "n_ranges": len(RANGES),
        "range_parse_correct": range_correct,
        "range_roundtrip_correct": round_trip_correct,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "vlan.json", obj,
         script="python3 claimlib/modules/vlan/evidence.py")
    # claim:CLAIM-LIB-VLAN-001 correct
    # Every VID validity check matches the 802.1Q rule, so correct = 9 and
    # errors = 0 (n_cases = 9); all 6 range parses and round-trips hold.
    print(f"vlan: {obj['correct']}/{obj['n_cases']} validity checks "
          f"({obj['errors']} errors), ranges {obj['range_parse_correct']}/{obj['n_ranges']}, "
          f"round-trip {obj['range_roundtrip_correct']}/{obj['n_ranges']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
