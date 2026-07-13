# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-AI-ACT-001 — the encoded AI Act taxonomy matches
the final OJ text and the screening arithmetic is exact.

Oracle: the published structure of Regulation (EU) 2024/1689, verified
mechanically against the Publications Office English text (CELEX
32024R1689): 13 chapters, 113 articles, 13 annexes; exactly eight lettered
prohibitions in Article 5(1) (a)-(h); exactly eight numbered high-risk
areas in Annex III; and the operative tier vocabulary (the popular
"unacceptable/limited/minimal risk" pyramid labels do NOT appear as legal
categories in the enacted text — "minimal risk" has zero occurrences).
Coverage percentages are recomputed with exact Fraction arithmetic.
Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from eu_ai_act import (  # noqa: E402
    ANNEX3_AREAS, ART5_PROHIBITIONS, OPERATIVE_TIERS, STRUCTURE, AIActError,
    area_coverage, is_high_risk_area, is_prohibition, prohibition_screen,
)
from _util import emit  # noqa: E402


def run() -> dict:
    structure_ok = int(STRUCTURE == {"chapters": 13, "articles": 113,
                                     "annexes": 13})
    prohibitions_ok = int(
        sorted(ART5_PROHIBITIONS) == list("abcdefgh")
        and len(ART5_PROHIBITIONS) == 8
        and "Social scoring" in ART5_PROHIBITIONS["c"]
        and "biometric identification" in ART5_PROHIBITIONS["h"])
    areas_ok = int(
        sorted(ANNEX3_AREAS) == list(range(1, 9))
        and ANNEX3_AREAS[1] == "Biometrics"
        and ANNEX3_AREAS[6] == "Law enforcement")
    tiers_ok = int(len(OPERATIVE_TIERS) == 5
                   and all("risk" in t or "Art" in t or "Chapter" in t
                           for t in OPERATIVE_TIERS))

    membership_ok = int(
        all(is_prohibition(c) for c in "abcdefgh")
        and not is_prohibition("i") and not is_prohibition("A")
        and all(is_high_risk_area(n) for n in range(1, 9))
        and not is_high_risk_area(0) and not is_high_risk_area(9)
        and not is_high_risk_area(True))

    screen_clean = prohibition_screen([])
    screen_hit = prohibition_screen(["c", "f"])
    screen_ok = int(screen_clean["compliant"] is True
                    and screen_clean["flagged_count"] == 0
                    and screen_hit["compliant"] is False
                    and screen_hit["flagged"] == ["c", "f"]
                    and screen_hit["prohibitions_total"] == 8)

    coverage_checks = 0
    coverage_ok = 0
    for assessed, want in [(range(1, 9), 8), ([1, 4, 6], 3), ([], 0)]:
        coverage_checks += 1
        got = area_coverage(assessed)
        exact_pct = round(float(Fraction(want, 8) * 100), 2)
        if got["assessed"] == want and got["coverage_pct"] == exact_pct \
                and len(got["gaps"]) == 8 - want:
            coverage_ok += 1

    rejects = 0
    for bad in (lambda: prohibition_screen(["z"]),
                lambda: prohibition_screen(["a", "x"]),
                lambda: area_coverage([9]),
                lambda: area_coverage([0]),
                lambda: area_coverage([True])):
        try:
            bad()
        except AIActError:
            rejects += 1

    total = 5 + 1 + coverage_checks
    matched = (structure_ok + prohibitions_ok + areas_ok + tiers_ok
               + membership_ok + screen_ok + coverage_ok)
    return {
        "schema": "claimlib_evidence_v1",
        "module": "eu_ai_act",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "chapters": STRUCTURE["chapters"],
        "articles": STRUCTURE["articles"],
        "annexes": STRUCTURE["annexes"],
        "prohibitions": len(ART5_PROHIBITIONS),
        "high_risk_areas": len(ANNEX3_AREAS),
        "operative_tiers": len(OPERATIVE_TIERS),
        "reject_cases": 5,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "eu_ai_act.json", obj,
         script="python3 claimlib/modules/eu_ai_act/evidence.py")
    # claim:CLAIM-LIB-AI-ACT-001 checks_matched
    # All 9 checks pass: the encoded structure (13 chapters / 113 articles /
    # 13 annexes), the eight Article 5(1) prohibitions, the eight Annex III
    # areas, the five operative tiers, membership logic, screening verdicts
    # and Fraction-exact coverage — checks_matched = 9, mismatches = 0.
    print(f"eu_ai_act: {obj['checks_matched']}/{obj['checks']} checks "
          f"({obj['chapters']} chapters / {obj['articles']} articles / "
          f"{obj['annexes']} annexes; {obj['prohibitions']} prohibitions, "
          f"{obj['high_risk_areas']} high-risk areas); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
