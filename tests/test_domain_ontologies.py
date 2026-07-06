# SPDX-License-Identifier: Apache-2.0
"""Ontology validator: classification is total on the fixture, catches gaps."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "domains" / "ontologies" / "src"))
from ontology import classify, validate  # noqa: E402

FIXTURE = json.loads(
    (ROOT / "domains/ontologies/data/sample_register.json").read_text())["claims"]


def test_validate_matches_artifact():
    art = json.loads(
        (ROOT / "domains/ontologies/artifacts/ontology_conformance.json").read_text())
    for k, v in validate(FIXTURE).items():
        assert art[k] == v


def test_every_fixture_claim_classifies():
    assert all(classify(c) is not None for c in FIXTURE)


def test_unknown_level_is_nonconforming():
    bad = [{"id": "B", "evidence_level": "vibes", "metrics": {"n_x": 1}}]
    assert validate(bad)["nonconforming"] == 1


def test_theorem_and_correctness_rules():
    assert classify({"evidence_level": "machine_checked", "metrics": {}}) == "theorem"
    assert classify(
        {"evidence_level": "benchmarked",
         "metrics": {"cases_total": 3, "cases_passing": 3}}) == "correctness"
