# SPDX-License-Identifier: Apache-2.0
"""Annuity loan mathematics in integer minor units (øre/cents) — reusable,
claim-bound.

A pre-verified claimlib code artifact. An annuity loan repays a principal P
over n periods at periodic rate i with a constant payment

    PMT = P * i / (1 - (1 + i)**-n)        (PMT = P / n when i == 0)

Each period pays interest on the outstanding balance first; the remainder
amortizes principal. This module computes the payment and the full
amortization schedule ENTIRELY in integer minor units (banker's rounding on
the interest accrual), with the final payment adjusted by at most a few
minor units so the balance ends at EXACTLY zero — the invariant an
accountant actually checks. That the schedule satisfies the exact
identities (final balance 0, principal parts summing precisely to the
principal, interest recomputable from each balance) and reproduces the
standard published textbook example is registered as a claim and proven by
a committed evidence artifact.

Not modelled: fees, varying rates, day-count conventions, grace periods —
the caveat travels with the claim.

Public API
----------
    payment(principal_mu: int, rate_per_period: float, periods: int) -> int
    schedule(principal_mu: int, rate_per_period: float, periods: int)
        -> list[dict]     # period, payment_mu, interest_mu, principal_mu,
                          # balance_mu
    total_interest(principal_mu: int, rate_per_period: float,
                   periods: int) -> int

    >>> payment(10_000_000, 0.005, 360)   # $100,000 at 0.5%/month, 30 years
    59955
"""
from __future__ import annotations


class AnnuityError(ValueError):
    """Invalid loan parameters (fail closed)."""


_MAX_PERIODS = 10_000


def _check(principal_mu: int, rate: float, periods: int) -> tuple:
    if isinstance(principal_mu, bool) or not isinstance(principal_mu, int):
        raise AnnuityError(f"principal must be an int of minor units, "
                           f"got {principal_mu!r}")
    if principal_mu <= 0:
        raise AnnuityError(f"principal must be > 0, got {principal_mu}")
    if isinstance(rate, bool) or not isinstance(rate, (int, float)):
        raise AnnuityError(f"rate must be a number, got {rate!r}")
    r = float(rate)
    if r != r or r in (float("inf"), float("-inf")) or r < 0:
        raise AnnuityError(f"rate must be finite and >= 0, got {rate!r}")
    if isinstance(periods, bool) or not isinstance(periods, int):
        raise AnnuityError(f"periods must be an int, got {periods!r}")
    if not 1 <= periods <= _MAX_PERIODS:
        raise AnnuityError(f"periods must be in [1, {_MAX_PERIODS}], "
                           f"got {periods}")
    return principal_mu, r, periods


def _round_half_even(x: float) -> int:
    """Banker's rounding to an integer of minor units (Python round)."""
    return round(x)


def payment(principal_mu: int, rate_per_period: float, periods: int) -> int:
    """The constant per-period payment, in minor units (banker's rounding)."""
    p, r, n = _check(principal_mu, rate_per_period, periods)
    if r == 0.0:
        # Even split; any remainder lands on the final payment via schedule().
        return -(-p // n)  # ceil division keeps the final payment <= regular
    factor = r / (1.0 - (1.0 + r) ** -n)
    return _round_half_even(p * factor)


def schedule(principal_mu: int, rate_per_period: float,
             periods: int) -> list:
    """Full amortization schedule in minor units; balance ends at exactly 0.

    Every row: interest = banker's-rounded balance*rate; principal part =
    payment - interest; the FINAL row's payment absorbs cumulative rounding
    (and never leaves a negative balance).
    """
    p, r, n = _check(principal_mu, rate_per_period, periods)
    pmt = payment(p, r, n)
    rows = []
    balance = p
    for period in range(1, n + 1):
        interest = _round_half_even(balance * r)
        if period < n:
            principal_part = min(pmt - interest, balance)
            if principal_part < 0:
                raise AnnuityError(
                    "payment does not cover interest: rate too high for "
                    "this schedule")
            pay = interest + principal_part
        else:
            principal_part = balance          # final payment clears exactly
            pay = interest + principal_part
        balance -= principal_part
        rows.append({"period": period, "payment_mu": pay,
                     "interest_mu": interest,
                     "principal_mu": principal_part,
                     "balance_mu": balance})
    return rows


def total_interest(principal_mu: int, rate_per_period: float,
                   periods: int) -> int:
    """Sum of the interest column of the schedule, in minor units."""
    return sum(row["interest_mu"]
               for row in schedule(principal_mu, rate_per_period, periods))
