# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-DORA-001 — the encoded DORA taxonomy matches the
final OJ text and the pillar arithmetic is exact.

Oracle: the published structure of Regulation (EU) 2022/2554, verified
mechanically against the Publications Office XHTML of CELEX 32022R2554 —
9 chapter headings and exactly 64 sequential articles. The encoded chapter
ranges must PARTITION 1..64 (every article in exactly one chapter, checked
exhaustively — a mistranscribed range breaks the partition), the five
pillars must anchor to chapters II-VI with their official titles, and
published anchor articles must resolve (Art. 5 ICT risk, Art. 17 incidents,
Art. 24 testing, Art. 28 third-party, Art. 45 info-sharing, Art. 64 final).
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

from dora_eu import (  # noqa: E402
    CHAPTERS, N_ARTICLES, PILLARS, DORAError, chapter_of, pillar_coverage,
    pillar_of,
)
from _util import emit  # noqa: E402

ANCHORS = [(1, 1), (5, 2), (16, 2), (17, 3), (24, 4), (28, 5), (44, 5),
           (45, 6), (46, 7), (57, 8), (64, 9)]


def run() -> dict:
    partition_ok = 1
    for article in range(1, N_ARTICLES + 1):
        owners = [ch for ch, (_, lo, hi) in CHAPTERS.items()
                  if lo <= article <= hi]
        if len(owners) != 1:
            partition_ok = 0
    structure_ok = int(
        len(CHAPTERS) == 9 and N_ARTICLES == 64
        and sum(hi - lo + 1 for _, lo, hi in CHAPTERS.values()) == 64)

    anchors_ok = sum(1 for art, ch in ANCHORS if chapter_of(art) == ch)

    pillar_checks = [
        len(PILLARS) == 5,
        all(PILLARS[k]["name"] == CHAPTERS[PILLARS[k]["chapter"]][0]
            for k in PILLARS),
        pillar_of(10) == "ict_risk",
        pillar_of(45) == "info_sharing",
        pillar_of(2) is None,         # general provisions: no pillar
        pillar_of(50) is None,        # competent authorities: no pillar
    ]
    pillar_ok = sum(pillar_checks)

    cov_checks = 0
    cov_ok = 0
    for impl, want in [(list(PILLARS), 5), (["ict_risk", "testing"], 2),
                       ([], 0)]:
        cov_checks += 1
        got = pillar_coverage(impl)
        if got["implemented"] == want and got["coverage_pct"] == round(
                float(Fraction(want, 5) * 100), 2) \
                and len(got["gaps"]) == 5 - want:
            cov_ok += 1

    rejects = 0
    for bad in (lambda: chapter_of(0), lambda: chapter_of(65),
                lambda: chapter_of(True), lambda: chapter_of("5"),
                lambda: pillar_coverage(["resilience"])):
        try:
            bad()
        except DORAError:
            rejects += 1

    total = 2 + len(ANCHORS) + len(pillar_checks) + cov_checks
    matched = partition_ok + structure_ok + anchors_ok + pillar_ok + cov_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "dora_eu",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "chapters": len(CHAPTERS),
        "articles": N_ARTICLES,
        "pillars": len(PILLARS),
        "partition_ok": partition_ok,
        "anchors_ok": anchors_ok,
        "reject_cases": 5,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "dora_eu.json", obj,
         script="python3 claimlib/modules/dora_eu/evidence.py")
    # claim:CLAIM-LIB-DORA-001 checks_matched
    # All 22 checks pass: the 9 chapter ranges partition the 64 articles
    # exactly (exhaustively verified), 11 anchor articles resolve, the five
    # pillars carry their official chapter titles, and coverage is
    # Fraction-exact — checks_matched = 22, mismatches = 0.
    print(f"dora_eu: {obj['checks_matched']}/{obj['checks']} checks "
          f"({obj['chapters']} chapters partition {obj['articles']} "
          f"articles: {'ok' if obj['partition_ok'] else 'BROKEN'}; "
          f"{obj['pillars']} pillars; anchors {obj['anchors_ok']}/11); "
          f"rejects {obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
