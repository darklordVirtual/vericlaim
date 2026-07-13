# SPDX-License-Identifier: Apache-2.0
"""PEM textual encoding of DER structures (RFC 7468) -- the on-disk form of
certificates and keys used throughout TLS / mutual TLS.

A pre-verified claimlib code artifact. PEM wraps binary DER in a labeled
base64 envelope: a ``-----BEGIN <label>-----`` line, the base64 of the DER
wrapped at 64 characters, and a matching ``-----END <label>-----`` line. This
module encodes and decodes that envelope; that its base64 body matches the
stdlib and that DER round-trips losslessly through PEM is registered as a claim
and proven by a committed evidence artifact.

Public API
----------
    encode(der: bytes, label: str = "CERTIFICATE") -> str
    decode(pem: str) -> tuple[str, bytes]              # (label, der) of first block
    decode_all(pem: str) -> list[tuple[str, bytes]]

    >>> decode(encode(b"\\x30\\x03\\x02\\x01\\x2a", "CERTIFICATE"))
    ('CERTIFICATE', b'0\\x03\\x02\\x01*')
"""
from __future__ import annotations

import base64
import re

_BLOCK_RE = re.compile(
    r"-----BEGIN ([A-Z0-9 ]+)-----\s*(.*?)\s*-----END \1-----",
    re.DOTALL)


class PEMError(ValueError):
    """Malformed PEM (missing boundaries, mismatched label, or bad base64)."""


def encode(der: bytes, label: str = "CERTIFICATE") -> str:
    """Wrap DER bytes in a PEM envelope with *label* (RFC 7468)."""
    if not isinstance(der, (bytes, bytearray)):
        raise PEMError("der must be bytes")
    if not re.fullmatch(r"[A-Z0-9 ]+", label):
        raise PEMError(f"invalid PEM label {label!r}")
    b64 = base64.b64encode(bytes(der)).decode("ascii")
    body = "\n".join(b64[i:i + 64] for i in range(0, len(b64), 64))
    return f"-----BEGIN {label}-----\n{body}\n-----END {label}-----\n"


def decode_all(pem: str) -> list[tuple[str, bytes]]:
    """Decode every PEM block in *pem* into a list of (label, der) pairs."""
    if not isinstance(pem, str):
        raise PEMError("pem must be a string")
    out = []
    for match in _BLOCK_RE.finditer(pem):
        label = match.group(1)
        body = re.sub(r"\s+", "", match.group(2))
        try:
            der = base64.b64decode(body, validate=True)
        except (ValueError, Exception) as exc:  # noqa: BLE001
            raise PEMError(f"invalid base64 in {label} block: {exc}")
        out.append((label, der))
    return out


def decode(pem: str) -> tuple[str, bytes]:
    """Decode the first PEM block in *pem*, returning (label, der)."""
    blocks = decode_all(pem)
    if not blocks:
        raise PEMError("no PEM block found")
    return blocks[0]
