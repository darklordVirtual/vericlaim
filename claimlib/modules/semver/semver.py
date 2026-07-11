# SPDX-License-Identifier: Apache-2.0
"""Semantic Versioning 2.0.0 parsing, precedence comparison, and a modest
range grammar — a reusable, stdlib-only building block.

A pre-verified code artifact from the VeriClaim claim library. The property
that makes it trustworthy — that it implements the published SemVer 2.0.0
precedence rules and a small, well-defined range grammar correctly — is
registered as a claim and proven by a committed evidence artifact; vendoring
this module carries that claim (and its caveat) with it.

Public API
----------
    parse(version: str) -> tuple
        ``"1.2.3-alpha.1+build"`` -> ``(1, 2, 3, ("alpha", 1))``.
        Returns a 4-tuple ``(major, minor, patch, prerelease)`` where
        *prerelease* is a tuple of identifiers, each an ``int`` (numeric
        identifier) or ``str`` (alphanumeric). Build metadata is validated
        then discarded — the spec (SemVer 2.0.0 §10) says it MUST be ignored
        for precedence, so it is not part of the returned tuple.

    compare(a: str, b: str) -> int
        ``-1`` if ``a < b``, ``0`` if equal precedence, ``1`` if ``a > b``,
        following the SemVer 2.0.0 §11 precedence rules exactly:
        core is compared numerically; a pre-release version is lower than the
        associated release; pre-release identifiers are compared left-to-right
        with numeric identifiers compared numerically, alphanumeric ones
        compared in ASCII order, numeric always lower than alphanumeric, and a
        larger set of identifiers winning when all preceding ones are equal.

    satisfies(version: str, spec: str) -> bool
        Whether *version* falls in the range *spec*. Supported spec forms:
            "x.y.z"     exact  (equal precedence)
            ">=x.y.z"   at least
            "<x.y.z"    strictly below
            "^x.y.z"    caret: up to the next left-most non-zero element
            "~x.y.z"    tilde: patch-level changes within x.y

Ranges are evaluated purely by SemVer precedence against derived bounds
(see the module caveat in the registry): a pre-release version is included
or excluded strictly by §11 precedence, not by npm's extra "same-tuple"
pre-release heuristic.

    >>> parse("1.2.3-alpha.1")
    (1, 2, 3, ('alpha', 1))
    >>> compare("1.0.0-alpha", "1.0.0")
    -1
    >>> satisfies("1.9.9", "^1.2.3")
    True
    >>> satisfies("2.0.0", "^1.2.3")
    False
"""
from __future__ import annotations

import re

# A numeric identifier: 0, or a non-zero digit followed by digits. No leading
# zeros (SemVer 2.0.0 §2 for core, §9 for pre-release numeric identifiers).
_NUMERIC = re.compile(r"^(?:0|[1-9]\d*)$")
# Allowed characters for a single dot-separated identifier (ASCII alphanumerics
# and hyphen), SemVer 2.0.0 §9 / §10.
_IDENT_CHARS = re.compile(r"^[0-9A-Za-z-]+$")


class SemverError(ValueError):
    """The version or range string is not a valid SemVer 2.0.0 value."""


def _parse_core(core: str) -> tuple:
    """Parse the ``major.minor.patch`` core into a tuple of three ints."""
    fields = core.split(".")
    if len(fields) != 3:
        raise SemverError(f"core must be major.minor.patch, got {core!r}")
    out = []
    for field in fields:
        if not _NUMERIC.match(field):
            raise SemverError(
                f"invalid numeric core field {field!r} "
                "(non-negative, no leading zeros)")
        out.append(int(field))
    return tuple(out)


def _parse_prerelease(pre: str) -> tuple:
    """Parse a dot-separated pre-release string into a tuple of identifiers.

    Numeric identifiers become ``int``; alphanumeric ones stay ``str``.
    """
    identifiers = []
    for ident in pre.split("."):
        if ident == "":
            raise SemverError("empty pre-release identifier")
        if ident.isascii() and ident.isdigit():
            # All digits -> numeric identifier; reject leading zeros (§9).
            if not _NUMERIC.match(ident):
                raise SemverError(
                    f"numeric pre-release identifier {ident!r} has a leading zero")
            identifiers.append(int(ident))
        else:
            if not _IDENT_CHARS.match(ident):
                raise SemverError(f"invalid pre-release identifier {ident!r}")
            identifiers.append(ident)
    return tuple(identifiers)


def _validate_build(build: str) -> None:
    """Validate build metadata (§10). It is discarded, only checked for shape."""
    for ident in build.split("."):
        if ident == "" or not _IDENT_CHARS.match(ident):
            raise SemverError(f"invalid build metadata identifier {ident!r}")


