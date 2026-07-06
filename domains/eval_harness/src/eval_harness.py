# SPDX-License-Identifier: Apache-2.0
"""A deterministic evaluation harness for claim-grounded answers.

The knowledge domain is *evaluation*: given a system that answers questions by
citing claim ids (like the vericlaim oracle), how do you measure whether it is
grounded and whether it refuses off-corpus questions? This harness scores a
fixed system-under-test against a committed gold standard and reports grounding
precision/recall/F1 and refusal accuracy — no model call, fully reproducible.

Nothing here is a live model benchmark: the "predictions" are a committed,
deliberately-imperfect answer set, so the numbers exercise the *scorer*, not any
LLM. Swap in real oracle outputs and the same scorer grades them.
"""
from __future__ import annotations

from dataclasses import dataclass

# claim:CLAIM-EVAL-001 n_cases
# The gold set below has exactly 10 cases — a registered claim; add or remove a
# case and evidence.py must be re-run and the register updated, or the gate fails.


@dataclass(frozen=True)
class Case:
    """One evaluation item: the question, the ids that truly support an answer,
    and whether a grounded system should REFUSE (no supporting claim exists)."""
    qid: str
    gold_ids: frozenset[str]
    should_refuse: bool


@dataclass(frozen=True)
class Prediction:
    """A system-under-test answer: the ids it cited and whether it refused."""
    qid: str
    cited_ids: frozenset[str]
    refused: bool


# A fixed gold standard (10 cases: 7 answerable, 3 that must be refused).
GOLD: tuple[Case, ...] = (
    Case("q1", frozenset({"CLAIM-A", "CLAIM-B"}), False),
    Case("q2", frozenset({"CLAIM-C"}), False),
    Case("q3", frozenset({"CLAIM-D", "CLAIM-E"}), False),
    Case("q4", frozenset({"CLAIM-F"}), False),
    Case("q5", frozenset({"CLAIM-G", "CLAIM-H"}), False),
    Case("q6", frozenset({"CLAIM-I"}), False),
    Case("q7", frozenset({"CLAIM-J"}), False),
    Case("q8", frozenset(), True),
    Case("q9", frozenset(), True),
    Case("q10", frozenset(), True),
)

# A deliberately-imperfect system-under-test: mostly grounded, but q3 misses one
# gold id (recall miss), q4 adds a hallucinated citation (precision miss), and q9
# fails to refuse an off-corpus question (refusal miss). This keeps the metrics
# off a trivial 1.0 so the scorer is actually exercised.
PREDICTIONS: tuple[Prediction, ...] = (
    Prediction("q1", frozenset({"CLAIM-A", "CLAIM-B"}), False),
    Prediction("q2", frozenset({"CLAIM-C"}), False),
    Prediction("q3", frozenset({"CLAIM-D"}), False),                 # recall miss
    Prediction("q4", frozenset({"CLAIM-F", "CLAIM-X"}), False),      # precision miss
    Prediction("q5", frozenset({"CLAIM-G", "CLAIM-H"}), False),
    Prediction("q6", frozenset({"CLAIM-I"}), False),
    Prediction("q7", frozenset({"CLAIM-J"}), False),
    Prediction("q8", frozenset(), True),
    Prediction("q9", frozenset({"CLAIM-Z"}), False),                 # refusal miss
    Prediction("q10", frozenset(), True),
)


def _round(x: float) -> float:
    """Round to 4 decimals so the artifact is byte-stable across platforms."""
    return round(x, 4)


def evaluate(gold: tuple[Case, ...],
             preds: tuple[Prediction, ...]) -> dict[str, float]:
    """Score *preds* against *gold*. Micro-averaged grounding precision/recall
    over answered cases, plus refusal accuracy over the refusal-relevant ones."""
    by_pred = {p.qid: p for p in preds}
    tp = fp = fn = 0                 # grounding citation counts (micro)
    refuse_total = refuse_correct = 0
    for case in gold:
        pred = by_pred[case.qid]
        if case.should_refuse:
            refuse_total += 1
            if pred.refused and not pred.cited_ids:
                refuse_correct += 1
            continue
        # Answerable case: compare cited ids to gold ids.
        tp += len(pred.cited_ids & case.gold_ids)
        fp += len(pred.cited_ids - case.gold_ids)
        fn += len(case.gold_ids - pred.cited_ids)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) else 0.0)
    refusal_accuracy = refuse_correct / refuse_total if refuse_total else 0.0
    return {
        "n_cases": len(gold),
        "grounding_precision": _round(precision),
        "grounding_recall": _round(recall),
        "grounding_f1": _round(f1),
        "refusal_accuracy": _round(refusal_accuracy),
    }
