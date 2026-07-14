# Bloom filter (no false negatives + exact FP analysis)

*Subject area: Data Structures / Probabilistic Sets. Language: python. Vendorable bundle `401309fa2e00`.*

A Bloom filter answers set membership in O(k) with a bit array m bits wide: k hash functions set k bits per insertion, and a query reports 'present' only when all k bits are set -- so absence answers are definitive and presence answers carry a tunable false-positive rate (1-(1-1/m)^(kn))^k. This module implements the filter with SHA-256-derived double hashing plus the exact analysis functions; the claim proves the no-false-negative guarantee and that the analysis math is exact, so you inherit a checked probabilistic set for dedupe, caching and pre-filters.

## Claim

<!-- claim:CLAIM-LIB-BLOOM-001 false_negatives -->
The vendored Bloom filter produces ZERO false negatives over an exhaustive 500-member battery (false_negatives = 0 -- the defining guarantee), its measured 46 false positives over 2000 disjoint probes sit within twice the analytical expectation, its false-positive formula matches exact rational recomputation on all 5 (m, n, k) triples to 12 decimal places, and optimal_k reproduces max(1, round((m/n) ln 2)) on all 4 cases. Verified value: <!-- v:CLAIM-LIB-BLOOM-001.false_negatives -->**0**
(`false_negatives`), backed by [`modules/bloom_filter/artifacts/bloom_filter.json`](../modules/bloom_filter/artifacts/bloom_filter.json).

## Vendor it

Ships `bloom_filter.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/401309fa2e005a9b582b288b56ecf68c0b6d4fbf21a18863a77b16936c3e7d76 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **Communications of the ACM, vol. 13, no. 7, pp. 422-426; doi:10.1145/362686.362692** — Space/Time Trade-offs in Hash Coding with Allowable Errors. [https://doi.org/10.1145/362686.362692](https://doi.org/10.1145/362686.362692)
