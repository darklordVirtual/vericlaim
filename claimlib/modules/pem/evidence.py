# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-PEM-001 -- PEM round-trips DER losslessly, its base64
body agrees with the stdlib, and it wraps lines at 64 characters (RFC 7468).

The stdlib ``base64`` module is the independent oracle for the body. For each DER
blob the evidence checks: decode(encode(der, label)) == (label, der) (round-trip);
that the base64 lines between the boundaries are all <= 64 chars and decode (via
base64.b64decode) back to der; and that a multi-block PEM parses into the right
list. Deterministic.
"""
from __future__ import annotations

import base64
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (pem.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from pem import encode, decode, decode_all  # noqa: E402
from _util import emit  # noqa: E402

# Fixed DER blobs (a tiny SEQUENCE, empty, single byte, and long payloads).
DERS = [
    (bytes.fromhex("30030201 2a".replace(" ", "")), "CERTIFICATE"),
    (b"", "PRIVATE KEY"),
    (b"\x00", "PUBLIC KEY"),
    (bytes(range(256)), "CERTIFICATE"),
    (b"\xde\xad\xbe\xef" * 40, "EC PRIVATE KEY"),
]


def run() -> dict:
    checks = 0
    matched = 0
    for der, label in DERS:
        pem = encode(der, label)
        # 1. round-trip
        checks += 1
        matched += int(decode(pem) == (label, der))
        # 2. base64 body agrees with stdlib and lines wrap at <= 64
        body_lines = re.search(r"-----BEGIN .*?-----\n(.*?)\n-----END",
                               pem, re.DOTALL).group(1).split("\n") if der else []
        line_ok = all(len(line) <= 64 for line in body_lines)
        joined = "".join(body_lines)
        b64_ok = (joined == base64.b64encode(der).decode("ascii"))
        checks += 1
        matched += int(line_ok and b64_ok)

    # 3. multi-block PEM parses into the right sequence.
    multi = encode(b"\x01\x02", "CERTIFICATE") + encode(b"\x03\x04", "CERTIFICATE")
    checks += 1
    matched += int(decode_all(multi) == [("CERTIFICATE", b"\x01\x02"),
                                         ("CERTIFICATE", b"\x03\x04")])

    return {
        "schema": "claimlib_pem_v1",
        "module": "pem",
        "n_ders": len(DERS),
        "checks": checks,
        "checks_matched": matched,
        "mismatches": checks - matched,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "pem.json", obj,
         script="python3 claimlib/modules/pem/evidence.py")
    # claim:CLAIM-LIB-PEM-001 checks_matched
    # Every round-trip, base64 agreement, line-wrap and multi-block check holds,
    # so checks_matched = 11 and mismatches = 0.
    print(f"pem: {obj['checks_matched']}/{obj['checks']} checks pass "
          f"({obj['mismatches']} mismatches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
