# Domain: Eval Harness

A deterministic **evaluation harness** for claim-grounded answering systems.
Scores a system-under-test against a committed gold standard: grounding
precision / recall / F1 (did it cite the right claim ids?) and refusal accuracy
(did it refuse off-corpus questions?).

- `src/eval_harness.py` — the gold set, a fixed system-under-test, and the scorer.
- `evidence.py` — runs the scorer and writes `artifacts/eval_report.json`.
- `docs/results.md` — the gate-bound results.

Reproduce: `python3 domains/eval_harness/evidence.py` ·
Claim: `CLAIM-EVAL-001` · Evidence level: `benchmarked`.

Why it is a *knowledge domain*, not a toy: the scoring rubric (micro-averaged
citation P/R/F1 + refusal accuracy) is exactly what you need to evaluate the
vericlaim oracle or any RAG system that must cite its sources and abstain.
