# Shannon entropy, cross-entropy, KL and perplexity

*Subject area: AI Assurance / Information Measures. Language: python. Vendorable bundle `67582f7174a3`.*

Shannon (1948) defined the units AI evaluation is written in: entropy measures a distribution's information in bits, cross-entropy is exactly the training loss of a language model, perplexity its exponential, and KL divergence the drift between model and reference. When an eval report states 'perplexity 12.3', this is the arithmetic behind it. This module implements the four measures with exact input validation and fail-closed infinities; the claim proves Shannon's identities including his own worked example, so evaluation code inherits checked information arithmetic.

## Claim

<!-- claim:CLAIM-LIB-ENTROPY-001 checks_matched -->
The vendored information-measures library passes all 40 checks with 0 mismatches: 10 exact anchors (a fair coin is exactly 1.0 bit; uniform 4/8/16/32-outcome distributions are exactly 2/3/4/5 bits; Shannon's own worked example H(1/2,1/4,1/4) is exactly 1.5 bits; perplexity of uniform-8 is exactly 8) and 30 theorem-shaped properties over a deterministic battery (uniform maximality, Gibbs' inequality KL >= 0, the chain identity H(p,q) = H(p) + KL(p||q) to 1e-12, permutation invariance). Verified value: <!-- v:CLAIM-LIB-ENTROPY-001.checks_matched -->**40**
(`checks_matched`), backed by [`modules/shannon_entropy/artifacts/shannon_entropy.json`](../modules/shannon_entropy/artifacts/shannon_entropy.json).

## Vendor it

Ships `shannon_entropy.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/67582f7174a3a0212570a2a0cd2dc067bb40046fb98dcf58d58cab092d5b0bf0 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **Bell Syst. Tech. J. 27(3): 379-423 (July 1948); 27(4): 623-656 (October 1948)** — A Mathematical Theory of Communication. [https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf)
