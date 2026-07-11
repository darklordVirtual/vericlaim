# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-LRU-001 — the fixed-capacity LRU cache returns the
right value for every lookup and evicts exactly the least-recently-used key.

Replays two fixed operation traces (LeetCode-146 style) whose expected
get-results AND expected post-operation key sets are HAND-COMPUTED below,
independently of this module — the cache's own output is never used as the
oracle. For every step we check the get return value, the resulting key set,
and the invariant that size never exceeds capacity. Deterministic: same
artifact on every run.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (lru.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from lru import LRU  # noqa: E402
from _util import emit  # noqa: E402

# Each step is (op, key, value, expected_get, expected_keys_after).
#   op              : "put" or "get"
#   value           : the put value (ignored for get)
#   expected_get    : hand-derived get return value, or None (also the miss
#                     result). Only checked when op == "get".
#   expected_keys_after : the FULL key set present after the step, given as a
#                     sorted list. Hand-computed by tracking recency order by
#                     hand; never read back from the cache.
GET = "get"
PUT = "put"

# --- Trace A: capacity 3, exercises hit-refresh, eviction, and update-in-place.
# Hand-traced recency order (LRU..MRU) shown in comments; eviction removes the
# leftmost key when a NEW key is inserted at capacity.
TRACE_A = {
    "name": "cap3_mixed",
    "capacity": 3,
    "steps": [
        # op   key  val  expect_get  keys_after (sorted)
        (PUT, 1, 10, None, [1]),           # [1]
        (PUT, 2, 20, None, [1, 2]),        # [1,2]
        (PUT, 3, 30, None, [1, 2, 3]),     # [1,2,3]  (now full)
        (GET, 2, None, 20, [1, 2, 3]),     # hit -> [1,3,2]
        (PUT, 4, 40, None, [2, 3, 4]),     # full: evict LRU=1 -> [3,2,4]
        (GET, 1, None, None, [2, 3, 4]),   # miss, order unchanged [3,2,4]
        (GET, 3, None, 30, [2, 3, 4]),     # hit -> [2,4,3]
        (PUT, 2, 25, None, [2, 3, 4]),     # update key 2 -> [4,3,2] (no evict)
        (PUT, 5, 50, None, [2, 3, 5]),     # full: evict LRU=4 -> [3,2,5]
        (GET, 4, None, None, [2, 3, 5]),   # miss (4 was evicted)
        (GET, 2, None, 25, [2, 3, 5]),     # hit, updated value 25 -> [3,5,2]
        (GET, 5, None, 50, [2, 3, 5]),     # hit -> [3,2,5]
    ],
}

# --- Trace B: the canonical LeetCode-146 example, capacity 2.
TRACE_B = {
    "name": "leetcode146_cap2",
    "capacity": 2,
    "steps": [
        (PUT, 1, 1, None, [1]),            # [1]
        (PUT, 2, 2, None, [1, 2]),         # [1,2]
        (GET, 1, None, 1, [1, 2]),         # hit -> [2,1]
        (PUT, 3, 3, None, [1, 3]),         # full: evict LRU=2 -> [1,3]
        (GET, 2, None, None, [1, 3]),      # miss (2 evicted)
        (PUT, 4, 4, None, [3, 4]),         # full: evict LRU=1 -> [3,4]
        (GET, 1, None, None, [3, 4]),      # miss (1 evicted)
        (GET, 3, None, 3, [3, 4]),         # hit -> [4,3]
        (GET, 4, None, 4, [3, 4]),         # hit -> [3,4]
    ],
}

TRACES = [TRACE_A, TRACE_B]


def _run_trace(trace: dict) -> dict:
    cache = LRU(trace["capacity"])
    cap = trace["capacity"]
    rows = []
    correct = 0
    max_size = 0
    for op, key, value, expected_get, expected_keys in trace["steps"]:
        got_get = None
        if op == PUT:
            cache.put(key, value)
        else:
            got_get = cache.get(key)
        size = len(cache)
        max_size = max(max_size, size)
        got_keys = sorted(cache.keys())
        keys_ok = (got_keys == sorted(expected_keys))
        get_ok = (op == PUT) or (got_get == expected_get)
        size_ok = size <= cap
        step_ok = keys_ok and get_ok and size_ok
        correct += int(step_ok)
        rows.append({
            "op": op, "key": key,
            "expected_get": expected_get if op == GET else None,
            "computed_get": got_get if op == GET else None,
            "expected_keys": sorted(expected_keys),
            "computed_keys": got_keys,
            "size": size, "size_ok": size_ok, "correct": step_ok,
        })
    return {
        "name": trace["name"], "capacity": cap,
        "n_steps": len(trace["steps"]), "correct": correct,
        "max_size_observed": max_size, "steps": rows,
    }


def run() -> dict:
    results = [_run_trace(t) for t in TRACES]
    n_operations = sum(r["n_steps"] for r in results)
    operations_correct = sum(r["correct"] for r in results)
    mismatches = n_operations - operations_correct
    # size never exceeded capacity in any trace
    size_invariant_ok = all(r["max_size_observed"] <= r["capacity"] for r in results)
    return {
        "schema": "claimlib_lru_v1",
        "module": "lru",
        "n_operations": n_operations,
        "operations_correct": operations_correct,
        "mismatches": mismatches,
        "size_invariant_ok": size_invariant_ok,
        "traces": results,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "lru.json", obj,
         script="python3 claimlib/modules/lru/evidence.py")
    # claim:CLAIM-LIB-LRU-001 operations_correct
    # All 21 operations across the two hand-traced batteries (12 in cap3_mixed +
    # 9 in leetcode146_cap2) match their independently hand-computed get-results
    # and key sets, so operations_correct = 21 and mismatches = 0.
    print(f"lru: {obj['operations_correct']}/{obj['n_operations']} operations "
          f"match hand-derived trace ({obj['mismatches']} mismatches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
