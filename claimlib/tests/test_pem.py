# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``pem`` library (RFC 7468)."""
import base64
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "pem"))

from pem import encode, decode, decode_all, PEMError  # noqa: E402


def test_round_trip():
    for der, label in ((bytes.fromhex("30030201 2a".replace(" ", "")), "CERTIFICATE"),
                       (bytes(range(256)), "PRIVATE KEY"), (b"", "PUBLIC KEY")):
        assert decode(encode(der, label)) == (label, der)


def test_structure_and_wrapping():
    pem = encode(bytes(range(200)), "CERTIFICATE")
    assert pem.startswith("-----BEGIN CERTIFICATE-----\n")
    assert pem.rstrip().endswith("-----END CERTIFICATE-----")
    body = pem.split("-----BEGIN CERTIFICATE-----\n")[1].split("\n-----END")[0]
    for line in body.split("\n"):
        assert len(line) <= 64
    assert base64.b64decode("".join(body.split("\n"))) == bytes(range(200))


def test_multi_block():
    pem = encode(b"\x01", "CERTIFICATE") + encode(b"\x02", "CERTIFICATE")
    assert decode_all(pem) == [("CERTIFICATE", b"\x01"), ("CERTIFICATE", b"\x02")]


def test_rejects_malformed():
    with pytest.raises(PEMError):
        decode("not a pem")
    with pytest.raises(PEMError):
        encode(b"\x00", "lower case label")
    with pytest.raises(PEMError):
        encode("not bytes", "CERTIFICATE")
