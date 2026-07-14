# Expected Calibration Error (ECE/MCE) reliability binning

*Subject area: AI Governance / Model Calibration. Language: python. Vendorable bundle `b020ebd639bf`.*

A model that says '90% confident' should be right about 90% of the time — that property is calibration, and modern networks notoriously lack it (Guo et al. 2017). The standard audit measurement partitions predictions into M equal-width confidence bins and sums the gap between each bin's accuracy and its average confidence, weighted by bin size: ECE. This module computes the bins, ECE and worst-bin MCE in exact arithmetic; the claim proves the numbers against hand computation and an independent re-derivation, so a model-risk review inherits a checked calibration figure.

## Claim

<!-- claim:CLAIM-LIB-ECE-001 checks_matched -->
The vendored calibration library passes all 14 checks as exact Fraction equalities with 0 mismatches: 7 hand-computed values (two predictions at confidence 4/5 with one correct give ECE exactly 3/10; a perfectly calibrated fixture gives exactly 0; the right-closed bin edges place 0.0, 0.1 and 1.0 correctly), agreement with an independent first-principles re-derivation on a 240-pair battery for 5, 10 and 15 bins, and the estimator's bound and permutation-invariance properties. Verified value: <!-- v:CLAIM-LIB-ECE-001.checks_matched -->**14**
(`checks_matched`), backed by [`modules/calibration_ece/artifacts/calibration_ece.json`](../modules/calibration_ece/artifacts/calibration_ece.json).

## Vendor it

Ships `calibration_ece.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/b020ebd639bf17571d5e77d295fca8fdfd6fcf99c9cdb69adba5642ebb53ef1b --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **PMLR 70:1321-1330; arXiv:1706.04599** — On Calibration of Modern Neural Networks. [https://proceedings.mlr.press/v70/guo17a.html](https://proceedings.mlr.press/v70/guo17a.html)
