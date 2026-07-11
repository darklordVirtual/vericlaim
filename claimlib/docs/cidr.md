# IPv4 CIDR / subnet math

*Subject area: Telecom / IP Address Management. Language: python. Vendorable bundle `34d77e8b3975`.*

CIDR subnetting is the everyday management-plane task on routers, firewalls and ISP IPAM: given 192.0.2.0/24 decide the network address, the directed broadcast, the mask, how many usable hosts, and whether an address is inside the block -- all of it bit arithmetic on the 32-bit integer. This module implements that arithmetic from scratch (so it carries no dependency) and the claim proves it matches Python's ipaddress across the battery, so you inherit a checked, dependency-free IPv4 calculator rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-CIDR-001 checks_matched -->
The vendored IPv4 CIDR calculator -- which implements the 32-bit subnet arithmetic DIRECTLY and never imports ipaddress -- agrees with Python's stdlib ipaddress on every one of 140 checks across a fixed 12-network battery (checks_matched = 140, mismatches = 0): network and broadcast address, netmask, total address count, usable host count, and first/last usable host per network, plus a full hosts() enumeration count for narrow prefixes and a membership sweep (network, broadcast, and the addresses just outside), including the RFC 3021 /31 point-to-point and single-host /32 cases. Verified value: <!-- v:CLAIM-LIB-CIDR-001.checks_matched -->**140**
(`checks_matched`), backed by [`modules/cidr/artifacts/cidr.json`](../modules/cidr/artifacts/cidr.json).

## Vendor it

Ships `cidr.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/34d77e8b397510d5efb169bb99e7107b871091e200f1c6f0f8049b41089f81e2 --target .
```
