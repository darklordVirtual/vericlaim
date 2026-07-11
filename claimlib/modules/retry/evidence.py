# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-RETRY-001 — deterministic full-jitter backoff keeps
every delay inside its un-jittered ceiling and reproduces the schedule from a
seed.

Runs the reusable ``retry`` module over a FIXED schedule (attempts 0..15, a
fixed base/cap/seed) and records, for each attempt:

  * the ceiling — computed **independently** here as ``min(cap, base*2**attempt)``
    straight from the spec, NOT read back from the library — and
  * whether the library's jittered delay falls in ``[0, ceiling]``.

It then re-runs the whole schedule with the same seed and checks the delays are
identical. Deterministic: same artifact on every run (hash-based jitter, no time,
no ``random``).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (retry.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from retry import backoff_delay  # noqa: E402
from _util import emit  # noqa: E402

# Fixed reference schedule. base/cap/seed are held constant; attempts run 0..N.
BASE = 1.0
CAP = 60.0
SEED = 1337
N = 15                       # attempts 0..15  ->  N + 1 = 16 delays
ATTEMPTS = list(range(N + 1))


def _reference_ceiling(attempt: int) -> float:
    """Independent, spec-derived ceiling: min(cap, base * 2**attempt).

    Computed here directly from the published full-jitter formula so the bounds
    check does not rely on the library it is meant to verify.
    """
    return float(min(CAP, BASE * (2 ** attempt)))


def run() -> dict:
    schedule = []
    within = 0
    out = 0
    for attempt in ATTEMPTS:
        ceiling = _reference_ceiling(attempt)
        delay = backoff_delay(attempt, BASE, CAP, SEED)
        ok = (0.0 <= delay <= ceiling)
        within += int(ok)
        out += int(not ok)
        schedule.append({"attempt": attempt, "ceiling": ceiling,
                         "delay": delay, "within": ok})

    # Reproduce the whole schedule with the same seed; identical => deterministic.
    replay = [backoff_delay(a, BASE, CAP, SEED) for a in ATTEMPTS]
    original = [row["delay"] for row in schedule]
    deterministic = int(replay == original)

    return {
        "schema": "claimlib_retry_v1",
        "module": "retry",
        "base": BASE,
        "cap": CAP,
        "seed": SEED,
        "n_attempts": len(ATTEMPTS),
        "within_bounds": within,
        "out_of_bounds": out,
        "deterministic": deterministic,
        "schedule": schedule,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "retry.json", obj,
         script="python3 claimlib/modules/retry/evidence.py")
    # claim:CLAIM-LIB-RETRY-001 within_bounds
    # All 16 jittered delays (attempts 0..15) land inside their [0, ceiling]
    # window, so within_bounds = 16 and out_of_bounds = 0; the seeded replay
    # is byte-identical, so deterministic = 1.
    print(f"retry: {obj['within_bounds']}/{obj['n_attempts']} delays within "
          f"bounds, out_of_bounds={obj['out_of_bounds']}, "
          f"deterministic={obj['deterministic']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
