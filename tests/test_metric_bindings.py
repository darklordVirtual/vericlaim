# SPDX-License-Identifier: Apache-2.0
"""Adversarial tests for schema-v2 metric bindings (vericlaim/binding.py).

The binding exists to close the v1 hole where an identically-named key
anywhere in the artifact could satisfy the metric check — so the central
adversarial test plants exactly that decoy and proves the binding sees
through it. Everything about a binding fails closed: unresolvable pointers,
wrong types, missing tolerances, ambiguous artifacts, decimal drift.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from vericlaim.binding import (
    PointerError,
    check_metric_bindings,
    resolve_pointer,
)
from vericlaim.config import Config
from vericlaim.gate import check_metrics_match_artifact
from vericlaim.register import RegisterError, load_register


def _cfg(tmp: Path, **over) -> Config:
    return Config(root=tmp, **over)


def _claim(tmp: Path, payload: dict, *, bindings: list,
           metrics: dict | None = None, arts: list | None = None) -> dict:
    art = tmp / "results" / "r.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(payload), encoding="utf-8", newline="\n")
    return {
        "id": "CLAIM-B-001",
        "artifact": arts if arts is not None else ["results/r.json"],
        "metrics": metrics if metrics is not None else {},
        "metric_bindings": bindings,
    }


# ── RFC 6901 pointer resolution ──────────────────────────────────────────────

def test_pointer_resolution_basics():
    doc = {"a": {"b": [10, {"c": 7}]}, "": 1, "x/y": 2, "t~u": 3}
    assert resolve_pointer(doc, "") == doc
    assert resolve_pointer(doc, "/a/b/0") == 10
    assert resolve_pointer(doc, "/a/b/1/c") == 7
    assert resolve_pointer(doc, "/") == 1          # empty key
    assert resolve_pointer(doc, "/x~1y") == 2      # ~1 -> /
    assert resolve_pointer(doc, "/t~0u") == 3      # ~0 -> ~


@pytest.mark.parametrize("bad", [
    "/missing", "/a/b/2", "/a/b/-", "/a/b/01", "/a/b/0/c", "a/b", None,
])
def test_pointer_failures_raise(bad):
    doc = {"a": {"b": [10]}}
    with pytest.raises(PointerError):
        resolve_pointer(doc, bad)


# ── the decoy attack the binding exists to stop ──────────────────────────────

def test_binding_defeats_identically_named_decoy(tmp_path):
    # v1 hole: the true metric is 9, but a decoy `count: 10` elsewhere in the
    # tree satisfies the any-depth key scan. The explicit pointer does not.
    payload = {"summary": {"count": 9}, "unrelated": {"count": 10}}
    claim = _claim(tmp_path, payload,
                   metrics={"count": 10},
                   bindings=[{"metric": "count",
                              "pointer": "/summary/count"}])
    cfg = _cfg(tmp_path)
    # v1 alone would pass (decoy matches) — with the binding it fails.
    v1 = check_metrics_match_artifact([dict(claim, metric_bindings=None)], cfg)
    assert v1 == []  # documents the hole the binding closes
    ids = [e for e, _ in check_metric_bindings([claim], cfg)]
    assert any(e.startswith("binding-value-mismatch") for e in ids)
    # ...and the bound metric is exempt from the v1 scan (no double report).
    assert check_metrics_match_artifact([claim], cfg) == []


# ── decimal-exact comparison ─────────────────────────────────────────────────

def test_decimal_exactness_no_float_drift(tmp_path):
    claim = _claim(tmp_path, {"ratio": 8.0584},
                   bindings=[{"metric": "ratio", "pointer": "/ratio",
                              "value": "8.0584"}])
    assert check_metric_bindings([claim], _cfg(tmp_path)) == []


def test_decimal_catches_tiny_drift(tmp_path):
    claim = _claim(tmp_path, {"ratio": 8.05840000000001},
                   bindings=[{"metric": "ratio", "pointer": "/ratio",
                              "value": "8.0584"}])
    ids = [e for e, _ in check_metric_bindings([claim], _cfg(tmp_path))]
    assert any(e.startswith("binding-value-mismatch") for e in ids)


# ── comparators ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("actual,comparator,register,ok", [
    (100, "minimum", 90, True),
    (89, "minimum", 90, False),
    (100, "maximum", 110, True),
    (111, "maximum", 110, False),
    (100, "exact", 100, True),
    (100, "exact", 101, False),
])
def test_ordering_comparators(tmp_path, actual, comparator, register, ok):
    claim = _claim(tmp_path, {"v": actual},
                   bindings=[{"metric": "v", "pointer": "/v",
                              "comparator": comparator, "value": register}])
    findings = check_metric_bindings([claim], _cfg(tmp_path))
    assert (findings == []) is ok, findings


def test_bounded_comparator(tmp_path):
    claim_ok = _claim(tmp_path, {"v": 10.05},
                      bindings=[{"metric": "v", "pointer": "/v",
                                 "comparator": "bounded", "value": "10",
                                 "tolerance": "0.05"}])
    assert check_metric_bindings([claim_ok], _cfg(tmp_path)) == []
    claim_bad = _claim(tmp_path, {"v": 10.06},
                       bindings=[{"metric": "v", "pointer": "/v",
                                  "comparator": "bounded", "value": "10",
                                  "tolerance": "0.05"}])
    ids = [e for e, _ in check_metric_bindings([claim_bad], _cfg(tmp_path))]
    assert any(e.startswith("binding-value-mismatch") for e in ids)
    claim_no_tol = _claim(tmp_path, {"v": 10.0},
                          bindings=[{"metric": "v", "pointer": "/v",
                                     "comparator": "bounded", "value": "10"}])
    ids = [e for e, _ in check_metric_bindings([claim_no_tol], _cfg(tmp_path))]
    assert any(e.startswith("binding-missing-tolerance") for e in ids)


# ── typing ───────────────────────────────────────────────────────────────────

def test_type_mismatch_fails(tmp_path):
    claim = _claim(tmp_path, {"n": "42"},
                   bindings=[{"metric": "n", "pointer": "/n",
                              "type": "integer", "value": 42}])
    ids = [e for e, _ in check_metric_bindings([claim], _cfg(tmp_path))]
    assert any(e.startswith("binding-type-mismatch") for e in ids)


def test_boolean_is_not_a_number(tmp_path):
    claim = _claim(tmp_path, {"flag": True},
                   bindings=[{"metric": "flag", "pointer": "/flag",
                              "type": "number", "value": 1}])
    ids = [e for e, _ in check_metric_bindings([claim], _cfg(tmp_path))]
    assert any(e.startswith("binding-type-mismatch") for e in ids)


def test_boolean_binds_as_boolean(tmp_path):
    claim = _claim(tmp_path, {"flag": True},
                   bindings=[{"metric": "flag", "pointer": "/flag",
                              "type": "boolean", "value": True}])
    assert check_metric_bindings([claim], _cfg(tmp_path)) == []


# ── fail-closed plumbing ─────────────────────────────────────────────────────

def test_pointer_missing_is_a_finding(tmp_path):
    claim = _claim(tmp_path, {"v": 1},
                   bindings=[{"metric": "v", "pointer": "/nope", "value": 1}])
    ids = [e for e, _ in check_metric_bindings([claim], _cfg(tmp_path))]
    assert any(e.startswith("binding-pointer-missing") for e in ids)


def test_ambiguous_artifact_is_a_finding(tmp_path):
    claim = _claim(tmp_path, {"v": 1},
                   arts=["results/r.json", "results/other.json"],
                   bindings=[{"metric": "v", "pointer": "/v", "value": 1}])
    ids = [e for e, _ in check_metric_bindings([claim], _cfg(tmp_path))]
    assert any(e.startswith("binding-artifact-ambiguous") for e in ids)


def test_unclaimed_artifact_is_a_finding(tmp_path):
    claim = _claim(tmp_path, {"v": 1},
                   bindings=[{"metric": "v", "pointer": "/v", "value": 1,
                              "artifact": "results/elsewhere.json"}])
    ids = [e for e, _ in check_metric_bindings([claim], _cfg(tmp_path))]
    assert any(e.startswith("binding-artifact-unclaimed") for e in ids)


def test_value_falls_back_to_metrics_and_missing_fails(tmp_path):
    ok = _claim(tmp_path, {"v": 5}, metrics={"v": 5},
                bindings=[{"metric": "v", "pointer": "/v"}])
    assert check_metric_bindings([ok], _cfg(tmp_path)) == []
    orphan = _claim(tmp_path, {"v": 5},
                    bindings=[{"metric": "v", "pointer": "/v"}])
    ids = [e for e, _ in check_metric_bindings([orphan], _cfg(tmp_path))]
    assert any(e.startswith("binding-no-value") for e in ids)


def test_bad_comparator_and_bad_type_are_findings(tmp_path):
    claim = _claim(tmp_path, {"v": 1},
                   bindings=[{"metric": "v", "pointer": "/v", "value": 1,
                              "comparator": "roughly"},
                             {"metric": "v", "pointer": "/v", "value": 1,
                              "type": "float"}])
    ids = [e for e, _ in check_metric_bindings([claim], _cfg(tmp_path))]
    assert any(e.startswith("binding-bad-comparator") for e in ids)
    assert any(e.startswith("binding-bad-type") for e in ids)


def test_unreadable_artifact_is_a_finding(tmp_path):
    claim = {"id": "C", "artifact": ["results/gone.json"],
             "metric_bindings": [{"metric": "v", "pointer": "/v",
                                  "value": 1}]}
    ids = [e for e, _ in check_metric_bindings([claim], _cfg(tmp_path))]
    assert any(e.startswith("binding-artifact-unreadable") for e in ids)


# ── register shape validation + parser parity ───────────────────────────────

REG_V2 = """\
claims:
  - id: CLAIM-V2-001
    statement: >
      s
    evidence_level: measured
    artifact:
      - results/r.json
    caveat: >
      c
    metrics:
      ratio: 8.0584
    metric_bindings:
      - metric: ratio
        pointer: /ratio
        comparator: exact
        type: number
