# Percentiles / quantiles (p50 / p95 / p99)

*Subject area: Observability / Metrics & Statistics. Language: python. Vendorable bundle `5759c13284a2`.*

Percentiles are how you actually read a latency distribution: the p50 (median) is the typical experience, while the p95 / p99 tail is where SLOs live and where users feel pain that an average hides. The subtlety is that 'the 95th percentile' has several definitions that disagree on small samples; the common ones are linear interpolation between order statistics and the nearest-rank rule. This module implements both exactly; the claim proves the linear method matches Python's statistics module and the nearest-rank method matches its definition, so you inherit a checked quantile function rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-PERCENTILE-001 checks_matched -->
The vendored percentile calculator agrees with Python's stdlib statistics on every one of 605 checks across a fixed 6-dataset battery (checks_matched = 605, mismatches = 0): the linear method matches statistics.quantiles(data, n=100, method="inclusive") for every percentile p in 1..99 and matches statistics.median at the 50th, and the nearest-rank method matches its hand-computed definition on 5 boundary cases (including p=0, p=100, and interior ranks). Verified value: <!-- v:CLAIM-LIB-PERCENTILE-001.checks_matched -->**605**
(`checks_matched`), backed by [`modules/percentile/artifacts/percentile.json`](../modules/percentile/artifacts/percentile.json).

## Vendor it

Ships `percentile.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/5759c13284a202a9f7835d73eb87ddba6e6419ea33e89bba49765ab254ea2f0b --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **The American Statistician, vol. 50, no. 4, pp. 361-365, doi:10.1080/00031305.1996.10473566** — Sample Quantiles in Statistical Packages. [https://www.tandfonline.com/doi/abs/10.1080/00031305.1996.10473566](https://www.tandfonline.com/doi/abs/10.1080/00031305.1996.10473566)
