# SPDX-License-Identifier: Apache-2.0
"""The eval-harness scorer: deterministic, and the artifact matches the code."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "domains" / "eval_harness" / "src"))
from eval_harness import GOLD, PREDICTIONS, Case, Prediction, evaluate  # noqa: E402


def test_scorer_is_deterministic_and_matches_artifact():
    scores = evaluate(GOLD, PREDICTIONS)
    art = json.loads(
        (ROOT / "domains/eval_harness/artifacts/eval_report.json").read_text())
    for key, value in scores.items():
        assert art[key] == value, f"{key}: artifact {art[key]} != code {value}"


def test_perfect_predictions_score_one():
    perfect = tuple(
        Prediction(c.qid, c.gold_ids, c.should_refuse) for c in GOLD)
    scores = evaluate(GOLD, perfect)
    assert scores["grounding_f1"] == 1.0
    assert scores["refusal_accuracy"] == 1.0


def test_hallucinated_citation_lowers_precision():
    gold = (Case("q", frozenset({"A"}), False),)
    preds = (Prediction("q", frozenset({"A", "HALLUCINATED"}), False),)
    scores = evaluate(gold, preds)
    assert scores["grounding_precision"] == 0.5
    assert scores["grounding_recall"] == 1.0


def test_failing_to_refuse_is_penalised():
    gold = (Case("q", frozenset(), True),)
    preds = (Prediction("q", frozenset({"X"}), False),)
    assert evaluate(gold, preds)["refusal_accuracy"] == 0.0
