# groupBy array partition (order-preserving)

*Subject area: TypeScript / Collections. Language: typescript. Vendorable bundle `cb31bbbbe454`.*

groupBy is the workhorse collection primitive for turning a flat list into buckets keyed by a projection — the SQL GROUP BY of everyday code, used for tallies, indexes, and report rollups. The subtle correctness properties are stability (items must stay in input order within a bucket) and safety against a data-driven "__proto__" key, which naive plain-object implementations mishandle by mutating the prototype chain. This module accumulates in a Map (safe for every string key, order-preserving) and materialises the result with defineProperty, so it is both stable and pollution-safe; vendor it to inherit a checked partitioner rather than re-auditing another hand-rolled reduce.

## Claim

<!-- claim:CLAIM-LIB-GROUPBY-001 correct -->
The vendored TypeScript groupBy(items, key) partitions an array into a Record<string, T[]> and produces the expected record on every one of a fixed 10-case reference battery whose expected records are hand-written independently of the module (correct = 10, errors = 0): buckets appear in first-seen key order and items keep their original input order within each bucket, covering parity/first-letter/object-field grouping, empty and singleton inputs, numeric-key coercion, and a data-driven "__proto__" key that becomes an ordinary own bucket with no prototype pollution. Verified value: <!-- v:CLAIM-LIB-GROUPBY-001.correct -->**10**
(`correct`), backed by [`ts/groupBy/artifacts/groupBy.json`](../ts/groupBy/artifacts/groupBy.json).

## Vendor it

Ships `groupBy.ts` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/cb31bbbbe4549e2552baec77aa237ba7622c98304957688f3f58286ea20f33fe --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **ECMA-262, 15th edition (June 2024)** — ECMAScript® 2024 Language Specification. [https://262.ecma-international.org/15.0/](https://262.ecma-international.org/15.0/)
