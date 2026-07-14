# SPDX-License-Identifier: Apache-2.0
"""Group-fairness metrics for classifier audits — demographic parity,
disparate impact (the four-fifths rule) and equalized odds — reusable,
claim-bound.

A pre-verified claimlib code artifact for AI governance. Given per-group
confusion counts (integers, straight from an evaluation run), this module
computes the standard group-fairness measurements EXACTLY (fractions.Fraction
— no float drift in an audit number):

    selection_rate       P(Yhat=1 | group)            per group
    demographic_parity_difference   max |rate_a - rate_b| over group pairs
    disparate_impact_ratio          min rate / max rate  (EEOC four-fifths
                                    rule: ratio >= 4/5 passes)
    tpr / fpr             true/false-positive rates    per group
    equalized_odds_difference       max over {TPR, FPR} of the largest
                                    pairwise group gap (Hardt et al. 2016)

The numbers are measurements, not verdicts: which metric matters, at what
threshold, on which population is a governance decision — and the metrics
can conflict with each other and with calibration. The caveat travels with
the claim.

Public API
----------
    GroupCounts(tp, fp, fn, tn)                       # non-negative ints
    selection_rate(counts) -> Fraction
    tpr(counts) -> Fraction        # requires tp + fn > 0
    fpr(counts) -> Fraction        # requires fp + tn > 0
    demographic_parity_difference(groups: dict) -> Fraction
    disparate_impact_ratio(groups: dict) -> Fraction
    four_fifths_ok(groups: dict) -> bool
    equalized_odds_difference(groups: dict) -> Fraction

    >>> g = {"a": GroupCounts(40, 10, 10, 40), "b": GroupCounts(20, 5, 30, 45)}
    >>> float(demographic_parity_difference(g))
    0.25
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


class FairnessError(ValueError):
    """Invalid confusion counts or group structure (fail closed)."""


@dataclass(frozen=True)
class GroupCounts:
    """Confusion counts for one protected group: predictions vs outcomes."""
    tp: int
    fp: int
    fn: int
    tn: int

    def __post_init__(self) -> None:
        for name in ("tp", "fp", "fn", "tn"):
            v = getattr(self, name)
            if isinstance(v, bool) or not isinstance(v, int):
                raise FairnessError(f"{name} must be an int, got {v!r}")
            if v < 0:
                raise FairnessError(f"{name} must be >= 0, got {v}")
        if self.tp + self.fp + self.fn + self.tn == 0:
            raise FairnessError("group has no observations")

    @property
    def n(self) -> int:
        return self.tp + self.fp + self.fn + self.tn


def _check_groups(groups: dict, minimum: int = 2) -> dict:
    if not isinstance(groups, dict) or len(groups) < minimum:
        raise FairnessError(f"need a dict of >= {minimum} groups")
    for key, g in groups.items():
        if not isinstance(g, GroupCounts):
            raise FairnessError(f"group {key!r} is not a GroupCounts")
    return groups


def selection_rate(counts: GroupCounts) -> Fraction:
    """P(Yhat = 1) for the group: (tp + fp) / n. Exact."""
    return Fraction(counts.tp + counts.fp, counts.n)


def tpr(counts: GroupCounts) -> Fraction:
    """True-positive rate tp / (tp + fn); the group must have positives."""
    if counts.tp + counts.fn == 0:
        raise FairnessError("TPR undefined: group has no actual positives")
    return Fraction(counts.tp, counts.tp + counts.fn)


def fpr(counts: GroupCounts) -> Fraction:
    """False-positive rate fp / (fp + tn); the group must have negatives."""
    if counts.fp + counts.tn == 0:
        raise FairnessError("FPR undefined: group has no actual negatives")
    return Fraction(counts.fp, counts.fp + counts.tn)


def demographic_parity_difference(groups: dict) -> Fraction:
    """Largest pairwise gap in selection rates across groups (0 = parity)."""
    rates = [selection_rate(g) for g in _check_groups(groups).values()]
    return max(rates) - min(rates)


def disparate_impact_ratio(groups: dict) -> Fraction:
    """min selection rate / max selection rate (1 = parity).

    The EEOC four-fifths rule flags adverse impact when the ratio falls
    below 4/5. The max rate must be > 0 (a model that selects nobody has
    no disparate-impact ratio to speak of — fail closed).
    """
    rates = [selection_rate(g) for g in _check_groups(groups).values()]
    top = max(rates)
    if top == 0:
        raise FairnessError("disparate impact undefined: no group is "
                            "selected at a positive rate")
    return min(rates) / top


def four_fifths_ok(groups: dict) -> bool:
    """True iff the disparate-impact ratio meets the four-fifths rule."""
    return disparate_impact_ratio(groups) >= Fraction(4, 5)


def equalized_odds_difference(groups: dict) -> Fraction:
    """Hardt et al. (2016) equalized odds, as its largest violation.

    A predictor satisfies equalized odds when TPR and FPR are equal across
    groups; this returns max(spread of TPRs, spread of FPRs), which is 0
    exactly when equalized odds holds on the sample.
    """
    gs = list(_check_groups(groups).values())
    tprs = [tpr(g) for g in gs]
    fprs = [fpr(g) for g in gs]
    return max(max(tprs) - min(tprs), max(fprs) - min(fprs))
