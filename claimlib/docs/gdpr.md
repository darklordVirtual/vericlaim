# GDPR structure, Art. 5 principles + Art. 32 measures

*Subject area: Compliance / Privacy (GDPR). Language: python. Vendorable bundle `09b02ece40a9`.*

The GDPR -- Regulation (EU) 2016/679 -- is the backbone of European privacy law: 99 articles in 11 chapters, with Article 5 stating the processing principles (lawfulness, purpose limitation, data minimisation, accuracy, storage limitation, integrity/confidentiality, accountability) and Article 32 the security-of-processing measures every controller and processor must weigh. This module encodes that structure with fail-closed lookups and coverage scoring; the claim proves the chapter ranges partition all 99 articles and the enumerations match the Regulation, so a compliance tool inherits a checked map of the law's shape.

## Claim

<!-- claim:CLAIM-LIB-GDPR-001 checks_matched -->
The vendored GDPR library passes all 14 checks with 0 mismatches: the encoded 11 chapter ranges PARTITION the Regulation's 99 articles exactly (verified article-by-article, exhaustively), 7 published anchor articles resolve to their correct chapters (Art. 5 to II, Art. 17 to III, Art. 33 to IV, Art. 83 to VIII, ...), the principle and measure sets match Article 5 (six lettered principles plus accountability) and Article 32(1) (four measures), and coverage percentages agree with exact Fraction arithmetic. Verified value: <!-- v:CLAIM-LIB-GDPR-001.checks_matched -->**14**
(`checks_matched`), backed by [`modules/gdpr/artifacts/gdpr.json`](../modules/gdpr/artifacts/gdpr.json).

## Vendor it

Ships `gdpr.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/09b02ece40a9be1e7cf91a419cdd84efe4393576d9306cb8cde5c5765c99a028 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **Regulation (EU) 2016/679, OJ L 119, 4.5.2016, p. 1-88** — Regulation (EU) 2016/679 (General Data Protection Regulation). [https://eur-lex.europa.eu/eli/reg/2016/679/oj](https://eur-lex.europa.eu/eli/reg/2016/679/oj)
