# UUID parse/format + deterministic v3/v5 (RFC 9562)

*Subject area: Data / Identifiers (UUID). Language: python. Vendorable bundle `98c0879b5f07`.*

A UUID is a 128-bit identifier whose version and variant bits encode how it was generated; RFC 9562 (which obsoletes RFC 4122) specifies the layout and algorithms. Name-based UUIDs (v3/v5) hash a namespace UUID plus a name so independent systems derive the SAME identifier without coordination -- ideal for content addressing and idempotency keys. This module implements parse, format, inspection and v3/v5 generation from scratch; the claim proves it matches the RFC's vectors and the stdlib's independent implementation, so you inherit checked identifier plumbing.

## Claim

<!-- claim:CLAIM-LIB-UUID-001 rfc_vectors_matched -->
The vendored UUID library reproduces all 12 RFC 9562 published vectors exactly (rfc_vectors_matched = 12, mismatches = 0), agrees with Python's independent stdlib uuid3/uuid5 on all 64 cross-checks over a fixed (namespace, name) battery, and places the version and variant bits correctly in all 128 bit-placement checks. Verified value: <!-- v:CLAIM-LIB-UUID-001.rfc_vectors_matched -->**12**
(`rfc_vectors_matched`), backed by [`modules/uuid_tools/artifacts/uuid_tools.json`](../modules/uuid_tools/artifacts/uuid_tools.json).

## Vendor it

Ships `uuid_tools.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/98c0879b5f07deaef0425949e61fb89aa3ce6b0631b933a988735bef5052a775 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **RFC 9562 (STD 97)** — Universally Unique IDentifiers (UUIDs). [https://www.rfc-editor.org/rfc/rfc9562](https://www.rfc-editor.org/rfc/rfc9562)
