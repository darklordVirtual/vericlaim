# GSN assurance-case structure validation

*Subject area: AI Assurance / Safety Cases. Language: python. Vendorable bundle `4796000bd256`.*

Safety and assurance cases — increasingly demanded for AI systems (Clymer et al. 2024) — are written in Goal Structuring Notation: goals decompose via strategies down to solutions (evidence), with context, assumptions and justifications attached. A circular argument, a dangling goal, or evidence in the wrong place invalidates the case before anyone reads the prose, and exactly that is machine-checkable. This module validates GSN structure fail-closed; the claim proves every rule via mutation testing and exhaustive edge-type enumeration, so an assurance workflow inherits a checked case linter.

## Claim

<!-- claim:CLAIM-LIB-GSN-001 checks_matched -->
The vendored GSN validator passes all 50 checks with 0 mismatches: a fixed exemplar exercising every legal edge type of the GSN Community Standard v3 validates clean, an honestly-undeveloped case validates, every one of 12 adversarial single mutations is caught (mutations_missed = 0 — illegal edge types in both relations, a circular argument, an unsupported goal, an undeveloped-with-support contradiction, a solution with outgoing edges, a disconnected argument island, a rootless cycle), and the exhaustive 36-pair supported_by enumeration admits exactly the standard's 4 legal pairs. Verified value: <!-- v:CLAIM-LIB-GSN-001.checks_matched -->**50**
(`checks_matched`), backed by [`modules/gsn_case/artifacts/gsn_case.json`](../modules/gsn_case/artifacts/gsn_case.json).

## Vendor it

Ships `gsn_case.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/4796000bd256ef7ac4d03ad6044bb8a189cbe608cd9035c21a8fd53fb81c01ce --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **SCSC-141C** — Goal Structuring Notation Community Standard, Version 3 (SCSC-141C). [https://scsc.uk/scsc-141c](https://scsc.uk/scsc-141c)
- **arXiv:2403.10462** — Safety Cases: How to Justify the Safety of Advanced AI Systems. [https://arxiv.org/abs/2403.10462](https://arxiv.org/abs/2403.10462)
