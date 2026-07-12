# Benford's Law leading-digit analysis

*Subject area: Audit / Forensic Analytics. Language: python. Vendorable bundle `e17ef0b06d30`.*

Benford's Law says that in many natural datasets the leading digit is 1 about 30% of the time and 9 under 5%, following log10(1 + 1/d). Forensic accountants and auditors screen ledgers, expense reports, and tax data against this distribution: a sharp deviation is a red flag worth investigating (invented numbers tend to be too uniform). This module computes the leading digit, the expected/observed distributions, and the chi-square and MAD statistics; the claim proves the expected distribution equals the Benford formula and the statistics behave as defined, so you inherit a checked anomaly screen rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-BENFORD-001 checks_matched -->
The vendored Benford's Law analyzer passes all 25 checks with 0 mismatches: the expected distribution equals log10(1 + 1/d) for every digit 1..9 (matching the published frequencies 0.301, 0.176, ... 0.046 to 3 dp and summing to 1), leading-digit extraction is correct on 10 cases (including sub-1 and negative values), and the conformance statistics behave as defined -- a near-Benford dataset (the leading digits of 2**1..2**500) conforms while a strongly non-Benford dataset does not, with a larger MAD and chi-square. Verified value: <!-- v:CLAIM-LIB-BENFORD-001.checks_matched -->**25**
(`checks_matched`), backed by [`modules/benford/artifacts/benford.json`](../modules/benford/artifacts/benford.json).

## Vendor it

Ships `benford.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/e17ef0b06d3045c3064277391358afb6f964176160769cb462e879f5c94cce2f --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **Proc. Am. Philos. Soc. 78(4):551-572** — The Law of Anomalous Numbers. [https://www.jstor.org/stable/984802](https://www.jstor.org/stable/984802)
