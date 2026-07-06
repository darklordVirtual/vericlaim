# SPDX-License-Identifier: Apache-2.0
"""End-to-end test of autonomous operation and development ("autonom drift og
utvikling") against the bounded self-improvement machinery.

It drives a full cycle on a THROWAWAY scaffolded repo and asserts two things:

  1. Safe DEVELOPMENT is admitted — an autonomous agent that adds a claim and
     more tests passes the non-weakening envelope.
  2. Autonomous DRIFT is blocked — demotion, claim removal, editing the verifier
     core, and (end-to-end) corrupting the register so the REAL gate goes red are
     all refused by the envelope and/or the gate.

Run it any time: `python3 tools/autonomous_cycle_demo.py`. It mutates only a temp
directory, never your repo. Deterministic: no clocks, no randomness.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vericlaim.config import load_config  # noqa: E402
from vericlaim.gate import run  # noqa: E402
from vericlaim.scaffold import init  # noqa: E402
from vericlaim.selfimprove import (  # noqa: E402
    PROTECTED_CORE,
    Snapshot,
    check_non_weakening,
)


def run_demo(root: Path) -> dict:
    """Run one autonomous cycle in *root* and return a structured result.

    Every value is a boolean that must be True for the system to be SAFE:
    development admitted, and every drift vector blocked."""
    init(root)
    cfg = load_config(root)

    # 1. Baseline: a fresh scaffold passes the real gate.
    baseline_gate_green = run(cfg, quiet=True) == 0
    base = Snapshot.capture(cfg, gate_ok=baseline_gate_green, test_count=100)

    # 2. Safe development: add a claim + more tests -> envelope ADMITS.
    developed = Snapshot(
        {**base.claim_levels, "NEW-1": 3}, base.test_count + 5,
        base.baseline_count, base.core_hashes, gate_ok=True)
    development_admitted = check_non_weakening(base, developed) == []

    # A baseline that actually holds a claim, so demotion/removal are meaningful.
    with_claim = Snapshot({"C-1": 3}, 100, 0, base.core_hashes, gate_ok=True)

    # 3. Autonomous drift attempts — each must be BLOCKED (non-empty result).
    drift_demote_blocked = bool(check_non_weakening(
        with_claim, Snapshot({"C-1": 1}, 100, 0, base.core_hashes, gate_ok=True)))
    drift_remove_blocked = bool(check_non_weakening(
        with_claim, Snapshot({}, 100, 0, base.core_hashes, gate_ok=True)))
    drift_shrink_tests_blocked = bool(check_non_weakening(
        with_claim, Snapshot({"C-1": 3}, 1, 0, base.core_hashes, gate_ok=True)))
    hacked_core = {**base.core_hashes, PROTECTED_CORE[0]: "HACKED"}
    drift_core_edit_blocked = bool(check_non_weakening(
        with_claim, Snapshot({"C-1": 3}, 100, 0, hacked_core, gate_ok=True)))

    # 4. End-to-end: corrupt the register so the REAL gate goes red, then confirm
    #    the gate fails closed and the envelope refuses the corrupted state.
    cfg.path(cfg.register).write_text("claims:\n  - id: [broken\n", encoding="utf-8")
    gate_after_corruption_green = run(cfg, quiet=True) == 0
    gate_catches_corruption = not gate_after_corruption_green
    corrupt = Snapshot.capture(cfg, gate_ok=gate_after_corruption_green, test_count=100)
    envelope_refuses_red_gate = bool(check_non_weakening(with_claim, corrupt))

    result = {
        "baseline_gate_green": baseline_gate_green,
        "development_admitted": development_admitted,
        "drift_demote_blocked": drift_demote_blocked,
        "drift_remove_blocked": drift_remove_blocked,
        "drift_shrink_tests_blocked": drift_shrink_tests_blocked,
        "drift_core_edit_blocked": drift_core_edit_blocked,
        "gate_catches_corruption": gate_catches_corruption,
        "envelope_refuses_red_gate": envelope_refuses_red_gate,
    }
    result["ALL_SAFE"] = all(result.values())
    return result


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="vericlaim-autocycle-") as tmp:
        result = run_demo(Path(tmp))
    print("Autonomous cycle — drift & development test")
    print("=" * 52)
    labels = {
        "baseline_gate_green": "fresh scaffold passes the gate",
        "development_admitted": "safe development admitted (add claim + tests)",
        "drift_demote_blocked": "drift blocked: evidence demotion",
        "drift_remove_blocked": "drift blocked: claim removal",
        "drift_shrink_tests_blocked": "drift blocked: test-count reduction",
        "drift_core_edit_blocked": "drift blocked: verifier-core edit",
        "gate_catches_corruption": "real gate fails closed on register corruption",
        "envelope_refuses_red_gate": "envelope refuses a red-gate candidate",
    }
    for key, label in labels.items():
        mark = "PASS" if result[key] else "FAIL"
        print(f"  [{mark}] {label}")
    print("=" * 52)
    ok = result["ALL_SAFE"]
    print(f"  {'ALL SAFE — autonomous drift is bounded' if ok else 'UNSAFE — a drift vector was not blocked'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
