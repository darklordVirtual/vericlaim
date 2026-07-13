# 802.1Q VLAN ID validation + ranges

*Subject area: Telecom / VLAN Management. Language: python. Vendorable bundle `5958f35e2446`.*

An 802.1Q VLAN ID is a 12-bit field, but only 1..4094 are assignable: 0 marks a priority-tagged (untagged) frame and 4095 is reserved. Switch and ISP configs express VLAN membership as compact ranges like '1,10-12,4094', which must be parsed, de-duplicated, and re-emitted canonically. This module validates VIDs and round-trips those range lists; the claim proves the validity rule matches 802.1Q and the parse/format round-trips, so you inherit a checked VLAN helper rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-VLAN-001 correct -->
The vendored 802.1Q VLAN library classifies VLAN-ID validity correctly on every one of a fixed 9-case battery (correct = 9, errors = 0), pinning the reservations (0 priority-tagged and 4095 reserved are invalid; 1..4094 valid); and over 6 range strings it parses the compact 'a,b-c' notation to the expected sorted, de-duplicated list and reformats it to the canonical range text (range_parse_correct = 6, range_roundtrip_correct = 6). Verified value: <!-- v:CLAIM-LIB-VLAN-001.correct -->**9**
(`correct`), backed by [`modules/vlan/artifacts/vlan.json`](../modules/vlan/artifacts/vlan.json).

## Vendor it

Ships `vlan.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/5958f35e2446a45193bc1407fc761b1fe57f42562552f48bb647c2bde86e23b1 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **IEEE Std 802.1Q-2022** — IEEE Standard for Local and Metropolitan Area Networks—Bridges and Bridged Networks. [https://standards.ieee.org/ieee/802.1Q/10323/](https://standards.ieee.org/ieee/802.1Q/10323/)
