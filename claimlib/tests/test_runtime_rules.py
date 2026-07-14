# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the runtime_rules module (AgentSpec-style enforcement)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "runtime_rules"
_spec = importlib.util.spec_from_file_location(
    "claimlib_runtime_rules", _MOD_DIR / "runtime_rules.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_runtime_rules"] = _m
_spec.loader.exec_module(_m)

RuleError = _m.RuleError
Rule = _m.Rule
ENFORCEMENTS = _m.ENFORCEMENTS
evaluate = _m.evaluate
run_trace = _m.run_trace


def _rules():
    return [
        Rule("stop-secrets", "tool_call",
             {"path": {"contains": "secret"}}, "stop"),
        Rule("inspect-pay", "tool_call",
             {"tool": {"eq": "pay"}, "nok": {"gt": 1000}},
             "user_inspection"),
    ]


def test_agentspec_enforcement_kinds():
    assert ENFORCEMENTS == ("user_inspection", "llm_self_examine",
                            "invoke_action", "stop")
    with pytest.raises(RuleError):
        Rule("r", "t", {}, "skip")


def test_first_match_wins_in_declaration_order():
    ev = {"kind": "tool_call", "tool": "pay", "nok": 5000,
          "path": "/x/secret"}
    assert evaluate(_rules(), ev).rule_id == "stop-secrets"
    assert evaluate(list(reversed(_rules())), ev).rule_id == "inspect-pay"


def test_no_match_is_explicit_proceed():
    v = evaluate(_rules(), {"kind": "tool_call", "tool": "ls"})
    assert v.enforce == "proceed" and v.rule_id is None


def test_missing_attribute_fails_predicate_closed():
    assert evaluate(_rules(), {"kind": "tool_call", "tool": "pay"}
                    ).enforce == "proceed"


def test_numeric_boundaries_decimal_exact():
    rs = _rules()
    assert evaluate(rs, {"kind": "tool_call", "tool": "pay", "nok": 1000}
                    ).enforce == "proceed"
    assert evaluate(rs, {"kind": "tool_call", "tool": "pay",
                         "nok": "1000.01"}).enforce == "user_inspection"


def test_eq_type_strict_and_bool_not_number():
    r = [Rule("r", "e", {"n": {"eq": 1}}, "stop")]
    assert evaluate(r, {"kind": "e", "n": True}).enforce == "proceed"
    g = [Rule("g", "e", {"n": {"gt": 0}}, "stop")]
    assert evaluate(g, {"kind": "e", "n": True}).enforce == "proceed"


def test_malformed_event_fails_closed_to_stop():
    assert evaluate(_rules(), {"tool": "x"}).enforce == "stop"
    assert evaluate(_rules(), 42).enforce == "stop"


def test_trace_halts_at_stop():
    trace = [{"kind": "tool_call", "tool": "ls"},
             {"kind": "tool_call", "path": "secret"},
             {"kind": "tool_call", "tool": "never-reached"}]
    verdicts = run_trace(_rules(), trace)
    assert len(verdicts) == 2 and verdicts[-1].enforce == "stop"


@pytest.mark.parametrize("call", [
    lambda: Rule("", "t", {}, "stop"),
    lambda: Rule("r", "", {}, "stop"),
    lambda: Rule("r", "t", {}, "deny"),
    lambda: Rule("r", "t", {"a": {"glob": "*"}}, "stop"),
    lambda: Rule("r", "t", {"a": {"eq": 1, "gt": 0}}, "stop"),
    lambda: Rule("r", "t", {"a": {"gt": "x"}}, "stop"),
    lambda: Rule("r", "t", {"a": {"contains": 9}}, "stop"),
    lambda: evaluate([Rule("r", "t", {}, "stop")] * 2, {"kind": "t"}),
    lambda: run_trace("rules", []),
    lambda: run_trace([Rule("r", "t", {}, "stop"), "x"], []),
])
def test_malformed_rules_rejected(call):
    with pytest.raises(RuleError):
        call()
