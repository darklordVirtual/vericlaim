# SPDX-License-Identifier: Apache-2.0
"""Least-privilege and separation-of-duties auditing for access-control grants.

A reusable, stdlib-only building block from the VeriClaim claim library. Given
the permissions each identity actually holds, the least-privilege baseline for
each role, and a set of separation-of-duties (SoD) constraints, this module
reports two independent classes of finding:

* **Excess grants** — permissions an identity holds that its assigned role does
  not need. This is the *least-privilege* check: everything beyond the role's
  documented baseline is flagged.
* **SoD violations** — an identity that simultaneously holds permissions from
  both sides of a toxic pair (e.g. *create payment* and *approve payment*). This
  check is independent of least privilege: a violation is reported even when a
  (misconfigured) role legitimately grants both halves.

Public API
----------
    audit(grants, role_needs, user_roles, sod_pairs=None) -> dict
    excess_grants(grants, role_needs, user_roles) -> dict[user, list[str]]
    sod_violations(grants, sod_pairs, users=None) -> list[dict]

The module is pure: no I/O, no globals, no third-party imports. All list-valued
outputs are sorted so results are deterministic and comparable.

    >>> report = audit(
    ...     grants={"alice": {"read", "write"}, "bob": {"read", "delete"}},
    ...     role_needs={"editor": {"read", "write"}, "viewer": {"read"}},
    ...     user_roles={"alice": "editor", "bob": "viewer"},
    ... )
    >>> report["total_excess"], report["excess_by_user"]["bob"]
    (1, ['delete'])
"""
from __future__ import annotations

from typing import Iterable, Mapping


class RbacError(ValueError):
    """The access-control model is internally inconsistent.

    Raised when an audited identity has no role assignment, or an assigned role
    has no defined least-privilege baseline. The audit fails closed rather than
    silently treating an unknown baseline as "allow" or "deny".
    """


def _needs_for(user: str, role_needs: Mapping[str, Iterable[str]],
               user_roles: Mapping[str, str]) -> frozenset:
    """Return the least-privilege permission set owed to *user*.

    Fails closed: an unassigned user or an undefined role is a modelling error,
    not an empty baseline.
    """
    if user not in user_roles:
        raise RbacError(f"user {user!r} has no role assignment")
    role = user_roles[user]
    if role not in role_needs:
        raise RbacError(f"role {role!r} (user {user!r}) has no defined needs")
    return frozenset(role_needs[role])


def excess_grants(grants: Mapping[str, Iterable[str]],
                  role_needs: Mapping[str, Iterable[str]],
                  user_roles: Mapping[str, str]) -> dict:
    """Map each over-privileged identity to its sorted list of excess permissions.

    An identity's excess set is ``held - needed`` where *needed* is the
    least-privilege baseline of its assigned role. Identities with no excess are
    omitted. Every identity in *grants* must have a role (in *user_roles*) whose
    baseline is defined (in *role_needs*); otherwise :class:`RbacError` is raised.
    """
    out: dict[str, list[str]] = {}
    for user, held in grants.items():
        needed = _needs_for(user, role_needs, user_roles)
        extra = frozenset(held) - needed
        if extra:
            out[user] = sorted(extra)
    return out


def sod_violations(grants: Mapping[str, Iterable[str]],
                   sod_pairs: Iterable[tuple],
                   users: Iterable[str] | None = None) -> list:
    """List every separation-of-duties violation.

    *sod_pairs* is an iterable of ``(set_a, set_b)`` toxic permission pairs. An
    identity violates a pair when it holds at least one permission from *set_a*
    AND at least one from *set_b*. Each violation is reported as a dict with the
    offending ``user``, the ``pair`` index, and the sorted permissions it holds
    from each side (``held_a`` / ``held_b``). Results are sorted by
    ``(pair, user)`` for determinism.

    If *users* is given, only those identities are checked; otherwise every
    identity in *grants* is checked.
    """
    pairs = list(sod_pairs)
    who = sorted(users) if users is not None else sorted(grants)
    out: list[dict] = []
    for idx, pair in enumerate(pairs):
        side_a, side_b = frozenset(pair[0]), frozenset(pair[1])
        for user in who:
            held = frozenset(grants.get(user, ()))
            in_a = held & side_a
            in_b = held & side_b
            if in_a and in_b:
                out.append({
                    "user": user,
                    "pair": idx,
                    "held_a": sorted(in_a),
                    "held_b": sorted(in_b),
                })
    return out


def audit(grants: Mapping[str, Iterable[str]],
          role_needs: Mapping[str, Iterable[str]],
          user_roles: Mapping[str, str],
          sod_pairs: Iterable[tuple] | None = None) -> dict:
    """Run the full least-privilege + separation-of-duties audit.

    Parameters
    ----------
    grants:
        ``{identity: iterable of held permissions}``.
    role_needs:
        ``{role: iterable of permissions the role needs}`` — the least-privilege
        baseline per role.
    user_roles:
        ``{identity: role}``. Every identity in *grants* must appear here, and
        its role must appear in *role_needs*, else :class:`RbacError`.
    sod_pairs:
        Optional iterable of ``(set_a, set_b)`` toxic permission pairs.

    Returns
    -------
    dict
        A deterministic report:

        * ``n_identities`` — number of distinct identities considered (union of
          *grants* and *user_roles* keys).
        * ``excess_by_user`` — ``{identity: sorted excess permissions}``.
        * ``total_excess`` — total count of excess (identity, permission) grants.
        * ``sod_violations`` — list of violation records (see
          :func:`sod_violations`).
        * ``total_sod`` — number of violation records.
        * ``flagged_users`` — sorted identities with any excess or SoD finding.
        * ``clean_users`` — sorted identities considered but not flagged.

    The two findings are computed independently: an SoD violation is reported
    even if both permissions are within the role baseline (so it is not also an
    excess grant), and an excess grant is reported even if it never trips an SoD
    pair.
    """
    identities = set(grants) | set(user_roles)
    exc = excess_grants(grants, role_needs, user_roles)
    sod = sod_violations(grants, sod_pairs or [], users=identities)
    flagged = set(exc) | {v["user"] for v in sod}
    return {
        "n_identities": len(identities),
        "excess_by_user": {u: exc[u] for u in sorted(exc)},
        "total_excess": sum(len(v) for v in exc.values()),
        "sod_violations": sod,
        "total_sod": len(sod),
        "flagged_users": sorted(flagged),
        "clean_users": sorted(identities - flagged),
    }
