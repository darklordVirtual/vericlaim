# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-TOKENBUCKET-001 — the token bucket never lets available
tokens exceed capacity.

Replays the reusable ``tokenbucket`` module over a FIXED chronological event
trace and records, for every event, the token level after refilling (capped) but
before consumption. It counts allowed/denied grants and, crucially, counts
``capacity_violations`` — events where the available level exceeded the bucket's
capacity. The safety property is that this count is exactly 0, even across a long
idle gap that would otherwise "bank" tokens without the clamp.

Deterministic: timestamps are fixed literals, no wall clock, no randomness.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (tokenbucket.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from tokenbucket import TokenBucket  # noqa: E402
from _util import emit  # noqa: E402

# Fixed reference scenario. capacity=3 tokens, refill=1 token/sec, cost=1 each.
CAPACITY = 3.0
REFILL_PER_SEC = 1.0

# A fixed chronological trace of request timestamps (seconds), non-decreasing.
# Four requests fire simultaneously at t=0 (bucket starts full = 3), then two at
# t=1, one at t=2, and one after a long idle gap at t=10. The t=10 event is the
# key test: 8s of refill would add 8 tokens, but the clamp holds the level at
# capacity (3), so no burst is banked.
TRACE = [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 2.0, 10.0]
COST = 1.0

# Independently hand-computed expected outcome (NOT produced by this code).
# Simulating capacity=3, refill=1/s, cost=1, starting full:
#   t=0  level 3 -> allow (2 left)      ALLOW
#   t=0  level 2 -> allow (1 left)      ALLOW
#   t=0  level 1 -> allow (0 left)      ALLOW
#   t=0  level 0 -> 0 < 1               DENY
#   t=1  +1 -> level 1 -> allow (0)     ALLOW
#   t=1  level 0 -> 0 < 1               DENY
#   t=2  +1 -> level 1 -> allow (0)     ALLOW
#   t=10 +8 clamped to 3 -> allow (2)   ALLOW
# => allowed = 6, denied = 2, and every capped level (3,2,1,0,1,0,1,3) <= 3.
EXPECTED_ALLOWED = 6
EXPECTED_DENIED = 2
TOLERANCE = 1e-9


def run() -> dict:
    bucket = TokenBucket(capacity=CAPACITY, refill_per_sec=REFILL_PER_SEC)
    allowed = 0
    denied = 0
    capacity_violations = 0
    max_level = 0.0
    cases = []
    for t in TRACE:
        level = bucket.available(t)          # capped, post-refill, pre-consume
        if level > CAPACITY + TOLERANCE:
            capacity_violations += 1
        if level > max_level:
            max_level = level
        granted = bucket.allow(t, COST)
        if granted:
            allowed += 1
        else:
            denied += 1
        cases.append({
            "t": round(t, 4),
            "level_before": round(level, 4),
            "granted": granted,
            "tokens_after": round(bucket.tokens, 4),
        })
    return {
        "schema": "claimlib_tokenbucket_v1",
        "module": "tokenbucket",
        "capacity": round(CAPACITY, 4),
        "refill_per_sec": round(REFILL_PER_SEC, 4),
        "n_events": len(TRACE),
        "allowed": allowed,
        "denied": denied,
        "capacity_violations": capacity_violations,
        "max_level_observed": round(max_level, 4),
        "cases": cases,
    }


def main() -> int:
    obj = run()
    # Cross-check against the independently hand-computed reference outcome so a
    # regression in the library surfaces here, not just in the metric.
    assert obj["allowed"] == EXPECTED_ALLOWED, obj["allowed"]
    assert obj["denied"] == EXPECTED_DENIED, obj["denied"]
    emit(HERE / "artifacts" / "tokenbucket.json", obj,
         script="python3 claimlib/modules/tokenbucket/evidence.py")
    # claim:CLAIM-LIB-TOKENBUCKET-001 capacity_violations
    # Across all 8 events in the fixed trace — including the t=10 idle gap that
    # would bank 8 tokens without the clamp — the available level never exceeds
    # capacity, so capacity_violations = 0 (allowed = 6, denied = 2).
    print(f"tokenbucket: {obj['allowed']} allowed / {obj['denied']} denied over "
          f"{obj['n_events']} events, capacity_violations={obj['capacity_violations']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
