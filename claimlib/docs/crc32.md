# CRC-32 (IEEE 802.3) checksum

*Subject area: Data / Integrity & Checksums. Language: python. Vendorable bundle `005031ecf66f`.*

CRC-32 (IEEE 802.3) is the cyclic redundancy check used by zip, gzip, PNG and Ethernet to catch accidental data corruption. It treats the message as a polynomial over GF(2) and computes the remainder modulo the reflected generator polynomial 0xEDB88320, with input/output reflected and init/final XOR of 0xFFFFFFFF, yielding an unsigned 32-bit value. This module implements the standard byte-wise table algorithm directly (no zlib inside), so you can vendor a dependency-free checksum; the claim proves it matches the published check vectors and agrees byte-for-byte with zlib.crc32, so you inherit a checked implementation rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-CRC32-001 reference_vectors_matched -->
The vendored CRC-32 (IEEE 802.3, reflected poly 0xEDB88320) implementation reproduces every value in a fixed 291-vector reference set exactly, with 0 mismatches: the 3 published check values (crc32(b"")==0, crc32(b"123456789")==0xCBF43926, crc32 of the lazy-dog pangram==0x414FA339) plus 288 byte strings cross-checked for exact equality against the independent stdlib oracle zlib.crc32, so reference_vectors_matched == reference_vectors == 291. Verified value: <!-- v:CLAIM-LIB-CRC32-001.reference_vectors_matched -->**291**
(`reference_vectors_matched`), backed by [`modules/crc32/artifacts/crc32.json`](../modules/crc32/artifacts/crc32.json).

## Vendor it

Ships `crc32.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/005031ecf66ff2355825c46ba0faa5e3b9db421ae0c85d448d6f3a6f5ad0faa2 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **IEEE 802.3-2022** — IEEE Standard for Ethernet. [https://standards.ieee.org/ieee/802.3/10422/](https://standards.ieee.org/ieee/802.3/10422/)
- **RFC 1952** — GZIP file format specification version 4.3. [https://www.rfc-editor.org/rfc/rfc1952](https://www.rfc-editor.org/rfc/rfc1952)
