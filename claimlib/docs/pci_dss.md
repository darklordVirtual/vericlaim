# PCI DSS v4.0 coverage

*Subject area: Compliance / Audit Frameworks. Language: python. Vendorable bundle `5e70171b38c3`.*

PCI DSS governs any organization that handles payment card data; version 4.0 keeps the familiar twelve requirements under six goals, from 'build and maintain a secure network' to 'maintain an information security policy'. Merchants and service providers track which requirements they meet to scope and prepare for assessment. This module encodes the requirements and their goal grouping and computes coverage; the claim proves the encoded structure matches the standard and the math is correct, so you inherit a checked coverage model rather than a spreadsheet to re-audit.

## Claim

<!-- claim:CLAIM-LIB-PCI-DSS-001 checks_matched -->
The vendored PCI DSS v4.0 coverage model matches the standard and arithmetic on all 20 checks with 0 mismatches: the six goals and twelve requirements are present, each requirement maps to the correct goal (1-2 under goal 1, 3-4 under 2, 5-6 under 3, 7-9 under 4, 10-11 under 5, 12 under 6), and coverage() computes hand-verified per-goal and overall fractions. Verified value: <!-- v:CLAIM-LIB-PCI-DSS-001.checks_matched -->**20**
(`checks_matched`), backed by [`modules/pci_dss/artifacts/pci_dss.json`](../modules/pci_dss/artifacts/pci_dss.json).

## Vendor it

Ships `pci_dss.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/5e70171b38c355ee071792ed41194f83e24d305ad6832d3daf3b4b7f8733ac38 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **PCI DSS v4.0** — Payment Card Industry Data Security Standard, Version 4.0. [https://www.pcisecuritystandards.org/document_library/](https://www.pcisecuritystandards.org/document_library/)
