# RFC 6901 JSON Pointer resolution

*Subject area: Data / JSON Processing. Language: python. Vendorable bundle `8cea598ece7b`.*

A JSON Pointer (RFC 6901) is a compact string that identifies one value inside a JSON document: the empty string references the whole document, and otherwise a sequence of '/'-separated reference tokens walks object members by key and array elements by base-10 index. Because '/' and '~' are structural, they are escaped inside a token as ~1 and ~0 and must be unescaped ~1-before-~0 so that a literal '~1' round-trips. Vendor this module to dereference config paths, JSON Patch targets, or API response fields consistently; the claim proves it matches the RFC's own example evaluations, so you inherit a checked resolver rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-JSONPOINTER-001 reference_cases_passed -->
The vendored RFC 6901 JSON Pointer resolver reproduces every published result in RFC 6901 section 5's worked example — the exact example document evaluated at all 12 example pointers ("" -> whole document, "/foo" -> ["bar","baz"], "/foo/0" -> "bar", "/" -> 0, "/a~1b" -> 1, "/c%d" -> 2, "/e^f" -> 3, "/g|h" -> 4, "/i\\j" -> 5, "/k\"l" -> 6, "/ " -> 7, "/m~0n" -> 8) — with reference_cases_passed = 12 and failures = 0, including the ~1 and ~0 unescaping (in that order) and the empty-pointer whole-document case. Verified value: <!-- v:CLAIM-LIB-JSONPOINTER-001.reference_cases_passed -->**12**
(`reference_cases_passed`), backed by [`modules/jsonpointer/artifacts/jsonpointer.json`](../modules/jsonpointer/artifacts/jsonpointer.json).

## Vendor it

Ships `jsonpointer.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/8cea598ece7ba4288703c35dab907e4f27bce5851bb8f5629ee38cea4389ef53 --target .
```
