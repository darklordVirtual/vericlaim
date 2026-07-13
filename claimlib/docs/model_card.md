# Model-card completeness (Mitchell et al. 2019)

*Subject area: AI Governance / Model Documentation. Language: python. Vendorable bundle `90faaf9a9d4b`.*

Model cards are the disclosure document of record for trained models: Mitchell et al. proposed nine sections covering what the model is, what it is for, how it behaves across factors, and what it must not be used for. Enterprise AI inventories increasingly REQUIRE a card per deployed model, which makes 'is the card structurally complete' a governance gate worth automating. This module scores exactly that, fail-closed on typoed section names; the claim proves the taxonomy matches the paper and the arithmetic is exact, so a review pipeline inherits a checked completeness gate.

## Claim

<!-- claim:CLAIM-LIB-MODEL-CARD-001 checks_matched -->
The vendored model-card library passes all 8 checks with 0 mismatches: the encoded section taxonomy matches the nine sections of Mitchell et al.'s FAT* 2019 paper verbatim (Model Details through Caveats and Recommendations), and completeness scoring is Fraction-exact on full, empty and partial cards — whitespace-only sections count as empty and unknown section names fail closed rather than silently scoring as gaps. Verified value: <!-- v:CLAIM-LIB-MODEL-CARD-001.checks_matched -->**8**
(`checks_matched`), backed by [`modules/model_card/artifacts/model_card.json`](../modules/model_card/artifacts/model_card.json).

## Vendor it

Ships `model_card.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/90faaf9a9d4bef1b183157761e0dbcd8111964d3cb506fa13b4165761903b133 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **doi:10.1145/3287560.3287596; FAT* '19 pp. 220-229; arXiv:1810.03993** — Model Cards for Model Reporting. [https://doi.org/10.1145/3287560.3287596](https://doi.org/10.1145/3287560.3287596)
