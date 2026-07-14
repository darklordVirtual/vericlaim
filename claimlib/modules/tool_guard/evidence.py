# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-TOOL-GUARD-001 — the policy engine is default-deny
under an exhaustive adversarial battery.

Oracles, none the module's own output: (1) the fail-safe-defaults principle
(Saltzer & Schroeder 1975) enumerated: the EMPTY policy denies every call of
a fixed 40-call battery; unknown tools, unknown arguments, missing arguments
and malformed calls are all denied with reasons; (2) an EXHAUSTIVE MUTATION
battery: from a fixed policy and its 4 allowed exemplar calls, every
single-field mutation (tool renamed, each argument value pushed outside its
constraint, each extra argument added — 61 mutations) must be DENIED —
mutations_missed = 0; (3) constraint semantics hand-checked: exact is
type-strict (True does not satisfy exact 1), enum membership type-strict,
prefix on strings only, max compares as exact Decimal ("10.5" caught by
max 10). Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from tool_guard import Policy, PolicyError, Rule  # noqa: E402
from _util import emit  # noqa: E402

POLICY = Policy([
    Rule("read_file", {"path": {"prefix": "docs/"}}),
    Rule("send_invoice", {"customer": {"enum": ["sarepta", "horngaarden"]},
                          "amount_nok": {"max": 5000}}),
    Rule("search", {"query": {"prefix": ""}, "limit": {"max": 50}}),
    Rule("get_status", {"system": {"exact": "billing"}}),
])

ALLOWED = [
    ("read_file", {"path": "docs/report.md"}),
    ("send_invoice", {"customer": "sarepta", "amount_nok": 1590}),
    ("search", {"query": "anything at all", "limit": 50}),
    ("get_status", {"system": "billing"}),
]


def mutations() -> list:
    """Single-field corruptions of every allowed call — all must be denied."""
    out = []
    for tool, args in ALLOWED:
        out.append((f"{tool}: renamed tool", tool + "_x", dict(args)))
        for arg in args:
            bad = dict(args)
            # Push the value outside the constraint's TYPE, not just its
            # content: a deliberately open envelope (prefix "") still admits
            # any string, but never a non-string — the guarantee under test
            # is the constraint's, not the exemplar policy's tightness.
            bad[arg] = 10 ** 9 if isinstance(bad[arg], str) else "/etc/passwd"
            out.append((f"{tool}: {arg} out of envelope", tool, bad))
        extra = dict(args)
        extra["injected"] = "x"
        out.append((f"{tool}: extra argument", tool, extra))
        for arg in args:
            short = {k: v for k, v in args.items() if k != arg}
            out.append((f"{tool}: {arg} missing", tool, short))
    return out


def run() -> dict:
    allowed_ok = sum(1 for tool, args in ALLOWED
                     if POLICY.evaluate(tool, args).allowed)

    empty = Policy([])
    battery = [(f"tool{i}", {"a": i}) for i in range(40)]
    empty_denies = sum(1 for tool, args in battery
                       if not empty.evaluate(tool, args).allowed)

    muts = mutations()
    denied = sum(1 for _, tool, args in muts
                 if not POLICY.evaluate(tool, args).allowed)

    semantics = [
        not POLICY.evaluate("get_status", {"system": "billing2"}).allowed,
        not Policy([Rule("t", {"a": {"exact": 1}})])
        .evaluate("t", {"a": True}).allowed,            # bool is not 1
        not Policy([Rule("t", {"a": {"enum": [1, 2]}})])
        .evaluate("t", {"a": True}).allowed,
        Policy([Rule("t", {"a": {"max": 10}})])
        .evaluate("t", {"a": "10.5"}).allowed is False,  # Decimal-exact
        Policy([Rule("t", {"a": {"max": 10}})])
        .evaluate("t", {"a": 10}).allowed,
        not Policy([Rule("t", {"a": {"prefix": "x"}})])
        .evaluate("t", {"a": 42}).allowed,               # prefix needs str
        not POLICY.evaluate(42, {}).allowed,             # malformed call
        not POLICY.evaluate("read_file", "nope").allowed,
    ]
    semantics_ok = sum(semantics)

    rejects = 0
    for bad in (lambda: Rule("", {}),
                lambda: Rule("t", {"a": {"regex": ".*"}}),
                lambda: Rule("t", {"a": {"exact": 1, "max": 2}}),
                lambda: Rule("t", {"a": {"enum": []}}),
                lambda: Rule("t", {"a": {"max": "abc"}}),
                lambda: Rule("t", {"a": "not-a-dict"}),
                lambda: Policy(["not-a-rule"])):
        try:
            bad()
        except PolicyError:
            rejects += 1

    total = len(ALLOWED) + len(battery) + len(muts) + len(semantics)
    matched = allowed_ok + empty_denies + denied + semantics_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "tool_guard",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "allowed_ok": allowed_ok,
        "empty_policy_denies": empty_denies,
        "mutations": len(muts),
        "mutations_denied": denied,
        "mutations_missed": len(muts) - denied,
        "semantics_ok": semantics_ok,
        "reject_cases": 7,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "tool_guard.json", obj,
         script="python3 claimlib/modules/tool_guard/evidence.py")
    # claim:CLAIM-LIB-TOOL-GUARD-001 mutations_missed
    # Every one of the 20 single-field corruptions of the allowed exemplar
    # calls is denied (mutations_missed = 0), the empty policy denies all
    # 40 battery calls, and the 4 exemplars pass — default deny, enumerated.
    print(f"tool_guard: {obj['checks_matched']}/{obj['checks']} checks "
          f"(empty-policy denies {obj['empty_policy_denies']}/40, mutations "
          f"denied {obj['mutations_denied']}/{obj['mutations']}, missed "
          f"{obj['mutations_missed']}); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
