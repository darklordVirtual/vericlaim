# Conformal Risk Control (lambda-hat + risk theorem)

*Subject area: AI Assurance / Conformal Prediction. Language: python. Vendorable bundle `25160d2cd640`.*

Conformal Risk Control (Angelopoulos, Bates, Fisch, Lei, Schuster — ICLR 2024) generalizes conformal prediction from one loss (miscoverage) to ANY bounded, monotone loss: false-negative rate, token-level F1 deficit, factuality loss of an LLM's filtered output. Calibrate the loss curve on n held-out units, pick the smallest lambda with (n/(n+1))Rhat(lambda) + B/(n+1) <= alpha, and the deployed expected loss is at most alpha. This module implements the selection rule with exact rational arithmetic and an exhaustive leave-one-out enumerator; the claim proves the theorem by enumeration and the exact reduction to conformal prediction, so a risk-controlled deployment inherits checked machinery.

## Claim

<!-- claim:CLAIM-LIB-CRC-001 checks_matched -->
The vendored conformal-risk-control library passes all 21 checks with 0 mismatches: the published selection rule lambdahat = inf{lambda : (n/(n+1)) Rhat_n(lambda) + B/(n+1) <= alpha} reproduces 5 hand-computed selections and algebraic bounds, THE RISK THEOREM IS ENUMERATED over the 10 pool-by-alpha combinations satisfying its preconditions (exhaustive leave-one-out risk <= alpha as exact Fractions, for binary and fractional bounded losses), 2 out-of-precondition cases refuse honestly, and with the miscoverage-indicator loss the selection reduces EXACTLY to the split-conformal quantile rule on all 4 alphas. Verified value: <!-- v:CLAIM-LIB-CRC-001.checks_matched -->**21**
(`checks_matched`), backed by [`modules/conformal_risk/artifacts/conformal_risk.json`](../modules/conformal_risk/artifacts/conformal_risk.json).

## Vendor it

Ships `conformal_risk.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/25160d2cd6402f00e77c1538f158b7724d412480d4c3103531fecd8a250a458c --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **arXiv:2208.02814** — Conformal Risk Control. [https://arxiv.org/abs/2208.02814](https://arxiv.org/abs/2208.02814)
- **arXiv:2107.07511** — A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification. [https://arxiv.org/abs/2107.07511](https://arxiv.org/abs/2107.07511)
