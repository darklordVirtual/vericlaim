# Domain Ontologies — Results

A **conformance claim**: define a machine-readable ontology for claims (an
ordered evidence ladder + a set of claim types with explicit classification
rules) and validate that a register conforms — every level known, every claim
typed by exactly one rule.

<!-- claim:CLAIM-ONTO-001 n_levels -->
The ontology defines **6** ordered evidence levels

<!-- claim:CLAIM-ONTO-001 n_claim_types -->
and **5** claim types (theorem, correctness, capability, benchmark, roadmap).

<!-- claim:CLAIM-ONTO-001 nonconforming -->
Validated over a 6-claim fixture: **0** non-conforming claims — every claim has
a known level and classifies into exactly one type.

Artifact: [`../artifacts/ontology_conformance.json`](../artifacts/ontology_conformance.json) ·
Reproduce: `python3 domains/ontologies/evidence.py`

> Scope: the taxonomy is a proposal, not a standard, and conformance is checked
> over `data/sample_register.json`. It demonstrates ontology-driven validation,
> not that this particular vocabulary is canonical.
