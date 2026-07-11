# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-SPKI-PIN-001 -- a pin equals base64(sha256(spki)) and
matching accepts a pinned key while rejecting an unpinned one.

The stdlib ``hashlib`` and ``base64`` are the independent oracles: for each SPKI
sample the evidence checks pin_sha256(spki) == base64(sha256(spki)) computed
directly, that matches() accepts the correct pin (including when it is the backup
among several) and rejects a wrong pin, and that the pin_directive form is
well-shaped. Deterministic.
"""
from __future__ import annotations

import base64
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (spki_pin.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from spki_pin import pin_sha256, pin_directive, matches  # noqa: E402
from _util import emit  # noqa: E402

SPKIS = [
    b"",
    b"a public key info blob",
    bytes(range(256)),
    b"\x30\x59\x30\x13\x06\x07" + b"\x00" * 80,   # SPKI-shaped prefix + payload
]


def run() -> dict:
    checks = 0
    matched = 0
    for spki in SPKIS:
        oracle = base64.b64encode(hashlib.sha256(spki).digest()).decode("ascii")
        # 1. pin equals base64(sha256(spki))
        checks += 1
        matched += int(pin_sha256(spki) == oracle)
        # 2. matches() accepts the pin when present (as the backup among several)
        checks += 1
        matched += int(matches(spki, ["AAAA-not-a-pin", pin_sha256(spki)]) is True)
        # 3. matches() rejects when the pin is absent
        wrong = base64.b64encode(b"\x00" * 32).decode("ascii")
        checks += 1
        matched += int(matches(spki, [wrong]) is False)
        # 4. directive is well-shaped
        checks += 1
        matched += int(pin_directive(spki) == f'pin-sha256="{oracle}"')

    return {
        "schema": "claimlib_spki_pin_v1",
        "module": "spki_pin",
        "n_spkis": len(SPKIS),
        "checks": checks,
        "checks_matched": matched,
        "mismatches": checks - matched,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "spki_pin.json", obj,
         script="python3 claimlib/modules/spki_pin/evidence.py")
    # claim:CLAIM-LIB-SPKI-PIN-001 checks_matched
    # Every pin-equals-oracle, accept, reject and directive check holds, so
    # checks_matched = 16 and mismatches = 0.
    print(f"spki_pin: {obj['checks_matched']}/{obj['checks']} checks pass "
          f"({obj['mismatches']} mismatches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
