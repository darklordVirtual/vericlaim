# CVSS v3.1 base scoring

*Subject area: Security / Vulnerability Management. Language: python. Vendorable bundle `5918c26d6785`.*

CVSS v3.1 turns an attack vector, complexity, privileges, user interaction, scope and CIA impact into a 0.0-10.0 base score. This module parses the standard `CVSS:3.1/...` vector string and applies the published FIRST formula (impact, exploitability, scope, Roundup). Vendor it to score vulnerabilities consistently; the claim proves the arithmetic matches the reference, so you inherit a checked scorer, not a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-CVSS-001 reference_vectors_matched -->
The vendored CVSS v3.1 base-score scorer reproduces all published reference base scores in a fixed set exactly, with 0 mismatches — including scope change and the v3.1 Roundup rule. Verified value: <!-- v:CLAIM-LIB-CVSS-001.reference_vectors_matched -->**9**
(`reference_vectors_matched`), backed by [`modules/cvss/artifacts/cvss.json`](../modules/cvss/artifacts/cvss.json).

## Vendor it

Ships `cvss.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/5918c26d678535d8ba556617b9dafb724d09ca635c9f0b34c7aa86eac5bb2916 --target .
```
