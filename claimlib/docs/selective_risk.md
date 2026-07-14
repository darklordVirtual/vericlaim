# Selective classification (coverage, risk, risk-coverage curve)

*Subject area: AI Assurance / Selective Prediction. Language: python. Vendorable bundle `ae0e31c2c1b9`.*

A selective classifier may abstain: accept an input when confidence clears a threshold, and be judged only on what was accepted — coverage is the accept rate, selective risk the error rate among accepted (Geifman & El-Yaniv 2017). The risk-coverage curve is the menu of operating points an abstention policy can buy, and it is how 'the model defers to a human below X% confidence' becomes a measurable contract. This module computes all of it in exact rational arithmetic; the claim proves the definitions and their structural properties, so an escalation policy inherits checked numbers.

## Claim

<!-- claim:CLAIM-LIB-SELECTIVE-001 checks_matched -->
The vendored selective-classification library passes all 15 checks as exact Fraction equalities with 0 mismatches: 6 hand-computed audit values (coverage exactly 1/2 at threshold 0.7 with selective risk exactly 1/4; full coverage reproducing the plain mean 3/8), 8 structural properties of the risk-coverage curve over a 40-point battery (last point coverage exactly 1 at the unconditional mean, monotone coverage, permutation invariance), and the zero-coverage case failing closed rather than reporting 0. Verified value: <!-- v:CLAIM-LIB-SELECTIVE-001.checks_matched -->**15**
(`checks_matched`), backed by [`modules/selective_risk/artifacts/selective_risk.json`](../modules/selective_risk/artifacts/selective_risk.json).

## Vendor it

Ships `selective_risk.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/ae0e31c2c1b976737bd3538738f8c99ddaafb0b8292fd64406de658028a027b7 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **arXiv:1705.08500** — Selective Classification for Deep Neural Networks. [https://proceedings.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html](https://proceedings.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html)
