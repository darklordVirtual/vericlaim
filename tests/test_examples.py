# SPDX-License-Identifier: Apache-2.0
"""Tests for the greetings and tipcalc examples, and that their committed
artifacts stay honest (match a fresh recomputation)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


# ── greetings (capability claim) ────────────────────────────────────────────

def test_greetings_supports_registered_count():
    sys.path.insert(0, str(ROOT / "examples" / "greetings" / "src"))
    import greetings  # noqa: E402

    art = json.loads(
        (ROOT / "examples" / "greetings" / "artifacts" / "greetings.json")
        .read_text(encoding="utf-8"))
    assert art["n_languages"] == len(greetings.supported_languages())
    assert greetings.greet("Ada", "no").startswith("Hei")
    assert greetings.greet("Ada", "xx").startswith("Hello")  # fallback


# ── tipcalc (correctness claim) ─────────────────────────────────────────────

def test_tipcalc_all_reference_cases_pass():
    base = ROOT / "examples" / "tipcalc"
    sys.path.insert(0, str(base / "src"))
    sys.path.insert(0, str(base))
    from cases import CASES  # noqa: E402
    from tipcalc import total_with_tip  # noqa: E402

    passing = sum(total_with_tip(b, t) == exp for b, t, exp in CASES)
    art = json.loads((base / "artifacts" / "tipcalc.json").read_text(encoding="utf-8"))
    assert passing == art["cases_passing"] == art["cases_total"] == len(CASES)
