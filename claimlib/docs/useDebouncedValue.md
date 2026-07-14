# useDebouncedValue React hook

*Subject area: React / UI State. Language: react. Vendorable bundle `134ba87eece1`.*

Debouncing coalesces a rapid stream of events (keystrokes, resize, scroll) into a single trailing update that fires only after activity has been quiet for delayMs, so expensive work runs once instead of on every change. The effective React pattern is to put the timing model in a pure, framework-agnostic function and make the hook a thin binding, so the off-by-one-prone logic is unit-testable without a DOM or fake timers. debounce.logic.ts is a deterministic simulator: emitDebounced(events, delayMs) returns, for a trace of timed values, exactly the emissions a trailing debounce would produce, and useDebouncedValue.tsx wraps that same model in useState + useEffect + setTimeout. Vendor both; the claim proves the core timing is correct, so you inherit checked debounce behaviour rather than re-deriving timer-reset logic in every project.

## Claim

<!-- claim:CLAIM-LIB-USEDEBOUNCED-001 correct -->
The pure trailing-debounce core behind the useDebouncedValue React hook reproduces the hand-computed emissions on every one of a fixed 9-case reference battery of event traces (correct = n_cases = 9, errors = 0): rapid bursts collapse to their last value, events spaced at least delayMs apart each emit at eventTime + delayMs, a gap exactly equal to delayMs counts as fired, and a gap one below is coalesced. Expected emissions are derived by hand from the trailing-debounce definition, independent of the module. Verified value: <!-- v:CLAIM-LIB-USEDEBOUNCED-001.correct -->**9**
(`correct`), backed by [`react/useDebouncedValue/artifacts/useDebouncedValue.json`](../react/useDebouncedValue/artifacts/useDebouncedValue.json).

## Vendor it

Ships `useDebouncedValue.tsx`, `debounce.logic.ts` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/134ba87eece12362afb41be56b3ad8444f5dbf3c1d66a87335d02e9fbc4dae42 --target .
```
