# Levenshtein edit distance

*Subject area: General / Strings & Text. Language: python. Vendorable bundle `24525b8a0f82`.*

Levenshtein distance is the minimum number of single-character insertions, deletions, or substitutions to turn one string into another -- the workhorse behind spell-check suggestions, fuzzy matching, and diff tooling. The standard Wagner-Fischer dynamic program computes it in O(m*n) time; a correct implementation also forms a true metric (identity, symmetry, triangle inequality). This module uses the two-row DP; the claim proves it matches the published distances and satisfies the metric axioms, so you inherit a checked distance function rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-LEVENSHTEIN-001 reference_correct -->
The vendored Levenshtein edit distance reproduces every published textbook value in a fixed 8-row battery (reference_correct = 8, reference_errors = 0): kitten->sitting = 3, Saturday->Sunday = 3, flaw->lawn = 2, gumbo->gambol = 2, book->back = 2, ''->'abc' = 3, and identity pairs = 0; and over a fixed word set it satisfies the metric axioms -- identity, symmetry on all 100 ordered pairs, and the triangle inequality on all 1000 ordered triples. Verified value: <!-- v:CLAIM-LIB-LEVENSHTEIN-001.reference_correct -->**8**
(`reference_correct`), backed by [`modules/levenshtein/artifacts/levenshtein.json`](../modules/levenshtein/artifacts/levenshtein.json).

## Vendor it

Ships `levenshtein.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/24525b8a0f828e9e1791802438e7d45e9bb8bb5c9ceb756e235b611ff64f3e2a --target .
```
