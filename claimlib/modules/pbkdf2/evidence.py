# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-PBKDF2-001 -- the from-scratch PBKDF2 reproduces the
RFC 6070 vectors and agrees with stdlib ``hashlib.pbkdf2_hmac`` everywhere.

``hashlib.pbkdf2_hmac`` is a completely independent implementation this module
never calls, so it is a genuine oracle. Two references:
  1. Published: the RFC 6070 PBKDF2-HMAC-SHA1 vectors -- ("password","salt",1,20)
     -> 0c60c80f...37a6 and (...,2,20) -> ea6c014d...8957 and (...,4096,20) ->
     4b007901...29c1 -- hand-written from the RFC.
  2. Independent oracle: over a battery of (hash, password, salt, iterations,
     dklen) combinations (SHA-1 and SHA-256, multi-block outputs, empty salt)
     the module must equal hashlib.pbkdf2_hmac byte-for-byte.
Deterministic.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (pbkdf2.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from pbkdf2 import pbkdf2_hmac  # noqa: E402
from _util import emit  # noqa: E402

# RFC 6070 PBKDF2-HMAC-SHA1 published vectors (kept to iterations <= 4096).
RFC6070 = [
    (b"password", b"salt", 1, 20, "0c60c80f961f0e71f3a9b524af6012062fe037a6"),
    (b"password", b"salt", 2, 20, "ea6c014dc72d6f8ccd1ed92ace1d41f0d8de8957"),
    (b"password", b"salt", 4096, 20, "4b007901b765489abead49d926f721d065a429c1"),
]

# (hash_name, password, salt, iterations, dklen) cross-checked vs hashlib.
BATTERY = [
    ("sha1", b"password", b"salt", 1, 20),
    ("sha1", b"password", b"salt", 4096, 20),
    ("sha256", b"password", b"salt", 1, 32),
    ("sha256", b"password", b"salt", 1000, 32),
    ("sha256", b"passwd", b"salt", 1, 64),        # two output blocks
    ("sha256", b"", b"salt", 100, 32),            # empty password
    ("sha256", b"password", b"", 100, 20),        # empty salt, truncated
    ("sha512", b"password", b"salt", 500, 64),
]


def run() -> dict:
    matched = 0
    published_rows = []
    for password, salt, iters, dklen, expected in RFC6070:
        got = pbkdf2_hmac("sha1", password, salt, iters, dklen).hex()
        ok = (got == expected)
        matched += int(ok)
        published_rows.append({"iterations": iters, "expected": expected,
                               "computed": got, "match": ok})

    oracle_matched = 0
    for hash_name, password, salt, iters, dklen in BATTERY:
        got = pbkdf2_hmac(hash_name, password, salt, iters, dklen)
        oracle = hashlib.pbkdf2_hmac(hash_name, password, salt, iters, dklen)
        if got == oracle:
            oracle_matched += 1
    matched += oracle_matched

    reference_vectors = len(RFC6070) + len(BATTERY)
    return {
        "schema": "claimlib_pbkdf2_v1",
        "module": "pbkdf2",
        "reference_vectors": reference_vectors,
        "reference_vectors_matched": matched,
        "mismatches": reference_vectors - matched,
        "rfc6070_vectors": len(RFC6070),
        "oracle_cases": len(BATTERY),
        "oracle_matched": oracle_matched,
        "published_detail": published_rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "pbkdf2.json", obj,
         script="python3 claimlib/modules/pbkdf2/evidence.py")
    # claim:CLAIM-LIB-PBKDF2-001 reference_vectors_matched
    # The 3 RFC 6070 vectors plus 8 hashlib-cross-checked cases all reproduce,
    # so reference_vectors_matched = 11 and mismatches = 0.
    print(f"pbkdf2: {obj['reference_vectors_matched']}/{obj['reference_vectors']} "
          f"reference vectors reproduced ({obj['mismatches']} mismatches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
