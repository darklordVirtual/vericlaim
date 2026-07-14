# SPDX-License-Identifier: Apache-2.0
"""in-toto supply-chain layout verification — artifact-rule chains between
signed steps — reusable, claim-bound.

A pre-verified claimlib code artifact for AI assurance and supply-chain
integrity. in-toto (Torres-Arias et al., USENIX Security 2019) secures a
software/ML pipeline against tampering between steps: a LAYOUT (signed by
the project owner) declares STEPS, each with authorized functionaries, a
signature threshold, and artifact rules over its expected materials and
products; per-step LINK metadata records what each functionary actually
consumed and produced. Verification checks the links against the layout.

This module implements the artifact-rule engine — the seven rule types the
in-toto specification defines — and step verification:

    MATCH     a step's product/material corresponds to another step's
    CREATE    a matched product must NOT have been a material
    DELETE    a matched material must NOT be a product
    MODIFY    an artifact is both material and product with a changed hash
    ALLOW     the artifact may pass unrestricted
    DISALLOW  the artifact is forbidden (usual final catch-all)
    REQUIRE   a named artifact must be present

The engine checks structure, not cryptography: it verifies the artifact
FLOW and that each step meets its signature threshold from AUTHORIZED
functionaries, given already-verified link signatures. Signature checking
and key management are the caller's layer. The caveat travels with the
claim.

Public API
----------
    apply_rules(rules, materials, products, links) -> (bool, reason)
    verify_step(step, link_signers, links) -> (bool, reason)

    rules are (RULE, pattern[, extra]) tuples; a step is a dict with
    'name', 'threshold', 'authorized' (set of key ids); a link records
    'signers', 'materials' (dict path->hash), 'products'.

    >>> ok, _ = apply_rules([("DISALLOW", "*")], {}, {}, {})
    >>> ok
    True
"""
from __future__ import annotations

import fnmatch

RULE_TYPES = ("MATCH", "CREATE", "DELETE", "MODIFY", "ALLOW", "DISALLOW",
              "REQUIRE")


class InTotoError(ValueError):
    """Malformed layout / rule / link (fail closed)."""


def _match(pattern: str, name: str) -> bool:
    return fnmatch.fnmatchcase(name, pattern)


def _filtered(artifacts: dict, pattern: str) -> set:
    return {name for name in artifacts if _match(pattern, name)}


def apply_rules(rules, materials, products, links) -> tuple:
    """Apply an ordered artifact-rule list to one step's materials/products.

    Semantics (in-toto spec): rules are consumed top to bottom; each rule
    "claims" the artifacts it applies to, and DISALLOW fires on any
    still-unclaimed artifact it matches. Returns (ok, reason).
    ``links`` maps step-name -> {"materials": {...}, "products": {...}} for
    MATCH resolution.
    """
    for coll in (materials, products):
        if not isinstance(coll, dict):
            raise InTotoError("materials and products must be dicts of "
                              "path -> hash")
    if not isinstance(rules, (list, tuple)):
        raise InTotoError("rules must be a list of rule tuples")

    # Track which artifacts remain unclaimed (DISALLOW guards these).
    unclaimed_m = set(materials)
    unclaimed_p = set(products)

    for rule in rules:
        if not isinstance(rule, tuple) or len(rule) < 2:
            raise InTotoError(f"rule {rule!r} must be (RULE, pattern, ...)")
        kind, pattern = rule[0], rule[1]
        if kind not in RULE_TYPES:
            raise InTotoError(f"unknown artifact rule {kind!r} "
                              f"(expected one of {RULE_TYPES})")

        if kind == "REQUIRE":
            if not (_filtered(materials, pattern)
                    or _filtered(products, pattern)):
                return False, f"REQUIRE {pattern!r}: no matching artifact"
            continue
        if kind == "ALLOW":
            unclaimed_m -= _filtered(materials, pattern)
            unclaimed_p -= _filtered(products, pattern)
            continue
        if kind == "DISALLOW":
            bad = (_filtered(materials, pattern) & unclaimed_m) | \
                  (_filtered(products, pattern) & unclaimed_p)
            if bad:
                return False, f"DISALLOW {pattern!r}: {sorted(bad)}"
            continue
        if kind == "CREATE":
            hits = _filtered(products, pattern)
            if hits & set(materials):
                return False, (f"CREATE {pattern!r}: also a material "
                               f"{sorted(hits & set(materials))}")
            unclaimed_p -= hits
            continue
        if kind == "DELETE":
            hits = _filtered(materials, pattern)
            if hits & set(products):
                return False, (f"DELETE {pattern!r}: also a product "
                               f"{sorted(hits & set(products))}")
            unclaimed_m -= hits
            continue
        if kind == "MODIFY":
            hits = _filtered(materials, pattern) & _filtered(products, pattern)
            for name in hits:
                if materials[name] == products[name]:
                    return False, (f"MODIFY {pattern!r}: {name} unchanged")
            unclaimed_m -= hits
            unclaimed_p -= hits
            continue
        # MATCH: (MATCH, pattern, dest_step, dest_type in {materials, products})
        if len(rule) != 4:
            raise InTotoError("MATCH rule must be "
                              "(MATCH, pattern, dest_step, dest_type)")
        _, pat, dest_step, dest_type = rule
        if dest_type not in ("materials", "products"):
            raise InTotoError(f"MATCH dest_type must be 'materials' or "
                              f"'products', got {dest_type!r}")
        if dest_step not in links:
            return False, f"MATCH {pat!r}: no link for step {dest_step!r}"
        dest = links[dest_step].get(dest_type, {})
        for name in _filtered(products, pat) | _filtered(materials, pat):
            src = products.get(name, materials.get(name))
            if name not in dest:
                return False, (f"MATCH {pat!r}: {name} missing in "
                               f"{dest_step}.{dest_type}")
            if dest[name] != src:
                return False, (f"MATCH {pat!r}: {name} hash mismatch with "
                               f"{dest_step}.{dest_type}")
        unclaimed_m -= _filtered(materials, pat)
        unclaimed_p -= _filtered(products, pat)
    return True, "all artifact rules satisfied"


def verify_step(step, link_signers, links) -> tuple:
    """A step passes when at least `threshold` of its link signers are
    authorized functionaries AND its product rules hold. Returns
    (ok, reason)."""
    if not isinstance(step, dict) or "name" not in step:
        raise InTotoError("step must be a dict with a 'name'")
    authorized = step.get("authorized")
    if not isinstance(authorized, (set, frozenset, list, tuple)):
        raise InTotoError(f"{step.get('name')}: 'authorized' must be a set "
                          f"of key ids")
    authorized = set(authorized)
    threshold = step.get("threshold", 1)
    if not isinstance(threshold, int) or isinstance(threshold, bool) \
            or threshold < 1:
        raise InTotoError(f"{step['name']}: threshold must be an int >= 1")
    if not isinstance(link_signers, (set, frozenset, list, tuple)):
        raise InTotoError("link_signers must be a collection of key ids")
    good = set(link_signers) & authorized
    if len(good) < threshold:
        return False, (f"{step['name']}: {len(good)} authorized signer(s) "
                       f"< threshold {threshold}")
    name = step["name"]
    link = links.get(name, {})
    return apply_rules(step.get("expected_products", []),
                       link.get("materials", {}),
                       link.get("products", {}), links)
