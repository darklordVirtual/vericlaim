// SPDX-License-Identifier: Apache-2.0
// stepper.logic.ts — the framework-agnostic core of the useStepper hook.
//
// All the multi-step-wizard navigation math lives here as pure functions, so it
// can be tested deterministically (run under `node`) without a DOM or React. The
// React binding (useStepper.tsx) is a thin wrapper over this — vendor both.

export interface StepperState {
  readonly index: number; // clamped current step, 0-based
  readonly stepCount: number;
  readonly isFirst: boolean;
  readonly isLast: boolean;
  readonly progress: number; // index/(stepCount-1), or 0 when a single step; 4 dp
  readonly nextIndex: number; // clamped index + 1
  readonly prevIndex: number; // clamped index - 1
}

const round4 = (x: number): number => Math.round(x * 1e4) / 1e4;

/** Clamp an arbitrary target index into [0, stepCount-1]. */
export const goto = (stepCount: number, target: number): number => {
  if (!Number.isInteger(stepCount) || stepCount < 1) {
    throw new RangeError(`stepCount must be a positive integer, got ${stepCount}`);
  }
  return Math.min(Math.max(0, Math.trunc(target)), stepCount - 1);
};

/** Move one step forward, clamped to the last step. */
export const next = (stepCount: number, index: number): number => goto(stepCount, goto(stepCount, index) + 1);

/** Move one step back, clamped to the first step. */
export const prev = (stepCount: number, index: number): number => goto(stepCount, goto(stepCount, index) - 1);

/** Pure wizard-navigation math. Clamps `index` into range and derives flags/progress. */
export const stepper = (stepCount: number, index: number): StepperState => {
  const clamped = goto(stepCount, index); // validates stepCount and clamps index
  return {
    index: clamped,
    stepCount,
    isFirst: clamped === 0,
    isLast: clamped === stepCount - 1,
    progress: stepCount === 1 ? 0 : round4(clamped / (stepCount - 1)),
    nextIndex: next(stepCount, clamped),
    prevIndex: prev(stepCount, clamped),
  };
};
