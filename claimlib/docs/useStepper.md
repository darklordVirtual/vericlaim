# useStepper React hook

*Subject area: React / UI State. Language: react. Vendorable bundle `c44b9c30aa64`.*

Multi-step wizards are a classic source of off-by-one bugs: clamping the active step, deciding when Back/Next should disable, and computing a progress fraction all invite index errors. The durable pattern is to put that arithmetic in a pure, framework-agnostic function and make the hook a thin binding, so the hard part is unit-testable without a DOM. useStepper does exactly that: stepper.logic.ts derives the clamped index, isFirst/isLast flags, a 0..1 progress value and clamped next/prev targets, and useStepper.tsx wraps it in useState/useMemo. Vendor both; the claim proves the core is correct, so you inherit checked wizard-navigation state rather than re-deriving clamp and progress math in every project.

## Claim

<!-- claim:CLAIM-LIB-USESTEPPER-001 correct -->
The pure stepper core behind the useStepper React hook computes the correct multi-step navigation state (index clamped to [0, stepCount-1], isFirst/isLast flags, progress = index/(stepCount-1) rounded to 4 dp or 0 for a single step, and clamped next/prev targets) on every one of a fixed 11-case reference battery with independently hand-computed expected states (correct = n_cases = 11, errors = 0). Verified value: <!-- v:CLAIM-LIB-USESTEPPER-001.correct -->**11**
(`correct`), backed by [`react/useStepper/artifacts/useStepper.json`](../react/useStepper/artifacts/useStepper.json).

## Vendor it

Ships `useStepper.tsx`, `stepper.logic.ts` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/c44b9c30aa649e219256b03799175e21031073a2e9da2c7fc35bca396f077a2f --target .
```
