# Learn then Test (risk control as multiple testing)

*Subject area: AI Assurance / Risk Control. Language: python. Vendorable bundle `4c0a2ab86266`.*

Learn then Test (Angelopoulos, Bates, Candès, Jordan, Lei — arXiv 2021; Ann. Appl. Stat. 2025) controls risk for ANY loss and ANY hyperparameter grid, where conformal risk control needs one monotone loss: it reframes calibration as multiple testing, computing for each lambda a super-uniform p-value for the null 'R(lambda) > alpha' and returning the lambdas a family-wise-error-controlling procedure rejects, so P(R(lambda) <= alpha for ALL returned lambda) >= 1 - delta. This module uses the EXACT binomial-tail p-value in rational arithmetic and proves super-uniformity and FWER control by exhaustive enumeration; a risk-controlled hyperparameter selection inherits checked machinery rather than a re-derived multiple-testing loop.

## Claim

<!-- claim:CLAIM-LIB-LTT-001 checks_matched -->
The vendored Learn-then-Test library passes all 43 checks with 0 mismatches: the exact binomial-tail p-value P(Bin(n, alpha) <= k) matches 5 hand-computed anchors (P(Bin(10,1/2)<=0)=1/1024) and an independent Fraction re-derivation; SUPER-UNIFORMITY is ENUMERATED — under the null P(p <= u) <= u holds at every achievable threshold over three (n, alpha) settings (30/30); and FAMILY-WISE ERROR is ENUMERATED EXACTLY as exact Fractions over all 343 joint outcomes of 3 independent nulls, with both the Bonferroni and fixed-sequence procedures bounding P(any false rejection) <= delta (2/2); plus 6 procedure-semantics checks (fixed-sequence stops at the first non-rejection, Bonferroni is order-free, both return the honest empty set), and 10/10 malformed inputs rejected. Verified value: <!-- v:CLAIM-LIB-LTT-001.checks_matched -->**43**
(`checks_matched`), backed by [`modules/learn_then_test/artifacts/learn_then_test.json`](../modules/learn_then_test/artifacts/learn_then_test.json).

## Vendor it

Ships `learn_then_test.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/4c0a2ab862666b7c7cf7ba603db6166b04af844a05200f9c75f16815c8080d4c --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **arXiv:2110.01052; Ann. Appl. Stat. 19(2):1641-1662** — Learn then Test: Calibrating Predictive Algorithms to Achieve Risk Control. [https://arxiv.org/abs/2110.01052](https://arxiv.org/abs/2110.01052)
- **arXiv:2208.02814** — Conformal Risk Control. [https://arxiv.org/abs/2208.02814](https://arxiv.org/abs/2208.02814)
