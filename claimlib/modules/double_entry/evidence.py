# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-DOUBLE-ENTRY-001 -- the balance check correctly
classifies journals and the accounting invariants hold.

The core property is self-verifying and needs no external oracle: for a balanced
journal, total debits equal total credits AND every account's net balances sum to
zero. The evidence runs a fixed battery of journals whose balanced/unbalanced
status is independently known by construction, checks is_balanced against it,
verifies the net-balances-sum-to-zero invariant on the balanced ones, and checks
a hand-computed trial balance. Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (double_entry.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from double_entry import (  # noqa: E402
    is_balanced, account_balances, trial_balance)
from _util import emit  # noqa: E402

# (journal, expected_balanced). Amounts in minor units.
JOURNALS = [
    ([{"account": "cash", "debit": 10000, "credit": 0},
      {"account": "sales", "debit": 0, "credit": 10000}], True),
    ([{"account": "cash", "debit": 10000, "credit": 0},
      {"account": "sales", "debit": 0, "credit": 9999}], False),
    ([{"account": "inventory", "debit": 5000, "credit": 0},
      {"account": "vat", "debit": 1250, "credit": 0},
      {"account": "payable", "debit": 0, "credit": 6250}], True),        # split entry
    ([{"account": "a", "debit": 0, "credit": 0}], True),                  # empty amounts
    ([{"account": "x", "debit": 100, "credit": 0}], False),              # one-sided
]


def run() -> dict:
    classify_correct = 0
    invariant_ok = 0
    for journal, expected in JOURNALS:
        if is_balanced(journal) == expected:
            classify_correct += 1
        # For balanced journals, the net balances must sum to zero.
        if expected:
            invariant_ok += int(sum(account_balances(journal).values()) == 0)

    # Hand-computed trial balance for the split entry.
    tb = trial_balance(JOURNALS[2][0])
    tb_checks = [
        tb["total_debits"] == 6250,
        tb["total_credits"] == 6250,
        tb["balanced"] is True,
        tb["accounts"]["vat"] == {"debit": 1250, "credit": 0},
        account_balances(JOURNALS[2][0]) == {"inventory": 5000, "vat": 1250, "payable": -6250},
    ]
    tb_correct = sum(int(c) for c in tb_checks)

    n_balanced = sum(1 for _, e in JOURNALS if e)
    checks = len(JOURNALS) + n_balanced + len(tb_checks)
    matched = classify_correct + invariant_ok + tb_correct
    return {
        "schema": "claimlib_double_entry_v1",
        "module": "double_entry",
        "n_journals": len(JOURNALS),
        "checks": checks,
        "checks_matched": matched,
        "mismatches": checks - matched,
        "classify_correct": classify_correct,
        "invariant_ok": invariant_ok,
        "trial_balance_correct": tb_correct,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "double_entry.json", obj,
         script="python3 claimlib/modules/double_entry/evidence.py")
    # claim:CLAIM-LIB-DOUBLE-ENTRY-001 checks_matched
    # All 5 classifications, 3 net-balance invariants and 5 trial-balance checks
    # hold, so checks_matched = 13 and mismatches = 0.
    print(f"double_entry: {obj['checks_matched']}/{obj['checks']} checks "
          f"(classify {obj['classify_correct']}/{obj['n_journals']}, "
          f"invariant {obj['invariant_ok']}, trial_balance {obj['trial_balance_correct']}/5); "
          f"mismatches {obj['mismatches']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
