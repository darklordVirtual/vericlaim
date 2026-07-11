# Fixed-capacity LRU cache

*Subject area: Data Structures / Caching. Language: python. Vendorable bundle `eccbff55d1cb`.*

An LRU cache bounds memory by keeping at most `capacity` entries and, when full, evicting the key that has gone longest without being read or written -- the workhorse policy behind page caches, HTTP/object caches, and memoization tables. The classic O(1) implementation pairs a hash map with a recency-ordered linked list so both lookup and eviction are constant time; this module uses Python's `collections.OrderedDict` (move_to_end / popitem) to get the same behaviour in pure stdlib. Vendor it to add a checked, dependency-free cache; the claim proves the recency and eviction semantics match hand-derived reference traces, so you inherit a checked data structure rather than a re-implementation with an off-by-one eviction bug to re-audit.

## Claim

<!-- claim:CLAIM-LIB-LRU-001 operations_correct -->
The vendored fixed-capacity LRU cache reproduces the correct behaviour on every operation of two hand-traced batteries (a capacity-3 mixed trace exercising hit-refresh, capacity eviction, and update-in-place, plus the canonical LeetCode-146 capacity-2 example): all 21 operations match their independently hand-computed get-results AND post-operation key sets (operations_correct = 21, mismatches = 0), and the cache size never exceeds capacity at any step. Verified value: <!-- v:CLAIM-LIB-LRU-001.operations_correct -->**21**
(`operations_correct`), backed by [`modules/lru/artifacts/lru.json`](../modules/lru/artifacts/lru.json).

## Vendor it

Ships `lru.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/eccbff55d1cb178a186e28e9eb1e9a784d94777d5103563d289640535688dd18 --target .
```
