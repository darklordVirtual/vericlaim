# formatDuration compact duration formatter

*Subject area: TypeScript / Formatting. Language: typescript. Vendorable bundle `47ef3bd64b73`.*

A compact duration formatter turns a raw millisecond count into a short human-readable string for logs, dashboards and UIs. formatDuration decomposes the value into days (86400s), hours (3600s), minutes (60s) and seconds, then drops zero-valued units so only the significant magnitudes show (with the whole-value 0 special-cased to "0s"), floors sub-second remainders, and rejects negative or non-finite input with a RangeError. Vendor it for consistent, dependency-free duration display; the claim proves the output matches an independent reference table, so you inherit a checked formatter rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-FORMATDURATION-001 correct -->
The vendored TypeScript formatDuration(ms) renders a compact human-readable duration matching a hand-written reference table on every one of a fixed 21-case battery whose expected strings are computed independently of the module (correct = 21, errors = 0): it drops zero-valued units, renders the value 0 as "0s", truncates sub-second remainders to whole seconds, composes d/h/m/s (e.g. 90061000ms -> "1d 1h 1m 1s"), and throws RangeError on negative and non-finite input. Verified value: <!-- v:CLAIM-LIB-FORMATDURATION-001.correct -->**21**
(`correct`), backed by [`ts/formatDuration/artifacts/formatDuration.json`](../ts/formatDuration/artifacts/formatDuration.json).

## Vendor it

Ships `formatDuration.ts` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/47ef3bd64b73a40b743c0f46352d07ef1f8cbd062b264960dca26d9e1526ee59 --target .
```
