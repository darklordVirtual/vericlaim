# SLO / error-budget arithmetic

*Subject area: SRE / Reliability Engineering. Language: python. Vendorable bundle `2990416cb259`.*

Site Reliability Engineering measures a service against a Service Level Objective (SLO) — e.g. 99.9% availability over 30 days. The complement of the SLO is the error budget: the amount of downtime the target permits over the window (budget = window * (1 - SLO/100)). Teams spend that budget on risk — releases, experiments, incidents — and 'budget remaining' tracks how much allowance is left before the SLO is breached, going negative once overspent. Vendor this module to compute availability and error budgets consistently; the claim proves the arithmetic matches the published formulas, so you inherit a checked calculator rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-ERRORBUDGET-001 correct -->
The vendored SLO / error-budget calculator reproduces the textbook SRE availability, error-budget, and budget-remaining formulas exactly on every one of a fixed 9-row hand-computed reference battery (correct = 9, errors = 0), including budget-exhaustion, overspend (negative remaining), zero-downtime, and 4-dp rounding edge cases. Verified value: <!-- v:CLAIM-LIB-ERRORBUDGET-001.correct -->**9**
(`correct`), backed by [`modules/errorbudget/artifacts/errorbudget.json`](../modules/errorbudget/artifacts/errorbudget.json).

## Vendor it

Ships `errorbudget.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/2990416cb259452c27406dd4a33b70681a92edd56fae1c1aa9297d0c2c23dd99 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **ISBN 978-1-491-92912-4** — Site Reliability Engineering: How Google Runs Production Systems. [https://sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/)
