# cx classnames combiner

*Subject area: TypeScript / UI Utilities. Language: typescript. Vendorable bundle `6a34517aaaab`.*

A classnames combiner assembles the `class` attribute for a component from a mix of static strings and conditional flags, so you write cx("btn", { active: isActive }, isLarge && "btn-lg") instead of hand-splicing strings and stray spaces. This is the ubiquitous `classnames`/`clsx` pattern: truthy tokens are joined with single spaces and every falsy value is dropped, with nested arrays flattened and object keys included only when their value is truthy. Vendor it to get dependency-free conditional class composition in TypeScript; the claim proves the join/skip/flatten behaviour matches hand-written expected strings, so you inherit a checked utility rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-CX-001 correct -->
The vendored TypeScript cx classnames combiner produces the expected space-separated string on every one of a fixed 14-case reference battery whose expected outputs are hand-written literals independent of the module (correct = n_cases = 14, errors = 0), covering strings, numbers (nonzero kept, 0/NaN dropped), recursively flattened arrays, { className: boolean } objects (truthy keys only), skipped falsy inputs, preserved document order, and preserved duplicates. Verified value: <!-- v:CLAIM-LIB-CX-001.correct -->**14**
(`correct`), backed by [`ts/cx/artifacts/cx.json`](../ts/cx/artifacts/cx.json).

## Vendor it

Ships `cx.ts` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/6a34517aaaab4faf10ffd648bbca5633ab0f58997d11033486f8015dba24c0bc --target .
```
