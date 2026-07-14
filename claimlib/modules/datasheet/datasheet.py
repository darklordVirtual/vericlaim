# SPDX-License-Identifier: Apache-2.0
"""Datasheets for Datasets completeness scoring per Gebru et al. (2021) —
reusable, claim-bound.

A pre-verified claimlib code artifact for AI governance. Where a model card
documents a trained model, a DATASHEET documents the dataset it learned
from. Gebru et al. (CACM 2021; arXiv 1803.09010) organise the disclosure
around the dataset lifecycle in SEVEN sections:

    Motivation · Composition · Collection Process ·
    Preprocessing/cleaning/labeling · Uses · Distribution · Maintenance

This module encodes that taxonomy and scores structural completeness. It
adds the datasheet's own escape hatch, which a model card does not have:
the paper repeatedly notes that some questions "may not be applicable" — a
section can be legitimately answered "not applicable" PROVIDED a
justification is given. So a section is COVERED when it is either answered
with non-empty text OR explicitly declared not-applicable WITH a reason; an
empty answer or a bare "N/A" with no justification is a gap.

Structure is what a machine CAN check: a present section can still be
vacuous, and a claimed N/A can be dishonest. A 100% score means "every
lifecycle section is accounted for", never "the dataset is adequately
documented". The caveat travels with the claim.

Public API
----------
    SECTIONS: tuple[str, ...]            # the seven, in the paper's order
    completeness(sheet: dict) -> dict    # section -> text | {"na", "reason"}

    A section value is either a non-empty str (answered) or a mapping
    {"na": True, "reason": "<why it does not apply>"}.

    >>> len(SECTIONS)
    7
    >>> completeness({"Motivation": "Built to study X."})["answered"]
    1
"""
from __future__ import annotations

from fractions import Fraction

SECTIONS = (
    "Motivation",
    "Composition",
    "Collection Process",
    "Preprocessing/cleaning/labeling",
    "Uses",
    "Distribution",
    "Maintenance",
)


class DatasheetError(ValueError):
    """Unknown section or malformed sheet (fail closed)."""


def _classify(name: str, value) -> str:
    """One section's state: 'answered', 'na', or 'gap'. Fails closed on a
    malformed value rather than scoring it as a silent gap."""
    if isinstance(value, str):
        return "answered" if value.strip() else "gap"
    if isinstance(value, dict):
        if value.get("na") is not True:
            raise DatasheetError(
                f"section {name!r}: mapping value must declare na=True; "
                f"got {value!r}")
        reason = value.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            # An unjustified N/A is not coverage — it is a gap.
            return "gap"
        return "na"
    raise DatasheetError(
        f"section {name!r} must be a str or an {{'na', 'reason'}} mapping, "
        f"got {type(value).__name__}")


def completeness(sheet: dict) -> dict:
    """Structural completeness of *sheet* against the seven lifecycle
    sections. Unknown section names fail closed (a typo must not silently
    score as a gap). A section is COVERED when answered or justified-N/A."""
    if not isinstance(sheet, dict):
        raise DatasheetError("sheet must be a dict of section -> value")
    unknown = sorted(set(sheet) - set(SECTIONS))
    if unknown:
        raise DatasheetError(f"unknown section(s): {unknown}")

    answered, na, gaps = [], [], []
    for name in SECTIONS:
        if name not in sheet:
            gaps.append(name)
            continue
        state = _classify(name, sheet[name])
        (answered if state == "answered"
         else na if state == "na" else gaps).append(name)

    covered = answered + na
    return {
        "sections_total": len(SECTIONS),
        "answered": len(answered),
        "not_applicable": len(na),
        "covered": len(covered),
        "answered_sections": answered,
        "na_sections": na,
        "missing": gaps,
        "completeness_pct": round(
            float(Fraction(len(covered), len(SECTIONS)) * 100), 2),
        "complete": len(covered) == len(SECTIONS),
    }
