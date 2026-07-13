# MAC / EUI-48 parsing + IEEE 802 flags

*Subject area: Telecom / Layer-2 Addressing. Language: python. Vendorable bundle `a084b6ab051a`.*

A MAC address is written four different ways (aa:bb:.., aa-bb-.., Cisco aabb.ccdd.eeff, bare aabbccddeeff), and the two low bits of its first octet carry meaning: the I/G bit marks multicast vs unicast and the U/L bit marks a locally-administered (e.g. virtualised/randomised) vs globally-unique address. This module parses every notation to one integer and decodes those flags; the claim proves the decoding matches the IEEE rules and the notations agree, so you inherit a checked L2-address helper rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-MACADDR-001 correct -->
The vendored MAC / EUI-48 library decodes the IEEE 802 flag bits correctly on every one of a fixed 7-address battery (correct = 7, errors = 0): the I/G multicast bit and U/L locally-administered bit of the first octet, plus broadcast detection -- checked against hand-written expected flags for well-known MACs (01:00:5e:.. and 33:33:.. multicast, ff:ff:ff:ff:ff:ff broadcast, 02:.. and 52:54:00:.. locally administered, ordinary vendor-OUI unicast). Independently, the colon, hyphen, Cisco-dotted, and bare-hex spellings of one address all parse to the same 48-bit integer. Verified value: <!-- v:CLAIM-LIB-MACADDR-001.correct -->**7**
(`correct`), backed by [`modules/macaddr/artifacts/macaddr.json`](../modules/macaddr/artifacts/macaddr.json).

## Vendor it

Ships `macaddr.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/a084b6ab051afbb0648ac65fdbb5713d7c5be8cad6884b41c75f5aa6e9d8f474 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **IEEE Std 802-2024** — IEEE Standard for Local and Metropolitan Area Networks: Overview and Architecture. [https://standards.ieee.org/ieee/802/10894/](https://standards.ieee.org/ieee/802/10894/)
- **IEEE RA Guidelines for Use of EUI, OUI, and CID (2017-08-03)** — Guidelines for Use of Extended Unique Identifier (EUI), Organizationally Unique Identifier (OUI), and Company ID (CID). [https://standards.ieee.org/wp-content/uploads/import/documents/tutorials/eui.pdf](https://standards.ieee.org/wp-content/uploads/import/documents/tutorials/eui.pdf)
