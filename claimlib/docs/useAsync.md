# useAsync React hook (async request state machine)

*Subject area: React / UI State. Language: react. Vendorable bundle `22774916c52e`.*

Most async-UI bugs are state-machine bugs, not markup: a request is simultaneously loading, has stale data, and might error, and ad-hoc booleans (isLoading, hasError) drift out of sync. The durable fix is to model the request as an explicit status: idle | pending | success | error and drive it with a pure reducer, keeping the React hook a thin binding so the transitions are unit-testable without a DOM. useAsync does exactly that: async.logic.ts is the reducer over {status, data, error} and useAsync.tsx wraps it in useReducer with a run() that dispatches start then resolve/reject. Vendor both; the claim proves the core transitions, so you inherit a checked request state machine rather than re-deriving loading-flag logic in every component.

## Claim

<!-- claim:CLAIM-LIB-USEASYNC-001 correct -->
The pure async state machine behind the useAsync React hook produces the correct next-state on every one of a fixed 9-row transition table with independently hand-written expected states (correct = n_cases = 9, errors = 0): start -> pending always clears error and preserves prior data (stale-while-revalidate), resolve -> success sets data and clears error, and reject -> error sets error and preserves prior data, across idle/pending/success/error origins including falsy (0) resolve data. Verified value: <!-- v:CLAIM-LIB-USEASYNC-001.correct -->**9**
(`correct`), backed by [`react/useAsync/artifacts/useAsync.json`](../react/useAsync/artifacts/useAsync.json).

## Vendor it

Ships `useAsync.tsx`, `async.logic.ts` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/22774916c52eb9df6a80356b7087524319f1349692dc578613cba67e14e5b5bd --target .
```
