# SPDX-License-Identifier: Apache-2.0
"""Conformal Risk Control (CRC) — distribution-free control of any monotone
risk, not just miscoverage — reusable, claim-bound.

A pre-verified claimlib code artifact for AI assurance. Split conformal
prediction bounds ONE loss (miscoverage). Conformal Risk Control
(Angelopoulos, Bates, Fisch, Lei, Schuster 2022) generalizes it: for any
loss L(lambda) that is NON-INCREASING in a threshold parameter lambda and
bounded above by B, pick

    lambdahat = the smallest lambda in the grid with
                (n/(n+1)) * Rhat_n(lambda) + B/(n+1) <= alpha

where Rhat_n is the mean of the n calibration losses at lambda. Under
exchangeability the deployed risk satisfies E[L_{n+1}(lambdahat)] <= alpha.
With the miscoverage indicator as the loss, CRC reduces exactly to split
conformal prediction.

The guarantee is IN EXPECTATION and marginal — not per input, not a
high-probability bound — and rests on exchangeability plus the caller's
monotonicity: this module VERIFIES non-increasing losses on the supplied
grid and fails closed otherwise, but cannot check monotonicity off-grid.
The caveat travels with the claim.

Public API
----------
    lambda_hat(cal_losses, alpha, B) -> lambda | None
        cal_losses: dict lambda -> [n losses], same grid per unit;
        None: no grid point satisfies the inequality (alpha too small).
    controlled_risk_bound(n, alpha, B) -> Fraction
        the exact finite-sample requirement the rule enforces at lambdahat.
    loo_risk(pool_losses, alpha, B) -> Fraction
        exhaustive leave-one-out mean risk over an exchangeable pool of
        loss curves — the CRC theorem, enumerated.

    >>> grid = {0: [1, 1, 1], 1: [0, 1, 0], 2: [0, 0, 0]}
    >>> lambda_hat(grid, "0.5", 1)
    1
"""
from __future__ import annotations

from fractions import Fraction


class CRCError(ValueError):
    """Invalid losses / alpha / bound, or non-monotone loss (fail closed)."""


def _frac(value, what: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, float, str,
                                                         Fraction)):
        raise CRCError(f"{what} must be a number, got {value!r}")
    if isinstance(value, float) and (value != value or value in (
            float("inf"), float("-inf"))):
        raise CRCError(f"{what} must be finite")
    try:
        return Fraction(str(value)) if isinstance(value, (float, str)) \
            else Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise CRCError(f"bad {what}: {value!r}") from exc


def _check_grid(losses, B: Fraction) -> dict:
    """Validate a lambda -> losses grid: consistent n, losses in [0, B],
    mean loss non-increasing in lambda (the CRC monotonicity, checked on
    the grid)."""
    if not isinstance(losses, dict) or len(losses) < 1:
        raise CRCError("losses must be a non-empty dict of "
                       "lambda -> list of losses")
    grid = {}
    n = None
    for lam in sorted(losses, key=lambda v: _frac(v, "lambda")):
        row = losses[lam]
        if not isinstance(row, (list, tuple)) or not row:
            raise CRCError(f"lambda {lam!r}: losses must be a non-empty list")
        if n is None:
            n = len(row)
        elif len(row) != n:
            raise CRCError(f"lambda {lam!r}: expected {n} losses, "
                           f"got {len(row)}")
        vals = []
        for i, v in enumerate(row):
            f = _frac(v, f"loss[{i}] at lambda {lam!r}")
            if not 0 <= f <= B:
                raise CRCError(f"lambda {lam!r}: loss {v!r} outside [0, B]")
            vals.append(f)
        grid[_frac(lam, "lambda")] = vals
    means = [sum(v) / len(v) for _, v in sorted(grid.items())]
    for a, b in zip(means, means[1:]):
        if b > a:
            raise CRCError(
                "mean loss increases along the lambda grid — CRC requires a "
                "non-increasing loss in lambda (fail closed)")
    return grid


def controlled_risk_bound(n: int, alpha, B) -> Fraction:
    """The exact bound Rhat_n must satisfy at lambdahat:
    Rhat_n <= ((n+1) * alpha - B) / n."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise CRCError(f"n must be an int >= 1, got {n!r}")
    a = _frac(alpha, "alpha")
    b = _frac(B, "B")
    if b <= 0:
        raise CRCError(f"B must be > 0, got {B!r}")
    if not 0 < a < b + 1:
        raise CRCError(f"alpha must be in (0, B+1), got {alpha!r}")
    return ((n + 1) * a - b) / n


def lambda_hat(cal_losses, alpha, B):
    """The CRC threshold: smallest grid lambda with
    (n/(n+1)) * Rhat_n(lambda) + B/(n+1) <= alpha, or None if none
    qualifies (the honest 'cannot control at this alpha' answer)."""
    b = _frac(B, "B")
    if b <= 0:
        raise CRCError(f"B must be > 0, got {B!r}")
    a = _frac(alpha, "alpha")
    grid = _check_grid(cal_losses, b)
    n = len(next(iter(grid.values())))
    for lam in sorted(grid):
        rhat = sum(grid[lam]) / n
        if Fraction(n, n + 1) * rhat + b / (n + 1) <= a:
            return lam
    return None


def loo_risk(pool_losses, alpha, B) -> Fraction:
    """Exhaustive leave-one-out risk over an exchangeable pool.

    ``pool_losses`` maps lambda -> [m losses] for a pool of m exchangeable
    units. Every unit in turn is the test point: calibrate lambdahat on the
    other m-1, incur the held-out unit's loss at that lambdahat (loss B —
    the worst case — when no lambda qualifies). The mean over all m choices
    is the EXACT marginal risk of the CRC procedure on this pool; the CRC
    theorem promises it is <= alpha.
    """
    b = _frac(B, "B")
    grid = _check_grid(pool_losses, b)
    m = len(next(iter(grid.values())))
    if m < 2:
        raise CRCError("pool needs at least 2 units")
    total = Fraction(0)
    for i in range(m):
        rest = {lam: row[:i] + row[i + 1:] for lam, row in grid.items()}
        lam = lambda_hat(rest, alpha, b)
        total += b if lam is None else grid[lam][i]
    return total / m
