# Apdex application performance index

*Subject area: Observability / Service Level Indicators. Language: python. Vendorable bundle `975b6923ee5d`.*

Apdex (Application Performance Index) turns a pile of response-time samples into one 0..1 satisfaction score against a target time T: requests at or under T are 'satisfied', up to 4T 'tolerating' (counted half), and beyond that 'frustrated'. It is a compact SLI that product and ops teams can track and alert on without staring at a full histogram. This module implements the zoning and scoring exactly; the claim proves it matches the published definition on a hand-computed battery, so you inherit a checked SLI rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-APDEX-001 correct -->
The vendored Apdex calculator reproduces a fixed 5-case hand-computed reference battery exactly (correct = 5, errors = 0), including the all-satisfied (1.0) and all-frustrated (0.0) extremes and the zone boundaries (a sample exactly at T is satisfied, exactly at 4T is tolerating), and it classifies all 4 zone-boundary probes correctly -- computing Apdex_T = (satisfied + tolerating/2) / total with satisfied <= T, tolerating in (T, 4T], frustrated > 4T. Verified value: <!-- v:CLAIM-LIB-APDEX-001.correct -->**5**
(`correct`), backed by [`modules/apdex/artifacts/apdex.json`](../modules/apdex/artifacts/apdex.json).

## Vendor it

Ships `apdex.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/975b6923ee5da0047dda77447827fe382c48b1275e38b41103173f8f4c7675f8 --target .
```
