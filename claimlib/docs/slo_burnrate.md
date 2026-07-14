# SLO burn-rate alerting math (SRE Workbook ch. 5)

*Subject area: SRE / SLO Alerting. Language: python. Vendorable bundle `5c5f75180af4`.*

Error-budget alerting pages on how FAST the budget burns, not on raw error rates: burn rate = budget fraction consumed times period over window, so burn 14.4 means a 30-day budget gone in 50 hours. The Workbook's recommended policy pairs each long window with a short confirmation window (long/12) so pages stop when the bleeding stops, and tiers page/ticket severity. This module implements that arithmetic exactly; the claim proves the published table and the multiwindow semantics, so your alerting rules inherit checked math instead of re-derived constants.

## Claim

<!-- claim:CLAIM-LIB-SLO-BURNRATE-001 checks_matched -->
The vendored burn-rate library passes all 17 checks with 0 mismatches: it reproduces the Google SRE Workbook's published 30-day alerting table exactly (2% budget in 1 h is burn rate 14.4, 5% in 6 h is 6, 10% in 3 d is 1, each with its long/12 short window), validates the shipped three-tier policy against the formula, satisfies 7 algebraic identities (including burn rate 1000 exhausting a 30-day budget in 0.72 h), and implements the multiwindow condition so an at-threshold or single-window signal does NOT page. Verified value: <!-- v:CLAIM-LIB-SLO-BURNRATE-001.checks_matched -->**17**
(`checks_matched`), backed by [`modules/slo_burnrate/artifacts/slo_burnrate.json`](../modules/slo_burnrate/artifacts/slo_burnrate.json).

## Vendor it

Ships `slo_burnrate.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/5c5f75180af416b1a12cf0a50ed12d835eef4cc79a8033b4753f810f9b42718c --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **ISBN 978-1-492-02950-2** — The Site Reliability Workbook: Practical Ways to Implement SRE. [https://sre.google/workbook/table-of-contents/](https://sre.google/workbook/table-of-contents/)
- **ISBN 978-1-491-92912-4** — Site Reliability Engineering: How Google Runs Production Systems. [https://sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/)