"""


def test_bindings_parse_identically_under_both_parsers():
    from vericlaim import register as regmod
    claims_subset = regmod._parse_subset(REG_V2)
    got = claims_subset[0]["metric_bindings"]
    assert got == [{"metric": "ratio", "pointer": "/ratio",
                    "comparator": "exact", "type": "number"}]
    yaml = pytest.importorskip("yaml")
    assert yaml.safe_load(REG_V2)["claims"][0]["metric_bindings"] == got
    # and the public loader accepts it
    assert load_register(REG_V2)[0]["metric_bindings"] == got


@pytest.mark.parametrize("snippet", [
    "    metric_bindings: not-a-list\n",
    "    metric_bindings:\n      - just-a-string\n",
])
def test_malformed_bindings_raise(snippet):
    pytest.importorskip("yaml")
    text = ("claims:\n  - id: C\n    statement: s\n"
            "    evidence_level: measured\n    artifact: [a.json]\n"
            "    caveat: c\n" + snippet)
    with pytest.raises(RegisterError):
        load_register(text)


def test_binding_without_pointer_raises():
    pytest.importorskip("yaml")
    text = ("claims:\n  - id: C\n    statement: s\n"
            "    evidence_level: measured\n    artifact: [a.json]\n"
            "    caveat: c\n"
            "    metric_bindings:\n      - metric: v\n")
    with pytest.raises(RegisterError):
        load_register(text)
