# SPDX-License-Identifier: Apache-2.0
"""RFC 6901 JSON Pointer resolution — a reusable, stdlib-only building block.

A pre-verified code artifact from the VeriClaim claim library. The property that
makes it trustworthy — that it resolves the exact pointers from RFC 6901's own
worked example to the values the spec publishes — is registered as a claim and
proven by a committed evidence artifact; vendoring this module carries that claim
(and its caveat) with it.

Public API
----------
    resolve(doc, pointer: str) -> value        # RFC 6901 evaluation

A JSON Pointer is a Unicode string identifying a value within a JSON document.
The empty string ``""`` references the whole document. Otherwise the pointer is a
sequence of ``/``-prefixed *reference tokens*; each token selects an object
member (by key) or an array element (by base-10 index). Two escape sequences are
defined: ``~1`` denotes ``/`` and ``~0`` denotes ``~`` (unescaped in that order).

    >>> resolve({"foo": ["bar", "baz"]}, "/foo/0")
    'bar'
    >>> resolve({"a/b": 1}, "/a~1b")
    1

A missing object key raises :class:`KeyError`; an array index that is out of
range, non-numeric, or has a leading zero raises :class:`IndexError`.
"""
from __future__ import annotations


def _unescape(token: str) -> str:
    """Decode a single reference token per RFC 6901 section 4.

    ``~1`` -> ``/`` then ``~0`` -> ``~``. The order matters: doing ``~0`` first
    would turn ``~01`` into ``~1`` and then into ``/``, which is wrong.
    """
    return token.replace("~1", "/").replace("~0", "~")


def resolve(doc, pointer: str):
    """Resolve *pointer* (an RFC 6901 JSON Pointer string) against *doc*.

    ``""`` returns *doc* itself. A non-empty pointer must begin with ``/``.
    Raises :class:`KeyError` for a missing object member, :class:`IndexError`
    for an out-of-range / malformed array index, and :class:`TypeError` if a
    token is applied to a value that is neither a JSON object nor array.
    """
    if not isinstance(pointer, str):
        raise TypeError(f"pointer must be a str, got {type(pointer).__name__}")
    if pointer == "":
        return doc
    if not pointer.startswith("/"):
        raise ValueError(f"non-empty pointer must start with '/': {pointer!r}")

    current = doc
    # split() on "/" of a string starting with "/" yields a leading "" we drop.
    for raw in pointer.split("/")[1:]:
        token = _unescape(raw)
        if isinstance(current, dict):
            if token not in current:
                raise KeyError(token)
            current = current[token]
        elif isinstance(current, list):
            current = current[_index(token, len(current))]
        else:
            raise TypeError(
                f"cannot apply token {token!r} to non-container "
                f"{type(current).__name__}"
            )
    return current


def _index(token: str, length: int) -> int:
    """Validate an array reference token and return its int index.

    RFC 6901 section 4: an array index is either ``-`` (the nonexistent element
    after the last, always an error for resolution) or a base-10 number with no
    leading zeros. Anything else — or an out-of-range value — is an
    :class:`IndexError`.
    """
    if token == "-":
        raise IndexError("'-' refers to the nonexistent element after the array end")
    if not token.isdigit():
        raise IndexError(f"invalid array index {token!r}")
    if len(token) > 1 and token[0] == "0":
        raise IndexError(f"array index has leading zero: {token!r}")
    idx = int(token)
    if idx >= length:
        raise IndexError(f"array index {idx} out of range for length {length}")
    return idx
