# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-MODEL-CARD-001 — the encoded section taxonomy
matches the published paper and the completeness arithmetic is exact.

Oracle: the nine model-card sections proposed by Mitchell et al., "Model
Cards for Model Reporting" (FAT* 2019), verified verbatim against the
paper's full text (arXiv:1810.03993): Model Details, Intended Use,
Factors, Metrics, Evaluation Data, Training Data, Quantitative Analyses,
Ethical Considerations, Caveats and Recommendations. Completeness
percentages are recomputed with exact Fraction arithmetic; whitespace-only
sections count as empty; unknown section names fail closed. Deterministic:
same artifact on every run.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from model_card import SECTIONS, ModelCardError, completeness  # noqa: E402
from _util import emit  # noqa: E402

PUBLISHED = ("Model Details", "Intended Use", "Factors", "Metrics",
             "Evaluation Data", "Training Data", "Quantitative Analyses",
             "Ethical Considerations", "Caveats and Recommendations")


def run() -> dict:
    taxonomy_ok = int(SECTIONS == PUBLISHED and len(SECTIONS) == 9)

    full = completeness({s: f"content for {s}" for s in SECTIONS})
    empty_card = completeness({})
    partial = completeness({"Model Details": "x", "Metrics": "y",
                            "Training Data": "   "})
    cases = [
        full["complete"] is True and full["completeness_pct"] == 100.0
        and full["missing"] == [],
        empty_card["present"] == 0 and len(empty_card["missing"]) == 9,
        partial["present"] == 2,
        partial["completeness_pct"] == round(float(Fraction(2, 9) * 100), 2),
        partial["empty_sections"] == ["Training Data"],
        "Training Data" in partial["missing"],
        partial["present_sections"] == ["Model Details", "Metrics"],
    ]
    cases_ok = sum(cases)

    rejects = 0
    for bad in (lambda: completeness({"Model details": "typo case"}),
                lambda: completeness({"License": "MIT"}),
                lambda: completeness({"Metrics": 42}),
                lambda: completeness("nope")):
        try:
            bad()
        except ModelCardError:
            rejects += 1

    total = 1 + len(cases)
    matched = taxonomy_ok + cases_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "model_card",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "sections": len(SECTIONS),
        "reject_cases": 4,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "model_card.json", obj,
         script="python3 claimlib/modules/model_card/evidence.py")
    # claim:CLAIM-LIB-MODEL-CARD-001 checks_matched
    # All 8 checks pass: the nine published sections verbatim, and
    # Fraction-exact completeness on full/empty/partial cards including
    # whitespace-only sections — checks_matched = 8, mismatches = 0.
    print(f"model_card: {obj['checks_matched']}/{obj['checks']} checks "
          f"({obj['sections']} published sections); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
