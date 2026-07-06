# Evidence Graph — Results

A **structural claim**: model the register as a graph (claims, artifacts,
literature, docs; edges bind/back/cite) and check integrity properties a flat
list cannot express. Computed over a committed fixture, so the artifact is
byte-stable.

<!-- claim:CLAIM-GRAPH-001 n_nodes -->
The evidence graph has **18** nodes

<!-- claim:CLAIM-GRAPH-001 n_edges -->
and **15** edges across 6 claims.

<!-- claim:CLAIM-GRAPH-001 orphan_claims -->
Integrity check: **0** orphan claims — every claim is backed by at least one
artifact (a claim bound in a doc but backed by nothing is exactly the failure
this graph surfaces).

Artifact: [`../artifacts/graph.json`](../artifacts/graph.json) ·
Reproduce: `python3 domains/evidence_graph/evidence.py`

> Scope: built over `data/sample_claims.json`, not the live register, so the
> numbers stay stable. The same builder runs on a real register exported to the
> same node/edge shape.
