# NIST AI RMF 1.0 Core taxonomy + coverage

*Subject area: AI Governance / NIST AI RMF. Language: python. Vendorable bundle `bd7e0505df5a`.*

NIST's AI Risk Management Framework is the de facto shared vocabulary for enterprise AI governance programmes: GOVERN builds the organizational structures, MAP contextualizes systems and risks, MEASURE quantifies them, MANAGE acts — 19 categories and 72 subcategories articulating seven characteristics of trustworthy AI. A maturity assessment is at bottom a coverage map over that taxonomy. This module encodes the verified Core with exact coverage scoring; the claim proves the counts match the published framework, so an assessment tool inherits a checked skeleton.

## Claim

<!-- claim:CLAIM-LIB-AI-RMF-001 checks_matched -->
The vendored AI RMF library passes all 18 checks with 0 mismatches: the encoded Core matches NIST AI 100-1 — four functions (GOVERN, MAP, MEASURE, MANAGE) with published category counts 6/5/4/4 totalling 19 and subcategory counts 19/18/22/13 totalling 72, plus the seven characteristics of trustworthy AI — and per-function coverage on three fixed programmes matches exact Fraction arithmetic. Verified value: <!-- v:CLAIM-LIB-AI-RMF-001.checks_matched -->**18**
(`checks_matched`), backed by [`modules/nist_ai_rmf/artifacts/nist_ai_rmf.json`](../modules/nist_ai_rmf/artifacts/nist_ai_rmf.json).

## Vendor it

Ships `nist_ai_rmf.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/bd7e0505df5a7f21e8fd0f847d9c4f608673853e597349e2dc96d9f62db5e4ee --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **NIST AI 100-1; DOI 10.6028/NIST.AI.100-1** — Artificial Intelligence Risk Management Framework (AI RMF 1.0). [https://doi.org/10.6028/NIST.AI.100-1](https://doi.org/10.6028/NIST.AI.100-1)
