# Luhn (mod-10) checksum

*Subject area: Payments / Data Integrity. Language: python. Vendorable bundle `e1cbdb383b3a`.*

The Luhn algorithm (ISO/IEC 7812-1, the 'mod 10' formula) is the check-digit standard used to catch typos in payment card numbers, IMEIs, and many national IDs. Working right-to-left it doubles every second digit (subtracting 9 when the result exceeds 9), sums all digits, and treats the number as valid when that total is a multiple of 10. This module exposes is_valid() to check a full number and check_digit() to compute the digit that completes a partial one; vendor it to validate identifiers at data-entry time and inherit a checked implementation rather than re-auditing another hand-rolled loop.

## Claim

<!-- claim:CLAIM-LIB-LUHN-001 correct -->
The vendored Luhn (mod-10) implementation classifies every number in a fixed table of 12 independently-known cases correctly — 8 known-valid (the Wikipedia example, published Visa/Mastercard/Amex/Discover/Diners test cards, and a trivial single-zero) and 4 known-invalid (off-by-one and non-Luhn sequences) — with 0 errors, and its check_digit() reproduces the trailing check digit of each valid reference number. Verified value: <!-- v:CLAIM-LIB-LUHN-001.correct -->**12**
(`correct`), backed by [`modules/luhn/artifacts/luhn.json`](../modules/luhn/artifacts/luhn.json).

## Vendor it

Ships `luhn.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/e1cbdb383b3ad7902e9cb9c4df6e34f4c004bfa224455d9e6d4828f74599dc8e --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **U.S. Patent 2,950,048** — Computer for Verifying Numbers. [https://patents.google.com/patent/US2950048A/en](https://patents.google.com/patent/US2950048A/en)
- **ISO/IEC 7812-1:2017** — Identification cards — Identification of issuers — Part 1: Numbering system. [https://www.iso.org/standard/70484.html](https://www.iso.org/standard/70484.html)
