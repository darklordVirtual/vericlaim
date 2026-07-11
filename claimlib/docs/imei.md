# IMEI validation (Luhn check digit)

*Subject area: Telecom / Device Identity. Language: python. Vendorable bundle `0d0b0d105a40`.*

An IMEI is the 15-digit identity of a cellular device: an 8-digit Type Allocation Code, a 6-digit serial, and a trailing Luhn check digit over the first 14 digits -- the same mod-10 scheme used on payment cards. Networks and device registries validate it at the check-digit level before any lookup. Vendor this module to validate and parse IMEIs with zero dependencies; the claim proves it accepts the published example and agrees with an independent Luhn oracle across the battery, so you inherit a checked validator rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-IMEI-001 reference_vectors_matched -->
The vendored IMEI validator accepts the published GSMA / Wikipedia example IMEI 490154203237518 and reconstructs its check digit (check_digit("49015420323751") == 8), and its is_valid verdict agrees with an INDEPENDENT from-scratch Luhn implementation on every one of a fixed 261-vector battery (the published IMEI, corrupted and wrong-length variants, and 256 deterministic pseudo-random 15-digit strings): reference_vectors_matched = 261, mismatches = 0. Verified value: <!-- v:CLAIM-LIB-IMEI-001.reference_vectors_matched -->**261**
(`reference_vectors_matched`), backed by [`modules/imei/artifacts/imei.json`](../modules/imei/artifacts/imei.json).

## Vendor it

Ships `imei.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/0d0b0d105a40d7eaa441ae5aec237bd7fd77d8ef35f678adb060f2b98d1c58e5 --target .
```
