# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable jsonpointer module (claimlib/modules/jsonpointer)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "jsonpointer"))

from jsonpointer import resolve  # noqa: E402

# The exact RFC 6901 section 5 example document.
DOC = {
    "foo": ["bar", "baz"],
    "": 0,
    "a/b": 1,
    "c%d": 2,
    "e^f": 3,
    "g|h": 4,
    "i\\j": 5,
    "k\"l": 6,
    " ": 7,
    "m~n": 8,
}


def test_rfc6901_section5_examples():
    # Published pointer -> value pairs, transcribed from RFC 6901 section 5.
    assert resolve(DOC, "") == DOC
    assert resolve(DOC, "/foo") == ["bar", "baz"]
    assert resolve(DOC, "/foo/0") == "bar"
    assert resolve(DOC, "/") == 0
    assert resolve(DOC, "/a~1b") == 1
    assert resolve(DOC, "/c%d") == 2
    assert resolve(DOC, "/e^f") == 3
    assert resolve(DOC, "/g|h") == 4
    assert resolve(DOC, "/i\\j") == 5
    assert resolve(DOC, "/k\"l") == 6
    assert resolve(DOC, "/ ") == 7
    assert resolve(DOC, "/m~0n") == 8


def test_escape_order_tilde():
    # ~01 must decode as ~1 (literal), NOT be double-unescaped into /.
    assert resolve({"~1": "ok"}, "/~01") == "ok"
    assert resolve({"m~n": 9}, "/m~0n") == 9


def test_missing_object_key_raises_keyerror():
    with pytest.raises(KeyError):
        resolve(DOC, "/nope")


def test_array_index_out_of_range_raises_indexerror():
    with pytest.raises(IndexError):
        resolve(DOC, "/foo/2")


def test_array_index_leading_zero_and_dash_rejected():
    with pytest.raises(IndexError):
        resolve(DOC, "/foo/01")   # leading zero not allowed
    with pytest.raises(IndexError):
        resolve(DOC, "/foo/-")    # element after the end
    with pytest.raises(IndexError):
        resolve(DOC, "/foo/x")    # non-numeric


def test_non_container_token_raises_typeerror():
    with pytest.raises(TypeError):
        resolve(DOC, "/foo/0/1")  # "bar" is a str, not a container


def test_non_string_pointer_rejected():
    with pytest.raises(TypeError):
        resolve(DOC, 0)


def test_pointer_without_leading_slash_rejected():
    with pytest.raises(ValueError):
        resolve(DOC, "foo")
