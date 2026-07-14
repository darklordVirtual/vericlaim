# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-GSN-001 — the assurance-case validator enforces
every GSN structural rule and catches every seeded violation.

Oracles, none the module's own output: (1) the GSN Community Standard v3
relation rules encoded verbatim (goal supported by goal/strategy/solution,
strategy supported by goal; goals/strategies take context/assumption/
justification as context) — a fixed well-formed case exercising every legal
edge type must validate clean; (2) an ADVERSARIAL MUTATION BATTERY: from
the valid case, every one of a fixed set of single mutations (illegal edge
types in both relations, a circular argument, an unsupported goal, an
undeveloped-with-support contradiction, a non-goal marked undeveloped, a
solution with outgoing edges, an unreachable island, a rootless cycle) must
be caught — mutations_missed = 0; (3) exhaustive edge-type enumeration:
all 36 (from-kind, to-kind) pairs for supported_by are classified and
exactly the 4 legal pairs validate. Deterministic: same artifact always.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from gsn_case import (  # noqa: E402
    ELEMENT_KINDS, Case, GSNError, is_valid, validate,
)
from _util import emit  # noqa: E402

VALID = Case(
    elements={
        "G1": "goal", "G2": "goal", "G3": "goal", "G4": "goal",
        "St1": "strategy",
        "Sn1": "solution", "Sn2": "solution",
        "C1": "context", "A1": "assumption", "J1": "justification",
    },
    supported_by=[
        ("G1", "St1"),            # goal -> strategy
        ("St1", "G2"),            # strategy -> goal
        ("St1", "G3"),
        ("G2", "Sn1"),            # goal -> solution
        ("G3", "G4"),             # goal -> goal
        ("G4", "Sn2"),
    ],
    in_context_of=[
        ("G1", "C1"), ("St1", "J1"), ("G2", "A1"),
    ],
    undeveloped=set(),
)


def mutations() -> list:
    """(label, Case) pairs — every case must FAIL validation."""
    e = dict(VALID.elements)
    sb = list(VALID.supported_by)
    ctx = list(VALID.in_context_of)
    return [
        ("goal supported by context",
         Case(e, sb + [("G4", "C1")], ctx, set())),
        ("strategy supported by solution",
         Case(e, sb + [("St1", "Sn1")], ctx, set())),
        ("strategy supported by strategy",
         Case({**e, "St2": "strategy"}, sb + [("St1", "St2")], ctx, set())),
        ("solution takes context",
         Case(e, sb, ctx + [("Sn1", "C1")], set())),
        ("context supports a goal",
         Case(e, sb + [("C1", "G2")], ctx, set())),
        ("circular argument",
         Case(e, sb + [("G4", "G3")], ctx, set())),
        ("unsupported goal",
         Case({**e, "G5": "goal"}, sb, ctx, set())),
        ("undeveloped AND supported",
         Case(e, sb, ctx, {"G2"})),
        ("non-goal marked undeveloped",
         Case(e, sb, ctx, {"Sn1"})),
        ("unknown edge endpoint",
         Case(e, sb + [("G4", "GHOST")], ctx, set())),
        ("unreachable island",
         Case({**e, "G9": "goal", "Sn9": "solution"},
              sb + [("G9", "Sn9")], ctx, set())),
        ("rootless: every goal a target",
         Case({"Ga": "goal", "Gb": "goal"},
              [("Ga", "Gb"), ("Gb", "Ga")], [], set())),
    ]


def run() -> dict:
    valid_ok = int(is_valid(VALID))
    undeveloped_ok = int(is_valid(Case(
        {"G1": "goal", "St1": "strategy", "G2": "goal", "G3": "goal",
         "Sn1": "solution"},
        [("G1", "St1"), ("St1", "G2"), ("St1", "G3"), ("G2", "Sn1")],
        [], {"G3"})))

    muts = mutations()
    caught = sum(1 for _, case in muts if not is_valid(case))

    # Exhaustive supported_by pair enumeration: exactly 4 legal pairs.
    legal = {("goal", "goal"), ("goal", "strategy"), ("goal", "solution"),
             ("strategy", "goal")}
    enum_checks = 0
    enum_ok = 0
    for ks in ELEMENT_KINDS:
        for kd in ELEMENT_KINDS:
            enum_checks += 1
            case = Case(
                {"root": "goal", "X": ks, "Y": kd, "SnR": "solution",
                 "SnX": "solution", "SnY": "solution"},
                [("root", "SnR")]
                + ([("root", "X")] if ks in ("goal", "strategy",
                                             "solution") else [])
                + ([("X", "Y")])
                + ([("X", "SnX")] if ks == "goal" else [])
                + ([("Y", "SnY")] if kd == "goal" else []),
                ([("root", "X")] if ks in ("context", "assumption",
                                           "justification") else [])
                + ([("X", "Y")] if False else []),
                frozenset(),
            )
            edge_problems = [p for p in validate(case)
                             if p.startswith("supported_by X->Y")]
            is_legal = (ks, kd) in legal
            if is_legal == (not edge_problems):
                enum_ok += 1

    rejects = 0
    for bad in (lambda: Case({}, [], [], set()),
                lambda: Case({"G1": "target"}, [], [], set()),
                lambda: Case({"": "goal"}, [], [], set()),
                lambda: Case({"G1": "goal"}, [("G1",)], [], set()),
                lambda: Case({"G1": "goal"}, "nope", [], set())):
        try:
            bad()
        except GSNError:
            rejects += 1

    total = 1 + 1 + len(muts) + enum_checks
    matched = valid_ok + undeveloped_ok + caught + enum_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "gsn_case",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "valid_case_ok": valid_ok,
        "undeveloped_ok": undeveloped_ok,
        "mutations": len(muts),
        "mutations_caught": caught,
        "mutations_missed": len(muts) - caught,
        "pair_enum_checks": enum_checks,
        "pair_enum_ok": enum_ok,
        "reject_cases": 5,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "gsn_case.json", obj,
         script="python3 claimlib/modules/gsn_case/evidence.py")
    # claim:CLAIM-LIB-GSN-001 checks_matched
    # All 50 checks pass: the exemplar case exercising every legal GSN edge
    # validates clean, the honestly-undeveloped case validates, every one of
    # the 12 adversarial mutations is caught (mutations_missed = 0), and the
    # exhaustive 36-pair supported_by enumeration admits exactly the
    # standard's 4 legal pairs — checks_matched = 50, mismatches = 0.
    print(f"gsn_case: {obj['checks_matched']}/{obj['checks']} checks "
          f"(mutations {obj['mutations_caught']}/{obj['mutations']} caught, "
          f"pair enum {obj['pair_enum_ok']}/{obj['pair_enum_checks']}); "
          f"rejects {obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
