# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the jwt_hs256 module (RFC 7515 JWS / RFC 7519 JWT)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "jwt_hs256"
_spec = importlib.util.spec_from_file_location(
    "claimlib_jwt_hs256", _MOD_DIR / "jwt_hs256.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_jwt_hs256"] = _m
_spec.loader.exec_module(_m)

JWTError = _m.JWTError
InvalidToken = _m.InvalidToken
InvalidSignature = _m.InvalidSignature
ClaimValidationError = _m.ClaimValidationError
b64url_encode = _m.b64url_encode
b64url_decode = _m.b64url_decode
sign_claims = _m.sign_claims
verify = _m.verify
validate_claims = _m.validate_claims
decode = _m.decode

KEY = b"claimlib-test-key-32-bytes-long!"


def test_b64url_roundtrip_no_padding():
    for data in (b"", b"f", b"fo", b"foo", bytes(range(256))):
        enc = b64url_encode(data)
        assert "=" not in enc and "+" not in enc and "/" not in enc
        assert b64url_decode(enc) == data


def test_sign_and_decode_roundtrip():
    claims = {"sub": "user-1", "iss": "luftfiber"}
    token = sign_claims(claims, KEY)
    assert token.count(".") == 2
    assert decode(token, KEY) == claims


def test_verify_rejects_tampered_payload():
    token = sign_claims({"sub": "a"}, KEY)
    h, p, s = token.split(".")
    forged_payload = b64url_encode(json.dumps({"sub": "b"}).encode())
    with pytest.raises(InvalidSignature):
        verify(f"{h}.{forged_payload}.{s}", KEY)


def test_verify_rejects_wrong_key():
    token = sign_claims({"sub": "a"}, KEY)
    with pytest.raises(InvalidSignature):
        verify(token, b"other-key")


def test_verify_rejects_alg_none_and_confusion():
    # Hand-build a token whose header claims alg=none: must be rejected,
    # never accepted on the strength of the header alone.
    header = b64url_encode(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    payload = b64url_encode(json.dumps({"sub": "evil"}).encode())
    with pytest.raises(JWTError):
        verify(f"{header}.{payload}.", KEY)
    rs_header = b64url_encode(json.dumps({"alg": "RS256"}).encode())
    with pytest.raises(JWTError):
        verify(f"{rs_header}.{payload}.sig", KEY)


def test_malformed_tokens_rejected():
    for bad in ("", "a.b", "a.b.c.d", "not-a-token", "..",
                "!!!.b64.c"):
        with pytest.raises(JWTError):
            verify(bad, KEY)


def test_exp_nbf_validation_with_explicit_now():
    validate_claims({"exp": 100}, now=99)
    with pytest.raises(ClaimValidationError):
        validate_claims({"exp": 100}, now=101)
    validate_claims({"exp": 100}, now=101, leeway=5)
    validate_claims({"nbf": 50}, now=50)
    with pytest.raises(ClaimValidationError):
        validate_claims({"nbf": 50}, now=49)


def test_decode_applies_time_validation():
    token = sign_claims({"sub": "x", "exp": 1000}, KEY)
    assert decode(token, KEY, now=999)["sub"] == "x"
    with pytest.raises(ClaimValidationError):
        decode(token, KEY, now=1001)
