# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``csv_rfc4180`` library, cross-checked against stdlib csv."""
import csv
import io
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "csv_rfc4180"))

from csv_rfc4180 import parse, format_row, format_rows, CSVError  # noqa: E402


def test_agrees_with_stdlib_csv():
    for text in ('a,b,c', 'a,"b,c",d', '"a""b",c', '"line1\nline2",x',
                 'a,,c', '1,2\r\n3,4', 'trailing,\r\n'):
        assert parse(text) == list(csv.reader(io.StringIO(text)))


def test_basic_parse():
    assert parse("a,b,c") == [["a", "b", "c"]]
    assert parse('a,"b,c",d') == [["a", "b,c", "d"]]
    assert parse("") == []


def test_format_quoting():
    assert format_row(["a", "b,c", "d"]) == 'a,"b,c",d'
    assert format_row(['has "q"', "x"]) == '"has ""q""",x'
    assert format_row(["plain", "text"]) == "plain,text"


def test_round_trip():
    rows = [["a", "b,c", "d"], ["line\nbreak", 'has "quote"'], ["", "", ""]]
    assert parse(format_rows(rows)) == rows


def test_rejects_bad_config():
    with pytest.raises(CSVError):
        parse("a,b", delimiter=",,")
    with pytest.raises(CSVError):
        parse("a,b", delimiter=",", quotechar=",")
