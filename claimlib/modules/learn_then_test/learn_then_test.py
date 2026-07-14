# SPDX-License-Identifier: Apache-2.0
"""Learn then Test (LTT) — hyperparameter selection with family-wise error
control — reusable, claim-bound.

A pre-verified claimlib code artifact for AI assurance. Where conformal
risk control handles ONE monotone loss, Learn then Test (Angelopoulos,
Bates, Candès, Jordan, Lei 2021) controls risk for ANY loss and ANY
hyperparameter grid by turning calibration into multiple testing:

    for each lambda_j:  H_j : R(lambda_j) > alpha     (the null: too risky)
    compute a super-uniform p-value p_j from n calibration losses
    return every lambda whose H_j a FWER-controlling procedure rejects
    guarantee:  P( R(lambda) <= alpha for ALL returned lambda ) >= 1 - delta

For binary losses this module uses the EXACT binomial tail p-value
p_j = P(Bin(n, alpha) <= k_j), k_j the number of calibration failures at
lambda_j, computed in exact rational arithmetic — no normal approximation.
Two published FWER procedures are implemented: Bonferroni (reject when
p_j <= delta/K) and fixed-sequence testing (a caller-declared order,
walked until the first non-rejection at level delta).

The guarantee is frequentist over calibration draws — a returned lambda is
not certified individually, and validity needs i.i.d. calibration data and
a loss faithfully 0/1. The caveat travels with the claim.

Public API
----------
    binom_tail_p(n, k, alpha) -> Fraction     # P(Bin(n, alpha) <= k), exact
    ltt_bonferroni(failures: dict, n, alpha, delta) -> set
    ltt_fixed_sequence(failures: dict, order: list, n, alpha, delta) -> set

    failures maps lambda -> number of calibration failures (0..n).

    >>> binom_tail_p(10, 0, "0.5") == Fraction(1, 1024)
    True
"""
from __future__ import annotations

from fractions import Fraction
from math import comb


class LTTError(ValueError):
    """Invalid counts / levels (fail closed)."""


def _frac01(value, what: str, *, open_ends: bool = True) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, float, str,
                                                         Fraction)):
        raise LTTError(f"{what} must be a number, got {value!r}")
    if isinstance(value, float) and (value != value or value in (
            float("inf"), float("-inf"))):
        raise LTTError(f"{what} must be finite")
    try:
        f = Fraction(str(value)) if isinstance(value, (float, str)) \
            else Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise LTTError(f"bad {what}: {value!r}") from exc
    if open_ends and not 0 < f < 1:
        raise LTTError(f"{what} must be in (0, 1), got {value!r}")
    return f


def _check_n(n) -> int:
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise LTTError(f"n must be an int >= 1, got {n!r}")
    return n


def binom_tail_p(n: int, k: int, alpha) -> Fraction:
    """P(Bin(n, alpha) <= k), exactly — the LTT p-value for H: R > alpha
    with k observed failures among n binary calibration losses. Small
    observed risk gives a small p-value (strong evidence the true risk is
    <= alpha)."""
    n = _check_n(n)
    if isinstance(k, bool) or not isinstance(k, int) or not 0 <= k <= n:
        raise LTTError(f"k must be an int in [0, n], got {k!r}")
    a = _frac01(alpha, "alpha")
    return sum(Fraction(comb(n, i)) * a ** i * (1 - a) ** (n - i)
               for i in range(k + 1))


def _check_failures(failures, n: int) -> dict:
    if not isinstance(failures, dict) or not failures:
        raise LTTError("failures must be a non-empty dict of "
                       "lambda -> failure count")
    out = {}
    for lam, k in failures.items():
        if isinstance(k, bool) or not isinstance(k, int) or not 0 <= k <= n:
            raise LTTError(f"lambda {lam!r}: failure count must be an int "
                           f"in [0, {n}], got {k!r}")
        out[lam] = k
    return out


def ltt_bonferroni(failures, n: int, alpha, delta) -> set:
    """Every lambda whose exact binomial p-value is <= delta / K
    (Bonferroni over the K grid points). Possibly empty — the honest
    'nothing is certifiably safe at this level' answer."""
    n = _check_n(n)
    fails = _check_failures(failures, n)
    a = _frac01(alpha, "alpha")
    d = _frac01(delta, "delta")
    threshold = d / len(fails)
    return {lam for lam, k in fails.items()
            if binom_tail_p(n, k, a) <= threshold}


def ltt_fixed_sequence(failures, order, n: int, alpha, delta) -> set:
    """Fixed-sequence testing: walk *order* (declared BEFORE seeing the
    data), rejecting while p <= delta; stop at the first non-rejection.
    Spends the full delta on every test, so it is more powerful than
    Bonferroni along a well-chosen path."""
    n = _check_n(n)
    fails = _check_failures(failures, n)
    if not isinstance(order, (list, tuple)) or not order:
        raise LTTError("order must be a non-empty list of lambdas")
    if len(set(order)) != len(order):
        raise LTTError("order must not repeat lambdas")
    unknown = [lam for lam in order if lam not in fails]
    if unknown:
        raise LTTError(f"order contains lambdas without failure counts: "
                       f"{unknown}")
    a = _frac01(alpha, "alpha")
    d = _frac01(delta, "delta")
    rejected: set = set()
    for lam in order:
        if binom_tail_p(n, fails[lam], a) <= d:
            rejected.add(lam)
        else:
            break
    return rejected
