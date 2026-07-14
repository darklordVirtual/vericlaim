# Result<T, E> typed error handling

*Subject area: TypeScript / Error Handling. Language: typescript. Vendorable bundle `02013500e053`.*

Result<T, E> makes failure a value instead of a thrown exception: a function returns Ok<T> on success or Err<E> on failure, and the caller must handle both branches before reaching the value. Combinators (map, mapErr, andThen) thread the happy path and short-circuit on the first error, the way Rust's Result or fp-ts's Either do. Vendor it to get exhaustive, type-checked error handling in TypeScript with zero dependencies; the claim proves the combinators behave as specified, so you inherit a checked primitive rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-RESULT-001 correct -->
The vendored TypeScript Result<T, E> combinators (ok, err, map, mapErr, andThen, unwrapOr, isOk, isErr, fromThrowing) produce the expected outcome on every one of a fixed reference battery whose expected values are written independently of the module (correct = n_cases, errors = 0), covering ok/err propagation, monadic short-circuiting, and throw capture. Verified value: <!-- v:CLAIM-LIB-RESULT-001.correct -->**12**
(`correct`), backed by [`ts/result/artifacts/result.json`](../ts/result/artifacts/result.json).

## Vendor it

Ships `result.ts` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/02013500e0534d86e568ff1ca361f938cdc53308c4f5a4da0dfd94f5bc805ea2 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **Advanced Functional Programming (J. Jeuring & E. Meijer, eds.), LNCS 925:24-52, doi:10.1007/3-540-59451-5_2** — Monads for functional programming. [https://doi.org/10.1007/3-540-59451-5_2](https://doi.org/10.1007/3-540-59451-5_2)
