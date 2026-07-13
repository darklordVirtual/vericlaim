# Annuity loan payment + integer-oere amortization

*Subject area: Finance / Loans & Interest. Language: python. Vendorable bundle `cd95d3855ea6`.*

An annuity loan repays principal P over n periods at rate i with the constant payment P*i/(1-(1+i)^-n); each payment covers the period's interest first and the remainder amortizes principal, so interest falls and amortization grows over the schedule. Doing this in floating-point kroner is how spreadsheets leak oere. This module computes the payment and the full schedule entirely in integer minor units with banker's rounding, ending at a balance of exactly zero; the claim proves the textbook example and the exact identities an accountant would check, so an invoicing or loan system inherits a schedule that reconciles to the oere.

## Claim

<!-- claim:CLAIM-LIB-ANNUITY-001 checks_matched -->
The vendored annuity library passes all 32 checks with 0 mismatches: it reproduces the standard published textbook payment ($100,000 at 0.5% per month over 360 months gives exactly $599.55), satisfies the exact accounting identities on every one of 6 loans -- final balance exactly 0, principal column summing exactly to the principal, every interest cell equal to the banker's-rounded balance-times-rate, payments summing to principal plus total interest -- agrees with an independent 50-digit decimal evaluation of the closed formula on all 6, and handles the zero-rate even split. Verified value: <!-- v:CLAIM-LIB-ANNUITY-001.checks_matched -->**32**
(`checks_matched`), backed by [`modules/annuity/artifacts/annuity.json`](../modules/annuity/artifacts/annuity.json).

## Vendor it

Ships `annuity.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/cd95d3855ea6b06b92e8facb670441ad55fad8591080fa26094eb3a33e286130 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **3rd edition, ISBN 978-0-07-338244-9** — The Theory of Interest. [https://www.mheducation.com/highered/product/theory-interest-kellison/M9780073382449.html](https://www.mheducation.com/highered/product/theory-interest-kellison/M9780073382449.html)
