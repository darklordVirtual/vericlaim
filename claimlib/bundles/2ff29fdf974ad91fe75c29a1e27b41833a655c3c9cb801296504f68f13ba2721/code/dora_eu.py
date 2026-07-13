# SPDX-License-Identifier: Apache-2.0
"""DORA (Regulation (EU) 2022/2554) structure + resilience-pillar coverage —
reusable, claim-bound.

A pre-verified claimlib code artifact for AI governance and enterprise
architecture in financial environments. The Digital Operational Resilience
Act harmonizes ICT risk requirements across the EU financial sector; any
AI system a financial entity runs lives inside its perimeter. This module
encodes the published structure of the final OJ text — 9 chapters
partitioning 64 articles — and the five operative resilience pillars with
their chapter/article anchors:

    ICT risk management                      Chapter II   (Arts. 5-16)
    ICT incident management & reporting     Chapter III  (Arts. 17-23)
    Digital operational resilience testing  Chapter IV   (Arts. 24-27)
    ICT third-party risk management         Chapter V    (Arts. 28-44)
    Information-sharing arrangements        Chapter VI   (Art. 45)

Pillar coverage scoring reports what a programme declares implemented.
Encoding the regulation is not legal advice, and DORA's Level 2 technical
standards (RTS/ITS) add binding detail this module does not carry. The
caveat travels with the claim.

Public API
----------
    CHAPTERS: dict[int, tuple[str, int, int]]  # ch -> (title, first, last)
    PILLARS: dict[str, dict]                   # key -> name, chapter, arts
    N_ARTICLES: int                            # 64
    chapter_of(article: int) -> int
    pillar_of(article: int) -> str | None      # None: outside the pillars
    pillar_coverage(implemented: Iterable[str]) -> dict

    >>> chapter_of(28)
    5
    >>> pillar_of(45)
    'info_sharing'
"""
from __future__ import annotations

from collections.abc import Iterable
from fractions import Fraction

# Chapter -> (title, first article, last article); Regulation (EU) 2022/2554.
CHAPTERS = {
    1: ("General provisions", 1, 4),
    2: ("ICT risk management", 5, 16),
    3: ("ICT-related incident management, classification and reporting",
        17, 23),
    4: ("Digital operational resilience testing", 24, 27),
    5: ("Managing of ICT third-party risk", 28, 44),
    6: ("Information-sharing arrangements", 45, 45),
    7: ("Competent authorities", 46, 56),
    8: ("Delegated acts", 57, 57),
    9: ("Transitional and final provisions", 58, 64),
}

N_ARTICLES = 64

PILLARS = {
    "ict_risk": {"name": "ICT risk management", "chapter": 2},
    "incidents": {"name": "ICT-related incident management, classification "
                          "and reporting", "chapter": 3},
    "testing": {"name": "Digital operational resilience testing",
                "chapter": 4},
    "third_party": {"name": "Managing of ICT third-party risk", "chapter": 5},
    "info_sharing": {"name": "Information-sharing arrangements",
                     "chapter": 6},
}


class DORAError(ValueError):
    """Unknown article or pillar (fail closed)."""


def chapter_of(article: int) -> int:
    """The chapter containing *article* (1..64)."""
    if isinstance(article, bool) or not isinstance(article, int):
        raise DORAError(f"article must be an int, got {article!r}")
    if not 1 <= article <= N_ARTICLES:
        raise DORAError(f"article must be in 1..{N_ARTICLES}, got {article}")
    for chapter, (_, first, last) in CHAPTERS.items():
        if first <= article <= last:
            return chapter
    raise DORAError(f"article {article} not covered "
                    f"(taxonomy corrupt)")  # pragma: no cover


def pillar_of(article: int):
    """The resilience pillar containing *article*, or None outside them."""
    ch = chapter_of(article)
    for key, meta in PILLARS.items():
        if meta["chapter"] == ch:
            return key
    return None


def pillar_coverage(implemented: Iterable[str]) -> dict:
    """Coverage of the five resilience pillars by a declared programme."""
    have = set(implemented)
    unknown = sorted(have - set(PILLARS))
    if unknown:
        raise DORAError(f"unknown pillar key(s): {unknown}")
    gaps = sorted(set(PILLARS) - have)
    return {
        "pillars_total": len(PILLARS),
        "implemented": len(have),
        "coverage_pct": round(
            float(Fraction(len(have), len(PILLARS)) * 100), 2),
        "gaps": gaps,
    }
