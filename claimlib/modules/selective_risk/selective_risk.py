# SPDX-License-Identifier: Apache-2.0
"""Selective classification — coverage, selective risk and the risk-coverage
curve — reusable, claim-bound.

A pre-verified claimlib code artifact for AI assurance. A selective
classifier may ABSTAIN: a gate accepts an input when its confidence clears a
threshold, and quality is judged only on what was accepted (Geifman &
El-Yaniv 2017):

    coverage(theta)       = fraction of inputs with confidence >= theta
    selective_risk(theta) = sum of accepted losses / number accepted

The risk-coverage curve sweeps theta over the observed confidences, tracing
the operating points an abstention policy can choose from. All arithmetic is
EXACT (fractions.Fraction) — an assurance number must not carry float drift.

The curve describes the evaluated sample only: thresholds chosen on it are
estimates, confidence may be miscalibrated, and risk at zero coverage is
undefined (this module fails closed rather than reporting 0). The caveat
travels with the claim.

Public API
----------
    coverage(pairs, threshold) -> Fraction
    selective_risk(pairs, threshold) -> Fraction    # >= 1 accepted required
    risk_coverage_curve(pairs) -> list[dict]        # theta desc, exact points

    pairs are (confidence, loss): confidence any finite number, loss a
    non-negative number (0/1 for classification error).

    >>> pairs = [(0.9, 0), (0.8, 0), (0.6, 1), (0.4, 0)]
    >>> float(coverage(pairs, 0.7))
    0.5
"""
from __future__ import annotations

from fractions import Fraction


class SelectiveError(ValueError):
    """Invalid pairs / threshold, or an empty selection (fail closed)."""


def _to_fraction(value, what: str, index: int, *, nonneg: bool = False):
    if isinstance(value, bool) or not isinstance(value, (int, float, str,
                                                         Fraction)):
        raise SelectiveError(f"pair {index}: {what} must be a number, "
                             f"got {value!r}")
    if isinstance(value, float) and (value != value or value in (
            float("inf"), float("-inf"))):
        raise SelectiveError(f"pair {index}: {what} must be finite")
    try:
        f = Fraction(str(value)) if isinstance(value, (float, str)) \
            else Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise SelectiveError(f"pair {index}: bad {what} {value!r}") from exc
    if nonneg and f < 0:
        raise SelectiveError(f"pair {index}: {what} must be >= 0, "
                             f"got {value!r}")
    return f


def _parse(pairs) -> list:
    if not isinstance(pairs, (list, tuple)) or not pairs:
        raise SelectiveError("pairs must be a non-empty sequence of "
                             "(confidence, loss)")
    out = []
    for i, pair in enumerate(pairs):
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise SelectiveError(f"pair {i}: expected (confidence, loss)")
        conf, loss = pair
        out.append((_to_fraction(conf, "confidence", i),
                    _to_fraction(loss, "loss", i, nonneg=True)))
    return out


def coverage(pairs, threshold) -> Fraction:
    """Fraction of inputs accepted at *threshold* (confidence >= theta)."""
    parsed = _parse(pairs)
    theta = _to_fraction(threshold, "threshold", -1)
    accepted = sum(1 for conf, _ in parsed if conf >= theta)
    return Fraction(accepted, len(parsed))


def selective_risk(pairs, threshold) -> Fraction:
    """Mean loss over the accepted inputs; fails closed on zero coverage
    (risk of an empty selection is undefined, not 0)."""
    parsed = _parse(pairs)
    theta = _to_fraction(threshold, "threshold", -1)
    accepted = [(c, loss) for c, loss in parsed if c >= theta]
    if not accepted:
        raise SelectiveError(
            f"no input accepted at threshold {threshold!r} — selective risk "
            f"is undefined at coverage 0")
    return sum(loss for _, loss in accepted) / Fraction(len(accepted))


def risk_coverage_curve(pairs) -> list:
    """Operating points at every distinct confidence, threshold descending.

    Each point: {threshold, coverage, risk, accepted} with exact Fractions.
    The last point always has coverage 1 (threshold = min confidence).
    """
    parsed = _parse(pairs)
    out = []
    for theta in sorted({c for c, _ in parsed}, reverse=True):
        accepted = [(c, loss) for c, loss in parsed if c >= theta]
        out.append({
            "threshold": theta,
            "coverage": Fraction(len(accepted), len(parsed)),
            "risk": sum(loss for _, loss in accepted)
            / Fraction(len(accepted)),
            "accepted": len(accepted),
        })
    return out
