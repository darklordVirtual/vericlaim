# Group-fairness metrics (parity, four-fifths, equalized odds)

*Subject area: AI Governance / Fairness Metrics. Language: python. Vendorable bundle `b09e9a3a5424`.*

When an enterprise audits a model for disparate treatment, three measurements carry most reviews: demographic parity (do groups get selected at the same rate), the EEOC four-fifths rule (is the lowest selection rate at least 4/5 of the highest — the classic adverse-impact screen Feldman et al. formalized), and Hardt et al.'s equalized odds (are true- and false-positive rates equal across groups). This module computes all three from per-group confusion counts in exact rational arithmetic; the claim proves the arithmetic and the defining properties, so an audit inherits checked numbers rather than a spreadsheet to re-derive.

## Claim

<!-- claim:CLAIM-LIB-FAIRNESS-001 checks_matched -->
The vendored fairness library passes all 73 checks as exact Fraction equalities with 0 mismatches: 10 hand-computed values on a fixed two-group audit (demographic-parity difference exactly 1/4, disparate-impact ratio exactly 1/2 failing the four-fifths rule, equalized-odds difference exactly 2/5), 60 property checks over a deterministic battery (relabel-invariance, [0,1] bounds, zeros on identical groups), the perfect-classifier equalized-odds zero, and the exact 4/5 threshold boundary. Verified value: <!-- v:CLAIM-LIB-FAIRNESS-001.checks_matched -->**73**
(`checks_matched`), backed by [`modules/fairness_metrics/artifacts/fairness_metrics.json`](../modules/fairness_metrics/artifacts/fairness_metrics.json).

## Vendor it

Ships `fairness_metrics.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/b09e9a3a5424f2f6aa05a8cd872f5a5b3deb8927b27429460f90a957c6d9c677 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **NIPS 2016, pp. 3315-3323; arXiv:1610.02413** — Equality of Opportunity in Supervised Learning. [https://papers.nips.cc/paper/6374-equality-of-opportunity-in-supervised-learning](https://papers.nips.cc/paper/6374-equality-of-opportunity-in-supervised-learning)
- **doi:10.1145/2783258.2783311; KDD '15 pp. 259-268; arXiv:1412.3756** — Certifying and Removing Disparate Impact. [https://doi.org/10.1145/2783258.2783311](https://doi.org/10.1145/2783258.2783311)
