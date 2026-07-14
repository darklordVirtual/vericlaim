# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the tool_guard module (default-deny tool policy)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "tool_guard"
_spec = importlib.util.spec_from_file_location(
    "claimlib_tool_guard", _MOD_DIR / "tool_guard.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_tool_guard"] = _m
_spec.loader.exec_module(_m)

PolicyError = _m.PolicyError
Policy = _m.Policy
Rule = _m.Rule


def _policy() -> "Policy":
    return Policy([
        Rule("read_file", {"path": {"prefix": "docs/"}}),
        Rule("pay", {"to": {"enum": ["a", "b"]}, "nok": {"max": 100}}),
    ])


def test_default_deny_unknown_tool():
    d = _policy().evaluate("delete_everything", {})
    assert not d.allowed and "default deny" in d.reason


def test_empty_policy_denies_all():
    assert not Policy([]).evaluate("anything", {}).allowed


def test_allowed_call_passes_with_reason():
    d = _policy().evaluate("read_file", {"path": "docs/x.md"})
    assert d.allowed and "read_file" in d.reason


def test_unknown_argument_fails_closed():
    d = _policy().evaluate("read_file", {"path": "docs/x.md", "mode": "w"})
    assert not d.allowed and "not covered" in d.reason


def test_missing_argument_denied():
    assert not _policy().evaluate("pay", {"to": "a"}).allowed


def test_prefix_constraint():
    assert not _policy().evaluate("read_file", {"path": "/etc/passwd"}).allowed
    assert not _policy().evaluate("read_file", {"path": 42}).allowed


def test_enum_and_max_constraints():
    p = _policy()
    assert p.evaluate("pay", {"to": "a", "nok": 100}).allowed
    assert not p.evaluate("pay", {"to": "c", "nok": 50}).allowed
    assert not p.evaluate("pay", {"to": "a", "nok": 101}).allowed
    assert not p.evaluate("pay", {"to": "a", "nok": "100.5"}).allowed


def test_exact_is_type_strict():
    p = Policy([Rule("t", {"a": {"exact": 1}})])
    assert p.evaluate("t", {"a": 1}).allowed
    assert not p.evaluate("t", {"a": True}).allowed
    assert not p.evaluate("t", {"a": "1"}).allowed


def test_multiple_rules_same_tool_any_may_allow():
    p = Policy([Rule("get", {"k": {"exact": "a"}}),
                Rule("get", {"k": {"exact": "b"}})])
    assert p.evaluate("get", {"k": "a"}).allowed
    assert p.evaluate("get", {"k": "b"}).allowed
    assert not p.evaluate("get", {"k": "c"}).allowed


def test_malformed_calls_denied_not_crashed():
    p = _policy()
    assert not p.evaluate(42, {}).allowed
    assert not p.evaluate("read_file", "args").allowed


@pytest.mark.parametrize("call", [
    lambda: Rule("", {}),
    lambda: Rule("t", {"": {"exact": 1}}),
    lambda: Rule("t", {"a": {"glob": "*"}}),
    lambda: Rule("t", {"a": {"exact": 1, "max": 5}}),
    lambda: Rule("t", {"a": {"enum": []}}),
    lambda: Rule("t", {"a": {"prefix": 5}}),
    lambda: Rule("t", {"a": {"max": "NaNsense"}}),
    lambda: Policy("rules"),
    lambda: Policy([{"tool": "t"}]),
])
def test_malformed_policy_rejected(call):
    with pytest.raises(PolicyError):
        call()
