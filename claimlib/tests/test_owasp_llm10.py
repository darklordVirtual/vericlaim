# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the owasp_llm10 module."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "owasp_llm10"
_spec = importlib.util.spec_from_file_location(
    "claimlib_owasp_llm10", _MOD_DIR / "owasp_llm10.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_owasp_llm10"] = _m
_spec.loader.exec_module(_m)

OWASPError = _m.OWASPError
RISKS = _m.RISKS
is_risk = _m.is_risk
coverage = _m.coverage


def test_published_2025_list():
    assert len(RISKS) == 10
    assert RISKS["LLM01"] == "Prompt Injection"
    assert RISKS["LLM07"] == "System Prompt Leakage"
    assert RISKS["LLM08"] == "Vector and Embedding Weaknesses"
    assert RISKS["LLM10"] == "Unbounded Consumption"


def test_membership_case_sensitive():
    assert is_risk("LLM05")
    assert not is_risk("llm05") and not is_risk("LLM11")


def test_coverage_math():
    full = coverage(list(RISKS))
    assert full["coverage_pct"] == 100.0 and full["gaps"] == []
    part = coverage(["LLM01"])
    assert part["mitigated"] == 1 and part["coverage_pct"] == 10.0


def test_duplicates_count_once():
    assert coverage(["LLM01", "LLM01"])["mitigated"] == 1


@pytest.mark.parametrize("bad", [["LLM00"], ["LLM11"], ["llm01"], ["A03"]])
def test_unknown_codes_rejected(bad):
    with pytest.raises(OWASPError):
        coverage(bad)
