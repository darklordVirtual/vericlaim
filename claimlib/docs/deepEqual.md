# deepEqual structural deep equality

*Subject area: TypeScript / Data Comparison. Language: typescript. Vendorable bundle `092ea5185c8a`.*

Deep equality compares two values by structure rather than by reference: two distinct objects are equal when their contents match recursively, unlike the === operator which only reports reference identity for objects. The subtle edges are the ones JavaScript gets 'wrong' by default -- NaN !== NaN (so a structural comparator must special-case it to true), Dates and arrays need element/timestamp comparison, and an explicit `{a: undefined}` must stay distinct from `{}`. Vendor it for test assertions, memoization/change-detection, and cache-key checks; the claim proves the comparator handles these edges as specified, so you inherit a checked primitive rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-DEEPEQUAL-001 correct -->
The vendored TypeScript deepEqual(a, b) structural equality function returns the expected boolean on every one of a fixed 42-row reference battery whose expected values are hand-written independently of the module (correct = n_cases = 42, errors = 0), covering primitives, NaN-equals-NaN, null-distinct-from-undefined, arrays (length + element-wise), plain objects (identical key-set + recursive values, key-order irrelevant, undefined-value-vs-absent-key distinct), Date-by-getTime, and differing-type mismatches. Verified value: <!-- v:CLAIM-LIB-DEEPEQUAL-001.correct -->**42**
(`correct`), backed by [`ts/deepEqual/artifacts/deepEqual.json`](../ts/deepEqual/artifacts/deepEqual.json).

## Vendor it

Ships `deepEqual.ts` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/092ea5185c8ab0d840837489e3b7f538c217487f6a548ae5f2a19e5d03b7107c --target .
```
