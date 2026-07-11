# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-TOTP-001 -- TOTP reproduces the published RFC 6238
Appendix B test vectors exactly.

Each expected value is the INDEPENDENTLY KNOWN published TOTP: for the SHA-1
reference secret b"12345678901234567890" with 8 digits and a 30-second step,
RFC 6238 Appendix B tabulates the TOTP at Unix times 59, 1111111109, 1111111111,
1234567890, 2000000000 and 20000000000 as 94287082, 07081804, 14050471,
89005924, 69279037 and 65353130. Those constants are written from the RFC, not
produced by this module. Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (totp.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from totp import totp  # noqa: E402
from _util import emit  # noqa: E402

SECRET = b"12345678901234567890"   # 20-byte ASCII SHA-1 reference seed
# RFC 6238 Appendix B (SHA-1, 8 digits, step 30s): unix_time -> published TOTP.
RFC6238 = [
    (59, "94287082"),
    (1111111109, "07081804"),
    (1111111111, "14050471"),
    (1234567890, "89005924"),
    (2000000000, "69279037"),
    (20000000000, "65353130"),
]


def run() -> dict:
    rows = []
    correct = 0
    for unix_time, expected in RFC6238:
        got = totp(SECRET, unix_time, digits=8, algorithm="sha1")
        ok = (got == expected)
        correct += int(ok)
        rows.append({"unix_time": unix_time, "expected": expected,
                     "computed": got, "correct": ok})
    return {
        "schema": "claimlib_totp_v1",
        "module": "totp",
        "n_cases": len(RFC6238),
        "correct": correct,
        "errors": len(RFC6238) - correct,
        "cases": rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "totp.json", obj,
         script="python3 claimlib/modules/totp/evidence.py")
    # claim:CLAIM-LIB-TOTP-001 correct
    # Every RFC 6238 Appendix B (SHA-1) vector reproduces, so correct = 6 and
    # errors = 0 (n_cases = 6).
    print(f"totp: {obj['correct']}/{obj['n_cases']} RFC 6238 vectors reproduced "
          f"({obj['errors']} errors)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
