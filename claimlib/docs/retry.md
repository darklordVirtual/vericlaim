# Deterministic exponential backoff with full jitter

*Subject area: Reliability / Distributed Systems. Language: python. Vendorable bundle `9f97845d25f9`.*

Retrying a failed remote call immediately, in lockstep with every other client, produces a synchronized 'thundering herd' that keeps the dependency down. Capped exponential backoff (min(cap, base*2**attempt)) grows the wait between attempts, and 'full jitter' (AWS, 2015) then draws the actual delay uniformly from [0, that ceiling] so clients decorrelate instead of all firing at the ceiling. This module keeps full jitter's spread but derives the draw from a SHA-256 hash of (seed, attempt) rather than a PRNG, so the schedule is reproducible in tests and logs and identical across processes, while different seeds still decorrelate different clients.

## Claim

<!-- claim:CLAIM-LIB-RETRY-001 within_bounds -->
The vendored full-jitter backoff computes each delay as a hash-seeded draw from [0, min(cap, base*2**attempt)]: over a fixed 16-attempt reference schedule (attempts 0..15, base=1.0, cap=60.0, seed=1337) all 16 delays land inside their independently-computed [0, ceiling] window (within_bounds=16, out_of_bounds=0), and a seeded replay reproduces the schedule byte-for-byte (deterministic=1). Verified value: <!-- v:CLAIM-LIB-RETRY-001.within_bounds -->**16**
(`within_bounds`), backed by [`modules/retry/artifacts/retry.json`](../modules/retry/artifacts/retry.json).

## Vendor it

Ships `retry.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/9f97845d25f9afbfb992ae527b62db4992909a332baf6e54e0fb0937678a81c7 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **AWS Architecture Blog, 4 March 2015** — Exponential Backoff And Jitter. [https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
