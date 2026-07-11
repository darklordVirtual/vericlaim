# Varint / LEB128 integer encoding

*Subject area: Data / Serialization. Language: python. Vendorable bundle `8a081a2ccc15`.*

A varint stores an integer in as few bytes as its magnitude needs, using seven bits per byte with the top bit as a continuation flag -- so small numbers cost one byte, and the stream is self-delimiting. It is the integer wire format of Protocol Buffers and many binary protocols; ZigZag mapping first folds signed numbers so that -1, 1, -2 encode as small unsigned 1, 2, 3 instead of maximal values. This module implements both; the claim proves it matches the published LEB128 vectors and round-trips, so you inherit a checked codec rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-VARINT-001 reference_vectors_matched -->
The vendored varint codec reproduces all 14 published reference vectors (reference_vectors_matched = 14): the 7 LEB128 unsigned vectors (0->00, 1->01, 127->7f, 128->8001, 255->ff01, 300->ac02, 624485->e58e26) and the 7 ZigZag mappings (0->0, -1->1, 1->2, -2->3, 2->4, -64->127, 63->126); and it round-trips losslessly over 76 unsigned values (powers of two up to 2**64-1) and 1004 signed values (-500..499 plus 31/62-bit boundaries). Verified value: <!-- v:CLAIM-LIB-VARINT-001.reference_vectors_matched -->**14**
(`reference_vectors_matched`), backed by [`modules/varint/artifacts/varint.json`](../modules/varint/artifacts/varint.json).

## Vendor it

Ships `varint.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/8a081a2ccc15e64820911cfa8a33a725184b92eff7b81549e6c43f282227e950 --target .
```
