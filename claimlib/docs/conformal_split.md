# Split conformal prediction (quantile + coverage theorem)

*Subject area: AI Assurance / Conformal Prediction. Language: python. Vendorable bundle `02f991778748`.*

Split conformal prediction turns ANY scoring model into prediction sets with a distribution-free, finite-sample coverage guarantee: calibrate nonconformity scores on held-out data, take the ceil((n+1)(1-alpha))-quantile, and include every candidate scoring at or below it — the true answer lands inside with probability at least 1-alpha (Angelopoulos & Bates 2021). It is the workhorse of AI uncertainty quantification, from classification to LLM factuality gating. This module implements the quantile, prediction sets and an exhaustive leave-one-out coverage enumerator; the claim proves the coverage theorem by enumeration, so an assurance case inherits checked conformal machinery.

## Claim

<!-- claim:CLAIM-LIB-CONFORMAL-001 checks_matched -->
The vendored split-conformal library passes all 32 checks with 0 mismatches: the published quantile rule qhat = ceil((n+1)(1-alpha))-th smallest calibration score reproduces 6 hand-computed ranks (including the classic n=100, alpha=0.1 -> rank 91), and THE COVERAGE THEOREM IS ENUMERATED — over 15 pool-by-alpha combinations, exhaustive leave-one-out coverage lands inside [1-alpha, 1-alpha + 1/n] as an exact Fraction, ties never fall below 1-alpha, prediction sets shrink monotonically in alpha, and the too-few-calibration-points case honestly returns everything. Verified value: <!-- v:CLAIM-LIB-CONFORMAL-001.checks_matched -->**32**
(`checks_matched`), backed by [`modules/conformal_split/artifacts/conformal_split.json`](../modules/conformal_split/artifacts/conformal_split.json).

## Vendor it

Ships `conformal_split.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/02f991778748305cda8d2dae38888822e5e0dc42483d04e9331f5ab59cbd2180 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **arXiv:2107.07511** — A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification. [https://arxiv.org/abs/2107.07511](https://arxiv.org/abs/2107.07511)
