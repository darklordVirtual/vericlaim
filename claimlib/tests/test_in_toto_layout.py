# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the in_toto_layout module."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "in_toto_layout"
_spec = importlib.util.spec_from_file_location(
    "claimlib_in_toto_layout", _MOD_DIR / "in_toto_layout.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_in_toto_layout"] = _m
_spec.loader.exec_module(_m)

InTotoError = _m.InTotoError
apply_rules = _m.apply_rules
verify_step = _m.verify_step


def test_create_accepts_fresh_product():
    ok, _ = apply_rules([("CREATE", "out.o"), ("DISALLOW", "*")],
                        {}, {"out.o": "h"}, {})
    assert ok


def test_create_rejects_preexisting_material():
    ok, _ = apply_rules([("CREATE", "out.o"), ("DISALLOW", "*")],
                        {"out.o": "h"}, {"out.o": "h"}, {})
    assert not ok


def test_match_requires_same_hash_in_dest_step():
    links = {"build": {"products": {"app.bin": "h1"}}}
    good, _ = apply_rules([("MATCH", "app.bin", "build", "products"),
                           ("DISALLOW", "*")], {}, {"app.bin": "h1"}, links)
    bad, _ = apply_rules([("MATCH", "app.bin", "build", "products"),
                          ("DISALLOW", "*")], {}, {"app.bin": "h2"}, links)
    assert good and not bad


def test_modify_requires_changed_hash():
    changed, _ = apply_rules([("MODIFY", "s"), ("DISALLOW", "*")],
                             {"s": "a"}, {"s": "b"}, {})
    unchanged, _ = apply_rules([("MODIFY", "s"), ("DISALLOW", "*")],
                               {"s": "a"}, {"s": "a"}, {})
    assert changed and not unchanged


def test_allow_shields_trailing_disallow():
    ok, _ = apply_rules([("ALLOW", "doc.md"), ("DISALLOW", "*")],
                        {}, {"doc.md": "h"}, {})
    assert ok


def test_rule_order_is_significant():
    ok, _ = apply_rules([("DISALLOW", "*"), ("ALLOW", "doc.md")],
                        {}, {"doc.md": "h"}, {})
    assert not ok


def test_require_present_and_absent():
    yes, _ = apply_rules([("REQUIRE", "sbom.json"), ("ALLOW", "*")],
                         {}, {"sbom.json": "h"}, {})
    no, _ = apply_rules([("REQUIRE", "sbom.json"), ("ALLOW", "*")],
                        {}, {"other": "h"}, {})
    assert yes and not no


def test_verify_step_threshold_enforced():
    step = {"name": "package", "authorized": {"carol", "dave"},
            "threshold": 2,
            "expected_products": [("CREATE", "app.tar"), ("DISALLOW", "*")]}
    links = {"package": {"materials": {}, "products": {"app.tar": "h"}}}
    below, _ = verify_step(step, {"carol"}, links)
    meets, _ = verify_step(step, {"carol", "dave"}, links)
    assert not below and meets


def test_verify_step_rejects_unauthorized_signer():
    step = {"name": "build", "authorized": {"bob"}, "threshold": 1,
            "expected_products": [("CREATE", "app.bin"), ("DISALLOW", "*")]}
    links = {"build": {"materials": {}, "products": {"app.bin": "h"}}}
    ok, _ = verify_step(step, {"mallory"}, links)
    assert not ok


@pytest.mark.parametrize("call", [
    lambda: apply_rules("notalist", {}, {}, {}),
    lambda: apply_rules([("BOGUS", "*")], {}, {}, {}),
    lambda: apply_rules([("MATCH", "x")], {}, {}, {}),
    lambda: apply_rules([("x",)], {}, {}, {}),
    lambda: apply_rules([("MATCH", "x", "s", "bogus")], {}, {"x": "h"},
                        {"s": {}}),
    lambda: verify_step({"name": "s", "authorized": "notaset"}, {"a"}, {}),
    lambda: verify_step({"name": "s", "authorized": {"a"}, "threshold": 0},
                        {"a"}, {}),
    lambda: verify_step({"no_name": True, "authorized": {"a"}}, {"a"}, {}),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(InTotoError):
        call()
