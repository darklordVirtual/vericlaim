# DORA structure + resilience-pillar coverage

*Subject area: AI Governance / Financial ICT Resilience (DORA). Language: python. Vendorable bundle `2ff29fdf974a`.*

DORA harmonizes digital operational resilience across the EU financial sector — banks, insurers, investment firms and their critical ICT providers — applying from 17 January 2025. Its requirements organize into five pillars: ICT risk management (Ch. II), incident management and reporting (Ch. III), resilience testing incl. TLPT (Ch. IV), ICT third-party risk (Ch. V) and information sharing (Ch. VI). Any AI system a financial entity operates is ICT under DORA, which makes this the enterprise-architecture frame around AI governance in finance. This module encodes the verified structure; the claim proves the chapter partition and pillar anchoring, so a resilience programme inherits a checked map.

## Claim

<!-- claim:CLAIM-LIB-DORA-001 checks_matched -->
The vendored DORA library passes all 22 checks with 0 mismatches: the encoded 9 chapter ranges PARTITION the Regulation's 64 articles exactly (verified article-by-article), 11 anchor articles resolve to their chapters, the five resilience pillars (ICT risk management, incident reporting, resilience testing, third-party risk, information sharing) carry their official chapter titles and map to chapters II-VI, and pillar coverage matches exact Fraction arithmetic. Verified value: <!-- v:CLAIM-LIB-DORA-001.checks_matched -->**22**
(`checks_matched`), backed by [`modules/dora_eu/artifacts/dora_eu.json`](../modules/dora_eu/artifacts/dora_eu.json).

## Vendor it

Ships `dora_eu.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/2ff29fdf974ad91fe75c29a1e27b41833a655c3c9cb801296504f68f13ba2721 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **CELEX:32022R2554; OJ L 333, 27.12.2022, p. 1-79; ELI: http://data.europa.eu/eli/reg/2022/2554/oj** — Regulation (EU) 2022/2554 (Digital Operational Resilience Act, DORA). [https://eur-lex.europa.eu/eli/reg/2022/2554/oj](https://eur-lex.europa.eu/eli/reg/2022/2554/oj)
