# SPDX-License-Identifier: Apache-2.0
"""RFC 4180 CSV parsing and writing -- a reusable, stdlib-free codec.

A pre-verified claimlib code artifact. It parses and formats comma-separated
values per RFC 4180: fields separated by a delimiter, records by newlines, and
fields containing the delimiter, a quote, or a newline wrapped in double quotes
with embedded quotes doubled. It does NOT import the ``csv`` module, so
cross-checking against ``csv`` is a genuine independent test. That its parser
agrees with ``csv.reader`` and its writer round-trips over a fixed battery is
registered as a claim and proven by a committed evidence artifact.

Public API
----------
    parse(text, delimiter=",", quotechar='"') -> list[list[str]]
    format_row(fields, delimiter=",", quotechar='"') -> str
    format_rows(rows, delimiter=",", quotechar='"') -> str   # CRLF-joined

    >>> parse('a,"b,c",d')
    [['a', 'b,c', 'd']]
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence


class CSVError(ValueError):
    """Malformed CSV (delimiter/quotechar must be single distinct chars)."""


def parse(text: str, delimiter: str = ",", quotechar: str = '"') -> list[list[str]]:
    """Parse *text* into a list of records (each a list of string fields)."""
    if len(delimiter) != 1 or len(quotechar) != 1 or delimiter == quotechar:
        raise CSVError("delimiter and quotechar must be distinct single characters")
    if not isinstance(text, str):
        raise CSVError("text must be a string")
    if text == "":
        return []
    rows: list[list[str]] = []
    row: list[str] = []
    field: list[str] = []
    in_quotes = False
    record_started = False
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if in_quotes:
            if c == quotechar:
                if i + 1 < n and text[i + 1] == quotechar:
                    field.append(quotechar)
                    i += 2
                    continue
                in_quotes = False
            else:
                field.append(c)
            i += 1
            continue
        if c == quotechar:
            in_quotes = True
            record_started = True
        elif c == delimiter:
            row.append("".join(field))
            field = []
            record_started = True
        elif c in "\r\n":
            row.append("".join(field))
            rows.append(row)
            row, field = [], []
            record_started = False
            if c == "\r" and i + 1 < n and text[i + 1] == "\n":
                i += 1                       # consume the \n of a CRLF pair
        else:
            field.append(c)
            record_started = True
        i += 1
    if record_started or field or row:
        row.append("".join(field))
        rows.append(row)
    return rows


def format_row(fields: Sequence, delimiter: str = ",", quotechar: str = '"') -> str:
    """Format one record, quoting fields that need it (RFC 4180)."""
    special = {delimiter, quotechar, "\r", "\n"}
    out = []
    for f in fields:
        s = str(f)
        if any(ch in s for ch in special):
            s = quotechar + s.replace(quotechar, quotechar * 2) + quotechar
        out.append(s)
    return delimiter.join(out)


def format_rows(rows: Iterable[Sequence], delimiter: str = ",", quotechar: str = '"') -> str:
    """Format records into CSV text (RFC 4180 CRLF line endings)."""
    return "\r\n".join(format_row(r, delimiter, quotechar) for r in rows)
