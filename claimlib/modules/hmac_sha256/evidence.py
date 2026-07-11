# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-HMAC-SHA256-001 -- the from-scratch HMAC construction
agrees with stdlib ``hmac`` over the RFC 4231 inputs and a fixed battery.

The stdlib ``hmac`` module is an independent implementation this module never
imports, so it is a genuine oracle. The evidence runs the module and
``hmac.new(key, msg, sha256)`` over the RFC 4231 (HMAC-SHA256 test) key/message
inputs -- including an oversized key that must be hashed down -- plus a battery
of varied keys and messages, and requires byte-for-byte agreement. It also
checks the published RFC 4231 Test Case 2 tag ("Jefe"/"what do ya want ...")
directly, and that ``verify`` accepts the right tag and rejects a flipped bit.
Deterministic.
"""
from __future__ import annotations

import hashlib
import hmac as stdlib_hmac
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (hmac_sha256.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from hmac_sha256 import hmac_sha256, hexdigest, verify  # noqa: E402
from _util import emit  # noqa: E402

# RFC 4231 test inputs (key, message). Outputs come from the independent oracle.
RFC4231 = [
    (b"\x0b" * 20, b"Hi There"),
    (b"Jefe", b"what do ya want for nothing?"),
    (b"\xaa" * 20, b"\xdd" * 50),
    (bytes(range(1, 26)), b"\xcd" * 50),
    (b"\xaa" * 131, b"Test Using Larger Than Block-Size Key - Hash Key First"),
    (b"\xaa" * 131,
     b"This is a test using a larger than block-size key and a larger "
     b"than block-size data. The key needs to be hashed before being used "
     b"by the HMAC algorithm."),
]

# Extra keys/messages, incl. the empty key/message and a block-sized key.
BATTERY = RFC4231 + [
    (b"", b""),
    (b"key", b"The quick brown fox jumps over the lazy dog"),
    (b"\x00" * 64, b"exactly one block key"),
    (b"\x01" * 100, bytes(range(256))),
]

# RFC 4231 Test Case 2 published tag (key "Jefe").
RFC4231_TC2_TAG = "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"


def run() -> dict:
    matched = 0
    for key, message in BATTERY:
        oracle = stdlib_hmac.new(key, message, hashlib.sha256).digest()
        matched += int(hmac_sha256(key, message) == oracle)

    published_ok = (hexdigest(b"Jefe", b"what do ya want for nothing?") == RFC4231_TC2_TAG)
    tag = hmac_sha256(b"key", b"message")
    verify_ok = verify(b"key", b"message", tag)
    reject_ok = not verify(b"key", b"message", bytes([tag[0] ^ 0x01]) + tag[1:])

    total = len(BATTERY) + 3   # oracle agreements + published + verify + reject
    matched_total = matched + int(published_ok) + int(verify_ok) + int(reject_ok)
    return {
        "schema": "claimlib_hmac_sha256_v1",
        "module": "hmac_sha256",
        "reference_vectors": total,
        "reference_vectors_matched": matched_total,
        "mismatches": total - matched_total,
        "oracle_agreements": matched,
        "oracle_cases": len(BATTERY),
        "published_tc2_ok": published_ok,
        "verify_ok": verify_ok,
        "reject_flipped_ok": reject_ok,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "hmac_sha256.json", obj,
         script="python3 claimlib/modules/hmac_sha256/evidence.py")
    # claim:CLAIM-LIB-HMAC-SHA256-001 reference_vectors_matched
    # All 10 oracle agreements plus the published tag and verify/reject checks
    # hold, so reference_vectors_matched = 13 and mismatches = 0.
    print(f"hmac_sha256: {obj['reference_vectors_matched']}/{obj['reference_vectors']} "
          f"checks agree with stdlib hmac / RFC 4231 ({obj['mismatches']} mismatches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
