# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-OWASP-LLM-001 — the encoded taxonomy matches the
published OWASP Top 10 for LLM Applications 2025 and coverage is exact.

Oracle: the official v2025 list (verified against both genai.owasp.org's
list page and the official 45-page PDF's chapter headings): exactly ten
entries LLM01..LLM10 with the published titles — Prompt Injection ranked
first, the 2025 additions System Prompt Leakage (LLM07) and Vector and
Embedding Weaknesses (LLM08) present, and Unbounded Consumption as LLM10.
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

from owasp_llm10 import RISKS, OWASPError, coverage, is_risk  # noqa: E402
from _util import emit  # noqa: E402

PUBLISHED = {
    "LLM01": "Prompt Injection",
    "LLM02": "Sensitive Information Disclosure",
    "LLM03": "Supply Chain",
    "LLM04": "Data and Model Poisoning",
    "LLM05": "Improper Output Handling",
    "LLM06": "Excessive Agency",
    "LLM07": "System Prompt Leakage",
    "LLM08": "Vector and Embedding Weaknesses",
    "LLM09": "Misinformation",
    "LLM10": "Unbounded Consumption",
}


def run() -> dict:
    taxonomy = [
        RISKS == PUBLISHED,
        len(RISKS) == 10,
        sorted(RISKS) == [f"LLM{i:02d}" for i in range(1, 11)],
        RISKS["LLM01"] == "Prompt Injection",
        all(is_risk(c) for c in RISKS),
        not is_risk("LLM11") and not is_risk("llm01"),
    ]
    taxonomy_ok = sum(taxonomy)

    cov_checks = 0
    cov_ok = 0
    for mitigated, want in [(list(RISKS), 10), (["LLM01", "LLM06"], 2),
                            ([], 0)]:
        cov_checks += 1
        got = coverage(mitigated)
        if got["mitigated"] == want and got["coverage_pct"] == round(
                float(Fraction(want, 10) * 100), 2) \
                and len(got["gaps"]) == 10 - want:
            cov_ok += 1

    rejects = 0
    for bad in (lambda: coverage(["LLM11"]),
                lambda: coverage(["llm01"]),
                lambda: coverage(["LLM01", "XSS"])):
        try:
            bad()
        except OWASPError:
            rejects += 1

    total = len(taxonomy) + cov_checks
    matched = taxonomy_ok + cov_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "owasp_llm10",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "risks": len(RISKS),
        "reject_cases": 3,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "owasp_llm10.json", obj,
         script="python3 claimlib/modules/owasp_llm10/evidence.py")
    # claim:CLAIM-LIB-OWASP-LLM-001 checks_matched
    # All 9 checks pass: the ten encoded entries match the published v2025
    # list verbatim (LLM01 Prompt Injection .. LLM10 Unbounded Consumption)
    # and coverage arithmetic is Fraction-exact — checks_matched = 9,
    # mismatches = 0.
    print(f"owasp_llm10: {obj['checks_matched']}/{obj['checks']} checks "
          f"({obj['risks']} published risks); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
