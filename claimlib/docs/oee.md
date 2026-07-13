# OEE (Overall Equipment Effectiveness)

*Subject area: Industrial / Manufacturing Analytics. Language: python. Vendorable bundle `214c0e8580a3`.*

Overall Equipment Effectiveness is the factory-floor standard for how fully a machine is used, the product of three ratios: Availability (run time over planned time), Performance (actual over theoretical throughput), and Quality (good units over total). 100% is perfect production; about 85% is considered world-class. The published worked example resolves to 74.79%, and this module reproduces it. Vendor it to compute OEE and its factors consistently across lines and shifts; the claim proves the arithmetic matches the published reference, so you inherit a checked calculator rather than a spreadsheet formula to re-audit.

## Claim

<!-- claim:CLAIM-LIB-OEE-001 correct -->
The vendored OEE calculator reproduces the canonical published worked example (Vorne / oee.com) exactly to 4 dp -- Availability 0.8881, Performance 0.8611, Quality 0.9780, OEE 0.7479 from Planned 420 min, Run 373 min, Ideal Cycle 1.0 s, Total 19271, Good 18848 -- and matches all 3 hand-computed reference cases (correct = 3, errors = 0), including the perfect-line boundary (all factors 1.0) and the each-factor-one-half case (OEE 0.125). Verified value: <!-- v:CLAIM-LIB-OEE-001.correct -->**3**
(`correct`), backed by [`modules/oee/artifacts/oee.json`](../modules/oee/artifacts/oee.json).

## Vendor it

Ships `oee.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/214c0e8580a3d80021e0cacdea367f69183c437e0407d8793dc27ed52466eaae --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **ISBN 0-915299-23-2** — Introduction to TPM: Total Productive Maintenance. [https://search.worldcat.org/title/Introduction-to-TPM-:-total-productive-maintenance/oclc/18441684](https://search.worldcat.org/title/Introduction-to-TPM-:-total-productive-maintenance/oclc/18441684)
