# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-NMEA-001 -- the NMEA 0183 checksum reproduces the
published example sentences and round-trips through build/verify.

Reference sentences whose ``*HH`` checksum is published (Wikipedia "NMEA 0183"
and the GPSd / u-blox protocol references) -- the two hex digits are the
INDEPENDENTLY KNOWN truth, not produced by the module:

    $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
    $GPRMC,225446,A,4916.45,N,12311.12,W,000.5,054.7,191194,020.3,E*68
    $GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39

Plus a self-consistency battery: for arbitrary payloads, ``build`` produces a
sentence that ``is_valid`` accepts, and flipping one character breaks it.
Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (nmea.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from nmea import checksum_hex, is_valid, build  # noqa: E402
from _util import emit  # noqa: E402

# (sentence, published_checksum_hex). Checksum field is the independent truth.
PUBLISHED = [
    ("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47", "47"),
    ("$GPRMC,225446,A,4916.45,N,12311.12,W,000.5,054.7,191194,020.3,E*68", "68"),
    ("$GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39", "39"),
]

# Payloads for the build/verify round-trip and tamper check.
PAYLOADS = [
    "GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,",
    "GPVTG,054.7,T,034.4,M,005.5,N,010.2,K",
    "PLFB,SENSOR,1,42.0,OK",
    "A",
]


def run() -> dict:
    published_rows = []
    published_correct = 0
    valid_correct = 0
    for sentence, expected in PUBLISHED:
        got = checksum_hex(sentence)
        ok = (got == expected)
        published_correct += int(ok)
        # is_valid must also accept the published sentence.
        valid_correct += int(is_valid(sentence))
        published_rows.append({"sentence": sentence, "expected": expected,
                               "computed": got, "match": ok})

    roundtrip_ok = 0
    tamper_detected = 0
    for payload in PAYLOADS:
        sentence = build(payload)
        if is_valid(sentence):
            roundtrip_ok += 1
        # Flip the first payload character; checksum must no longer match.
        star = sentence.find("*")
        flipped = "$" + chr(ord(sentence[1]) ^ 0x01) + sentence[2:star] + sentence[star:]
        if not is_valid(flipped):
            tamper_detected += 1

    return {
        "schema": "claimlib_nmea_v1",
        "module": "nmea",
        "n_published": len(PUBLISHED),
        "published_correct": published_correct,
        "published_errors": len(PUBLISHED) - published_correct,
        "published_accepted_by_is_valid": valid_correct,
        "n_payloads": len(PAYLOADS),
        "roundtrip_ok": roundtrip_ok,
        "tamper_detected": tamper_detected,
        "published_detail": published_rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "nmea.json", obj,
         script="python3 claimlib/modules/nmea/evidence.py")
    # claim:CLAIM-LIB-NMEA-001 published_correct
    # All 3 published sentences reproduce their checksum, so
    # published_correct = 3 and published_errors = 0 (n_published = 3).
    print(f"nmea: {obj['published_correct']}/{obj['n_published']} published "
          f"checksums reproduced, roundtrip {obj['roundtrip_ok']}/{obj['n_payloads']}, "
          f"tamper_detected {obj['tamper_detected']}/{obj['n_payloads']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
