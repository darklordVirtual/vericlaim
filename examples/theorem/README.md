# Theorem example — a machine-checked proof as evidence

The claim shape here is a **proved theorem**. The evidence is not a benchmark
run but a *proof object*: a committed Hilbert-system derivation
([`proofs/p_implies_p.json`](proofs/p_implies_p.json)) verified step by step by
a fail-closed checker ([`src/proofcheck.py`](src/proofcheck.py)). The checker's
verdict is the artifact; `vericlaim reproduce` re-runs the verification, so the
claim "this theorem is proved" is regenerated from the derivation itself on
every check — never asserted by hand.

The axiom system (Łukasiewicz A1–A3 + modus ponens) is cited via a
hash-verified `literature` entry in the register pointing at
[`docs/references/lukasiewicz-axioms.md`](../../docs/references/lukasiewicz-axioms.md):
the gate proves the cited note cannot silently change after registration. The
literature supports the *context*; correctness of the derivation is established
only by the checker.

This is also the pattern for real proof assistants: point `reproduce` at
`lake build` (Lean) or `coqc` (Coq) instead of the bundled checker, commit the
proof source as the artifact, and grade the claim `machine_checked`.

Numbers live in [`docs/results.md`](docs/results.md), bound to the register.
Reproduce: `python3 examples/theorem/evidence.py`
