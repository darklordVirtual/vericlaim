# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-SHA256-001 -- the from-scratch SHA-256 reproduces the
published FIPS 180-4 check values and agrees with stdlib ``hashlib`` everywhere.

``hashlib.sha256`` is a completely independent implementation this module never
imports, so it is a genuine oracle. Two references:
  1. Published: the FIPS 180-4 / NIST check values -- sha256(b"") ==
     e3b0c442...b855 and sha256(b"abc") == ba7816bf...15ad -- hand-written from
     the standard.
  2. Independent oracle: over a fixed battery (empty, ASCII, the exact 64- and
     65-byte block-boundary lengths, a long input, every single byte 0..255, and
     incremental lengths) the module's hexdigest must equal
     hashlib.sha256(...).hexdigest().
Every vector that matches counts toward reference_vectors_matched. Deterministic.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (sha256.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from sha256 import sha256, hexdigest  # noqa: E402
from _util import emit  # noqa: E402

# Published FIPS 180-4 check values (independent of this module).
PUBLISHED = [
    (b"", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    (b"abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
    (b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
     "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"),
]

CROSSCHECK = [
    b"",
    b"a",
    b"The quick brown fox jumps over the lazy dog",
    b"\x00" * 55,   # one byte short of a padded block
    b"\x00" * 56,   # forces an extra padding block
    b"\x00" * 64,   # exact block boundary
    b"\x00" * 65,
    b"\xff" * 1000,
    bytes(range(256)),
]
CROSSCHECK += [bytes([b]) for b in range(256)]
CROSSCHECK += [b"\x5a" * n for n in range(130)]   # incremental lengths across blocks


def run() -> dict:
    matched = 0
    published_rows = []
    for data, expected in PUBLISHED:
        ok = (hexdigest(data) == expected)
        matched += int(ok)
        published_rows.append({"input_len": len(data), "expected": expected,
                               "computed": hexdigest(data), "match": ok})

    cross_matched = 0
    for data in CROSSCHECK:
        if sha256(data).hex() == hashlib.sha256(data).hexdigest():
            cross_matched += 1
    matched += cross_matched

    reference_vectors = len(PUBLISHED) + len(CROSSCHECK)
    return {
        "schema": "claimlib_sha256_v1",
        "module": "sha256",
        "reference_vectors": reference_vectors,
        "reference_vectors_matched": matched,
        "mismatches": reference_vectors - matched,
        "published_vectors": len(PUBLISHED),
        "crosscheck_vectors": len(CROSSCHECK),
        "crosscheck_matched": cross_matched,
        "published_detail": published_rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "sha256.json", obj,
         script="python3 claimlib/modules/sha256/evidence.py")
    # claim:CLAIM-LIB-SHA256-001 reference_vectors_matched
    # The 3 published FIPS values plus 395 hashlib-cross-checked vectors all
    # reproduce, so reference_vectors_matched = 398 and mismatches = 0.
    print(f"sha256: {obj['reference_vectors_matched']}/{obj['reference_vectors']} "
          f"vectors reproduced ({obj['mismatches']} mismatches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
