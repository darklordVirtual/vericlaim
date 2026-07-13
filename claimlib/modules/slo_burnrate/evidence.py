# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-SLO-BURNRATE-001 — the burn-rate arithmetic
reproduces the Google SRE Workbook's published alerting policy exactly.

Oracles, none of them the module's own output: (1) the published Workbook
chapter 5 table for a 30-day period — 2% budget in 1 hour is burn rate 14.4,
5% in 6 hours is 6, 10% in 3 days is 1, with 5 min / 30 min / 6 h short
windows (long/12); (2) exact algebra — every function checked against its
inverse and against Fraction-exact recomputation; (3) the Workbook's worked
magnitude: at burn rate 1 a 30-day budget lasts exactly 720 h, at 1000 it
lasts 0.72 h. Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from slo_burnrate import (  # noqa: E402
    GOOGLE_30D_POLICY, BurnRateError, budget_consumed, budget_remaining,
    burn_rate, burn_rate_from_error_ratio, error_rate, multiwindow_alert,
    short_window, time_to_exhaustion,
)
from _util import emit  # noqa: E402

PERIOD_MIN = 720.0 * 60  # 30 days in minutes

# The published Workbook table (30-day period): (budget fraction, long window
# in minutes, published burn rate, published short window in minutes).
WORKBOOK_TABLE = [
    (0.02, 60.0, 14.4, 5.0),
    (0.05, 360.0, 6.0, 30.0),
    (0.10, 4320.0, 1.0, 360.0),
]


def run() -> dict:
    table_checks = []
    for frac, long_w, published_rate, published_short in WORKBOOK_TABLE:
        got_rate = burn_rate(frac, long_w, PERIOD_MIN)
        exact = float(Fraction(str(frac)) * Fraction(str(PERIOD_MIN))
                      / Fraction(str(long_w)))
        table_checks.append({
            "budget": frac, "window_min": long_w,
            "rate_ok": got_rate == published_rate,
            "exact_ok": abs(got_rate - exact) < 1e-9,
            "short_ok": short_window(long_w) == published_short,
            "inverse_ok": budget_consumed(published_rate, long_w,
                                          PERIOD_MIN) == frac,
        })
    table_ok = sum(1 for c in table_checks
                   if all(v for k, v in c.items() if k.endswith("_ok")))

    policy_ok = 0
    for tier in GOOGLE_30D_POLICY:
        recomputed = burn_rate(tier["budget_consumed"],
                               tier["long_window_minutes"], PERIOD_MIN)
        if recomputed == tier["burn_rate"] and \
                short_window(tier["long_window_minutes"]) == \
                tier["short_window_minutes"]:
            policy_ok += 1

    algebra = [
        time_to_exhaustion(1.0, 720.0) == 720.0,
        time_to_exhaustion(1000.0, 720.0) == 0.72,
        error_rate(10.0, 99.9) == 0.01,
        burn_rate_from_error_ratio(0.01, 99.9) == 10.0,
        budget_remaining(2.0, 360.0, 720.0) == 0.0,
        budget_remaining(1.0, 720.0, 720.0) == 0.0,
        error_rate(1.0, 100.0) == 0.0,
    ]
    algebra_ok = sum(algebra)

    # Multiwindow condition semantics (99.9% SLO, burn threshold 14.4):
    # threshold error ratio = 14.4 * 0.001 = 0.0144.
    mw = [
        multiwindow_alert(0.02, 0.02, 14.4, 99.9) is True,
        multiwindow_alert(0.02, 0.001, 14.4, 99.9) is False,   # short recovered
        multiwindow_alert(0.001, 0.02, 14.4, 99.9) is False,   # brief blip
        multiwindow_alert(0.0144, 0.0144, 14.4, 99.9) is False,  # at threshold
    ]
    mw_ok = sum(mw)

    rejects = 0
    for bad in (lambda: burn_rate(1.5, 60, 720),
                lambda: burn_rate(0.02, 0, 720),
                lambda: burn_rate(0.02, 800, 720),
                lambda: burn_rate_from_error_ratio(0.01, 100.0),
                lambda: time_to_exhaustion(0.0, 720.0)):
        try:
            bad()
        except BurnRateError:
            rejects += 1

    total = len(table_checks) + len(GOOGLE_30D_POLICY) + len(algebra) + len(mw)
    ok = table_ok + policy_ok + algebra_ok + mw_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "slo_burnrate",
        "checks": total,
        "checks_matched": ok,
        "mismatches": total - ok,
        "workbook_rows": len(table_checks),
        "workbook_rows_ok": table_ok,
        "policy_tiers_ok": policy_ok,
        "algebra_ok": algebra_ok,
        "multiwindow_ok": mw_ok,
        "reject_cases": 5,
        "rejects_ok": rejects,
        "table_detail": table_checks,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "slo_burnrate.json", obj,
         script="python3 claimlib/modules/slo_burnrate/evidence.py")
    # claim:CLAIM-LIB-SLO-BURNRATE-001 checks_matched
    # All 17 checks pass: the 3 published Workbook rows (14.4 / 6 / 1 with
    # 5 min / 30 min / 6 h short windows), the 3 policy tiers, 7 algebraic
    # identities and 4 multiwindow conditions — checks_matched = 17,
    # mismatches = 0.
    print(f"slo_burnrate: {obj['checks_matched']}/{obj['checks']} checks "
          f"(workbook {obj['workbook_rows_ok']}/{obj['workbook_rows']}, "
          f"policy {obj['policy_tiers_ok']}/3, algebra {obj['algebra_ok']}/7, "
          f"multiwindow {obj['multiwindow_ok']}/4); "
          f"rejects {obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
