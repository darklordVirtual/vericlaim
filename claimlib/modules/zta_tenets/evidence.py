# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-ZTA-001 — the encoded tenets match NIST SP 800-207
section 2.1 and coverage is exact.

Oracle: the seven tenets of zero trust as published in NIST SP 800-207
(Rose, Borchert, Mitchell, Connelly; August 2020), verified against the
official nvlpubs PDF: seven tenets, anchored by their distinctive published
phrases (resources, per-session, dynamic policy, integrity monitoring,
dynamic authentication, telemetry-driven posture improvement). Coverage
percentages are recomputed with exact Fraction arithmetic. Deterministic:
same artifact on every run.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from zta_tenets import TENETS, ZTAError, coverage  # noqa: E402
from _util import emit  # noqa: E402

ANCHORS = {
    1: "considered resources",
    2: "regardless of network location",
    3: "per-session basis",
    4: "dynamic policy",
    5: "integrity and security posture",
    6: "dynamic and strictly enforced",
    7: "improve its security posture",
}


def run() -> dict:
    taxonomy = [
        len(TENETS) == 7 and sorted(TENETS) == list(range(1, 8)),
        all(ANCHORS[n] in TENETS[n] for n in ANCHORS),
    ]
    taxonomy_ok = sum(taxonomy)

    cov_checks = 0
    cov_ok = 0
    for adhered, want in [(range(1, 8), 7), ([2, 4, 6], 3), ([], 0)]:
        cov_checks += 1
        got = coverage(adhered)
        if got["adhered"] == want and got["coverage_pct"] == round(
                float(Fraction(want, 7) * 100), 2) \
                and len(got["gaps"]) == 7 - want:
            cov_ok += 1

    rejects = 0
    for bad in (lambda: coverage([0]),
                lambda: coverage([8]),
                lambda: coverage([True]),
                lambda: coverage(["1"])):
        try:
            bad()
        except ZTAError:
            rejects += 1

    total = len(taxonomy) + cov_checks
    matched = taxonomy_ok + cov_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "zta_tenets",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "tenets": len(TENETS),
        "reject_cases": 4,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "zta_tenets.json", obj,
         script="python3 claimlib/modules/zta_tenets/evidence.py")
    # claim:CLAIM-LIB-ZTA-001 checks_matched
    # All 5 checks pass: seven tenets anchored to their published SP 800-207
    # phrases, and Fraction-exact coverage on three fixed architectures —
    # checks_matched = 5, mismatches = 0.
    print(f"zta_tenets: {obj['checks_matched']}/{obj['checks']} checks "
          f"({obj['tenets']} tenets); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
