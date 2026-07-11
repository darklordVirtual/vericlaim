# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``levenshtein`` library.

Reference: the canonical worked examples kitten->sitting = 3, flaw->lawn = 2.
"""
import sys
from itertools import product
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "levenshtein"))

from levenshtein import distance, LevenshteinError  # noqa: E402


def test_published_distances():
    assert distance("kitten", "sitting") == 3
    assert distance("Saturday", "Sunday") == 3
    assert distance("flaw", "lawn") == 2
    assert distance("gumbo", "gambol") == 2


def test_identity_and_empty():
    assert distance("abc", "abc") == 0
    assert distance("", "") == 0
    assert distance("", "abc") == 3
    assert distance("abc", "") == 3


def test_symmetry_and_triangle():
    words = ["", "a", "abc", "kitten", "sitting", "banana"]
    for x, y in product(words, words):
        assert distance(x, y) == distance(y, x)
    for x, y, z in product(words, words, words):
        assert distance(x, z) <= distance(x, y) + distance(y, z)


def test_single_edits():
    assert distance("cat", "cats") == 1     # insertion
    assert distance("cats", "cat") == 1     # deletion
    assert distance("cat", "cut") == 1      # substitution


def test_rejects_non_strings():
    with pytest.raises(LevenshteinError):
        distance("a", 5)
