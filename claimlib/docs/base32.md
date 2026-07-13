# RFC 4648 base32 encode/decode

*Subject area: Data / Encoding. Language: python. Vendorable bundle `e131a4a738ac`.*

Base32 (RFC 4648) encodes arbitrary bytes into a 32-character, case-insensitive-friendly alphabet (A-Z, 2-7), packing every 5 input bytes into 8 output symbols and padding a short final group with '=' — useful where the output must survive case-folding or be spoken/typed (TOTP secrets, DNS labels, filenames). This module implements the bit-packing directly rather than delegating to a library, exposing encode(bytes)->str and its exact inverse decode(str)->bytes, which fails closed on bad length, unknown symbols, or malformed padding. Vendor it for a dependency-free, auditable codec; the claim binds the RFC vectors and stdlib-oracle agreement, so you inherit a checked encoder rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-BASE32-001 reference_vectors_matched -->
The vendored RFC 4648 base32 codec passes all 17 reference checks with 0 mismatches: it reproduces every one of the 7 RFC 4648 section 10 test vectors exactly (b""->"", b"f"->"MY======", ... b"foobar"->"MZXW6YTBOI======"), and over 10 fixed byte inputs its encode/decode agree byte-for-byte with Python's stdlib base64.b32encode/b32decode (an independent oracle the module never calls) while round-tripping decode(encode(x)) == x exactly. Verified value: <!-- v:CLAIM-LIB-BASE32-001.reference_vectors_matched -->**17**
(`reference_vectors_matched`), backed by [`modules/base32/artifacts/base32.json`](../modules/base32/artifacts/base32.json).

## Vendor it

Ships `base32.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/e131a4a738acd4d5e3fb5703f3b8957a284dc9b676903b6b8f797fe0f76904a8 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **RFC 4648** — The Base16, Base32, and Base64 Data Encodings. [https://www.rfc-editor.org/rfc/rfc4648](https://www.rfc-editor.org/rfc/rfc4648)
