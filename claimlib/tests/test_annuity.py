# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the annuity module (integer minor-unit loan math)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "annuity"
_spec = importlib.util.spec_from_file_location(
    "claimlib_annuity", _MOD_DIR / "annuity.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_annuity"] = _m
_spec.loader.exec_module(_m)

AnnuityError = _m.AnnuityError
payment = _m.payment
schedule = _m.schedule
total_interest = _m.total_interest


def test_textbook_payment():
    # $100,000 at 0.5%/month over 360 months -> $599.55.
    assert payment(10_000_000, 0.005, 360) == 59_955


def test_schedule_balances_to_exactly_zero():
    for p, r, n in [(10_000_000, 0.005, 360), (777_777, 0.013, 48),
                    (100, 0.5, 3)]:
        rows = schedule(p, r, n)
        assert rows[-1]["balance_mu"] == 0
        assert sum(row["principal_mu"] for row in rows) == p


def test_interest_recomputable_from_balances():
    p, r, n = 500_000, 0.01, 24
    rows = schedule(p, r, n)
    balance = p
    for row in rows:
        assert row["interest_mu"] == round(balance * r)
        balance -= row["principal_mu"]


def test_zero_rate_even_split():
    rows = schedule(1_590_00, 0.0, 12)
    assert total_interest(1_590_00, 0.0, 12) == 0
    assert sum(row["principal_mu"] for row in rows) == 1_590_00
    assert rows[-1]["balance_mu"] == 0
    payments = {row["payment_mu"] for row in rows}
    assert len(payments) <= 2  # even split, remainder on the last payment


def test_declining_interest_increasing_principal():
    rows = schedule(1_000_000, 0.02, 36)
    interests = [row["interest_mu"] for row in rows]
    principals = [row["principal_mu"] for row in rows[:-1]]
    assert all(a >= b for a, b in zip(interests, interests[1:]))
    assert all(a <= b for a, b in zip(principals, principals[1:]))


def test_single_period_loan():
    rows = schedule(1000, 0.1, 1)
    assert len(rows) == 1
    assert rows[0]["principal_mu"] == 1000
    assert rows[0]["interest_mu"] == 100
    assert rows[0]["balance_mu"] == 0


@pytest.mark.parametrize("call", [
    lambda: payment(0, 0.01, 12),
    lambda: payment(-1, 0.01, 12),
    lambda: payment(100.5, 0.01, 12),
    lambda: payment(1000, -0.01, 12),
    lambda: payment(1000, float("inf"), 12),
    lambda: payment(1000, 0.01, 0),
    lambda: payment(1000, 0.01, 10_001),
    lambda: schedule(True, 0.01, 12),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(AnnuityError):
        call()
