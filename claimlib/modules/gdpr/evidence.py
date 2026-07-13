# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-GDPR-001 — the encoded GDPR taxonomy matches the
Regulation's published structure and the coverage arithmetic is exact.

Oracles, none the module's own output: (1) the Regulation's published shape —
Regulation (EU) 2016/679 has 99 articles in 11 chapters; the encoded chapter
ranges must PARTITION 1..99 exactly (every article in exactly one chapter —
verified exhaustively, an error in any transcribed range breaks the
partition); (2) published anchor articles: Art. 5 (principles) sits in
Chapter II, Art. 17 (erasure) in Chapter III, Art. 33 (breach notification)
in Chapter IV, Art. 83 (fines) in Chapter VIII; (3) Article 5 enumerates
six lettered principles plus accountability, and Article 32(1) four
measures; (4) coverage percentages recomputed independently with exact
Fraction arithmetic. Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from gdpr import (  # noqa: E402
    ART32_MEASURES, CHAPTERS, GDPRError, N_ARTICLES, PRINCIPLES,
    art32_coverage, chapter_of, principle_coverage,
)
from _util import emit  # noqa: E402

# Published anchor articles and their chapters (any GDPR text confirms them).
ANCHORS = [(5, 2), (17, 3), (33, 4), (44, 5), (77, 8), (83, 8), (99, 11)]

COVERAGE_CASES = [
    (["a", "b", "c", "d", "e", "f", "accountability"], 7),
    (["a", "f"], 2),
    ([], 0),
]


def run() -> dict:
    # 1) Exhaustive partition check over all 99 articles.
    partition_ok = 1
    seen = []
    for article in range(1, N_ARTICLES + 1):
        owners = [ch for ch, (_, first, last) in CHAPTERS.items()
                  if first <= article <= last]
        if len(owners) != 1:
            partition_ok = 0
        seen.append(len(owners) == 1)
    structure_ok = int(len(CHAPTERS) == 11 and N_ARTICLES == 99
                       and sum(last - first + 1
                               for _, first, last in CHAPTERS.values()) == 99)

    anchors_ok = sum(1 for art, ch in ANCHORS if chapter_of(art) == ch)

    counts_ok = int(len(PRINCIPLES) == 7 and len(ART32_MEASURES) == 4
                    and sorted(ART32_MEASURES) == ["a", "b", "c", "d"]
                    and sorted(PRINCIPLES) == sorted(
                        ["a", "b", "c", "d", "e", "f", "accountability"]))

    coverage_ok = 0
    for impl, want in COVERAGE_CASES:
        got = principle_coverage(impl)
        exact_pct = float(Fraction(want, 7) * 100)
        if got["implemented"] == want and \
                abs(got["coverage_pct"] - round(exact_pct, 2)) < 1e-9 and \
                len(got["gaps"]) == 7 - want:
            coverage_ok += 1
    art32 = art32_coverage(["a", "d"])
    art32_ok = int(art32["implemented"] == 2
                   and art32["coverage_pct"] == 50.0
                   and art32["gaps"] == ["b", "c"])

    rejects = 0
    for bad in (lambda: chapter_of(0), lambda: chapter_of(100),
                lambda: chapter_of(True),
                lambda: principle_coverage(["z"]),
                lambda: art32_coverage(["e"])):
        try:
            bad()
        except GDPRError:
            rejects += 1

    total = 1 + 1 + len(ANCHORS) + 1 + len(COVERAGE_CASES) + 1
    matched = partition_ok + structure_ok + anchors_ok + counts_ok \
        + coverage_ok + art32_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "gdpr",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "articles": N_ARTICLES,
        "chapters": len(CHAPTERS),
        "partition_ok": partition_ok,
        "anchors_ok": anchors_ok,
        "principles": len(PRINCIPLES),
        "art32_measures": len(ART32_MEASURES),
        "coverage_ok": coverage_ok + art32_ok,
        "reject_cases": 5,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "gdpr.json", obj,
         script="python3 claimlib/modules/gdpr/evidence.py")
    # claim:CLAIM-LIB-GDPR-001 checks_matched
    # All 14 checks pass: the 11 chapter ranges partition the 99 articles
    # exactly, 7 published anchor articles resolve to their chapters, the
    # principle/measure counts match Art. 5 and Art. 32(1), and coverage
    # arithmetic is Fraction-exact — checks_matched = 14, mismatches = 0.
    print(f"gdpr: {obj['checks_matched']}/{obj['checks']} checks "
          f"({obj['chapters']} chapters partition {obj['articles']} articles: "
          f"{'ok' if obj['partition_ok'] else 'BROKEN'}; anchors "
          f"{obj['anchors_ok']}/7); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
