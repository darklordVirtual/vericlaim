# Apdex application performance index

*Subject area: Observability / Service Level Indicators. Language: python. Vendorable bundle `215b6e4f3147`.*

Apdex (Application Performance Index) turns a pile of response-time samples into one 0..1 satisfaction score against a target time T: requests at or under T are 'satisfied', up to 4T 'tolerating' (counted half), and beyond that 'frustrated'. It is a compact SLI that product and ops teams can track and alert on without staring at a full histogram. This module implements the zoning and scoring exactly; the claim proves it matches the published definition on a hand-computed battery, so you inherit a checked SLI rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-APDEX-001 correct -->
The vendored Apdex calculator reproduces a fixed 5-case hand-computed reference battery exactly (correct = 5, errors = 0), including the all-satisfied (1.0) and all-frustrated (0.0) extremes and the zone boundaries (a sample exactly at T is satisfied, exactly at 4T is tolerating), and it classifies all 4 zone-boundary probes correctly -- computing Apdex_T = (satisfied + tolerating/2) / total with satisfied <= T, tolerating in (T, 4T], frustrated > 4T. Verified value: <!-- v:CLAIM-LIB-APDEX-001.correct -->**5**
(`correct`), backed by [`modules/apdex/artifacts/apdex.json`](../modules/apdex/artifacts/apdex.json).

## Vendor it

Ships `apdex.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/215b6e4f3147679a818b1ba244f3c112ab044ff27a6abb126550ec2e6c6e69bb --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **Apdex Technical Specification, Version 1.1 (22 January 2007)** — Application Performance Index — Apdex Technical Specification. [https://www.apdex.org/wp-content/uploads/2020/09/ApdexTechnicalSpecificationV11_000.pdf](https://www.apdex.org/wp-content/uploads/2020/09/ApdexTechnicalSpecificationV11_000.pdf)
