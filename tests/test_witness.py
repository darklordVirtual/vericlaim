# SPDX-License-Identifier: Apache-2.0
"""Tests for external ledger anchoring (witness records + client-side verify).

The threat model: whoever controls the Worker's D1 database can rebuild the
whole hash chain and it would still self-verify. The witness closes that gap:
chain heads are recorded in git (public history), and verification re-walks
the FULL export client-side — recomputing every hash — and requires today's
chain to *extend* every witnessed head at its witnessed length. A rebuilt,
truncated, or edited chain fails against any prior witness.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "cloudflare-ai"))

from witness import (  # noqa: E402
    CLAIM_FIELDS, LIBRARY_FIELDS, check_witnesses, entry_hash, rewalk,
)


def _chain(fields: tuple[str, ...], contents: list[dict]) -> list[dict]:
    rows, prev = [], ""
    for i, c in enumerate(contents, 1):
        row = {f: c.get(f, f"{f}-{i}") for f in fields}
        eh = entry_hash(prev, row)
        rows.append({**row, "seq": i, "prev_hash": prev, "entry_hash": eh})
        prev = eh
    return rows


def test_rewalk_accepts_intact_chain_and_returns_heads():
    rows = _chain(CLAIM_FIELDS, [{"claim_id": "C-1"}, {"claim_id": "C-2"}])
    result = rewalk(rows, CLAIM_FIELDS)
    assert result["ok"] is True and result["entries"] == 2
    assert result["head"] == rows[-1]["entry_hash"]
    assert result["heads_at"][1] == rows[0]["entry_hash"]  # head after 1 entry


def test_rewalk_detects_edited_row():
    rows = _chain(LIBRARY_FIELDS, [{"bundle_id": "b1"}, {"bundle_id": "b2"}])
    rows[0]["status"] = "tampered"
    result = rewalk(rows, LIBRARY_FIELDS)
    assert result["ok"] is False and result["broken_at"] == 1


def test_witness_extension_holds_for_grown_chain():
    rows = _chain(CLAIM_FIELDS, [{"claim_id": "C-1"}, {"claim_id": "C-2"},
                                 {"claim_id": "C-3"}])
    walk = rewalk(rows, CLAIM_FIELDS)
    # witnessed when the chain had 2 entries
    witness = {"claims_entries": 2, "claims_head": rows[1]["entry_hash"],
               "library_entries": 0, "library_head": ""}
    lib_walk = rewalk([], LIBRARY_FIELDS)
    problems = check_witnesses([witness], walk, lib_walk)
    assert problems == []


def test_rebuilt_chain_fails_against_witness():
    old = _chain(CLAIM_FIELDS, [{"claim_id": "C-1"}, {"claim_id": "C-2"}])
    witness = {"claims_entries": 2, "claims_head": old[1]["entry_hash"],
               "library_entries": 0, "library_head": ""}
    # adversary rebuilds the chain with different content — self-consistent,
    # same length, but a different history
    rebuilt = _chain(CLAIM_FIELDS, [{"claim_id": "C-1", "statement": "edited"},
                                    {"claim_id": "C-2"}])
    walk = rewalk(rebuilt, CLAIM_FIELDS)
    assert walk["ok"] is True                      # self-verifies!
    problems = check_witnesses([witness], walk, rewalk([], LIBRARY_FIELDS))
    assert problems and "claims" in problems[0]    # ...but the witness catches it


def test_truncated_chain_fails_against_witness():
    rows = _chain(CLAIM_FIELDS, [{"claim_id": "C-1"}, {"claim_id": "C-2"}])
    witness = {"claims_entries": 2, "claims_head": rows[1]["entry_hash"],
               "library_entries": 0, "library_head": ""}
    walk = rewalk(rows[:1], CLAIM_FIELDS)          # history shrank
    problems = check_witnesses([witness], walk, rewalk([], LIBRARY_FIELDS))
    assert problems
