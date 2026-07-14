# SPDX-License-Identifier: Apache-2.0
"""Double-entry bookkeeping invariants -- the balance check auditors rely on.

A pre-verified claimlib code artifact for accounting & audit. In double-entry
bookkeeping every transaction records equal debits and credits, so across a
journal the total debits equal the total credits and every account's net
balances sum to zero. This module checks that invariant and builds a trial
balance, working in integer minor units (cents/oere) to avoid floating point.
That it correctly identifies balanced vs. unbalanced journals and that the trial
balance sums are exact is registered as a claim and proven by a committed
evidence artifact.

A posting is a mapping ``{"account": str, "debit": int, "credit": int}`` in minor
units (one side is normally zero).

Public API
----------
    total_debits(postings) -> int
    total_credits(postings) -> int
    is_balanced(postings) -> bool
    validate(postings) -> None                 # raises if unbalanced
    account_balances(postings) -> dict[str, int]   # net = debit - credit
    trial_balance(postings) -> dict

    >>> is_balanced([{"account": "cash", "debit": 100, "credit": 0},
    ...              {"account": "sales", "debit": 0, "credit": 100}])
    True
"""
from __future__ import annotations

from collections.abc import Sequence


class LedgerError(ValueError):
    """A malformed posting, or a journal that does not balance (in validate)."""


def _check(postings: Sequence[dict]) -> None:
    for p in postings:
        if not isinstance(p, dict) or "account" not in p:
            raise LedgerError("each posting needs an 'account'")
        debit, credit = p.get("debit", 0), p.get("credit", 0)
        for value in (debit, credit):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise LedgerError("debit/credit must be non-negative ints (minor units)")


def total_debits(postings: Sequence[dict]) -> int:
    """Return the sum of all debit amounts (minor units)."""
    _check(postings)
    return sum(p.get("debit", 0) for p in postings)


def total_credits(postings: Sequence[dict]) -> int:
    """Return the sum of all credit amounts (minor units)."""
    _check(postings)
    return sum(p.get("credit", 0) for p in postings)


def is_balanced(postings: Sequence[dict]) -> bool:
    """Return True iff total debits equal total credits."""
    return total_debits(postings) == total_credits(postings)


def validate(postings: Sequence[dict]) -> None:
    """Raise :class:`LedgerError` if the journal does not balance."""
    if not is_balanced(postings):
        raise LedgerError(
            f"journal unbalanced: debits {total_debits(postings)} != "
            f"credits {total_credits(postings)}")


def account_balances(postings: Sequence[dict]) -> dict[str, int]:
    """Return each account's net balance (debit - credit) in minor units."""
    _check(postings)
    balances: dict[str, int] = {}
    for p in postings:
        net = p.get("debit", 0) - p.get("credit", 0)
        balances[p["account"]] = balances.get(p["account"], 0) + net
    return balances


def trial_balance(postings: Sequence[dict]) -> dict:
    """Return per-account debit/credit totals plus the balance check."""
    per_account: dict[str, dict[str, int]] = {}
    for p in postings:
        _check([p])
        acct = per_account.setdefault(p["account"], {"debit": 0, "credit": 0})
        acct["debit"] += p.get("debit", 0)
        acct["credit"] += p.get("credit", 0)
    return {
        "accounts": per_account,
        "total_debits": total_debits(postings),
        "total_credits": total_credits(postings),
        "balanced": is_balanced(postings),
    }
