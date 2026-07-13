# Attribute-sampling sample sizes (Poisson)

*Subject area: Audit / Statistical Sampling. Language: python. Vendorable bundle `8d4b99c17dc4`.*

When an auditor tests a control, they need a sample large enough that a clean result gives real assurance. The Poisson (AICPA Audit Guide) method sizes it from a reliability factor R: sample size = ceil(R / tolerable_rate), and after testing, the achieved upper deviation rate is R / sample size -- so a 5% tolerable rate at 95% confidence with zero expected deviations needs 60 items. This module encodes the factors and the arithmetic; the claim proves the factors match their Poisson basis, the sizes match the standard examples, and the plan achieves its tolerable rate, so you inherit a checked sampling calculator rather than a table to re-key.

## Claim

<!-- claim:CLAIM-LIB-AUDIT-SAMPLING-001 checks_matched -->
The vendored attribute-sampling calculator passes all 17 checks with 0 mismatches: each zero-deviation reliability factor equals -ln(1 - confidence) to within table rounding (the Poisson basis); the sample sizes reproduce the standard worked examples (5% tolerable at 95% confidence with 0 expected deviations -> 60; and 24, 30, 93 for other plans); sample size grows monotonically with expected deviations; and for every (tolerable, confidence) the achieved upper deviation rate at the computed size is at most the tolerable rate. Verified value: <!-- v:CLAIM-LIB-AUDIT-SAMPLING-001.checks_matched -->**17**
(`checks_matched`), backed by [`modules/audit_sampling/artifacts/audit_sampling.json`](../modules/audit_sampling/artifacts/audit_sampling.json).

## Vendor it

Ships `audit_sampling.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/8d4b99c17dc497c786cc742f9f12195fac8d2fbf7519e9c1c6d5dabebc8d484d --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **AICPA Audit Guide: Audit Sampling** — Audit Sampling (AICPA Audit Guide). [https://www.aicpa-cima.com/cpe-learning/publication/audit-sampling-audit-guide](https://www.aicpa-cima.com/cpe-learning/publication/audit-sampling-audit-guide)
