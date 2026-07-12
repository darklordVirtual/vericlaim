# Lamport one-time signatures (hash-based, post-quantum)

*Subject area: Security / Post-Quantum Cryptography. Language: python. Vendorable bundle `26313636b5b6`.*

Lamport signatures show that a digital signature needs nothing more than a one-way (hash) function: the private key is two secrets per message bit, the public key is their hashes, and signing reveals the secret matching each bit of the message digest -- a verifier re-hashes and checks. Because it relies only on hash preimage resistance, it is quantum-resistant, and it is the conceptual seed of the NIST post-quantum hash-based standards (SLH-DSA / SPHINCS+, XMSS). Vendor it to understand and use a checked post-quantum primitive; the claim proves valid signatures verify and forgeries are rejected, so you inherit a checked one-time signature rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-LAMPORT-001 valid_ok -->
The vendored Lamport one-time signature verifies every honestly-produced signature (valid_ok = 5 over a fixed 5-case battery) and rejects all 15 tampering attempts with forgeries_accepted = 0: for each (seed, message) case, verify(message, sign(message, sk), pk) is True, while verifying the signature against a changed message, against a signature with one byte flipped, and against a different key pair all return False. Security rests only on SHA-256 preimage resistance, so the scheme is post-quantum (not broken by Shor's algorithm). Verified value: <!-- v:CLAIM-LIB-LAMPORT-001.valid_ok -->**5**
(`valid_ok`), backed by [`modules/lamport/artifacts/lamport.json`](../modules/lamport/artifacts/lamport.json).

## Vendor it

Ships `lamport.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/26313636b5b6338dd8fe955e347c2ec90a318059754e52bd3cd197101ad6d0cb --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **SRI CSL-98** — Constructing Digital Signatures from a One-Way Function. [https://www.microsoft.com/en-us/research/publication/constructing-digital-signatures-one-way-function/](https://www.microsoft.com/en-us/research/publication/constructing-digital-signatures-one-way-function/)
- **FIPS 205** — Stateless Hash-Based Digital Signature Standard (SLH-DSA). [https://csrc.nist.gov/pubs/fips/205/final](https://csrc.nist.gov/pubs/fips/205/final)
- **RFC 8391** — XMSS: eXtended Merkle Signature Scheme. [https://www.rfc-editor.org/rfc/rfc8391](https://www.rfc-editor.org/rfc/rfc8391)
