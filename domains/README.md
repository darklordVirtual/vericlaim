# Applied domain modules

Larger, self-contained modules than [`../examples/`](../examples/) — each a real,
deterministic, `reproduce`-backed artifact that demonstrates a technique and is
bound to the claim register like everything else in this repo. Stdlib-only, no
network.

| Module | Demonstrates | Claim | Level |
|--------|--------------|-------|-------|
| [`eval_harness/`](eval_harness/) | grounding P/R/F1 + refusal accuracy scorer for cited-answer systems | `CLAIM-EVAL-001` | benchmarked |
| [`evidence_graph/`](evidence_graph/) | register-as-a-graph integrity (orphan claims, evidence depth) | `CLAIM-GRAPH-001` | measured |
| [`multitenant/`](multitenant/) | tenant-isolation invariant (no cross-tenant reads, no ledger interleave) | `CLAIM-TENANT-001` | benchmarked |
| [`ontologies/`](ontologies/) | machine-readable claim ontology + register conformance | `CLAIM-ONTO-001` | measured |
| [`cost_routing/`](cost_routing/) | cost-aware model routing under per-request quality floors | `CLAIM-ROUTE-001` | benchmarked |

Each module is the same shape as an example: `src/` (the logic), `evidence.py`
(deterministic, writes `artifacts/*.json` + provenance), `docs/results.md`
(gate-bound), and property tests under [`../tests/`](../tests/).

Regenerate all five and verify they still hold:

```bash
for m in eval_harness evidence_graph multitenant ontologies cost_routing; do
  python3 domains/$m/evidence.py
done
python3 -m vericlaim reproduce   # re-runs each and checks the artifact is unchanged
```

**Scope / honesty:** the gold sets, fixtures, price tables and quality scores
are synthetic and fixed. The numbers grade the *method* (the scorer, the graph
builder, the isolation logic, the validator, the router) — not any live model,
tenant, or price. Each `docs/results.md` states its own caveat.
