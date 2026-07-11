# usePagination React hook

*Subject area: React / UI State. Language: react. Vendorable bundle `44f7c6ca2b4e`.*

A huge share of React bugs live in state logic, not markup. The effective pattern is to put the logic in a pure, framework-agnostic function and make the hook a thin binding — so the hard part is unit-testable without a DOM. usePagination does exactly that: pagination.logic.ts computes the clamped page, slice indices and prev/next flags, and usePagination.tsx wraps it in useState/useMemo. Vendor both; the claim proves the core is correct, so you inherit checked pagination state rather than re-deriving off-by-one slice math in every project.

## Claim

<!-- claim:CLAIM-LIB-USEPAGINATION-001 correct -->
The pure pagination core behind the usePagination React hook computes the correct page window (page clamp, slice indices, item count, prev/next flags) on every one of a fixed reference battery with independently hand-written expected windows (correct = n_cases, errors = 0), and fails closed on all 4 invalid-sizing inputs. Verified value: <!-- v:CLAIM-LIB-USEPAGINATION-001.correct -->**8**
(`correct`), backed by [`react/usePagination/artifacts/usePagination.json`](../react/usePagination/artifacts/usePagination.json).

## Vendor it

Ships `usePagination.tsx`, `pagination.logic.ts` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/44f7c6ca2b4e90c8dddb16d751668a5f98b0a3afc8e8545775c11bc12c89b501 --target .
```
