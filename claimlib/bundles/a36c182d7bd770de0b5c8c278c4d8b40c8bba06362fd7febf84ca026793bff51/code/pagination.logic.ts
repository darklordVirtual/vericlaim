// SPDX-License-Identifier: Apache-2.0
// pagination.logic.ts — the framework-agnostic core of the usePagination hook.
//
// All the arithmetic that matters lives here as a pure function, so it can be
// tested deterministically (run under `node`) without a DOM or React. The React
// binding (usePagination.tsx) is a thin wrapper over this — vendor both.

export interface Pagination {
  readonly page: number; // clamped current page, 1-based (0 when empty)
  readonly pageCount: number;
  readonly pageSize: number;
  readonly total: number;
  readonly startIndex: number; // inclusive slice start
  readonly endIndex: number; // exclusive slice end
  readonly itemsOnPage: number;
  readonly hasPrev: boolean;
  readonly hasNext: boolean;
}

/** Pure pagination math. Clamps `page` into range; fails closed on bad sizing. */
export const paginate = (total: number, pageSize: number, page: number): Pagination => {
  if (!Number.isInteger(total) || total < 0) {
    throw new RangeError(`total must be a non-negative integer, got ${total}`);
  }
  if (!Number.isInteger(pageSize) || pageSize < 1) {
    throw new RangeError(`pageSize must be a positive integer, got ${pageSize}`);
  }
  const pageCount = total === 0 ? 0 : Math.ceil(total / pageSize);
  const clamped = pageCount === 0 ? 0 : Math.min(Math.max(1, Math.trunc(page)), pageCount);
  const startIndex = pageCount === 0 ? 0 : (clamped - 1) * pageSize;
  const endIndex = pageCount === 0 ? 0 : Math.min(startIndex + pageSize, total);
  return {
    page: clamped,
    pageCount,
    pageSize,
    total,
    startIndex,
    endIndex,
    itemsOnPage: endIndex - startIndex,
    hasPrev: clamped > 1,
    hasNext: clamped > 0 && clamped < pageCount,
  };
};
