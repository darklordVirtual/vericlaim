# NIST CSF 2.0 coverage

*Subject area: Security / Governance & Compliance. Language: python. Vendorable bundle `69749dc77bad`.*

The NIST Cybersecurity Framework 2.0 is the common language security programs use to organize and communicate risk work: six Functions (the 2024 revision added Govern) each broken into Categories and Subcategories. Teams map their controls to this structure to see where they are strong and where gaps sit. This module encodes the Function/Category taxonomy and computes coverage; the claim proves the encoded taxonomy matches the framework and the math is correct, so you inherit a checked coverage model rather than a hand-maintained spreadsheet to re-audit.

## Claim

<!-- claim:CLAIM-LIB-NIST-CSF-001 checks_matched -->
The vendored NIST CSF 2.0 coverage model matches the published taxonomy and arithmetic on all 30 checks with 0 mismatches: the six Functions are exactly Govern, Identify, Protect, Detect, Respond and Recover; all 22 Categories map to the correct Function (their two-letter prefix); and coverage() computes hand-verified fractions (all six Govern categories -> GV coverage 1.0, a 2-of-3 subset -> 0.6667, the full set -> overall 1.0, the empty set -> 0). Verified value: <!-- v:CLAIM-LIB-NIST-CSF-001.checks_matched -->**30**
(`checks_matched`), backed by [`modules/nist_csf/artifacts/nist_csf.json`](../modules/nist_csf/artifacts/nist_csf.json).

## Vendor it

Ships `nist_csf.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/69749dc77badee4881d5a4de6421c02015fc155d2b45803cf7ca0987d1df7a4b --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **NIST CSWP 29** — The NIST Cybersecurity Framework (CSF) 2.0. [https://csrc.nist.gov/pubs/cswp/29/the-nist-cybersecurity-framework-csf-20/final](https://csrc.nist.gov/pubs/cswp/29/the-nist-cybersecurity-framework-csf-20/final)
