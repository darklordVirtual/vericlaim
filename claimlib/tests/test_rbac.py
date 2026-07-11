# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``rbac`` library.

Expected values are derived by hand from the least-privilege / SoD definitions,
independent of the implementation.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
MODULE_DIR = HERE.parents[1] / "claimlib" / "modules" / "rbac"
if not MODULE_DIR.exists():  # when tests dir sits inside claimlib/
    MODULE_DIR = HERE.parent / "modules" / "rbac"
sys.path.insert(0, str(MODULE_DIR))

from rbac import audit, excess_grants, sod_violations, RbacError  # noqa: E402


def test_excess_grants_basic():
    # bob holds 'delete' beyond the viewer baseline {read}; alice is exact.
    exc = excess_grants(
        grants={"alice": {"read", "write"}, "bob": {"read", "delete"}},
        role_needs={"editor": {"read", "write"}, "viewer": {"read"}},
        user_roles={"alice": "editor", "bob": "viewer"},
    )
    assert exc == {"bob": ["delete"]}  # alice omitted (no excess)


def test_excess_multiple_are_sorted():
    exc = excess_grants(
        grants={"m": {"read", "write", "delete"}},
        role_needs={"viewer": {"read"}},
        user_roles={"m": "viewer"},
    )
    assert exc["m"] == ["delete", "write"]  # two excess, sorted


def test_clean_user_never_flagged():
    report = audit(
        grants={"c": {"read", "pay_create"}},
        role_needs={"clerk": {"read", "pay_create"}},
        user_roles={"c": "clerk"},
        sod_pairs=[({"pay_create"}, {"pay_approve"})],
    )
    assert report["total_excess"] == 0
    assert report["total_sod"] == 0
    assert report["flagged_users"] == []
    assert report["clean_users"] == ["c"]


def test_sod_violation_detected():
    viol = sod_violations(
        grants={"o": {"read", "pay_create", "pay_approve"}},
        sod_pairs=[({"pay_create"}, {"pay_approve"})],
    )
    assert len(viol) == 1
    assert viol[0]["user"] == "o"
    assert viol[0]["pair"] == 0
    assert viol[0]["held_a"] == ["pay_create"]
    assert viol[0]["held_b"] == ["pay_approve"]


def test_sod_independent_of_least_privilege():
    # superclerk role legitimately needs both halves => 0 excess, but the toxic
    # pair is still a violation.
    report = audit(
        grants={"t": {"read", "pay_create", "pay_approve"}},
        role_needs={"superclerk": {"read", "pay_create", "pay_approve"}},
        user_roles={"t": "superclerk"},
        sod_pairs=[({"pay_create"}, {"pay_approve"})],
    )
    assert report["total_excess"] == 0        # nothing beyond the baseline
    assert report["total_sod"] == 1           # but still a SoD violation
    assert report["flagged_users"] == ["t"]


def test_sod_needs_both_sides():
    # holding only one side of every pair is never a violation.
    viol = sod_violations(
        grants={"g": {"read", "pay_create"}, "h": {"read", "pay_approve"}},
        sod_pairs=[({"pay_create"}, {"pay_approve"})],
    )
    assert viol == []


def test_unknown_role_fails_closed():
    with pytest.raises(RbacError):
        excess_grants(
            grants={"x": {"read"}},
            role_needs={"viewer": {"read"}},
            user_roles={"x": "ghost"},  # 'ghost' has no defined needs
        )


def test_unassigned_user_fails_closed():
    with pytest.raises(RbacError):
        excess_grants(
            grants={"x": {"read"}},
            role_needs={"viewer": {"read"}},
            user_roles={},  # x has no role
        )


def test_empty_inputs():
    report = audit(grants={}, role_needs={}, user_roles={}, sod_pairs=[])
    assert report["n_identities"] == 0
    assert report["total_excess"] == 0
    assert report["total_sod"] == 0
    assert report["flagged_users"] == []


def test_full_matrix_counts():
    # A compact mirror of the evidence battery: 6 excess grants, 3 SoD
    # violations, 0 false positives across the flagged set.
    role_needs = {
        "editor": {"read", "write"},
        "viewer": {"read"},
        "admin": {"read", "write", "config", "user_admin"},
        "clerk": {"read", "pay_create"},
        "devops": {"read", "code_deploy"},
        "superclerk": {"read", "pay_create", "pay_approve"},
    }
    grants = {
        "dave": {"read", "write", "config"},                       # +1 excess
        "erin": {"read", "write", "config", "user_admin", "secret_export"},  # +1
        "mallory": {"read", "write", "delete"},                    # +2 excess
        "oscar": {"read", "pay_create", "pay_approve"},            # +1 excess, sod
        "peggy": {"read", "code_deploy", "code_review"},           # +1 excess, sod
        "trent": {"read", "pay_create", "pay_approve"},            # 0 excess, sod
        "clean": {"read"},                                         # clean
    }
    user_roles = {
        "dave": "editor", "erin": "admin", "mallory": "viewer",
        "oscar": "clerk", "peggy": "devops", "trent": "superclerk",
        "clean": "viewer",
    }
    sod_pairs = [({"pay_create"}, {"pay_approve"}),
                 ({"code_deploy"}, {"code_review"})]
    report = audit(grants, role_needs, user_roles, sod_pairs)
    assert report["total_excess"] == 6
    assert report["total_sod"] == 3
    assert "clean" not in report["flagged_users"]
    assert report["clean_users"] == ["clean"]
