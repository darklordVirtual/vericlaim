# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-DP-001 — the composition arithmetic implements the
published theorems exactly and the accountant fails closed.

Oracles, none the module's own output: (1) the theorem shapes themselves,
checked as exact Fraction identities over a deterministic 40-ledger battery
— sequential composition is additive and permutation-invariant, parallel
composition equals the max and never exceeds sequential, group privacy is
exactly k*eps and multiplicative in k; (2) hand-computed values (0.5 + 0.25
composes to exactly 3/4; parallel of the same pair is exactly 1/2); (3) the
fail-closed accountant: a spend that would exceed the budget by ANY margin
(down to 1/10^12) raises BEFORE being recorded, the ledger state is
unchanged after a refusal, and remaining() + spent totals reconstruct the
budget exactly. Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from dp_composition import (  # noqa: E402
    DPError, Ledger, Mechanism, group_privacy, parallel, sequential,
)
from _util import emit  # noqa: E402


def synth_mechs(seed: int, k: int) -> list:
    return [Mechanism(f"m{seed}-{i}",
                      Fraction((seed * 7 + i * 13) % 29 + 1, 40),
                      Fraction((seed * 11 + i * 17) % 5, 1000))
            for i in range(k)]


def run() -> dict:
    hand = [
        sequential([Mechanism("a", "0.5"), Mechanism("b", "0.25")])
        == (Fraction(3, 4), Fraction(0)),
        parallel([Mechanism("a", "0.5"), Mechanism("b", "0.25")])
        == (Fraction(1, 2), Fraction(0)),
        group_privacy("0.1", 5) == Fraction(1, 2),
        sequential([Mechanism("a", "0.3", "0.001"),
                    Mechanism("b", "0.2", "0.002")])
        == (Fraction(1, 2), Fraction(3, 1000)),
    ]
    hand_ok = sum(hand)

    prop_checks = 0
    prop_ok = 0
    for seed in range(10):
        ms = synth_mechs(seed, 4)
        prop_checks += 4
        seq = sequential(ms)
        if seq == (sum(m.epsilon for m in ms), sum(m.delta for m in ms)):
            prop_ok += 1
        if sequential(list(reversed(ms))) == seq:
            prop_ok += 1
        par = parallel(ms)
        if par[0] <= seq[0] and par[1] <= seq[1] and \
                par == (max(m.epsilon for m in ms),
                        max(m.delta for m in ms)):
            prop_ok += 1
        if group_privacy(ms[0].epsilon, 6) == \
                2 * group_privacy(ms[0].epsilon, 3):
            prop_ok += 1

    # Fail-closed accountant.
    ledger = Ledger("1.0", "0.01")
    ledger.spend(Mechanism("q1", "0.6", "0.004"))
    ledger.spend(Mechanism("q2", "0.4", "0.006"))
    exact_exhaustion = ledger.remaining() == (Fraction(0), Fraction(0))
    refused = 0
    try:
        ledger.spend(Mechanism("q3", Fraction(1, 10 ** 12)))
    except DPError:
        refused = 1
    state_unchanged = len(ledger.spent) == 2
    reconstruct = (ledger.remaining()[0]
                   + sum(m.epsilon for m in ledger.spent)
                   == Fraction(1))
    delta_guard = 0
    fresh = Ledger("10", "0.001")
    try:
        fresh.spend(Mechanism("d", "0.1", "0.002"))
    except DPError:
        delta_guard = 1
    accountant_ok = sum([exact_exhaustion, refused, state_unchanged,
                         reconstruct, delta_guard])

    rejects = 0
    for bad in (lambda: Mechanism("", "0.5"),
                lambda: Mechanism("a", "-0.1"),
                lambda: Mechanism("a", "0.1", "1.5"),
                lambda: Mechanism("a", float("nan")),
                lambda: Mechanism("a", True),
                lambda: sequential([]),
                lambda: parallel(["not-a-mechanism"]),
                lambda: group_privacy("0.1", 0),
                lambda: group_privacy("0.1", 2.5)):
        try:
            bad()
        except DPError:
            rejects += 1

    total = len(hand) + prop_checks + 5
    matched = hand_ok + prop_ok + accountant_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "dp_composition",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "hand_computed_ok": hand_ok,
        "property_checks": prop_checks,
        "property_ok": prop_ok,
        "accountant_ok": accountant_ok,
        "reject_cases": 9,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "dp_composition.json", obj,
         script="python3 claimlib/modules/dp_composition/evidence.py")
    # claim:CLAIM-LIB-DP-001 checks_matched
    # All 49 checks hold as exact Fraction identities: 4 hand-computed
    # compositions, 40 theorem-shaped properties over the ledger battery,
    # and the 5 fail-closed accountant checks (including refusal of a
    # 1/10^12 overspend with unchanged state) — checks_matched = 49,
    # mismatches = 0.
    print(f"dp_composition: {obj['checks_matched']}/{obj['checks']} exact "
          f"checks (hand {obj['hand_computed_ok']}/4, properties "
          f"{obj['property_ok']}/{obj['property_checks']}, accountant "
          f"{obj['accountant_ok']}/5); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
