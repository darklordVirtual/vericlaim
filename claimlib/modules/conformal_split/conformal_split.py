# SPDX-License-Identifier: Apache-2.0
"""Split conformal prediction — finite-sample prediction sets with a coverage
guarantee — reusable, claim-bound.

A pre-verified claimlib code artifact for AI assurance. Split conformal
prediction wraps ANY scoring model in a prediction set with a distribution-
free, finite-sample guarantee: given n calibration nonconformity scores and
a miscoverage level alpha, take

    qhat = the ceil((n+1)(1-alpha))-th smallest calibration score

and include every candidate whose score is <= qhat. If calibration and test
points are exchangeable, the set contains the true label with probability at
least 1 - alpha (and, for distinct scores, at most 1 - alpha + 1/(n+1)) —
Angelopoulos & Bates (2021).

The guarantee is MARGINAL (on average over calibration draws, not per input)
and rests on exchangeability: distribution shift between calibration and
deployment voids it. The caveat travels with the claim.

Public API
----------
    quantile_index(n, alpha) -> int | None   # 1-based k; None: qhat = +inf
    conformal_quantile(scores, alpha) -> score | None
    prediction_set(cal_scores, alpha, candidates: dict) -> set
    loo_coverage(pool, alpha) -> Fraction    # exhaustive leave-one-out
                                             # coverage over an exchangeable
                                             # pool (the theorem, enumerated)

    >>> quantile_index(100, 0.1)     # the classic n=100, alpha=0.1 case
    91
"""
from __future__ import annotations

from fractions import Fraction


class ConformalError(ValueError):
    """Invalid alpha / scores (fail closed)."""


def _check_alpha(alpha) -> Fraction:
    if isinstance(alpha, bool) or not isinstance(alpha, (int, float, str,
                                                         Fraction)):
        raise ConformalError(f"alpha must be a number in (0, 1), got {alpha!r}")
    try:
        a = Fraction(str(alpha)) if isinstance(alpha, (float, str)) \
            else Fraction(alpha)
    except (ValueError, ZeroDivisionError) as exc:
        raise ConformalError(f"alpha must be a number, got {alpha!r}") from exc
    if not 0 < a < 1:
        raise ConformalError(f"alpha must be in (0, 1), got {alpha!r}")
    return a


def _check_scores(scores) -> list:
    if not isinstance(scores, (list, tuple)) or not scores:
        raise ConformalError("scores must be a non-empty sequence")
    out = []
    for i, s in enumerate(scores):
        if isinstance(s, bool) or not isinstance(s, (int, float, Fraction)):
            raise ConformalError(f"scores[{i}] must be a number, got {s!r}")
        if isinstance(s, float) and (s != s or s in (float("inf"),
                                                     float("-inf"))):
            raise ConformalError(f"scores[{i}] must be finite, got {s!r}")
        out.append(s)
    return out


def quantile_index(n: int, alpha) -> int | None:
    """The 1-based rank k = ceil((n+1)(1-alpha)) into the sorted calibration
    scores, or None when k > n (too few calibration points for this alpha:
    qhat is +infinity and the prediction set is everything)."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ConformalError(f"n must be an int >= 1, got {n!r}")
    a = _check_alpha(alpha)
    k = -((-(n + 1) * (1 - a)) // 1)          # ceil, exact rational
    k = int(k)
    return k if k <= n else None


def conformal_quantile(scores, alpha):
    """qhat: the quantile_index-th smallest score, or None (= +infinity)."""
    xs = sorted(_check_scores(scores))
    k = quantile_index(len(xs), alpha)
    return None if k is None else xs[k - 1]


def prediction_set(cal_scores, alpha, candidates: dict) -> set:
    """Labels whose nonconformity score is <= qhat.

    ``candidates`` maps label -> score for the test input. A None quantile
    (n too small for alpha) honestly returns ALL labels — the guarantee
    holds vacuously and the set says so by being uninformative.
    """
    if not isinstance(candidates, dict) or not candidates:
        raise ConformalError("candidates must be a non-empty dict of "
                             "label -> score")
    _check_scores(list(candidates.values()))
    qhat = conformal_quantile(cal_scores, alpha)
    if qhat is None:
        return set(candidates)
    return {label for label, s in candidates.items() if s <= qhat}


def loo_coverage(pool, alpha) -> Fraction:
    """Exhaustive leave-one-out coverage over an exchangeable *pool*.

    Under exchangeability every element of the pool is equally likely to be
    the test point; enumerating each choice (calibrate on the rest, check
    whether the held-out score falls inside) computes the EXACT marginal
    coverage as a Fraction — the coverage theorem, enumerated rather than
    sampled. For a pool of distinct scores this lies in
    [1 - alpha, 1 - alpha + 1/n_pool].
    """
    xs = _check_scores(pool)
    if len(xs) < 2:
        raise ConformalError("pool needs at least 2 scores")
    covered = 0
    for i in range(len(xs)):
        held = xs[i]
        rest = xs[:i] + xs[i + 1:]
        qhat = conformal_quantile(rest, alpha)
        if qhat is None or held <= qhat:
            covered += 1
    return Fraction(covered, len(xs))
