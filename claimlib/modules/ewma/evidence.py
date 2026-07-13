# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-EWMA-001 -- the EWMA recursion matches exact
rational arithmetic and the control chart reproduces the published
NIST/SEMATECH worked example.

Two independent oracles, neither produced by the module under test:

1. Exact mathematics: the recursion z_i = lam*x_i + (1-lam)*z_{i-1} and the
   time-varying variance factor lam/(2-lam)*(1-(1-lam)^(2i)) are recomputed
   with ``fractions.Fraction`` (exact rational arithmetic, stdlib, never
   imported by ewma.py) over a fixed battery; the float implementation must
   agree to 12 decimal places.

2. Published vectors: the NIST/SEMATECH e-Handbook of Statistical Methods,
   section 6.3.2.4 "EWMA Control Charts" (doi:10.18434/M32189), gives a
   worked example -- 20 observations, lambda = 0.3, target 50, s = 2.0539,
   L = 3 -- with all 21 EWMA values printed to 2 dp, steady-state limits
   UCL = 52.5884 / LCL = 47.4115, and no point out of control. The chart
   must reproduce all of it.

Deterministic: fixed battery, integer counts, floats rounded to fixed dp.
"""
from __future__ import annotations

import math
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (ewma.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from ewma import ewma_series, control_limits, steady_state_limits, chart  # noqa: E402
from _util import emit  # noqa: E402

TOL = Fraction(1, 10 ** 12)  # "agrees to 12 decimal places"

# ---------------------------------------------------------------------------
# Oracle 2: NIST/SEMATECH e-Handbook 6.3.2.4 worked example (verbatim).
#   https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm
# Data, lambda = 0.3, EWMA_0 = target = 50, s = 2.0539, k = L = 3.
NIST_DATA = [52.0, 47.0, 53.0, 49.3, 50.1, 47.0, 51.0, 50.1, 51.2, 50.5,
             49.6, 47.6, 49.9, 51.3, 47.8, 51.2, 52.6, 52.4, 53.6, 52.1]
# The 21 EWMA statistics as printed on the page (z_0 = 50.00 first):
NIST_EWMA_2DP = [50.00, 50.60, 49.52, 50.56, 50.18, 50.16, 49.21, 49.75,
                 49.85, 50.26, 50.33, 50.11, 49.36, 49.52, 50.05, 49.38,
                 49.92, 50.73, 51.23, 51.94, 51.99]
NIST_LAMBDA = 0.3
NIST_TARGET = 50.0
NIST_SIGMA = 2.0539
NIST_L = 3.0
# "UCL = 50 + 3 (0.4201)(2.0539) = 52.5884, LCL = 50 - ... = 47.4115"
NIST_UCL = 52.5884
NIST_LCL = 47.4115
NIST_LIMIT_TOL = 1e-3  # the page prints a truncated 0.4201 factor

# ---------------------------------------------------------------------------
# Oracle 1a: fixed recursion battery, inputs as decimal strings so
# Fraction(str) is exact. (label, lam, z0, values)
FRACTION_BATTERY = [
    ("nist_lam0.3", "0.3", "50",
     ["52.0", "47.0", "53.0", "49.3", "50.1", "47.0", "51.0", "50.1",
      "51.2", "50.5", "49.6", "47.6", "49.9", "51.3", "47.8", "51.2",
      "52.6", "52.4", "53.6", "52.1"]),
    ("smooth_lam0.1", "0.1", "10",
     ["10.5", "9.8", "10.2", "11.0", "9.5", "10.1", "10.7", "9.9",
      "10.3", "10.0", "9.7", "10.4"]),
    ("alternating_lam0.5", "0.5", "0",
     ["1", "-1"] * 8),
    ("identity_lam1", "1", "7.5",
     ["3", "1", "4", "1", "5", "9", "2", "6"]),
    ("swings_lam0.25", "0.25", "100",
     ["150", "50", "125", "75", "110", "90", "105", "95", "102", "98"]),
    ("decimals_lam0.4", "0.4", "2.5",
     ["2.71", "3.14", "1.41", "1.73", "2.24", "2.65", "3.32", "3.61",
      "0.58", "1.62"]),
]

# Oracle 1b: variance-factor battery -- lambdas x observation indices 1..10.
FACTOR_LAMBDAS = ["0.05", "0.2", "0.3", "0.5", "1"]
FACTOR_INDICES = list(range(1, 11))


def _fraction_series(values: list[str], lam: str, z0: str) -> list[Fraction]:
    """The EWMA recursion in exact rational arithmetic (the oracle)."""
    lam_f = Fraction(lam)
    z = Fraction(z0)
    out = []
    for v in values:
        z = lam_f * Fraction(v) + (1 - lam_f) * z
        out.append(z)
    return out


def run() -> dict:
    checks = 0
    matched = 0

    # -- Oracle 1a: recursion vs exact rational arithmetic, 12 dp ----------
    fraction_points = 0
    fraction_matched = 0
    battery_rows = []
    for label, lam, z0, values in FRACTION_BATTERY:
        got = ewma_series([float(v) for v in values], float(Fraction(lam)),
                          float(Fraction(z0)))
        want = _fraction_series(values, lam, z0)
        ok_here = 0
        for g, w in zip(got, want):
            fraction_points += 1
            ok = abs(Fraction(g) - w) <= TOL  # Fraction(float) is exact
            ok_here += int(ok)
        fraction_matched += ok_here
        battery_rows.append({"label": label, "points": len(values),
                             "matched": ok_here})
    checks += fraction_points
    matched += fraction_matched

    # -- Oracle 1b: time-varying limit factor vs exact rational, 12 dp -----
    # With mu0=0, sigma=1, L=3 the module's UCL is 3*sqrt(factor); the
    # oracle recomputes the factor exactly with Fraction and only then
    # takes one float sqrt.
    factor_checks = 0
    factor_matched = 0
    for lam in FACTOR_LAMBDAS:
        lam_fr = Fraction(lam)
        # sanity of the oracle itself: at i=1 the factor is exactly lam^2
        assert (lam_fr / (2 - lam_fr)) * (1 - (1 - lam_fr) ** 2) == lam_fr ** 2
        for i in FACTOR_INDICES:
            exact_factor = (lam_fr / (2 - lam_fr)) * (1 - (1 - lam_fr) ** (2 * i))
            want_ucl = 3.0 * math.sqrt(float(exact_factor))
            _, got_ucl = control_limits(0.0, 1.0, float(lam_fr), i, 3.0)
            factor_checks += 1
            factor_matched += int(abs(Fraction(got_ucl) - Fraction(want_ucl))
                                  <= TOL)
    checks += factor_checks
    matched += factor_matched

    # -- Oracle 2: NIST/SEMATECH 6.3.2.4 worked example ---------------------
    zs = [NIST_TARGET] + ewma_series(NIST_DATA, NIST_LAMBDA, NIST_TARGET)
    nist_values = len(NIST_EWMA_2DP)
    nist_values_matched = 0
    for z, published in zip(zs, NIST_EWMA_2DP):
        nist_values_matched += int(round(z, 2) == published)
    checks += nist_values
    matched += nist_values_matched

    lcl, ucl = steady_state_limits(NIST_TARGET, NIST_SIGMA, NIST_LAMBDA, NIST_L)
    ucl_ok = int(abs(ucl - NIST_UCL) <= NIST_LIMIT_TOL)
    lcl_ok = int(abs(lcl - NIST_LCL) <= NIST_LIMIT_TOL)
    checks += 2
    matched += ucl_ok + lcl_ok

    # the page: "all EWMA_t lie between the control limits"
    result = chart(NIST_DATA, NIST_TARGET, NIST_SIGMA, NIST_LAMBDA, NIST_L,
                   exact_limits=False)
    in_control_ok = int(result["out_of_control"] == [])
    checks += 1
    matched += in_control_ok

    return {
        "schema": "claimlib_ewma_v1",
        "module": "ewma",
        "checks": checks,
        "checks_matched": matched,
        "mismatches": checks - matched,
        "fraction_points": fraction_points,
        "fraction_matched": fraction_matched,
        "fraction_tolerance": "1e-12",
        "fraction_battery": battery_rows,
        "limit_factor_checks": factor_checks,
        "limit_factor_matched": factor_matched,
        "nist_values": nist_values,
        "nist_values_matched": nist_values_matched,
        "nist_ucl_published": NIST_UCL,
        "nist_lcl_published": NIST_LCL,
        "nist_ucl_computed_4dp": round(ucl, 4),
        "nist_lcl_computed_4dp": round(lcl, 4),
        "nist_limits_matched": ucl_ok + lcl_ok,
        "nist_all_in_control": bool(in_control_ok),
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "ewma.json", obj,
         script="python3 claimlib/modules/ewma/evidence.py")
    # claim:CLAIM-LIB-EWMA-001 checks_matched
    # All 76 recursion points and 50 limit factors match exact rational
    # arithmetic to 12 dp, and the NIST worked example is reproduced
    # (21 EWMA values, both limits, no false alarm), so checks_matched = 150
    # and mismatches = 0 (checks = 150).
    print(f"ewma: {obj['checks_matched']}/{obj['checks']} checks "
          f"(fraction oracle {obj['fraction_matched']}/{obj['fraction_points']}, "
          f"limit factors {obj['limit_factor_matched']}/{obj['limit_factor_checks']}, "
          f"NIST values {obj['nist_values_matched']}/{obj['nist_values']}, "
          f"limits {obj['nist_limits_matched']}/2); "
          f"mismatches {obj['mismatches']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
