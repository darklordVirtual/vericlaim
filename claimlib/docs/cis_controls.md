# CIS Critical Security Controls v8.1 taxonomy + IG coverage

*Subject area: Compliance / Security Frameworks. Language: python. Vendorable bundle `c340f5fc48a7`.*

The CIS Critical Security Controls are the most widely used prioritized baseline of defensive practices, organized since v8 into 18 Controls containing 153 Safeguards, tiered into Implementation Groups: IG1 (56 safeguards) as essential cyber hygiene for every enterprise, IG2 (cumulative 130) and IG3 (all 153) as resources and risk grow. This module encodes that structure and scores declared coverage per IG; the claim proves the encoded counts match the published framework and the arithmetic is exact, so a security program inherits a checked assessment skeleton.

## Claim

<!-- claim:CLAIM-LIB-CIS-001 checks_matched -->
The vendored CIS Controls library passes all 38 checks with 0 mismatches: the encoded taxonomy carries the published shape of CIS Critical Security Controls v8.1 -- 18 Controls and 153 Safeguards with the Implementation Group cumulative counts IG1 = 56, IG2 = 130, IG3 = 153 -- verified control-by-control (18 checks) and total-by-total (6), with coverage arithmetic exact on all 13 assessment cases. Verified value: <!-- v:CLAIM-LIB-CIS-001.checks_matched -->**38**
(`checks_matched`), backed by [`modules/cis_controls/artifacts/cis_controls.json`](../modules/cis_controls/artifacts/cis_controls.json).

## Vendor it

Ships `cis_controls.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/c340f5fc48a78e025f56a0027090f51a6e7fc054a67394f26e5340c956d47d28 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **CIS Controls v8.1** — CIS Critical Security Controls, Version 8.1. [https://www.cisecurity.org/controls/v8-1](https://www.cisecurity.org/controls/v8-1)
