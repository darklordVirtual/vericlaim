# Punycode (RFC 3492) encode/decode

*Subject area: Telecom / Internationalized DNS (IDNA). Language: python. Vendorable bundle `42a81da039dd`.*

Punycode is the Bootstring algorithm instantiated with DNS parameters: it maps any Unicode string to a unique ASCII string (the encoding beneath internationalized domain names' xn-- labels) by emitting the basic code points literally and encoding the positions and values of the rest as generalized-variable-length integers with bias adaptation. This module implements RFC 3492 encode and decode from scratch with the reference implementation's 32-bit overflow ceiling; the claim proves it reproduces every published sample of the RFC in both directions and matches the stdlib's independent implementation, so you inherit a checked IDN building block.

## Claim

<!-- claim:CLAIM-LIB-PUNYCODE-001 samples_matched -->
The vendored Punycode codec reproduces all 19 published RFC 3492 section 7.1 sample strings exactly in both directions (samples_matched = 19, mismatches = 0), accepts the RFC's mixed-case digit spelling on decode, and agrees with Python's independent stdlib punycode codec on all 56 cross-checks over the samples plus a fixed extra battery. Verified value: <!-- v:CLAIM-LIB-PUNYCODE-001.samples_matched -->**19**
(`samples_matched`), backed by [`modules/punycode/artifacts/punycode.json`](../modules/punycode/artifacts/punycode.json).

## Vendor it

Ships `punycode.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/42a81da039dddefaef30dc0910249f923b24b84363c026f8d98ae6632130994c --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **RFC 3492** — Punycode: A Bootstring encoding of Unicode for Internationalized Domain Names in Applications (IDNA). [https://www.rfc-editor.org/rfc/rfc3492](https://www.rfc-editor.org/rfc/rfc3492)
