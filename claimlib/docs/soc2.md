# SOC 2 Trust Services Criteria coverage

*Subject area: Compliance / Audit Frameworks. Language: python. Vendorable bundle `b751eae3bc8a`.*

SOC 2 is the service-organization audit report most SaaS vendors are asked for; it attests controls against the AICPA Trust Services Criteria -- five categories, with Security (the Common Criteria CC1..CC9) always in scope and Availability, Processing Integrity, Confidentiality, and Privacy added as needed. Teams map their controls to this structure to plan an audit and track readiness. This module encodes the taxonomy and computes coverage; the claim proves the encoded criteria match the framework and the math is correct, so you inherit a checked readiness model rather than a spreadsheet to re-audit.

## Claim

<!-- claim:CLAIM-LIB-SOC2-001 checks_matched -->
The vendored SOC 2 coverage model matches the AICPA Trust Services Criteria taxonomy and arithmetic on all 8 checks with 0 mismatches: the five Trust Services Categories are exactly Security, Availability, Processing Integrity, Confidentiality and Privacy; the nine Common Criteria series are CC1..CC9; and coverage() computes hand-verified fractions (empty -> 0.0, all nine CC -> 1.0, a 3-of-9 subset -> 0.3333 with the correct missing list). Verified value: <!-- v:CLAIM-LIB-SOC2-001.checks_matched -->**8**
(`checks_matched`), backed by [`modules/soc2/artifacts/soc2.json`](../modules/soc2/artifacts/soc2.json).

## Vendor it

Ships `soc2.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/b751eae3bc8aff389918d8496b41ceb8323d1d3758d6d4fb186321022b1d563b --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **AICPA TSP Section 100 (2017, rev. 2022)** — Trust Services Criteria for Security, Availability, Processing Integrity, Confidentiality, and Privacy. [https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022)
