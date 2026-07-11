# Cent-exact money allocation + banker's rounding

*Subject area: Finance / Accounting. Language: python. Vendorable bundle `b1c3b0ecbe49`.*

Two everyday money bugs are rounding bias and lost pennies. Rounding halves 'up' biases long-run totals upward; banker's rounding (ROUND_HALF_EVEN, the IEEE 754 and accounting default) rounds a tie to the nearest even digit so the bias cancels. Splitting a bill three ways with naive division loses or mints a cent; the largest-remainder (Hamilton) method floors each share and hands the leftover units to the largest remainders so the parts always sum back to the total. This module works in integer minor units to avoid float entirely; vendor it to allocate invoices, taxes, or payouts and inherit a checked cent-exact splitter and a checked banker's rounder rather than re-auditing another ad-hoc division.

## Claim

<!-- claim:CLAIM-LIB-MONEY-001 cent_exact -->
The vendored money library allocates a total into integer minor-unit shares that sum EXACTLY back to the total on every one of a fixed 8-case battery (cent_exact = 8, cent_lost = 0), matches 5 independently hand-computed splits (allocate(100,[1,1,1]) = [34,33,33], allocate(100,[1,1,1,1,1,1]) = [17,17,17,17,16,16], allocate(1000,[1,2,1]) = [250,500,250]), and reproduces published ROUND_HALF_EVEN (banker's rounding) results on all 10 rows of a fixed table (0.5 -> 0, 1.5 -> 2, 2.5 -> 2, 3.5 -> 4, 2.675 -> 2.68). Verified value: <!-- v:CLAIM-LIB-MONEY-001.cent_exact -->**8**
(`cent_exact`), backed by [`modules/money/artifacts/money.json`](../modules/money/artifacts/money.json).

## Vendor it

Ships `money.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/b1c3b0ecbe4909c5ae2e06d5322580ab3b361d95fb5c1eb1fe1b9063fb7fc03b --target .
```
