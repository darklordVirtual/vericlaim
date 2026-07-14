# NMEA 0183 sentence checksum

*Subject area: Industrial / Telemetry & Sensors. Language: python. Vendorable bundle `2caa4cfffbfc`.*

NMEA 0183 is the line-oriented ASCII protocol that GPS receivers, marine instruments, and much SCADA telemetry use to emit sentences like '$GPGGA,...*47'. The two hex digits after '*' are the XOR of every character between '$' and '*', a lightweight guard against line noise. Vendor this module to validate incoming sentences and to build correctly-checksummed ones with zero dependencies; the claim proves it reproduces the checksums of the canonical published sentences, so you inherit a checked checksum routine rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-NMEA-001 published_correct -->
The vendored NMEA 0183 checksum reproduces the published '*HH' checksum of every one of 3 canonical example sentences ($GPGGA,...*47, $GPRMC,...*68, $GPGSA,...*39) exactly (published_correct = 3, published_errors = 0) and all 3 are accepted by is_valid; independently, for 4 payloads the build / verify round-trip holds (a built sentence validates; roundtrip_ok = 4) and a single-character mutation is detected in every case (tamper_detected = 4). Verified value: <!-- v:CLAIM-LIB-NMEA-001.published_correct -->**3**
(`published_correct`), backed by [`modules/nmea/artifacts/nmea.json`](../modules/nmea/artifacts/nmea.json).

## Vendor it

Ships `nmea.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/2caa4cfffbfced04667ae689749df1f1205f49722ac07284acf88cd181c75912 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **NMEA 0183 v4.30** — NMEA 0183 Interface Standard. [https://www.nmea.org/nmea-0183.html](https://www.nmea.org/nmea-0183.html)
