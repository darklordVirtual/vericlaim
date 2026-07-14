# Differential-privacy budget composition + accountant

*Subject area: AI Governance / Privacy Budgets. Language: python. Vendorable bundle `472886eb4d10`.*

An enterprise running differentially-private releases spends a privacy budget: each (epsilon, delta) mechanism consumes some, and the totals compose by theorem — sequential runs on the same data add up, runs on disjoint partitions cost only the maximum, and protecting groups of k individuals scales epsilon by k (Dwork & Roth 2014). This module computes those bounds in exact rational arithmetic and ships a fail-closed accountant that refuses any spend past the budget before recording it; the claim proves the theorem shapes and the refusal behaviour, so a privacy office inherits checked budget arithmetic.

## Claim

<!-- claim:CLAIM-LIB-DP-001 checks_matched -->
The vendored DP-composition library passes all 49 checks as exact Fraction identities with 0 mismatches: 4 hand-computed compositions (0.5 and 0.25 compose sequentially to exactly 3/4 and in parallel to exactly 1/2), 40 theorem-shaped properties over a deterministic ledger battery (sequential additivity and permutation-invariance, parallel-equals-max never exceeding sequential, group privacy exactly k*epsilon), and 5 fail-closed accountant checks including refusal of a 1/10^12 overspend with the ledger state unchanged. Verified value: <!-- v:CLAIM-LIB-DP-001.checks_matched -->**49**
(`checks_matched`), backed by [`modules/dp_composition/artifacts/dp_composition.json`](../modules/dp_composition/artifacts/dp_composition.json).

## Vendor it

Ships `dp_composition.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/472886eb4d109c9c3f1990d722cc99dfd3ccfdaafc48ccbd19ac99272977e3ad --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **doi:10.1561/0400000042; Found. Trends Theor. Comput. Sci. Vol. 9, Nos. 3-4 (2014), pp. 211-407** — The Algorithmic Foundations of Differential Privacy. [https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf](https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf)
