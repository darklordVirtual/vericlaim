// SPDX-License-Identifier: Apache-2.0
// usePagination.tsx — a drop-in React hook, a thin binding over the tested
// pure core in pagination.logic.ts. Vendor both files; the claim is on the core.
import { useState, useMemo, useCallback } from "react";
import { paginate, type Pagination } from "./pagination.logic.ts";

export interface UsePagination extends Pagination {
  setPage: (page: number) => void;
  next: () => void;
  prev: () => void;
}

/**
 * Controlled pagination state for a list of `total` items in `pageSize` chunks.
 * Returns the current window (indices, flags) plus setters. All range logic is
 * delegated to `paginate`, so the page is always clamped into bounds.
 */
export function usePagination(
  total: number,
  pageSize: number,
  initialPage = 1,
): UsePagination {
  const [page, setPage] = useState(initialPage);
  const view = useMemo(() => paginate(total, pageSize, page), [total, pageSize, page]);
  const goto = useCallback((p: number) => setPage(p), []);
  const next = useCallback(() => setPage((p) => p + 1), []);
  const prev = useCallback(() => setPage((p) => p - 1), []);
  // Reflect the clamped page back so callers never hold an out-of-range value.
  return { ...view, setPage: goto, next, prev };
}
