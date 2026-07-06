# Domain: Evidence Graph

Model a claim register as a directed graph — claims, artifacts, literature and
docs are nodes; **binds**, **backed_by**, **cites** are edges — and check
integrity properties a flat list cannot express (orphan claims, deepest
evidence chain).

- `src/evidence_graph.py` — graph builder + integrity queries.
- `data/sample_claims.json` — the committed fixture it runs on.
- `evidence.py` — writes `artifacts/graph.json`. `docs/results.md` — gate-bound.

Reproduce: `python3 domains/evidence_graph/evidence.py` ·
Claim: `CLAIM-GRAPH-001` · Evidence level: `measured`.
