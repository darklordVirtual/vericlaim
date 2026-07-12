# chunk array into fixed-size groups

*Subject area: TypeScript / Array Utilities. Language: typescript. Vendorable bundle `f1c3964d1de0`.*

Chunking splits a flat list into fixed-size batches — the standard primitive behind paginating results, batching API/database writes, and laying items into grid rows. chunk(arr, size) walks the array in strides of `size`, slicing each window, so the final batch is shorter whenever the length is not a multiple of the size, and an empty input yields no chunks. A size below 1 has no sensible meaning (and a naive loop would never advance), so it fails closed with a RangeError. Vendor it to get dependency-free, off-by-one-checked batching instead of re-deriving slice math in every project.

## Claim

<!-- claim:CLAIM-LIB-CHUNK-001 correct -->
The vendored TypeScript chunk<T>(arr, size) partitions an array into consecutive fixed-size sub-arrays (final chunk shorter when length is not an exact multiple) and produces the expected partition on every one of a fixed 8-case reference battery whose expected outputs are hand-written independently of the module (correct = n_cases = 8, errors = 0), including the spec examples chunk([1..7],3)->[[1,2,3],[4,5,6],[7]] and chunk([],3)->[]; it also rejects all 4 invalid sizes (0, -1, -5, 1.5) with a RangeError (invalid_inputs_rejected = 4). Verified value: <!-- v:CLAIM-LIB-CHUNK-001.correct -->**8**
(`correct`), backed by [`ts/chunk/artifacts/chunk.json`](../ts/chunk/artifacts/chunk.json).

## Vendor it

Ships `chunk.ts` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/f1c3964d1de02298057f17d8733bf3b2af0530e75a7853c90bbec5d5edc898d1 --target .
```
