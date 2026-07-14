# PROV-DM core provenance-graph validation

*Subject area: AI Assurance / Provenance. Language: python. Vendorable bundle `16229465a563`.*

W3C PROV-DM is the standard vocabulary for provenance: entities (a model file, a dataset), activities (a training run), agents (a team, a service), connected by seven typed relations — used, wasGeneratedBy, wasDerivedFrom, wasAttributedTo and the rest. AI supply chains need exactly this graph: which dataset trained which model, evaluated by which run, attributed to whom. This module validates PROV core documents fail-closed, including cycle detection on derivation and delegation; the claim proves the taxonomy against the Recommendation and the rules by exhaustive enumeration, so a provenance pipeline inherits a checked validator.

## Claim

<!-- claim:CLAIM-LIB-PROV-001 checks_matched -->
The vendored PROV-DM validator passes all 77 checks with 0 mismatches: the encoded core matches the W3C Recommendation exactly — three types (entity, activity, agent) and exactly seven relations with their published signatures, Start/End correctly absent as expanded structures — an ML-pipeline exemplar (dataset -> training -> model -> evaluation with attribution and delegation) validates clean, ALL 63 (relation x subject-type x object-type) combinations are classified with exactly the 7 published signatures passing, every one of 8 corruptions (swapped endpoints, wrong types, unknown relation/id, derivation and delegation cycles, self-derivation) is caught, and diamond-shaped derivation DAGs pass. Verified value: <!-- v:CLAIM-LIB-PROV-001.checks_matched -->**77**
(`checks_matched`), backed by [`modules/prov_dm/artifacts/prov_dm.json`](../modules/prov_dm/artifacts/prov_dm.json).

## Vendor it

Ships `prov_dm.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/16229465a563a6d867da551047af5e4b9302860715c8e783f1282a96f5ba0e96 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **W3C Recommendation REC-prov-dm-20130430** — PROV-DM: The PROV Data Model. [https://www.w3.org/TR/2013/REC-prov-dm-20130430/](https://www.w3.org/TR/2013/REC-prov-dm-20130430/)
