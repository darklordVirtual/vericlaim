# CRC-16/MODBUS frame check

*Subject area: Industrial / Fieldbus & Protocols. Language: python. Vendorable bundle `1c173bc22b68`.*

Modbus RTU, the serial fieldbus dialect ubiquitous in PLCs and industrial sensors, protects every frame with a 16-bit CRC using the reflected polynomial 0xA001, an initial value of 0xFFFF, and no final XOR, transmitted low byte first. This module computes the CRC and offers append / verify helpers; the claim proves it reproduces the published catalogue check value 0x4B37 and agrees with an independent table-driven CRC, so you can vendor a dependency-free, checked frame-check for Modbus tooling or gateways rather than re-auditing another CRC loop.

## Claim

<!-- claim:CLAIM-LIB-MODBUS-CRC-001 reference_vectors_matched -->
The vendored CRC-16/MODBUS implementation (reflected poly 0xA001, init 0xFFFF, no final XOR) reproduces every value in a fixed 267-vector reference set with 0 mismatches: the published CRC-catalogue check value crc16_modbus(b"123456789") == 0x4B37, plus 266 byte strings (empty, single bytes, all-zero / all-0xFF runs, a Modbus read-holding-registers frame, and every single byte value 0..255) that agree byte-for-byte with an independent table-driven implementation computed in the evidence. Verified value: <!-- v:CLAIM-LIB-MODBUS-CRC-001.reference_vectors_matched -->**267**
(`reference_vectors_matched`), backed by [`modules/modbus_crc/artifacts/modbus_crc.json`](../modules/modbus_crc/artifacts/modbus_crc.json).

## Vendor it

Ships `modbus_crc.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/1c173bc22b688e1a25bb7a049da445c48d5246aa15cf9c2edccb27e52a750978 --target .
```
