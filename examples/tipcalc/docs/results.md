# Tip calculator — Results

A **correctness claim**: does it compute the right answer? The counts below are
bound to the claim register. If a future change breaks a case, the evidence
artifact records fewer passing cases and the gate fails — the docs cannot keep
saying "all cases pass."

<!-- claim:CLAIM-TIP-001 cases_passing cases_total -->
All **12** of the **12** reference bills produce the expected total to the cent.

Artifact: [`../artifacts/tipcalc.json`](../artifacts/tipcalc.json) ·
Reproduce: `python examples/tipcalc/evidence.py`
