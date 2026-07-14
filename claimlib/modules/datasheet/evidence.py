# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-DATASHEET-001 — the datasheet completeness scorer
counts lifecycle coverage exactly, over EVERY possible section state.

Oracles, none the module's own scoring path: (1) EXHAUSTIVE ENUMERATION —
each of the seven sections can be answered, justified-N/A, or a gap
(unanswered / empty / unjustified-N/A); all 3**7 = 2187 combinations are
generated, and for each the module's covered count and completeness
percentage are checked against an INDEPENDENT direct count of the assigned
states and an exact Fraction percentage; (2) the "covered = answered OR
justified-N/A" rule is pinned on hand-built anchors, including the datasheet
escape hatch (a section marked N/A with a reason counts, a bare N/A does
not); (3) unknown-section and malformed-value inputs fail closed.
Deterministic: same artifact every run.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from datasheet import (  # noqa: E402
    SECTIONS, DatasheetError, completeness,
)
from _util import emit  # noqa: E402

# Three representative values for the three states.
_VALUES = {
    "answered": "documented in full",
    "na": {"na": True, "reason": "dataset does not relate to people"},
    "gap": {"na": True, "reason": "   "},   # unjustified N/A -> gap
}


def run() -> dict:
    n = len(SECTIONS)

    # (1) Exhaustive: every assignment of a state to each of the 7 sections.
    enum_total = 0
    enum_ok = 0
    for states in product(("answered", "na", "gap"), repeat=n):
        sheet = {SECTIONS[i]: _VALUES[states[i]] for i in range(n)}
        got = completeness(sheet)
        # Independent direct count.
        exp_answered = states.count("answered")
        exp_na = states.count("na")
        exp_covered = exp_answered + exp_na
        exp_pct = round(float(Fraction(exp_covered, n) * 100), 2)
        enum_total += 1
        if (got["answered"] == exp_answered
                and got["not_applicable"] == exp_na
                and got["covered"] == exp_covered
                and got["completeness_pct"] == exp_pct
                and got["complete"] == (exp_covered == n)):
            enum_ok += 1

    # (2) Escape-hatch anchors, hand-derived.
    anchors = [
        completeness({})["covered"] == 0,
        completeness({s: "x" for s in SECTIONS})["complete"] is True,
        # a justified N/A covers its section
        completeness({"Composition": {"na": True, "reason": "n/a here"}}
                     )["covered"] == 1,
        # a bare/unjustified N/A does NOT cover
        completeness({"Composition": {"na": True, "reason": ""}}
                     )["covered"] == 0,
        # empty answer is a gap
        completeness({"Uses": "   "})["answered"] == 0,
        # mixed sheet: 2 answered + 1 justified-na = 3 covered of 7
        completeness({"Motivation": "why", "Uses": "how",
                      "Maintenance": {"na": True, "reason": "frozen"}}
                     )["covered"] == 3,
    ]
    anchors_ok = sum(anchors)

    rejects = 0
    reject_total = 4
    for bad in (lambda: completeness("notadict"),
                lambda: completeness({"Bogus Section": "x"}),
                lambda: completeness({"Uses": 123}),
                lambda: completeness({"Uses": {"reason": "no na flag"}})):
        try:
            bad()
        except DatasheetError:
            rejects += 1

    checks = enum_total + len(anchors)
    matched = enum_ok + anchors_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "datasheet",
        "checks": checks,
        "checks_matched": matched,
        "mismatches": checks - matched,
        "sections": n,
        "enumerated_combinations": enum_total,
        "enumerated_ok": enum_ok,
        "anchor_checks": len(anchors),
        "anchors_ok": anchors_ok,
        "reject_cases": reject_total,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "datasheet.json", obj,
         script="python3 claimlib/modules/datasheet/evidence.py")
    # claim:CLAIM-LIB-DATASHEET-001 checks_matched
    # All 2193 checks hold: the covered count and exact completeness
    # percentage
    # match an independent direct count over ALL 2187 (= 3**7) assignments
    # of {answered, justified-N/A, gap} to the seven lifecycle sections, and
    # six escape-hatch anchors pin the "justified-N/A covers, bare-N/A does
    # not" rule; mismatches = 0.
    print(f"datasheet: {obj['checks_matched']}/{obj['checks']} checks "
          f"(enumerated {obj['enumerated_ok']}/"
          f"{obj['enumerated_combinations']} over 3**7 states, anchors "
          f"{obj['anchors_ok']}/{obj['anchor_checks']}); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
