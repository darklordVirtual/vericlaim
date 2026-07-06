# SPDX-License-Identifier: Apache-2.0
"""Centralized, fail-closed path validation for the vericlaim core.

Every place that turns an untrusted string (a claim's `artifact`, a manifest
row, a bundle manifest key, a literature `file`) into a filesystem path MUST go
through here. One tested implementation, one policy — so a traversal or
symlink-escape bug cannot hide in a copy.

Policy (all fail closed — reject unless provably safe):

* only non-empty **relative POSIX** paths are accepted;
* absolute paths, Windows drive prefixes (``C:``), and backslashes are rejected;
* ``.``, ``..``, empty segments, and any path whose normalized form differs from
  the input (``a/./b``, ``a//b``, trailing slash) are rejected — the string must
  already be canonical, so nothing is silently rewritten;
* NUL bytes and control characters are rejected;
* the resolved destination must stay at or below its declared root, following
  symlinks — so a symlink pointing outside the repo cannot launder an external
  file into a "committed artifact".

`bundle_id` values are validated as strict lowercase SHA-256 hex.
"""
from __future__ import annotations

import posixpath
import re
from pathlib import Path

__all__ = [
    "PathSafetyError",
    "check_relpath",
    "is_safe_relpath",
    "safe_join",
    "SHA256_HEX_RE",
    "check_bundle_id",
    "is_bundle_id",
]


class PathSafetyError(ValueError):
    """A path (or bundle id) failed validation. Always fail closed on this."""


_WIN_DRIVE_RE = re.compile(r"^[A-Za-z]:")
SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")


def check_relpath(rel: str) -> str:
    """Return *rel* unchanged if it is a safe relative POSIX path, else raise.

    This validates the STRING only (no filesystem access). Use `safe_join` when
    you also need containment against a concrete root (symlink-aware).
    """
    if not isinstance(rel, str):
        raise PathSafetyError(f"path must be a string, got {type(rel).__name__}")
    if rel == "":
        raise PathSafetyError("empty path")
    if "\x00" in rel:
        raise PathSafetyError("path contains a NUL byte")
    if any(ord(ch) < 0x20 for ch in rel):
        raise PathSafetyError("path contains a control character")
    if "\\" in rel:
        raise PathSafetyError(f"backslash in path (use POSIX '/'): {rel!r}")
    if _WIN_DRIVE_RE.match(rel):
        raise PathSafetyError(f"Windows drive prefix not allowed: {rel!r}")
    if rel.startswith("/") or posixpath.isabs(rel):
        raise PathSafetyError(f"absolute path not allowed: {rel!r}")
    segments = rel.split("/")
    for seg in segments:
        if seg == "":
            raise PathSafetyError(f"empty path segment (leading/trailing/double slash): {rel!r}")
        if seg == ".":
            raise PathSafetyError(f"'.' segment not allowed: {rel!r}")
        if seg == "..":
            raise PathSafetyError(f"'..' traversal not allowed: {rel!r}")
    # The string must already be canonical: normalization must be a no-op, so no
    # input is silently rewritten into a different path than what was written.
    if posixpath.normpath(rel) != rel:
        raise PathSafetyError(f"non-canonical path (normalizes to a different string): {rel!r}")
    return rel


def is_safe_relpath(rel: str) -> bool:
    try:
        check_relpath(rel)
        return True
    except PathSafetyError:
        return False


def safe_join(root: Path, rel: str) -> Path:
    """Validate *rel* and resolve it under *root*, symlink-aware, or raise.

    Returns the resolved absolute path. Raises PathSafetyError if the string is
    unsafe or if the resolved destination escapes *root* (including via a symlink
    inside the repo that points outside it). The target need not exist —
    ``resolve()`` follows symlinks in the existing prefix, which is where an
    escape would be planted.
    """
    check_relpath(rel)
    root_resolved = root.resolve()
    candidate = (root / rel).resolve()
    if candidate == root_resolved:
        raise PathSafetyError(f"path resolves to the root itself: {rel!r}")
    if root_resolved not in candidate.parents:
        raise PathSafetyError(
            f"path {rel!r} escapes the root {root_resolved} (absolute, '..', or a "
            f"symlink pointing outside the repository)")
    return candidate


def is_bundle_id(bundle_id: str) -> bool:
    return isinstance(bundle_id, str) and bool(SHA256_HEX_RE.match(bundle_id))


def check_bundle_id(bundle_id: str) -> str:
    """Return *bundle_id* if it is a strict lowercase 64-hex SHA-256, else raise."""
    if not is_bundle_id(bundle_id):
        raise PathSafetyError(
            f"invalid bundle_id {bundle_id!r}: must be 64 lowercase hex chars (sha256)")
    return bundle_id
