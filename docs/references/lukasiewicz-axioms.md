# Łukasiewicz's third axiomatization of classical propositional logic

This note is the committed literature extract backing `CLAIM-THM-001` (see the
`literature` entry in `claims/register.yaml`). The register records this file's
SHA-256, so the gate proves the citation the theorem example builds on cannot
silently change after registration.

## The system

Jan Łukasiewicz (1929) gave a three-axiom basis for classical propositional
logic over implication and negation, with **modus ponens** (from φ and φ → ψ,
infer ψ) as the only rule of inference and uniform substitution understood
schematically:

- **A1** φ → (ψ → φ)
- **A2** (φ → (ψ → χ)) → ((φ → ψ) → (φ → χ))
- **A3** (¬φ → ¬ψ) → (ψ → φ)

The system is sound and complete for classical propositional logic. The
derivation of φ → φ from A1 and A2 alone, in five steps, is the classic
first exercise in Hilbert-style proof theory and is the theorem committed in
`examples/theorem/proofs/p_implies_p.json`.

## Sources

- Jan Łukasiewicz, *Elementy logiki matematycznej* (Warsaw, 1929); English
  translation: *Elements of Mathematical Logic*, Pergamon Press, 1963.
- Elliott Mendelson, *Introduction to Mathematical Logic*, 6th ed., CRC Press,
  2015 — presents the same axiom system (§1.4) and the φ → φ derivation as
  Lemma 1.8.
- Stanford Encyclopedia of Philosophy, "Łukasiewicz's Logic" and "The
  Development of Proof Theory" (https://plato.stanford.edu/).

## Scope of this note

This is our own summary of a public-domain axiom system, committed so the
citation is hash-verifiable. It asserts nothing beyond what any standard logic
text states; correctness of the *derivation* is not taken from the literature
at all — it is machine-checked by `examples/theorem/src/proofcheck.py` on
every `vericlaim reproduce`.
