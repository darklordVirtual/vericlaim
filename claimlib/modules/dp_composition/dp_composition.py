# SPDX-License-Identifier: Apache-2.0
"""Differential-privacy budget composition — sequential, parallel and group
privacy per Dwork & Roth — reusable, claim-bound.

A pre-verified claimlib code artifact for AI governance. An
(epsilon, delta)-differentially-private mechanism bounds how much any one
individual's data can change its output distribution. Enterprise pipelines
run MANY mechanisms, and the privacy budget composes by theorem, not by
vibes (Dwork & Roth 2014, "The Algorithmic Foundations of Differential
Privacy"):

    Sequential composition (Thm 3.16): running k mechanisms on the SAME
    data is (sum eps_i, sum delta_i)-DP.
    Parallel composition (McSherry): mechanisms on DISJOINT partitions
    compose to (max eps_i, max delta_i)-DP.
    Group privacy (Thm 2.2, pure DP): an eps-DP mechanism is (k*eps)-DP
    for groups of size k.

This module tracks a mechanism ledger and computes the composed budget in
EXACT arithmetic (fractions.Fraction). These are the BASIC bounds — they
are tight in the worst case but pessimistic for many mechanisms; advanced
composition, RDP and zCDP accountants give tighter epsilons and are out of
scope. The caveat travels with the claim.

Public API
----------
    Mechanism(name, epsilon, delta=0)
    sequential(mechanisms) -> (Fraction, Fraction)
    parallel(mechanisms) -> (Fraction, Fraction)
    group_privacy(epsilon, k) -> Fraction        # pure DP only
    Ledger(budget_epsilon, budget_delta=0)       # fail-closed accountant
        .spend(mechanism)                        # raises over budget
        .remaining() -> (Fraction, Fraction)

    >>> seq = sequential([Mechanism("a", "0.5"), Mechanism("b", "0.25")])
    >>> str(seq[0])
    '3/4'
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


class DPError(ValueError):
    """Invalid privacy parameter or over-budget spend (fail closed)."""


def _param(value, name: str, upper=None) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float) and (
            value != value or value in (float("inf"), float("-inf"))):
        raise DPError(f"{name} must be a finite number, got {value!r}")
    try:
        f = Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise DPError(f"{name} must be a number, got {value!r}") from exc
    if f < 0:
        raise DPError(f"{name} must be >= 0, got {value!r}")
    if upper is not None and f > upper:
        raise DPError(f"{name} must be <= {upper}, got {value!r}")
    return f


@dataclass(frozen=True)
class Mechanism:
    """One differentially-private release: a name and its (eps, delta)."""
    name: str
    epsilon: object
    delta: object = 0

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise DPError(f"name must be a non-empty str, got {self.name!r}")
        object.__setattr__(self, "epsilon", _param(self.epsilon, "epsilon"))
        object.__setattr__(self, "delta", _param(self.delta, "delta", 1))


def _mechs(mechanisms) -> list:
    if not isinstance(mechanisms, (list, tuple)) or not mechanisms:
        raise DPError("mechanisms must be a non-empty sequence")
    for m in mechanisms:
        if not isinstance(m, Mechanism):
            raise DPError(f"{m!r} is not a Mechanism")
    return list(mechanisms)


def sequential(mechanisms) -> tuple:
    """(sum eps, sum delta): the basic sequential-composition bound."""
    ms = _mechs(mechanisms)
    return (sum(m.epsilon for m in ms), sum(m.delta for m in ms))


def parallel(mechanisms) -> tuple:
    """(max eps, max delta): composition over DISJOINT data partitions.

    The disjointness is the CALLER's precondition — this function cannot
    check it and the bound is unsound without it.
    """
    ms = _mechs(mechanisms)
    return (max(m.epsilon for m in ms), max(m.delta for m in ms))


def group_privacy(epsilon, k: int) -> Fraction:
    """k * epsilon: pure-DP group privacy for groups of size k."""
    eps = _param(epsilon, "epsilon")
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise DPError(f"group size k must be an int >= 1, got {k!r}")
    return eps * k


class Ledger:
    """A fail-closed privacy-budget accountant under sequential composition.

    Every spend is checked BEFORE it is recorded: a mechanism that would
    push the composed (eps, delta) past the budget raises and is NOT added.
    """

    def __init__(self, budget_epsilon, budget_delta=0) -> None:
        self.budget_epsilon = _param(budget_epsilon, "budget_epsilon")
        self.budget_delta = _param(budget_delta, "budget_delta", 1)
        self.spent: list = []

    def _spent_totals(self) -> tuple:
        return (sum((m.epsilon for m in self.spent), Fraction(0)),
                sum((m.delta for m in self.spent), Fraction(0)))

    def spend(self, mechanism: Mechanism) -> None:
        if not isinstance(mechanism, Mechanism):
            raise DPError(f"{mechanism!r} is not a Mechanism")
        eps, delta = self._spent_totals()
        if eps + mechanism.epsilon > self.budget_epsilon or \
                delta + mechanism.delta > self.budget_delta:
            raise DPError(
                f"over budget: spending {mechanism.name!r} would compose to "
                f"({eps + mechanism.epsilon}, {delta + mechanism.delta}) "
                f"against budget ({self.budget_epsilon}, {self.budget_delta})")
        self.spent.append(mechanism)

    def remaining(self) -> tuple:
        eps, delta = self._spent_totals()
        return (self.budget_epsilon - eps, self.budget_delta - delta)
