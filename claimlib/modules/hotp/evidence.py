# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-HOTP-001 -- HOTP reproduces the published RFC 4226
Appendix D test vectors exactly.

Each expected value is the INDEPENDENTLY KNOWN published HOTP: for the reference
secret b"12345678901234567890" (ASCII), RFC 4226 tabulates the 6-digit HOTP for
counters 0..9 as 755224, 287082, 359152, 969429, 338314, 254676, 287922,
162583, 399871, 520489. Those constants are written from the RFC, not produced
by this module. Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (hotp.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from hotp import hotp  # noqa: E402
from _util import emit  # noqa: E402

SECRET = b"12345678901234567890"
# RFC 4226 Appendix D: counter -> published 6-digit HOTP.
RFC4226 = [
    (0, "755224"), (1, "287082"), (2, "359152"), (3, "969429"), (4, "338314"),
    (5, "254676"), (6, "287922"), (7, "162583"), (8, "399871"), (9, "520489"),
]


def run() -> dict:
    rows = []
    correct = 0
    for counter, expected in RFC4226:
        got = hotp(SECRET, counter)
        ok = (got == expected)
        correct += int(ok)
        rows.append({"counter": counter, "expected": expected, "computed": got, "correct": ok})
    return {
        "schema": "claimlib_hotp_v1",
        "module": "hotp",
        "n_cases": len(RFC4226),
        "correct": correct,
        "errors": len(RFC4226) - correct,
        "cases": rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "hotp.json", obj,
         script="python3 claimlib/modules/hotp/evidence.py")
    # claim:CLAIM-LIB-HOTP-001 correct
    # Every RFC 4226 Appendix D vector reproduces, so correct = 10 and
    # errors = 0 (n_cases = 10).
    print(f"hotp: {obj['correct']}/{obj['n_cases']} RFC 4226 vectors reproduced "
          f"({obj['errors']} errors)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
