# SPDX-License-Identifier: Apache-2.0
"""Expected Calibration Error (ECE) and reliability binning for model
confidence audits — reusable, claim-bound.

A pre-verified claimlib code artifact for AI governance. A classifier is
CALIBRATED when its confidence means what it says: among predictions made
with confidence ~0.8, about 80% should be correct. The standard audit
measurement (Naeini et al. 2015; Guo et al. 2017) partitions predictions
into M equal-width confidence bins and compares each bin's accuracy to its
average confidence:

    ECE = sum_b (n_b / N) * |acc(b) - conf(b)|
    MCE = max_b            |acc(b) - conf(b)|

This module computes the bins, ECE and MCE in EXACT arithmetic
(fractions.Fraction) from (confidence, correct) pairs, binning [0, 1] into
M equal-width bins with the conventional right-closed edges: bin i holds
confidences in (i/M, (i+1)/M], with 0.0 assigned to the first bin.

ECE is an audit statistic, not a guarantee: it depends on the bin count,
ignores per-class effects, and a low ECE does not imply correct individual
probabilities. The caveat travels with the claim.

Public API
----------
    bins(pairs, n_bins) -> list[dict]      # n, acc, conf per bin (Fractions)
    ece(pairs, n_bins=10) -> Fraction
    mce(pairs, n_bins=10) -> Fraction

    pairs are (confidence, correct) with confidence a number in [0, 1]
    (int/float/Fraction/str accepted — parsed exactly via Fraction) and
    correct a bool.

    >>> float(ece([("0.8", True), ("0.8", False)], n_bins=10))
    0.3
"""
from __future__ import annotations

from fractions import Fraction


class CalibrationError(ValueError):
    """Invalid confidence/correctness input (fail closed)."""


def _to_fraction(value, index: int) -> Fraction:
    if isinstance(value, bool):
        raise CalibrationError(f"pair {index}: confidence must be a number, "
                               f"got bool")
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise CalibrationError(f"pair {index}: confidence must be finite")
        f = Fraction(value).limit_denominator(10 ** 12)
    elif isinstance(value, (int, Fraction, str)):
        try:
            f = Fraction(value)
        except (ValueError, ZeroDivisionError) as exc:
            raise CalibrationError(f"pair {index}: bad confidence "
                                   f"{value!r}") from exc
    else:
        raise CalibrationError(f"pair {index}: confidence must be a number, "
                               f"got {type(value).__name__}")
    if not 0 <= f <= 1:
        raise CalibrationError(f"pair {index}: confidence must be in [0, 1], "
                               f"got {value!r}")
    return f


def _parse(pairs, n_bins: int) -> tuple:
    if isinstance(n_bins, bool) or not isinstance(n_bins, int) or n_bins < 1:
        raise CalibrationError(f"n_bins must be a positive int, "
                               f"got {n_bins!r}")
    if not isinstance(pairs, (list, tuple)) or not pairs:
        raise CalibrationError("pairs must be a non-empty sequence of "
                               "(confidence, correct)")
    parsed = []
    for i, pair in enumerate(pairs):
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise CalibrationError(f"pair {i}: expected (confidence, correct)")
        conf, correct = pair
        if not isinstance(correct, bool):
            raise CalibrationError(f"pair {i}: correct must be a bool, "
                                   f"got {correct!r}")
        parsed.append((_to_fraction(conf, i), correct))
    return parsed, n_bins


def bins(pairs, n_bins: int = 10) -> list:
    """Reliability bins: for each equal-width bin, n, accuracy, confidence.

    Bin i (0-based) holds confidences in (i/M, (i+1)/M]; confidence 0 goes
    to bin 0. acc and conf are exact Fractions (None when the bin is empty).
    """
    parsed, m = _parse(pairs, n_bins)
    counts = [0] * m
    correct_sum = [0] * m
    conf_sum = [Fraction(0)] * m
    for conf, correct in parsed:
        if conf == 0:
            b = 0
        else:
            # right-closed bins: the smallest b with conf <= (b+1)/m
            b = int(-(-(conf * m) // 1)) - 1   # ceil(conf*m) - 1, exact
        counts[b] += 1
        correct_sum[b] += 1 if correct else 0
        conf_sum[b] += conf
    out = []
    for b in range(m):
        n = counts[b]
        out.append({
            "bin": b,
            "lo": Fraction(b, m),
            "hi": Fraction(b + 1, m),
            "n": n,
            "acc": Fraction(correct_sum[b], n) if n else None,
            "conf": conf_sum[b] / n if n else None,
        })
    return out


def ece(pairs, n_bins: int = 10) -> Fraction:
    """Expected Calibration Error over equal-width bins. Exact."""
    total = sum(1 for _ in pairs)
    acc = Fraction(0)
    for b in bins(pairs, n_bins):
        if b["n"]:
            acc += Fraction(b["n"], total) * abs(b["acc"] - b["conf"])
    return acc


def mce(pairs, n_bins: int = 10) -> Fraction:
    """Maximum Calibration Error: the worst bin's |acc - conf|. Exact."""
    gaps = [abs(b["acc"] - b["conf"]) for b in bins(pairs, n_bins) if b["n"]]
    return max(gaps)
