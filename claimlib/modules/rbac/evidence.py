# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-RBAC-001 — the RBAC auditor detects every seeded
excess grant and every seeded separation-of-duties violation, with no false
positives on clean identities.

The reference battery below is a FIXED access-control matrix. Its seeded counts
are established by hand (each user is annotated with why it is clean / excess /
SoD-violating), independent of what the auditor computes. The evidence runs the
reusable ``rbac`` module over it and confirms:

    detected_excess == seeded_excess      (all over-privilege found)
    detected_sod    == seeded_sod         (all toxic pairs found)
    false_positives == 0                  (no clean identity flagged)

Deterministic: same artifact on every run (no time, no randomness).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (rbac.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from rbac import audit  # noqa: E402
from _util import emit  # noqa: E402

# --- Least-privilege baselines: the permissions each role legitimately needs.
ROLE_NEEDS = {
    "viewer":     {"read"},
    "editor":     {"read", "write"},
    "approver":   {"read", "approve"},
    "admin":      {"read", "write", "config", "user_admin"},
    "clerk":      {"read", "pay_create"},
    "releaser":   {"read", "pay_approve"},
    "devops":     {"read", "code_deploy"},
    "reviewer":   {"read", "code_review"},
    # Deliberately over-broad role that bundles both halves of a toxic pair,
    # so an SoD violation exists that is NOT also an excess grant.
    "superclerk": {"read", "pay_create", "pay_approve"},
}

# --- Separation-of-duties toxic pairs: a single identity must not hold both.
#   pair 0: create a payment vs. approve/release it (financial control).
#   pair 1: deploy code vs. review the code being deployed (change control).
SOD_PAIRS = [
    ({"pay_create"}, {"pay_approve"}),
    ({"code_deploy"}, {"code_review"}),
]

# --- The identities. Each carries a hand-derived verdict used to seed the
# expected counts (NOT taken from the auditor's output).
#   user -> (role, granted permissions, expected excess count, is_sod_violation)
IDENTITIES = {
    # ---- Clean: grants match the role baseline exactly. Never flag these. ----
    "alice": ("viewer",   {"read"},                                  0, False),
    "bob":   ("editor",   {"read", "write"},                         0, False),
    "carol": ("approver", {"read", "approve"},                       0, False),
    "grace": ("clerk",    {"read", "pay_create"},                    0, False),  # only one SoD side
    "heidi": ("releaser", {"read", "pay_approve"},                   0, False),  # only other SoD side
    "ivan":  ("devops",   {"read", "code_deploy"},                   0, False),
    "judy":  ("reviewer", {"read", "code_review"},                   0, False),

    # ---- Excess only: over-privileged but no toxic pair held. ----
    "dave":  ("editor",   {"read", "write", "config"},               1, False),  # +config
    "erin":  ("admin",    {"read", "write", "config",
                           "user_admin", "secret_export"},           1, False),  # +secret_export
    "mallory": ("viewer", {"read", "write", "delete"},               2, False),  # +write,+delete

    # ---- Excess AND SoD: the extra perm both over-privileges and trips a pair.
    "oscar": ("clerk",    {"read", "pay_create", "pay_approve"},     1, True),   # +pay_approve => pair0
    "peggy": ("devops",   {"read", "code_deploy", "code_review"},    1, True),   # +code_review  => pair1

    # ---- SoD only: role legitimately grants both halves, so 0 excess but a
    #      genuine separation-of-duties violation. Proves SoD is independent
    #      of least privilege.
    "trent": ("superclerk", {"read", "pay_create", "pay_approve"},   0, True),   # pair0, no excess
}

# Identities that must never be flagged (used to measure false positives).
CLEAN_USERS = {u for u, (_r, _g, exc, sod) in IDENTITIES.items()
               if exc == 0 and not sod}


def _build_inputs():
    grants = {u: set(g) for u, (_r, g, _e, _s) in IDENTITIES.items()}
    user_roles = {u: r for u, (r, _g, _e, _s) in IDENTITIES.items()}
    return grants, user_roles


def run() -> dict:
    grants, user_roles = _build_inputs()

    # Hand-derived expected totals (the ground truth to test against).
    seeded_excess = sum(exc for (_r, _g, exc, _s) in IDENTITIES.values())
    seeded_sod = sum(1 for (_r, _g, _e, sod) in IDENTITIES.values() if sod)

    report = audit(grants, ROLE_NEEDS, user_roles, SOD_PAIRS)

    detected_excess = report["total_excess"]
    detected_sod = report["total_sod"]
    # A false positive is a hand-verified clean identity that got flagged.
    false_positives = sum(1 for u in report["flagged_users"] if u in CLEAN_USERS)

    return {
        "schema": "claimlib_rbac_v1",
        "module": "rbac",
        "n_identities": report["n_identities"],
        "seeded_excess": seeded_excess,
        "detected_excess": detected_excess,
        "seeded_sod": seeded_sod,
        "detected_sod": detected_sod,
        "false_positives": false_positives,
        "excess_recall_ok": detected_excess == seeded_excess,
        "sod_recall_ok": detected_sod == seeded_sod,
        "flagged_users": report["flagged_users"],
        "clean_users": report["clean_users"],
        "excess_by_user": report["excess_by_user"],
        "sod_violations": report["sod_violations"],
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "rbac.json", obj,
         script="python3 claimlib/modules/rbac/evidence.py")
    # claim:CLAIM-LIB-RBAC-001 detected_excess
    # Over the fixed 13-identity matrix, 6 excess grants and 3 separation-of-duties
    # violations are seeded by hand. The auditor detects every one, so
    # detected_excess = 6 (== seeded_excess), detected_sod = 3 (== seeded_sod),
    # and false_positives = 0 (no clean identity is flagged).
    print(f"rbac: detected_excess={obj['detected_excess']}/{obj['seeded_excess']} "
          f"detected_sod={obj['detected_sod']}/{obj['seeded_sod']} "
          f"false_positives={obj['false_positives']} "
          f"over {obj['n_identities']} identities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
