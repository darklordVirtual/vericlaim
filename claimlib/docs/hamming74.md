# Hamming(7,4) single-error correction

*Subject area: Telecom / Forward Error Correction. Language: python. Vendorable bundle `5d01b5150c69`.*

Forward error correction lets a receiver fix bit errors without retransmission -- essential on one-way or high-latency links. The Hamming(7,4) code adds 3 parity bits to 4 data bits so that the parity syndrome of a received word points directly at the position of any single flipped bit, which the decoder then corrects. Because its 16 codewords are pairwise at Hamming distance >= 3, any single-bit error stays closest to the true codeword. Vendor this module for a checked, dependency-free single-error-correcting building block; the claim proves correction over the ENTIRE single-error space by enumeration, so you inherit a proven coder rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-HAMMING74-001 corrected -->
The vendored Hamming(7,4) coder corrects EVERY single-bit error, verified exhaustively: over the complete space of 16 data values x 8 error patterns (no error plus a flip at each of the 7 positions) = 128 trials, decoding always recovers the original 4 bits and reports the exact flipped position (corrected = 128, miscorrected = 0, error_position_correct = 128), and the 16 codewords have minimum Hamming distance 3. Verified value: <!-- v:CLAIM-LIB-HAMMING74-001.corrected -->**128**
(`corrected`), backed by [`modules/hamming74/artifacts/hamming74.json`](../modules/hamming74/artifacts/hamming74.json).

## Vendor it

Ships `hamming74.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/5d01b5150c69d81fa12c2ac24a0b3ba49bfb74543217771562eedeaaf186a7cf --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **Bell System Technical Journal, vol. 29, no. 2, pp. 147-160, doi:10.1002/j.1538-7305.1950.tb00463.x** — Error Detecting and Error Correcting Codes. [https://doi.org/10.1002/j.1538-7305.1950.tb00463.x](https://doi.org/10.1002/j.1538-7305.1950.tb00463.x)
