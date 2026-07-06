# SPDX-License-Identifier: Apache-2.0
"""Adversarial tests for the centralized path-safety policy (vericlaim.pathsafe).

These are security regression tests: each represents a way an untrusted string
could try to read or write outside the repository. They must all fail closed.
"""
from __future__ import annotations

import os

import pytest

from vericlaim.pathsafe import (
    PathSafetyError,
    check_bundle_id,
    check_relpath,
    is_bundle_id,
    is_safe_relpath,
    safe_join,
)

SAFE = [
    "a.json",
    "results/bench.json",
    "a/b/c/d.txt",
    "examples/rle/artifacts/rle_bench.json",
]

UNSAFE = [
    "",                       # empty
    "/etc/passwd",            # absolute unix
    "/",                      # root
    "../escape.json",         # parent traversal
    "a/../../etc/passwd",     # embedded traversal
    "./a.json",               # non-canonical leading dot
    "a/./b.json",             # non-canonical dot segment
    "a//b.json",              # double slash / empty segment
    "a/b/",                   # trailing slash
    "..",                     # bare parent
    ".",                      # bare dot
    "C:/Windows/system32",    # windows drive
    "c:\\temp\\x",            # windows drive + backslash
    "a\\b.json",              # backslash traversal
    "a\x00b.json",            # NUL byte
    "a\nb.json",              # control character
]


@pytest.mark.parametrize("rel", SAFE)
def test_safe_relpaths_accepted(rel):
    assert is_safe_relpath(rel)
    assert check_relpath(rel) == rel


@pytest.mark.parametrize("rel", UNSAFE)
def test_unsafe_relpaths_rejected(rel):
    assert not is_safe_relpath(rel)
    with pytest.raises(PathSafetyError):
        check_relpath(rel)


@pytest.mark.parametrize("rel", ["../escape.json", "/etc/passwd", "C:/x", "a\\b"])
def test_safe_join_rejects_escapes(tmp_path, rel):
    with pytest.raises(PathSafetyError):
        safe_join(tmp_path, rel)


def test_safe_join_accepts_in_root(tmp_path):
    resolved = safe_join(tmp_path, "sub/a.json")
    assert str(resolved).startswith(str(tmp_path.resolve()))


def test_safe_join_rejects_root_itself(tmp_path):
    with pytest.raises(PathSafetyError):
        safe_join(tmp_path, "sub/..")  # rejected as non-canonical before resolve


def test_safe_join_blocks_symlink_escape(tmp_path):
    """A symlink INSIDE the root that points OUTSIDE it must be rejected — the
    exact reason safe_join resolves symlinks. Previously the one untested branch."""
    secret = tmp_path.parent / "outside_secret.txt"
    secret.write_text("leaked")
    proj = tmp_path / "proj"
    proj.mkdir()
    link = proj / "link.txt"
    try:
        os.symlink(secret, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported on this platform")
    with pytest.raises(PathSafetyError):
        safe_join(proj, "link.txt")


def test_symlinked_directory_escape_is_blocked(tmp_path):
    """A symlinked DIRECTORY inside the root pointing outside, with a child file
    under it, must also be rejected (resolve() follows the dir symlink)."""
    outside = tmp_path.parent / "outside_dir"
    outside.mkdir()
    (outside / "f.json").write_text("{}")
    proj = tmp_path / "proj"
    proj.mkdir()
    try:
        os.symlink(outside, proj / "linkdir")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported on this platform")
    with pytest.raises(PathSafetyError):
        safe_join(proj, "linkdir/f.json")


@pytest.mark.parametrize("bid", [
    "a" * 64,
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
])
def test_valid_bundle_ids(bid):
    assert is_bundle_id(bid)
    assert check_bundle_id(bid) == bid


@pytest.mark.parametrize("bid", [
    "A" * 64,          # uppercase
    "a" * 63,          # too short
    "a" * 65,          # too long
    "g" * 64,          # non-hex
    "../" + "a" * 61,  # path-y
    "",
])
def test_invalid_bundle_ids(bid):
    assert not is_bundle_id(bid)
    with pytest.raises(PathSafetyError):
        check_bundle_id(bid)
