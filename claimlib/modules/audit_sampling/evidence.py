# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-AUDIT-SAMPLING-001 -- the reliability factors match their
Poisson basis, sample sizes reproduce the standard examples, and the arithmetic
is self-consistent.

Independent checks: the zero-deviation reliability factor for each confidence must
equal -ln(1 - confidence) to within table rounding (the Poisson basis, an exact
mathematical fact); the sample size for a 5% tolerable rate at 95% confidence with
zero expected deviations is the textbook 60; sample size grows with the expected
deviation count (monotonicity); and after testing, upper_deviation_rate at the
computed sample size is at most the tolerable rate (the plan achieves its goal).
Deterministic.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (audit_sampling.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from audit_sampling import (  # noqa: E402
    POISSON_FACTORS, reliability_factor, sample_size, upper_deviation_rate)
from _util import emit  # noqa: E402


def run() -> dict:
    # 1. Zero-deviation factors match -ln(1 - confidence) within rounding.
    poisson_basis_ok = 0
    for confidence in POISSON_FACTORS:
        exact = -math.log(1 - confidence)
        poisson_basis_ok += int(abs(reliability_factor(confidence, 0) - exact) < 0.01)

    # 2. Standard worked sample sizes.
    example_checks = [
        sample_size(0.05, confidence=0.95, expected_deviations=0) == 60,      # 3.00 / 0.05
        sample_size(0.10, confidence=0.90, expected_deviations=0) == 24,      # 2.31 / 0.10 -> 24
        sample_size(0.10, confidence=0.95, expected_deviations=0) == 30,      # 3.00 / 0.10
        sample_size(0.05, confidence=0.99, expected_deviations=0) == 93,      # 4.61 / 0.05 -> 93
    ]
    example_ok = sum(int(c) for c in example_checks)

    # 3. Monotonicity in expected deviations (more expected -> larger sample).
    sizes = [sample_size(0.05, 0.95, k) for k in range(0, 4)]
    monotonic_ok = int(all(sizes[i] < sizes[i + 1] for i in range(3)))

    # 4. Self-consistency: the achieved upper deviation rate is within tolerable.
    consistency_ok = 0
    for tolerable in (0.02, 0.05, 0.10):
        for confidence in (0.90, 0.95, 0.99):
            n = sample_size(tolerable, confidence, 0)
            consistency_ok += int(upper_deviation_rate(n, 0, confidence) <= tolerable)

    checks = len(POISSON_FACTORS) + len(example_checks) + 1 + 9
    matched = poisson_basis_ok + example_ok + monotonic_ok + consistency_ok
    return {
        "schema": "claimlib_audit_sampling_v1",
        "module": "audit_sampling",
        "checks": checks,
        "checks_matched": matched,
        "mismatches": checks - matched,
        "poisson_basis_ok": poisson_basis_ok,
        "example_ok": example_ok,
        "monotonic_ok": monotonic_ok,
        "consistency_ok": consistency_ok,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "audit_sampling.json", obj,
         script="python3 claimlib/modules/audit_sampling/evidence.py")
    # claim:CLAIM-LIB-AUDIT-SAMPLING-001 checks_matched
    # The 3 Poisson-basis, 4 example, 1 monotonicity and 9 self-consistency checks
    # all hold, so checks_matched = 17 and mismatches = 0.
    print(f"audit_sampling: {obj['checks_matched']}/{obj['checks']} checks "
          f"(poisson {obj['poisson_basis_ok']}/3, examples {obj['example_ok']}/4, "
          f"consistency {obj['consistency_ok']}/9); mismatches {obj['mismatches']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
