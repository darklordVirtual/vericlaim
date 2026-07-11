# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-CVSS-001 — the CVSS v3.1 scorer reproduces published
reference base scores.

Runs the reusable ``cvss`` module over a fixed set of vectors whose base scores
are published (FIRST CVSS v3.1 examples / widely-cited CVE scores) and records
how many reproduce exactly. Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (cvss.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from cvss import base_score, severity  # noqa: E402
from _util import emit  # noqa: E402

# (vector, published base score). Each is an independently-known CVSS v3.1
# reference value — not produced by this scorer.
REFERENCE = [
    ("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", 9.8),   # unauth network RCE
    ("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H", 10.0),  # + scope change
    ("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N", 7.5),   # info disclosure
    ("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N", 5.3),   # low-conf leak
    ("CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N", 6.1),   # reflected XSS
    ("CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H", 8.8),   # authed RCE
    ("CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N", 4.3),   # authed low leak
    ("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N", 0.0),   # no impact
    ("CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H", 7.8),   # local priv-esc
]


def run() -> dict:
    cases = []
    matched = 0
    for vector, published in REFERENCE:
        got = base_score(vector)
        ok = (got == published)
        matched += int(ok)
        cases.append({"vector": vector, "expected": published,
                      "computed": got, "severity": severity(got), "match": ok})
    return {
        "schema": "claimlib_cvss_v1",
        "module": "cvss",
        "reference_vectors": len(REFERENCE),
        "reference_vectors_matched": matched,
        "mismatches": len(REFERENCE) - matched,
        "cases": cases,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "cvss.json", obj,
         script="python3 claimlib/modules/cvss/evidence.py")
    # claim:CLAIM-LIB-CVSS-001 reference_vectors_matched
    # All 9 published reference vectors reproduce exactly, so
    # reference_vectors_matched = 9 and mismatches = 0.
    print(f"cvss: {obj['reference_vectors_matched']}/{obj['reference_vectors']} "
          f"reference vectors reproduced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
