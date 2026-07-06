# Domain: Domain Ontologies

A machine-readable ontology for claims — an ordered evidence ladder plus claim
types with explicit classification rules — and a validator that a register
conforms (known level + exactly one type per claim).

- `src/ontology.py` — the ontology + classifier + validator.
- `data/sample_register.json` — the committed fixture it validates.
- `evidence.py` — writes `artifacts/ontology_conformance.json`. `docs/results.md` — gate-bound.

Reproduce: `python3 domains/ontologies/evidence.py` ·
Claim: `CLAIM-ONTO-001` · Evidence level: `measured`.

The taxonomy is a proposal, not a standard.
