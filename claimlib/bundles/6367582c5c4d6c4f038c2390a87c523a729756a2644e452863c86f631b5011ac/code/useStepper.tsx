// SPDX-License-Identifier: Apache-2.0
// useStepper.tsx — a drop-in React hook, a thin binding over the tested pure
// core in stepper.logic.ts. Vendor both files; the claim is on the core.
import { useState, useMemo, useCallback } from "react";
import { stepper, next as nextIdx, prev as prevIdx, goto as gotoIdx, type StepperState } from "./stepper.logic.ts";

export interface UseStepper extends StepperState {
  goto: (index: number) => void;
  next: () => void;
  prev: () => void;
}

/**
 * Controlled multi-step wizard state over `stepCount` steps. Returns the current
 * derived view (index, isFirst/isLast, progress) plus navigation setters. All
 * clamping is delegated to the pure core, so the index is always in bounds.
 */
export function useStepper(stepCount: number, initialIndex = 0): UseStepper {
  const [index, setIndex] = useState(initialIndex);
  const view = useMemo(() => stepper(stepCount, index), [stepCount, index]);
  const goto = useCallback((i: number) => setIndex(gotoIdx(stepCount, i)), [stepCount]);
  const next = useCallback(() => setIndex((cur) => nextIdx(stepCount, cur)), [stepCount]);
  const prev = useCallback(() => setIndex((cur) => prevIdx(stepCount, cur)), [stepCount]);
  // Reflect the clamped index back so callers never hold an out-of-range value.
  return { ...view, goto, next, prev };
}
