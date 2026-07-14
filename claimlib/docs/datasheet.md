# Datasheets for Datasets completeness scoring

*Subject area: AI Governance / Data Documentation. Language: python. Vendorable bundle `7aabf38204ce`.*

Datasheets for Datasets (Gebru et al., CACM 2021; arXiv 2018) document the dataset a model learns from, the way a model card documents the model: seven groups of questions along the dataset lifecycle — Motivation, Composition, Collection Process, Preprocessing/cleaning/labeling, Uses, Distribution, Maintenance — with the explicit provision that some questions may be answered 'not applicable' with justification. This module encodes that taxonomy and the justified-N/A escape hatch, scoring coverage exactly; the claim proves the count over all 3**7 section states by exhaustive enumeration, so a data-governance pipeline inherits a checked completeness gate rather than an ad-hoc checklist.

## Claim

<!-- claim:CLAIM-LIB-DATASHEET-001 checks_matched -->
The vendored datasheet completeness scorer passes all 2193 checks with 0 mismatches: the covered count and exact completeness percentage match an INDEPENDENT direct count over ALL 2187 (= 3**7) assignments of {answered, justified-N/A, gap} to the seven lifecycle sections (Motivation, Composition, Collection Process, Preprocessing/cleaning/labeling, Uses, Distribution, Maintenance), and 6 escape-hatch anchors pin the datasheet's own rule that a section marked 'not applicable' WITH a justification counts as covered while a bare unjustified N/A or an empty answer is a gap; 4/4 malformed inputs (unknown section, non-str value, N/A without the na flag) are rejected. Verified value: <!-- v:CLAIM-LIB-DATASHEET-001.checks_matched -->**2193**
(`checks_matched`), backed by [`modules/datasheet/artifacts/datasheet.json`](../modules/datasheet/artifacts/datasheet.json).

## Vendor it

Ships `datasheet.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/7aabf38204ce3c3c325873dbb5dcb93839c073920ce4dafd24c54c9d42529199 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **arXiv:1803.09010; Commun. ACM 64(12):86-92** — Datasheets for Datasets. [https://arxiv.org/abs/1803.09010](https://arxiv.org/abs/1803.09010)
- **doi:10.1145/3287560.3287596; FAT* '19 pp. 220-229; arXiv:1810.03993** — Model Cards for Model Reporting. [https://doi.org/10.1145/3287560.3287596](https://doi.org/10.1145/3287560.3287596)
