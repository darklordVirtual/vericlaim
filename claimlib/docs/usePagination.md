# usePagination React hook

*Subject area: React / UI State. Language: react. Vendorable bundle `dd5c1b35bbd6`.*

A huge share of React bugs live in state logic, not markup. The effective pattern is to put the logic in a pure, framework-agnostic function and make the hook a thin binding — so the hard part is unit-testable without a DOM. usePagination does exactly that: pagination.logic.ts computes the clamped page, slice indices and prev/next flags, and usePagination.tsx wraps it in useState/useMemo. Vendor both; the claim proves the core is correct, so you inherit checked pagination state rather than re-deriving off-by-one slice math in every project.

## Claim

<!-- claim:CLAIM-LIB-USEPAGINATION-001 correct -->
The pure pagination core behind the usePagination React hook computes the correct page window (page clamp, slice indices, item count, prev/next flags) on every one of a fixed reference battery with independently hand-written expected windows (correct = n_cases, errors = 0), and fails closed on all 4 invalid-sizing inputs. Verified value: <!-- v:CLAIM-LIB-USEPAGINATION-001.correct -->**8**
(`correct`), backed by [`react/usePagination/artifacts/usePagination.json`](../react/usePagination/artifacts/usePagination.json).

## Vendor it

Ships `usePagination.tsx`, `pagination.logic.ts` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/dd5c1b35bbd61712df91862f79197e324e330d7e9961a89627a3f1b214b32e25 --target .
```
