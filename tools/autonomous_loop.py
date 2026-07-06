# SPDX-License-Identifier: Apache-2.0
"""Autonomous governance loop — iterative, bounded, operator-stoppable.

Runs round after round. Each round is a full governance heartbeat:

  gate (adopt) · gate (strict) · reproduce · full test suite ·
  autonomous-cycle safety test · capture a Snapshot · compare to the PREVIOUS
  round with the non-weakening envelope · run the propose-only improver.

The loop keeps going only while everything is green AND the round did not weaken
the previous round. It fails closed: any regression, red gate, or inter-round
weakening HALTS the loop and reports — autonomy is only extended while it stays
defensible. Development stays propose-only: the loop never applies, commits,
pushes, or merges. A human acts on proposals; the envelope guards whatever they
apply.

Operator stop:
  * create claims/STOP_SELF_IMPROVEMENT (the kill switch), or
  * interrupt the process.

Usage: python3 tools/autonomous_loop.py [rounds]   (default 3; 0 = until stopped)
"""
from __future__ import annotations

import contextlib
import io
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from autonomous_cycle_demo import run_demo  # noqa: E402
from vericlaim.config import load_config  # noqa: E402
from vericlaim.selfimprove import Snapshot, check_non_weakening, propose, stopped  # noqa: E402

PY = sys.executable


def _cli(args: list[str]) -> tuple[bool, str]:
    r = subprocess.run([PY, "-m", "vericlaim", *args], cwd=ROOT,
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def _pytest() -> tuple[bool, int]:
    r = subprocess.run([PY, "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True)
    m = re.search(r"(\d+) passed", r.stdout + r.stderr)
    return r.returncode == 0, (int(m.group(1)) if m else 0)


def run_round(n: int, prev: Snapshot | None) -> tuple[Snapshot | None, bool, list[str]]:
    """Execute one heartbeat round. Returns (snapshot, healthy, notes)."""
    notes: list[str] = []
    cfg = load_config(ROOT)

    gate_adopt, _ = _cli(["--quiet"])
    gate_strict, _ = _cli(["--profile", "strict", "--quiet"])
    repro_ok, _ = _cli(["reproduce", "--quiet"])
    tests_ok, test_count = _pytest()
    with tempfile.TemporaryDirectory(prefix="vericlaim-loop-") as tmp:
        with contextlib.redirect_stdout(io.StringIO()):
            cycle = run_demo(Path(tmp))
    cycle_ok = bool(cycle.get("ALL_SAFE"))

    print(f"  gate(adopt)={_m(gate_adopt)}  gate(strict)={_m(gate_strict)}  "
          f"reproduce={_m(repro_ok)}  tests={_m(tests_ok)}({test_count})  "
          f"autocycle={_m(cycle_ok)}")

    healthy = all([gate_adopt, gate_strict, repro_ok, tests_ok, cycle_ok])
    if not healthy:
        notes.append("a health check failed this round")

    snap = Snapshot.capture(cfg, gate_ok=gate_adopt, test_count=test_count)

    if prev is not None:
        weakenings = check_non_weakening(prev, snap)
        if weakenings:
            healthy = False
            notes.append("inter-round weakening detected: " + "; ".join(weakenings))
            print(f"  [DRIFT] round {n} weakened round {n-1}: {weakenings}")
        else:
            print(f"  [STABLE] round {n} is non-weakening vs round {n-1} "
                  f"({len(snap.claim_levels)} claims, {test_count} tests, "
                  f"{snap.baseline_count} baseline)")

    suggestions = propose(cfg)
    kinds: dict[str, int] = {}
    for s in suggestions:
        kinds[s.kind] = kinds.get(s.kind, 0) + 1
    print(f"  [PROPOSE-ONLY] {len(suggestions)} suggestion(s): " +
          (", ".join(f"{k}×{v}" for k, v in sorted(kinds.items())) or "none"))
    return snap, healthy, notes


def _m(ok: bool) -> str:
    return "OK" if ok else "FAIL"


def main() -> int:
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    max_seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    print("Autonomous governance loop — verbose; propose-only; envelope-guarded")
    print(f"rounds={'until stopped' if rounds == 0 else rounds}  interval={interval}s"
          f"  max_seconds={'none' if max_seconds <= 0 else max_seconds}")
    print(f"Operator stop: create {ROOT / 'claims' / 'STOP_SELF_IMPROVEMENT'} or interrupt.")
    print("=" * 68)
    start = time.monotonic()
    prev: Snapshot | None = None
    n = 0
    while rounds == 0 or n < rounds:
        elapsed = time.monotonic() - start
        if max_seconds > 0 and elapsed >= max_seconds:
            print(f"\n[DONE] time budget reached ({max_seconds:g}s) after {n} round(s).")
            break
        n += 1
        cfg = load_config(ROOT)
        if stopped(cfg):
            print(f"[HALT] round {n}: kill-switch present — operator stopped the loop.")
            break
        print(f"\n── round {n} (t+{elapsed:.0f}s) ──", flush=True)
        snap, healthy, notes = run_round(n, prev)
        if not healthy:
            print(f"[HALT] round {n} failed closed: {notes}")
            print("Autonomy withdrawn — a human must review before it may continue.")
            return 1
        prev = snap
        if interval > 0 and (rounds == 0 or n < rounds):
            remaining = (max_seconds - (time.monotonic() - start)) if max_seconds > 0 else interval
            if max_seconds > 0 and remaining <= 0:
                continue
            nap = min(interval, remaining) if max_seconds > 0 else interval
            print(f"  … sleeping {nap:g}s until next round (kill-switch honored on wake)",
                  flush=True)
            time.sleep(nap)
    total = time.monotonic() - start
    print("\n" + "=" * 68)
    print(f"[OK] {n} round(s) over {total:.0f}s; every round green and non-weakening. "
          f"Loop applied nothing (propose-only).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
