# Result<T, E> typed error handling

*Subject area: TypeScript / Error Handling. Language: typescript. Vendorable bundle `da35fc79cb2d`.*

Result<T, E> makes failure a value instead of a thrown exception: a function returns Ok<T> on success or Err<E> on failure, and the caller must handle both branches before reaching the value. Combinators (map, mapErr, andThen) thread the happy path and short-circuit on the first error, the way Rust's Result or fp-ts's Either do. Vendor it to get exhaustive, type-checked error handling in TypeScript with zero dependencies; the claim proves the combinators behave as specified, so you inherit a checked primitive rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-RESULT-001 correct -->
The vendored TypeScript Result<T, E> combinators (ok, err, map, mapErr, andThen, unwrapOr, isOk, isErr, fromThrowing) produce the expected outcome on every one of a fixed reference battery whose expected values are written independently of the module (correct = n_cases, errors = 0), covering ok/err propagation, monadic short-circuiting, and throw capture. Verified value: <!-- v:CLAIM-LIB-RESULT-001.correct -->**12**
(`correct`), backed by [`ts/result/artifacts/result.json`](../ts/result/artifacts/result.json).

## Vendor it

Ships `result.ts` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/da35fc79cb2d7327dd87d8a7a14be2d62504493431b92c9e4c31932b98d88283 --target .
```
