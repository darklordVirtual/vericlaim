# Double-entry bookkeeping invariants

*Subject area: Audit / Accounting Integrity. Language: python. Vendorable bundle `a408f86973d8`.*

Double-entry bookkeeping is the 500-year-old integrity check at the heart of every ledger: each transaction posts equal debits and credits, so across the books total debits equal total credits and every account's net balances sum to zero -- the trial balance an auditor runs first. This module checks that invariant and builds a trial balance in integer minor units; the claim proves it identifies balanced vs. unbalanced journals correctly and that the sums are exact, so you inherit a checked ledger primitive rather than a re-implementation with a rounding bug to re-audit.

## Claim

<!-- claim:CLAIM-LIB-DOUBLE-ENTRY-001 checks_matched -->
The vendored double-entry ledger library passes all 13 checks with 0 mismatches: it classifies every journal in a fixed 5-case battery as balanced or unbalanced correctly (including split entries and one-sided postings), the net account balances of every balanced journal sum to exactly zero, and a hand-computed trial balance reproduces the per-account debit/credit totals and net balances exactly (integer minor units, no floating point). Verified value: <!-- v:CLAIM-LIB-DOUBLE-ENTRY-001.checks_matched -->**13**
(`checks_matched`), backed by [`modules/double_entry/artifacts/double_entry.json`](../modules/double_entry/artifacts/double_entry.json).

## Vendor it

Ships `double_entry.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/a408f86973d89a944e097364342812754025277719c23aa347c63917ad2d0ac9 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **Venice: Paganino de Paganini, 10–20 November 1494 (LCCN 49036374)** — Summa de arithmetica, geometria, proportioni et proportionalita. [https://www.loc.gov/item/49036374/](https://www.loc.gov/item/49036374/)
