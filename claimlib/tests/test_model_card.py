# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the model_card module (Mitchell et al. 2019)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "model_card"
_spec = importlib.util.spec_from_file_location(
    "claimlib_model_card", _MOD_DIR / "model_card.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_model_card"] = _m
_spec.loader.exec_module(_m)

ModelCardError = _m.ModelCardError
SECTIONS = _m.SECTIONS
completeness = _m.completeness


def test_nine_published_sections_in_order():
    assert len(SECTIONS) == 9
    assert SECTIONS[0] == "Model Details"
    assert SECTIONS[-1] == "Caveats and Recommendations"
    assert "Ethical Considerations" in SECTIONS


def test_complete_card_scores_100():
    got = completeness({s: "text" for s in SECTIONS})
    assert got["complete"] and got["completeness_pct"] == 100.0


def test_empty_card_scores_0():
    got = completeness({})
    assert got["present"] == 0 and not got["complete"]
    assert got["missing"] == list(SECTIONS)


def test_whitespace_section_counts_as_empty():
    got = completeness({"Factors": " \n\t "})
    assert got["present"] == 0
    assert got["empty_sections"] == ["Factors"]


def test_partial_card_exact_percentage():
    got = completeness({"Model Details": "a", "Intended Use": "b",
                        "Metrics": "c"})
    assert got["present"] == 3
    assert got["completeness_pct"] == 33.33


def test_present_sections_keep_paper_order():
    got = completeness({"Metrics": "y", "Model Details": "x"})
    assert got["present_sections"] == ["Model Details", "Metrics"]


@pytest.mark.parametrize("call", [
    lambda: completeness({"model details": "case typo"}),
    lambda: completeness({"Limitations": "not a section"}),
    lambda: completeness({"Metrics": None}),
    lambda: completeness({"Metrics": 3.14}),
    lambda: completeness(["Model Details"]),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(ModelCardError):
        call()
