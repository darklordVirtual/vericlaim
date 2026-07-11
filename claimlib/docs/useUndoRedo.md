# useUndoRedo React hook

*Subject area: React / UI State. Language: react. Vendorable bundle `6fa7c59a513d`.*

Undo/redo is most robustly modeled as three immutable stacks — past states, the present, and a future (redo) stack — rather than mutating one buffer. A new edit (push) records the old present onto past and clears future, so an edit made after undoing forks history and discards the abandoned redo branch, matching how editors behave. Keeping this logic in a pure, framework-agnostic core makes the tricky part (stack transitions, boundary no-ops) unit-testable without a DOM, while the React hook stays a thin useReducer binding. Vendor both; the claim proves the core transitions are correct, so you inherit checked history state instead of re-deriving stack juggling per project.

## Claim

<!-- claim:CLAIM-LIB-USEUNDOREDO-001 correct -->
The pure undo/redo core behind the useUndoRedo React hook (a {past, present, future} history with push/undo/redo/canUndo/canRedo) produces the correct present value and canUndo/canRedo flags after every step of a fixed 12-action reference sequence with independently hand-computed expected snapshots (correct = n_cases = 12, errors = 0), including redo-stack clearing on a new set(), and undo-at-base / redo-at-tip fail-closed no-ops. Verified value: <!-- v:CLAIM-LIB-USEUNDOREDO-001.correct -->**12**
(`correct`), backed by [`react/useUndoRedo/artifacts/useUndoRedo.json`](../react/useUndoRedo/artifacts/useUndoRedo.json).

## Vendor it

Ships `useUndoRedo.tsx`, `undoredo.logic.ts` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/6fa7c59a513d7aae75ec5f118e579960e742e7a55cf52c5d0b4ee8e62c3c68a3 --target .
```
