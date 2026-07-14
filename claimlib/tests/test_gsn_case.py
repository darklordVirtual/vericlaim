# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the gsn_case module (GSN Community Standard structure)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "gsn_case"
_spec = importlib.util.spec_from_file_location(
    "claimlib_gsn_case", _MOD_DIR / "gsn_case.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_gsn_case"] = _m
_spec.loader.exec_module(_m)

GSNError = _m.GSNError
Case = _m.Case
validate = _m.validate
is_valid = _m.is_valid


def _base() -> Case:
    return Case(
        {"G1": "goal", "St1": "strategy", "G2": "goal", "Sn1": "solution",
         "C1": "context"},
        [("G1", "St1"), ("St1", "G2"), ("G2", "Sn1")],
        [("G1", "C1")],
        set())


def test_wellformed_case_valid():
    assert is_valid(_base())


def test_every_legal_supported_by_pair():
    assert is_valid(Case({"G1": "goal", "G2": "goal", "Sn": "solution"},
                         [("G1", "G2"), ("G2", "Sn")], [], set()))
    assert is_valid(Case({"G1": "goal", "St": "strategy", "G2": "goal",
                          "Sn": "solution"},
                         [("G1", "St"), ("St", "G2"), ("G2", "Sn")],
                         [], set()))


def test_illegal_edges_caught():
    assert not is_valid(Case({"G1": "goal", "C1": "context"},
                             [("G1", "C1")], [], set()))
    assert not is_valid(Case({"St": "strategy", "Sn": "solution",
                              "G": "goal"},
                             [("G", "St"), ("St", "Sn")], [], set()))


def test_circular_argument_caught():
    case = Case({"G1": "goal", "G2": "goal", "G3": "goal"},
                [("G1", "G2"), ("G2", "G3"), ("G3", "G2")], [], set())
    assert any("circular" in p for p in validate(case))


def test_goal_must_be_supported_or_undeveloped():
    dangling = Case({"G1": "goal", "G2": "goal"}, [("G1", "G2")], [], set())
    assert any("neither supported nor" in p for p in validate(dangling))
    honest = Case({"G1": "goal", "G2": "goal"}, [("G1", "G2")], [], {"G2"})
    assert is_valid(honest)


def test_undeveloped_with_support_is_contradiction():
    case = Case({"G1": "goal", "Sn": "solution"}, [("G1", "Sn")], [], {"G1"})
    assert any("pick one" in p for p in validate(case))


def test_single_root_rule():
    two_roots = Case({"G1": "goal", "G2": "goal", "Sn1": "solution",
                      "Sn2": "solution"},
                     [("G1", "Sn1"), ("G2", "Sn2")], [], set())
    assert any("multiple root goals" in p for p in validate(two_roots))


def test_solution_must_be_terminal():
    case = Case({"G1": "goal", "Sn": "solution", "C": "context"},
                [("G1", "Sn")], [("Sn", "C")], set())
    assert any("terminal" in p for p in validate(case))


@pytest.mark.parametrize("call", [
    lambda: Case({}, [], [], set()),
    lambda: Case({"G1": "claim"}, [], [], set()),
    lambda: Case({"": "goal"}, [], [], set()),
    lambda: Case({"G1": "goal"}, [("G1", "X", "Y")], [], set()),
    lambda: Case({"G1": "goal"}, "edges", [], set()),
])
def test_malformed_cases_rejected(call):
    with pytest.raises(GSNError):
        call()
