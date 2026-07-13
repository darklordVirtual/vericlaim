# SPDX-License-Identifier: Apache-2.0
"""EU AI Act (Regulation (EU) 2024/1689) structure — prohibited practices,
high-risk areas and the operative risk tiers — reusable, claim-bound.

A pre-verified claimlib code artifact for AI governance in enterprise
environments. Encodes the published structure of the AI Act's final OJ
text: 13 chapters, 113 articles and 13 annexes; the eight Article 5(1)
prohibited practices (a)-(h); the eight Annex III high-risk areas; and the
Act's OPERATIVE tier vocabulary (prohibited practices, high-risk AI
systems, Article 50 transparency obligations, general-purpose AI models,
GPAI with systemic risk) — note the popular "unacceptable/limited/minimal"
pyramid labels are not the Regulation's operative terms.

Screening functions score a declared practice inventory against the
prohibitions and map use-cases to Annex III areas. Encoding the law is not
legal advice, and Annex III areas carry conditions and exceptions in the
full text — classification of a real system belongs to counsel. The caveat
travels with the claim.

Public API
----------
    STRUCTURE                        # chapters/articles/annexes counts
    ART5_PROHIBITIONS: dict[str, str]     # "a".."h"
    ANNEX3_AREAS: dict[int, str]          # 1..8
    OPERATIVE_TIERS: tuple[str, ...]
    is_prohibition(code) / is_high_risk_area(n)
    prohibition_screen(declared: Iterable[str]) -> dict
    area_coverage(assessed: Iterable[int]) -> dict

    >>> ART5_PROHIBITIONS["c"]
    'Social scoring causing detrimental treatment'
"""
from __future__ import annotations

from collections.abc import Iterable

STRUCTURE = {"chapters": 13, "articles": 113, "annexes": 13}

# Article 5(1)(a)-(h), Regulation (EU) 2024/1689 (short labels).
ART5_PROHIBITIONS = {
    "a": "Subliminal or manipulative deceptive techniques",
    "b": "Exploiting vulnerabilities (age, disability, social situation)",
    "c": "Social scoring causing detrimental treatment",
    "d": "Profiling-based criminal offence risk prediction",
    "e": "Untargeted facial image scraping",
    "f": "Emotion inference in workplace and education",
    "g": "Biometric categorisation of sensitive attributes",
    "h": "Real-time remote biometric identification (law enforcement)",
}

# Annex III high-risk areas 1-8 (short labels).
ANNEX3_AREAS = {
    1: "Biometrics",
    2: "Critical infrastructure",
    3: "Education and vocational training",
    4: "Employment, workers' management and self-employment",
    5: "Essential private and public services and benefits",
    6: "Law enforcement",
    7: "Migration, asylum and border control management",
    8: "Administration of justice and democratic processes",
}

# The Regulation's operative tier vocabulary (chapter/article anchored).
OPERATIVE_TIERS = (
    "prohibited AI practices (Art. 5)",
    "high-risk AI systems (Art. 6 / Annex III)",
    "transparency obligations (Art. 50)",
    "general-purpose AI models (Chapter V)",
    "general-purpose AI models with systemic risk (Art. 51)",
)


class AIActError(ValueError):
    """Unknown prohibition code or Annex III area (fail closed)."""


def is_prohibition(code: str) -> bool:
    """True iff *code* is one of the Article 5(1) letters (a)-(h)."""
    return code in ART5_PROHIBITIONS


def is_high_risk_area(n: int) -> bool:
    """True iff *n* is an Annex III area number (1-8)."""
    return not isinstance(n, bool) and isinstance(n, int) \
        and n in ANNEX3_AREAS


def prohibition_screen(declared: Iterable[str]) -> dict:
    """Screen a declared practice inventory against Article 5(1).

    ``declared`` holds prohibition codes an assessment flagged as present.
    Returns the flagged practices and a pass/fail verdict (any hit fails).
    Unknown codes fail closed.
    """
    flagged = set(declared)
    unknown = sorted(flagged - set(ART5_PROHIBITIONS))
    if unknown:
        raise AIActError(f"unknown Article 5(1) code(s): {unknown}")
    hits = sorted(flagged)
    return {
        "prohibitions_total": len(ART5_PROHIBITIONS),
        "flagged": hits,
        "flagged_count": len(hits),
        "compliant": len(hits) == 0,
    }


def area_coverage(assessed: Iterable[int]) -> dict:
    """Coverage of the 8 Annex III areas by a high-risk assessment."""
    done = set(assessed)
    unknown = sorted(a for a in done if not is_high_risk_area(a))
    if unknown:
        raise AIActError(f"unknown Annex III area(s): {unknown}")
    gaps = sorted(set(ANNEX3_AREAS) - done)
    return {
        "areas_total": len(ANNEX3_AREAS),
        "assessed": len(done),
        "coverage_pct": round(100.0 * len(done) / len(ANNEX3_AREAS), 2),
        "gaps": gaps,
    }
