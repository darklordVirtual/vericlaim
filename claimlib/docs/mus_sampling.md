# Monetary-unit sampling: PPS selection + tainting projection

*Subject area: Audit / Monetary-Unit Sampling. Language: python. Vendorable bundle `e66e3e092033`.*

Monetary-unit sampling treats every krone/dollar in a population as the sampling unit, so a NOK 700,000 invoice is 700,000 chances -- large items are selected with probability proportional to size, and anything at least one sampling interval big is selected with certainty (the top stratum). Misstatements found in sampled items project to the population by tainting: the misstatement fraction of the item times the interval. This module implements the selection and projection in exact Fraction arithmetic; the claim proves the selection guarantees exhaustively and the projection against independent recomputation, so an audit tool inherits checked PPS mechanics.

## Claim

<!-- claim:CLAIM-LIB-MUS-001 checks_matched -->
The vendored monetary-unit sampling library passes all 10 checks with 0 mismatches: the top-stratum guarantee -- an item at least as large as the sampling interval is selected -- holds for EVERY one of the 500000 possible selection starts of the fixed population (exhaustive, as does the selection-point count identity), zero-value items are never selected, the guide's worked projection reproduces ($3,000 item overstated 10% with a $5,000 interval projects $500), and all 4 projection cases match exact Fraction recomputation, including top-stratum actuals and understatements. Verified value: <!-- v:CLAIM-LIB-MUS-001.checks_matched -->**10**
(`checks_matched`), backed by [`modules/mus_sampling/artifacts/mus_sampling.json`](../modules/mus_sampling/artifacts/mus_sampling.json).

## Vendor it

Ships `mus_sampling.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/e66e3e09203359480d4f79dae0dac3d0caad1185c1c46c96e87873573e8894d7 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **AICPA Audit Guide: Audit Sampling** — Audit Sampling (AICPA Audit Guide). [https://www.aicpa-cima.com/cpe-learning/publication/audit-sampling-audit-guide](https://www.aicpa-cima.com/cpe-learning/publication/audit-sampling-audit-guide)
