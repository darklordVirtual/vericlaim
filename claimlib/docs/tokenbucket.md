# Token-bucket rate limiter (capacity invariant)

*Subject area: Reliability / Rate Limiting. Language: python. Vendorable bundle `7d2a1a4e8b23`.*

A token bucket is the classic rate-limiting primitive: a bucket holds up to `capacity` tokens and refills at a steady `refill_per_sec`, and each request spends tokens, so short bursts pass (up to the bucket depth) while the long-run average rate stays bounded. Its key safety property is that refills are clamped at capacity, so accumulated idle time can never be banked into an unbounded later burst. This module makes time an explicit argument to every call, which removes hidden wall-clock reads and makes limiter behaviour fully deterministic and testable. Vendor it to meter API quotas or traffic consistently and inherit a checked capacity invariant rather than re-auditing another ad-hoc limiter.

## Claim

<!-- claim:CLAIM-LIB-TOKENBUCKET-001 capacity_violations -->
The vendored token-bucket rate limiter enforces its capacity invariant with 0 capacity_violations across a fixed 8-event chronological trace: the number of available tokens is clamped to capacity on every refill, so even a long idle gap (t=10s, which would otherwise bank 8 tokens) never grants more than a full bucket's burst (measured allowed=6, denied=2). Verified value: <!-- v:CLAIM-LIB-TOKENBUCKET-001.capacity_violations -->**0**
(`capacity_violations`), backed by [`modules/tokenbucket/artifacts/tokenbucket.json`](../modules/tokenbucket/artifacts/tokenbucket.json).

## Vendor it

Ships `tokenbucket.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/7d2a1a4e8b2347943b963700e220e88772e86aa2beea1a9701e07f244dbbc1b2 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **RFC 2697** — A Single Rate Three Color Marker. [https://www.rfc-editor.org/info/rfc2697](https://www.rfc-editor.org/info/rfc2697)
