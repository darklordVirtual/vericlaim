# ChaCha20 stream cipher (RFC 8439) from scratch

*Subject area: Security / Stream Ciphers. Language: python. Vendorable bundle `a6051bcfba30`.*

ChaCha20 is the stream cipher used by TLS 1.3, WireGuard and OpenSSH: a 4x4 state of 32-bit words (constants, 256-bit key, counter, 96-bit nonce) run through 20 add-xor-rotate rounds produces a 64-byte keystream block that is XORed with the message; decryption is the same operation. This module implements the RFC 8439 IETF variant from scratch in pure integer arithmetic with fail-closed input checks and counter-overflow rejection; the claim proves it matches the RFC's published vectors byte-for-byte, so you inherit a checked reference implementation rather than one more unaudited copy.

## Claim

<!-- claim:CLAIM-LIB-CHACHA20-001 reference_vectors_matched -->
The vendored from-scratch ChaCha20 (RFC 8439) reproduces all 4 published reference vectors byte-exactly -- the section 2.1.1 quarter round, the section 2.3.2 block-function keystream, the Appendix A.1 all-zero keystream block, and the section 2.4.2 'sunscreen' ciphertext -- with 0 mismatches, and encrypt/decrypt round-trips losslessly on all 7 cases of a varied-length battery. Verified value: <!-- v:CLAIM-LIB-CHACHA20-001.reference_vectors_matched -->**4**
(`reference_vectors_matched`), backed by [`modules/chacha20/artifacts/chacha20.json`](../modules/chacha20/artifacts/chacha20.json).

## Vendor it

Ships `chacha20.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/a6051bcfba309f324701191e83306a85cdf2940f8334c4e8ffbd1f95178e3344 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **RFC 8439** — ChaCha20 and Poly1305 for IETF Protocols. [https://www.rfc-editor.org/rfc/rfc8439](https://www.rfc-editor.org/rfc/rfc8439)
