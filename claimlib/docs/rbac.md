# RBAC least-privilege & separation-of-duties audit

*Subject area: Security / Identity & Access Management. Language: python. Vendorable bundle `23c387e3c42d`.*

Role-Based Access Control grants permissions to roles and assigns roles to identities; two enduring control objectives sit on top of it. Least privilege says an identity should hold no permission its role does not need — anything extra ('excess') is attack surface and audit debt. Separation of duties says certain permissions are toxic in combination (create a payment AND approve it; deploy code AND review it) and must never rest with one identity, even when a mis-scoped role would technically allow both. This module makes both checks mechanical and independent, so an over-broad role cannot silently launder an SoD violation into 'authorized'.

## Claim

<!-- claim:CLAIM-LIB-RBAC-001 detected_excess -->
The vendored RBAC auditor detects every seeded over-privilege and separation-of-duties finding in a fixed 13-identity access matrix: all 6 excess grants (detected_excess == seeded_excess == 6) and all 3 toxic-pair violations (detected_sod == seeded_sod == 3), with 0 false positives — no hand-verified clean identity is ever flagged. Verified value: <!-- v:CLAIM-LIB-RBAC-001.detected_excess -->**6**
(`detected_excess`), backed by [`modules/rbac/artifacts/rbac.json`](../modules/rbac/artifacts/rbac.json).

## Vendor it

Ships `rbac.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/23c387e3c42d27c7cee1dd2d42d42b903b41c7debfa0b509a7ce49ef860ec41f --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **INCITS 359-2012 (R2022)** — Information technology — Role Based Access Control. [https://webstore.ansi.org/standards/incits/incits3592012r2022](https://webstore.ansi.org/standards/incits/incits3592012r2022)
- **Proceedings of the IEEE, vol. 63, no. 9, pp. 1278-1308; doi:10.1109/PROC.1975.9939** — The Protection of Information in Computer Systems. [https://doi.org/10.1109/PROC.1975.9939](https://doi.org/10.1109/PROC.1975.9939)
