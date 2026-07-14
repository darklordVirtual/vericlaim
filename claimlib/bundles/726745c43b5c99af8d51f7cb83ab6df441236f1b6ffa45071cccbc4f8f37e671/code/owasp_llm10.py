# SPDX-License-Identifier: Apache-2.0
"""OWASP Top 10 for LLM Applications 2025 — risk taxonomy + mitigation
coverage — reusable, claim-bound.

A pre-verified claimlib code artifact for AI assurance. The OWASP GenAI
Security Project's 2025 list ranks the ten most critical risks of
LLM-based applications; it is the shared vocabulary between AI engineering
and security review. This module encodes the published taxonomy (verified
against the official v2025 PDF) and scores declared mitigation coverage.

Coverage of a risk is the caller's declaration that mitigations exist, not
an assessment of their strength — and the Top 10 is a prioritized
vocabulary, not a complete threat model (pair it with a real one).
The caveat travels with the claim.

Public API
----------
    RISKS: dict[str, str]                # "LLM01".."LLM10" -> title
    is_risk(code) -> bool
    coverage(mitigated: Iterable[str]) -> dict

    >>> RISKS["LLM01"]
    'Prompt Injection'
"""
from __future__ import annotations

from collections.abc import Iterable
from fractions import Fraction

# OWASP Top 10 for LLM Applications, Version 2025 (released 2024-11-18).
RISKS = {
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


class OWASPError(ValueError):
    """Unknown risk code (fail closed)."""


def is_risk(code: str) -> bool:
    """True iff *code* is one of the ten 2025 risk codes."""
    return code in RISKS


def coverage(mitigated: Iterable[str]) -> dict:
    """Mitigation coverage of the ten risks by a declared programme."""
    have = set(mitigated)
    unknown = sorted(have - set(RISKS))
    if unknown:
        raise OWASPError(f"unknown risk code(s): {unknown} — expected "
                         f"LLM01..LLM10")
    gaps = sorted(set(RISKS) - have)
    return {
        "risks_total": len(RISKS),
        "mitigated": len(have),
        "coverage_pct": round(float(Fraction(len(have), len(RISKS)) * 100),
                              2),
        "gaps": gaps,
    }
