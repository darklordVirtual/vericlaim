# Semantic Versioning 2.0.0 compare + range grammar

*Subject area: Software Supply Chain / Dependency Resolution. Language: python. Vendorable bundle `a6fb30648747`.*

Semantic Versioning encodes MAJOR.MINOR.PATCH plus optional pre-release and build metadata, and defines a strict precedence order (spec section 11): core compared numerically, a pre-release ranked below its associated release, and pre-release identifiers compared left-to-right with numeric identifiers below alphanumeric ones. Package managers layer range operators on top of this ordering (caret pins the left-most non-zero element, tilde allows patch-level drift) to decide which published versions an install may resolve to. Vendor this module to compare versions and evaluate those common ranges consistently; the claim proves the precedence arithmetic and range bounds match the spec, so you inherit a checked resolver rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-SEMVER-001 correct -->
The vendored SemVer 2.0.0 library reproduces every required answer over a fixed 46-row reference battery (18 precedence comparisons drawn verbatim from the spec's golden ordering chain plus core/build/numeric-vs-alnum rules, and 28 satisfies rows over exact/>=/</caret/tilde ranges): correct = 46 with 0 errors. parse rejects malformed input and leading zeros; compare honors pre-release < release, numeric-below-alphanumeric, and larger-identifier-set precedence; build metadata is ignored for ordering. Verified value: <!-- v:CLAIM-LIB-SEMVER-001.correct -->**46**
(`correct`), backed by [`modules/semver/artifacts/semver.json`](../modules/semver/artifacts/semver.json).

## Vendor it

Ships `semver.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/a6fb3064874747bdd161658ca413d0c73a40e0d8257de7da36e3e203e3253c47 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **SemVer 2.0.0** — Semantic Versioning 2.0.0. [https://semver.org/spec/v2.0.0.html](https://semver.org/spec/v2.0.0.html)
