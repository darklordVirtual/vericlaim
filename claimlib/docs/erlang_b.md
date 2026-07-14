# Erlang B blocking probability + circuit planner

*Subject area: Telecom / Traffic Engineering. Language: python. Vendorable bundle `c11c6e9a0d43`.*

Erlang B answers the sizing question of every loss system -- how many circuits (trunks, DSP channels, charging points) does A erlangs of offered traffic need so that at most a target fraction of arrivals is blocked? B(N, A) = (A^N/N!)/sum(A^x/x!), computed here with the overflow-free recursion B(n) = A*B(n-1)/(n + A*B(n-1)), plus the planner's inverse. The claim proves the recursion IS the closed formula (exact-rational agreement) and matches the published engineering tables, so an ISP or telco vendoring it inherits checked dimensioning math.

## Claim

<!-- claim:CLAIM-LIB-ERLANG-B-001 checks_matched -->
The vendored Erlang B library passes all 20 checks with 0 mismatches: the stable recursion agrees with the closed formula recomputed in exact rational arithmetic on all 8 cases to 12 decimal places, satisfies B(1,A) = A/(1+A) algebraically on 4, reproduces the 3 published traffic-table rows for 10 circuits (4.461 E at 1% blocking, 5.092 E at 2%, 6.216 E at 5%) within table precision with the planner inverse recovering N = 10 for each, and is monotone in circuits and traffic. Verified value: <!-- v:CLAIM-LIB-ERLANG-B-001.checks_matched -->**20**
(`checks_matched`), backed by [`modules/erlang_b/artifacts/erlang_b.json`](../modules/erlang_b/artifacts/erlang_b.json).

## Vendor it

Ships `erlang_b.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/c11c6e9a0d4302ba191bac17e6e97cdeefcafdb3724108e374244ce0426f2288 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **Elektroteknikeren, vol. 13 (1917); P.O.E.E.J. vol. 10 (1918), pp. 189-197** — Solution of some Problems in the Theory of Probabilities of Significance in Automatic Telephone Exchanges. [https://en.wikipedia.org/wiki/Erlang_(unit)#cite_note-erlang1917-4](https://en.wikipedia.org/wiki/Erlang_(unit)#cite_note-erlang1917-4)
