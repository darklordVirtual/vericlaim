# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the prov_dm module (W3C PROV-DM core)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "prov_dm"
_spec = importlib.util.spec_from_file_location(
    "claimlib_prov_dm", _MOD_DIR / "prov_dm.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_prov_dm"] = _m
_spec.loader.exec_module(_m)

ProvError = _m.ProvError
ProvDocument = _m.ProvDocument
RELATIONS = _m.RELATIONS
validate = _m.validate
is_valid = _m.is_valid


def test_core_taxonomy_shape():
    assert len(RELATIONS) == 7
    assert RELATIONS["used"] == ("activity", "entity")
    assert RELATIONS["actedOnBehalfOf"] == ("agent", "agent")
    assert "wasStartedBy" not in RELATIONS


def test_wellformed_pipeline_valid():
    doc = ProvDocument(
        {"d": "entity", "m": "entity", "t": "activity", "g": "agent"},
        [("used", "t", "d"), ("wasGeneratedBy", "m", "t"),
         ("wasDerivedFrom", "m", "d"), ("wasAttributedTo", "m", "g"),
         ("wasAssociatedWith", "t", "g")])
    assert is_valid(doc)


def test_signature_violations_caught():
    doc = ProvDocument({"e": "entity", "a": "activity"},
                       [("used", "e", "a")])   # swapped
    assert any("signature" in p for p in validate(doc))


def test_unknown_relation_and_id_caught():
    doc = ProvDocument({"e": "entity"}, [("wasQuotedFrom", "e", "e")])
    assert not is_valid(doc)
    doc2 = ProvDocument({"e": "entity", "a": "activity"},
                        [("used", "a", "ghost")])
    assert any("unknown element" in p for p in validate(doc2))


def test_derivation_cycle_caught_dag_allowed():
    cyc = ProvDocument({"a": "entity", "b": "entity"},
                       [("wasDerivedFrom", "a", "b"),
                        ("wasDerivedFrom", "b", "a")])
    assert any("cycle" in p for p in validate(cyc))
    dag = ProvDocument({"a": "entity", "b": "entity", "c": "entity"},
                       [("wasDerivedFrom", "c", "a"),
                        ("wasDerivedFrom", "c", "b"),
                        ("wasDerivedFrom", "b", "a")])
    assert is_valid(dag)


def test_delegation_cycle_caught():
    doc = ProvDocument({"x": "agent", "y": "agent"},
                       [("actedOnBehalfOf", "x", "y"),
                        ("actedOnBehalfOf", "y", "x")])
    assert any("actedOnBehalfOf cycle" in p for p in validate(doc))


def test_communication_between_activities_ok():
    doc = ProvDocument({"a1": "activity", "a2": "activity"},
                       [("wasInformedBy", "a2", "a1")])
    assert is_valid(doc)


@pytest.mark.parametrize("call", [
    lambda: ProvDocument({}, []),
    lambda: ProvDocument({"x": "process"}, []),
    lambda: ProvDocument({"": "entity"}, []),
    lambda: ProvDocument({"x": "entity"}, [("used", "x")]),
    lambda: ProvDocument({"x": "entity"}, [["used", "x", "x"]]),
    lambda: ProvDocument({"x": "entity"}, "relations"),
])
def test_malformed_documents_rejected(call):
    with pytest.raises(ProvError):
        call()
