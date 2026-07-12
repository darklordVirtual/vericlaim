# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``double_entry`` library."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "double_entry"))

from double_entry import (  # noqa: E402
    is_balanced, validate, account_balances, trial_balance, LedgerError)

BALANCED = [{"account": "cash", "debit": 10000, "credit": 0},
            {"account": "sales", "debit": 0, "credit": 10000}]
SPLIT = [{"account": "inventory", "debit": 5000, "credit": 0},
         {"account": "vat", "debit": 1250, "credit": 0},
         {"account": "payable", "debit": 0, "credit": 6250}]


def test_balanced_and_unbalanced():
    assert is_balanced(BALANCED) is True
    assert is_balanced(SPLIT) is True
    assert is_balanced([{"account": "x", "debit": 100, "credit": 0}]) is False


def test_net_balances_sum_to_zero():
    assert sum(account_balances(BALANCED).values()) == 0
    assert account_balances(SPLIT) == {"inventory": 5000, "vat": 1250, "payable": -6250}


def test_trial_balance():
    tb = trial_balance(SPLIT)
    assert tb["total_debits"] == 6250
    assert tb["total_credits"] == 6250
    assert tb["balanced"] is True


def test_validate_raises_on_unbalanced():
    with pytest.raises(LedgerError):
        validate([{"account": "x", "debit": 100, "credit": 50}])
    validate(BALANCED)   # does not raise


def test_rejects_bad_postings():
    with pytest.raises(LedgerError):
        is_balanced([{"account": "x", "debit": -1, "credit": 0}])
    with pytest.raises(LedgerError):
        is_balanced([{"debit": 100, "credit": 0}])   # missing account
