# Luhn (mod-10) checksum

*Subject area: Payments / Data Integrity. Language: python. Vendorable bundle `7bd998cfc181`.*

The Luhn algorithm (ISO/IEC 7812-1, the 'mod 10' formula) is the check-digit standard used to catch typos in payment card numbers, IMEIs, and many national IDs. Working right-to-left it doubles every second digit (subtracting 9 when the result exceeds 9), sums all digits, and treats the number as valid when that total is a multiple of 10. This module exposes is_valid() to check a full number and check_digit() to compute the digit that completes a partial one; vendor it to validate identifiers at data-entry time and inherit a checked implementation rather than re-auditing another hand-rolled loop.

## Claim

<!-- claim:CLAIM-LIB-LUHN-001 correct -->
The vendored Luhn (mod-10) implementation classifies every number in a fixed table of 12 independently-known cases correctly — 8 known-valid (the Wikipedia example, published Visa/Mastercard/Amex/Discover/Diners test cards, and a trivial single-zero) and 4 known-invalid (off-by-one and non-Luhn sequences) — with 0 errors, and its check_digit() reproduces the trailing check digit of each valid reference number. Verified value: <!-- v:CLAIM-LIB-LUHN-001.correct -->**12**
(`correct`), backed by [`modules/luhn/artifacts/luhn.json`](../modules/luhn/artifacts/luhn.json).

## Vendor it

Ships `luhn.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/7bd998cfc18103391fff9b2c72bde21cb23d8fa586eb54863f4c49eed3c6b649 --target .
```