def parse(version: str) -> tuple:
    """Parse a SemVer 2.0.0 string into ``(major, minor, patch, prerelease)``.

    Build metadata is validated then dropped (ignored for precedence, §10).
    Raises :class:`SemverError` on any malformed input — fail closed rather
    than silently accept a partial or non-conforming version.
    """
    if not isinstance(version, str):
        raise SemverError(f"version must be a string, got {type(version).__name__}")
    if version != version.strip():
        raise SemverError(f"surrounding whitespace is not a valid version: {version!r}")
    text = version
    if not text:
        raise SemverError("empty version string")

    # Grammar: <core>[-<prerelease>][+<build>]. Strip build first (its '+' comes
    # after any pre-release '-'), then split core from pre-release on the first
    # '-' (the core never contains a hyphen).
    core_pre, plus, build = text.partition("+")
    if plus:
        if build == "":
            raise SemverError("empty build metadata after '+'")
        _validate_build(build)

    core, hyphen, pre = core_pre.partition("-")
    core_tuple = _parse_core(core)

    if hyphen:
        if pre == "":
            raise SemverError("empty pre-release after '-'")
        prerelease = _parse_prerelease(pre)
    else:
        prerelease = ()

    return core_tuple + (prerelease,)


def _cmp(x, y) -> int:
    """Three-way compare for orderable scalars."""
    if x < y:
        return -1
    if x > y:
        return 1
    return 0


def _cmp_identifier(a, b) -> int:
    """Compare two pre-release identifiers per SemVer 2.0.0 §11.4.

    Numeric identifiers compare numerically; alphanumeric compare in ASCII
    order; a numeric identifier always has lower precedence than an
    alphanumeric one.
    """
    a_num = isinstance(a, int)
    b_num = isinstance(b, int)
    if a_num and b_num:
        return _cmp(a, b)
    if a_num and not b_num:
        return -1          # numeric < alphanumeric (§11.4.3)
    if b_num and not a_num:
        return 1
    return _cmp(a, b)      # both strings: ASCII lexical order


def _compare_prerelease(pa: tuple, pb: tuple) -> int:
    """Compare two pre-release identifier tuples (§11.3, §11.4)."""
    if not pa and not pb:
        return 0
    # A release (empty pre-release) outranks any pre-release (§11.3).
    if not pa:
        return 1
    if not pb:
        return -1
    for ia, ib in zip(pa, pb):
        c = _cmp_identifier(ia, ib)
        if c != 0:
            return c
    # All shared identifiers equal: the longer set wins (§11.4.4).
    return _cmp(len(pa), len(pb))


def _compare_parsed(pa: tuple, pb: tuple) -> int:
    """Compare two parsed version tuples by SemVer precedence."""
    for x, y in zip(pa[:3], pb[:3]):
        c = _cmp(x, y)
        if c != 0:
            return c
    return _compare_prerelease(pa[3], pb[3])


def compare(a, b) -> int:
    """Return -1/0/1 comparing versions *a* and *b* by SemVer precedence.

    Accepts version strings (parsed here) or pre-parsed tuples from
    :func:`parse`. Build metadata does not affect the result (§10).
    """
    pa = a if isinstance(a, tuple) else parse(a)
    pb = b if isinstance(b, tuple) else parse(b)
    return _compare_parsed(pa, pb)


def _caret_upper(base: tuple) -> tuple:
    """Exclusive upper bound for a caret range (npm caret semantics).

    ^1.2.3 -> <2.0.0 ; ^0.2.3 -> <0.3.0 ; ^0.0.3 -> <0.0.4 ; ^0.0.0 -> <0.0.1.
    The bound is anchored to the left-most non-zero core element.
    """
    major, minor, patch, _pre = base
    if major > 0:
        return (major + 1, 0, 0, ())
    if minor > 0:
        return (0, minor + 1, 0, ())
    return (0, 0, patch + 1, ())


def _in_range(version: tuple, lower: tuple, upper: tuple) -> bool:
    """``lower <= version < upper`` by SemVer precedence."""
    return _compare_parsed(version, lower) >= 0 and _compare_parsed(version, upper) < 0


def satisfies(version: str, spec: str) -> bool:
    """Return whether *version* satisfies the range *spec*.

    Supported spec forms (see module docstring): exact ``x.y.z``, ``>=x.y.z``,
    ``<x.y.z``, caret ``^x.y.z``, tilde ``~x.y.z``. Raises :class:`SemverError`
    on an unrecognised operator or malformed version.
    """
    if not isinstance(spec, str):
        raise SemverError(f"spec must be a string, got {type(spec).__name__}")
    v = parse(version)
    text = spec.strip()
    if not text:
        raise SemverError("empty range spec")

    if text.startswith(">="):
        return _compare_parsed(v, parse(text[2:].strip())) >= 0
    if text.startswith("<"):
        return _compare_parsed(v, parse(text[1:].strip())) < 0
    if text.startswith("^"):
        base = parse(text[1:].strip())
        return _in_range(v, base, _caret_upper(base))
    if text.startswith("~"):
        base = parse(text[1:].strip())
        upper = (base[0], base[1] + 1, 0, ())
        return _in_range(v, base, upper)
    # No operator: exact match by precedence (build metadata ignored).
    return _compare_parsed(v, parse(text)) == 0
