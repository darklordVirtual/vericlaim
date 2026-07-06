# Theorem Example — Results

This document's numbers are **bound to the claim register** via the anchor
below. Change a number here without changing `claims/register.yaml` and the
vericlaim gate fails the build.

## The theorem

<!-- claim:CLAIM-THM-001 steps_verified n -->
The committed derivation of **p → p** in Łukasiewicz's axiom system (A1–A3 +
modus ponens; this particular derivation uses only A1–A2) machine-checks in <!-- v:CLAIM-THM-001.steps_verified -->**5** steps: every step verifies as an axiom
instance or a modus-ponens application, and the final step equals the declared
theorem. The checker is the example's own ~100-line, property-tested verifier —
not an independently audited kernel; that scope is part of the claim (see the
register caveat).

Artifact: [`../artifacts/theorem.json`](../artifacts/theorem.json) ·
Proof object: [`../proofs/p_implies_p.json`](../proofs/p_implies_p.json) ·
Reproduce: `python3 examples/theorem/evidence.py`
