# Base58 encode/decode (Bitcoin alphabet)

*Subject area: Data / Encoding. Language: python. Vendorable bundle `b33cfae46fdb`.*

Base58 is base-conversion encoding over an alphabet chosen to survive human eyes and keyboards: the ambiguous 0/O and I/l are removed, and each leading zero byte is written as a literal '1' so binary prefixes survive the integer conversion. It is the encoding of Bitcoin addresses, IPFS CIDs (base58btc) and many key formats. This module implements encode and decode from scratch with fail-closed alphabet checking; the claim proves it matches the published vector sets byte-for-byte, so you inherit a checked codec instead of a copy-pasted gist.

## Claim

<!-- claim:CLAIM-LIB-BASE58-001 reference_vectors_matched -->
The vendored Base58 codec reproduces all 24 published reference vectors exactly in both directions (reference_vectors_matched = 24, mismatches = 0) -- the draft-msporny-base58 vectors including 'Hello World!' -> '2NEpo7TZRRrLZSi2U' and the Bitcoin Core encode/decode set with its long leading-zero runs -- and round-trips losslessly on all 14 structural cases. Verified value: <!-- v:CLAIM-LIB-BASE58-001.reference_vectors_matched -->**24**
(`reference_vectors_matched`), backed by [`modules/base58/artifacts/base58.json`](../modules/base58/artifacts/base58.json).

## Vendor it

Ships `base58.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/b33cfae46fdbecbdc393eee81c3e37e8503687f75e21cb1f5cec4d26ad64abae --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **draft-msporny-base58-03** — The Base58 Encoding Scheme. [https://datatracker.ietf.org/doc/html/draft-msporny-base58-03](https://datatracker.ietf.org/doc/html/draft-msporny-base58-03)
