# Eval Harness — Results

A **benchmark claim** over a fixed gold standard: how well does a claim-grounded
answering system cite the right evidence and refuse off-corpus questions? The
harness scores a committed, deliberately-imperfect system-under-test — no model
call — so the numbers are fully reproducible and grade the *scorer*.

<!-- claim:CLAIM-EVAL-001 n_cases -->
The gold set has **10** cases (7 answerable, 3 that must be refused).

<!-- claim:CLAIM-EVAL-001 grounding_f1 -->
Micro-averaged grounding **F1 is 0.9** on the committed system-under-test.

<!-- claim:CLAIM-EVAL-001 refusal_accuracy -->
Refusal accuracy is **0.6667** — the system-under-test correctly refuses 2 of
the 3 off-corpus questions (one deliberate refusal miss).

Artifact: [`../artifacts/eval_report.json`](../artifacts/eval_report.json) ·
Reproduce: `python3 domains/eval_harness/evidence.py`

> Scope: a fixed gold set and a fixed answer set demonstrate the evaluation
> method; these are not results for any live model. Point the same scorer at
> real oracle outputs to grade them.
