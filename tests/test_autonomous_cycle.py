# SPDX-License-Identifier: Apache-2.0
"""End-to-end test: autonomous development is admitted; autonomous drift is
blocked (including a real gate run catching register corruption).

This exercises the whole loop — scaffold, real gate, snapshot capture, and the
non-weakening envelope — not just synthetic snapshots."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from autonomous_cycle_demo import run_demo  # noqa: E402


def test_autonomous_cycle_is_bounded(tmp_path):
    result = run_demo(tmp_path)
    # Every safety property must hold — no drift vector may slip through.
    assert result["ALL_SAFE"], result
    assert result["baseline_gate_green"]
    assert result["development_admitted"]
    assert result["drift_demote_blocked"]
    assert result["drift_remove_blocked"]
    assert result["drift_shrink_tests_blocked"]
    assert result["drift_core_edit_blocked"]
    assert result["gate_catches_corruption"]
    assert result["envelope_refuses_red_gate"]
