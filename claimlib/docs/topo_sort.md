# Topological sort + cycle detection

*Subject area: General / Graph Algorithms. Language: python. Vendorable bundle `1bc3e6cfee7e`.*

A topological sort orders a directed acyclic graph so every dependency comes before whatever depends on it -- the primitive behind build systems, task schedulers, database migration ordering, and package resolution. Kahn's algorithm repeatedly emits a node with no remaining incoming edges; if any node never reaches in-degree zero, the graph has a cycle and no order exists. This module emits ready nodes smallest-first for a deterministic result and fails closed on a cycle; the claim proves every output respects all edges and every cycle is caught, so you inherit a checked ordering primitive rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-TOPOSORT-001 valid_orderings -->
The vendored topological sort (Kahn's algorithm, deterministic smallest-first tie-break) produces an edge-respecting order for every one of a fixed 6-DAG battery (valid_orderings = 6, invalid_orderings = 0) -- each order contains every node exactly once and places the tail of every edge before its head -- and detects every one of 4 cyclic graphs (self-loop, 2-cycle, 3-cycle, embedded cycle), with has_cycle True and topo_sort raising CycleError. Verified value: <!-- v:CLAIM-LIB-TOPOSORT-001.valid_orderings -->**6**
(`valid_orderings`), backed by [`modules/topo_sort/artifacts/topo_sort.json`](../modules/topo_sort/artifacts/topo_sort.json).

## Vendor it

Ships `topo_sort.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/1bc3e6cfee7eb05df25cf15d270cfa62dd6be7217eec97d01613667a3bf23997 --target .
```
