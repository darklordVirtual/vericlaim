# SPDX-License-Identifier: Apache-2.0
"""Model-card completeness scoring per Mitchell et al. (2019) — reusable,
claim-bound.

A pre-verified claimlib code artifact for AI governance. Model cards are
the de facto disclosure document for trained models; Mitchell et al.'s
FAT* 2019 paper proposes NINE sections a card should carry:

    Model Details · Intended Use · Factors · Metrics · Evaluation Data ·
    Training Data · Quantitative Analyses · Ethical Considerations ·
    Caveats and Recommendations

This module encodes that section taxonomy and scores a card's structural
completeness: which of the nine sections are present and non-empty, which
are missing, and an exact completeness percentage. Structure is what a
machine CAN check — a present section can still be vacuous prose, so a
100% score means "all sections present", never "adequately disclosed".
The caveat travels with the claim.

Public API
----------
    SECTIONS: tuple[str, ...]          # the nine, in the paper's order
    completeness(card: dict) -> dict   # section -> text (str)

    >>> len(SECTIONS)
    9
    >>> completeness({"Model Details": "ResNet-50 v1.5"})["present"]
    1
"""
from __future__ import annotations

from fractions import Fraction

SECTIONS = (
    "Model Details",
    "Intended Use",
    "Factors",
    "Metrics",
    "Evaluation Data",
    "Training Data",
    "Quantitative Analyses",
    "Ethical Considerations",
    "Caveats and Recommendations",
)


class ModelCardError(ValueError):
    """Unknown section or malformed card (fail closed)."""


def completeness(card: dict) -> dict:
    """Structural completeness of *card* against the nine sections.

    ``card`` maps section names (exactly as in SECTIONS) to their text.
    A section counts as present only when its value is a non-empty,
    non-whitespace string. Unknown section names fail closed (a typo in
    'Ethical Considerations' must not silently score as a gap).
    """
    if not isinstance(card, dict):
        raise ModelCardError("card must be a dict of section -> text")
    unknown = sorted(set(card) - set(SECTIONS))
    if unknown:
        raise ModelCardError(f"unknown section(s): {unknown}")
    present = []
    empty = []
    for name in SECTIONS:
        if name not in card:
            continue
        text = card[name]
        if not isinstance(text, str):
            raise ModelCardError(f"section {name!r} must be a str, "
                                 f"got {type(text).__name__}")
        if text.strip():
            present.append(name)
        else:
            empty.append(name)
    missing = [s for s in SECTIONS if s not in present]
    return {
        "sections_total": len(SECTIONS),
        "present": len(present),
        "present_sections": present,
        "empty_sections": empty,
        "missing": missing,
        "completeness_pct": round(
            float(Fraction(len(present), len(SECTIONS)) * 100), 2),
        "complete": len(present) == len(SECTIONS),
    }
