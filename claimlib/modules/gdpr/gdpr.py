# SPDX-License-Identifier: Apache-2.0
"""GDPR (Regulation (EU) 2016/679) structure, principles and Article 32
security measures — reusable, claim-bound.

A pre-verified claimlib code artifact for privacy compliance. Encodes the
General Data Protection Regulation's published structure — 11 chapters
partitioning its 99 articles — the Article 5(1) processing principles
(a)-(f) plus the Article 5(2) accountability principle, and the Article
32(1) security-of-processing measures (a)-(d), with coverage scoring
against each set. That the encoded taxonomy matches the Regulation (the
chapter ranges partition articles 1..99 exactly) and that the coverage
arithmetic is correct is registered as a claim and proven by a committed
evidence artifact.

Encoding the law's structure is not legal advice: implementing all
measures does not make processing lawful — the caveat travels with the
claim.

Public API
----------
    CHAPTERS: dict[int, tuple[str, int, int]]   # chapter -> (title, first, last)
    PRINCIPLES: dict[str, str]                  # Art. 5(1)(a)-(f) + "accountability"
    ART32_MEASURES: dict[str, str]              # Art. 32(1)(a)-(d)
    chapter_of(article: int) -> int
    principle_coverage(implemented) -> dict
    art32_coverage(implemented) -> dict

    >>> chapter_of(17)      # right to erasure lives in Chapter III
    3
    >>> principle_coverage(["a", "b"])["implemented"]
    2
"""
from __future__ import annotations

from collections.abc import Iterable

# Chapter -> (title, first article, last article); Regulation (EU) 2016/679.
CHAPTERS = {
    1: ("General provisions", 1, 4),
    2: ("Principles", 5, 11),
    3: ("Rights of the data subject", 12, 23),
    4: ("Controller and processor", 24, 43),
    5: ("Transfers of personal data to third countries or international "
        "organisations", 44, 50),
    6: ("Independent supervisory authorities", 51, 59),
    7: ("Cooperation and consistency", 60, 76),
    8: ("Remedies, liability and penalties", 77, 84),
    9: ("Provisions relating to specific processing situations", 85, 91),
    10: ("Delegated acts and implementing acts", 92, 93),
    11: ("Final provisions", 94, 99),
}

N_ARTICLES = 99

# Article 5(1)(a)-(f) plus the 5(2) accountability principle.
PRINCIPLES = {
    "a": "Lawfulness, fairness and transparency",
    "b": "Purpose limitation",
    "c": "Data minimisation",
    "d": "Accuracy",
    "e": "Storage limitation",
    "f": "Integrity and confidentiality",
    "accountability": "Accountability (Art. 5(2))",
}

# Article 32(1)(a)-(d): security of processing.
ART32_MEASURES = {
    "a": "Pseudonymisation and encryption of personal data",
    "b": "Ability to ensure ongoing confidentiality, integrity, availability "
         "and resilience of processing systems and services",
    "c": "Ability to restore availability and access to personal data in a "
         "timely manner in the event of a physical or technical incident",
    "d": "Process for regularly testing, assessing and evaluating the "
         "effectiveness of technical and organisational measures",
}


class GDPRError(ValueError):
    """Unknown article, principle or measure code (fail closed)."""


def chapter_of(article: int) -> int:
    """The chapter containing *article* (1..99)."""
    if isinstance(article, bool) or not isinstance(article, int):
        raise GDPRError(f"article must be an int, got {article!r}")
    if not 1 <= article <= N_ARTICLES:
        raise GDPRError(f"article must be in 1..{N_ARTICLES}, got {article}")
    for chapter, (_, first, last) in CHAPTERS.items():
        if first <= article <= last:
            return chapter
    raise GDPRError(f"article {article} not covered by any chapter "
                    f"(taxonomy corrupt)")  # pragma: no cover


def _coverage(implemented: Iterable[str], universe: dict,
              what: str) -> dict:
    impl = set(implemented)
    unknown = sorted(impl - set(universe))
    if unknown:
        raise GDPRError(f"unknown {what} code(s): {unknown}")
    gaps = sorted(set(universe) - impl)
    return {
        "total": len(universe),
        "implemented": len(impl),
        "coverage_pct": round(100.0 * len(impl) / len(universe), 2),
        "gaps": gaps,
    }


def principle_coverage(implemented: Iterable[str]) -> dict:
    """Coverage of the 7 Article 5 principles (a-f + accountability)."""
    return _coverage(implemented, PRINCIPLES, "principle")


def art32_coverage(implemented: Iterable[str]) -> dict:
    """Coverage of the 4 Article 32(1) security measures (a-d)."""
    return _coverage(implemented, ART32_MEASURES, "Article 32 measure")
