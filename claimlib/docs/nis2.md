# EU NIS2 Directive Article 21 coverage

*Subject area: Security / Governance & Compliance. Language: python. Vendorable bundle `5eb36d23fe11`.*

The EU NIS2 Directive (2022/2555) raises the cybersecurity baseline for essential and important entities across the Union; its Article 21(2) lists ten minimum risk-management measures -- from risk analysis and incident handling to supply-chain security, cryptography, and multi-factor authentication. Organizations track which measures they have implemented to prepare for the obligation. This module encodes the ten measures and computes coverage; the claim proves the measures match the Directive and the math is correct, so you inherit a checked gap-tracking model rather than a hand-maintained checklist to re-audit.

## Claim

<!-- claim:CLAIM-LIB-NIS2-001 checks_matched -->
The vendored NIS2 coverage model matches the Directive and arithmetic on all 7 checks with 0 mismatches: the encoded measures are exactly the ten Article 21(2) items a..j of Directive (EU) 2022/2555, and coverage() computes hand-verified values -- the empty set -> 0.0, the full set -> 1.0, a 4-of-10 subset -> 0.4 with the missing list its exact complement. Verified value: <!-- v:CLAIM-LIB-NIS2-001.checks_matched -->**7**
(`checks_matched`), backed by [`modules/nis2/artifacts/nis2.json`](../modules/nis2/artifacts/nis2.json).

## Vendor it

Ships `nis2.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/5eb36d23fe11c7e9876a954ed8acab2dc607965697568c775469e245e98776a5 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **Directive (EU) 2022/2555** — Directive (EU) 2022/2555 (NIS2) on measures for a high common level of cybersecurity. [https://eur-lex.europa.eu/eli/dir/2022/2555/oj](https://eur-lex.europa.eu/eli/dir/2022/2555/oj)
