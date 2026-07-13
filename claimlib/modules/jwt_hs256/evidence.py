# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-JWT-HS256-001 — the JWS/JWT HS256 implementation
reproduces the RFC 7515 Appendix A.1 published example byte-for-byte, agrees
with the stdlib base64 oracle on a fixed codec battery, enforces the RFC 7519
exp/nbf boundary semantics exactly, and rejects a fixed battery of malformed
and forged tokens.

Every expected value is INDEPENDENTLY KNOWN, never produced by the module:
  * RFC 7515 Appendix A.1 (verified at rfc-editor.org/rfc/rfc7515.txt): the
    exact header octets {"typ":"JWT",CRLF SP"alg":"HS256"}, the exact 70-octet
    payload (the RFC publishes the octet array — note the 13,10,32 line-break
    octets), the JWK key "k" value, the base64url header/payload strings, and
    the signature dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk.
  * RFC 4648 section 10 base64 test vectors ("f"->"Zg==", ... "foobar"->
    "Zm9vYmFy"), restated unpadded per the JWS base64url rule, plus the
    stdlib base64.urlsafe_b64encode/b64decode oracle (never imported by the
    vendored module) over fixed byte inputs.
  * RFC 7519 sections 4.1.4/4.1.5 MUST-clauses: exp rejects "on or after"
    (valid iff now < exp), nbf accepts "after or equal" (valid iff
    now >= nbf) — boundary arithmetic is exact mathematics.
Deterministic: same artifact on every run.
"""
from __future__ import annotations

import base64  # independent stdlib oracle — the module itself never imports it
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from jwt_hs256 import (  # noqa: E402
    JWTError, InvalidToken, InvalidSignature, ClaimValidationError,
    b64url_encode, b64url_decode, sign_bytes, sign_claims,
    verify, validate_claims, decode,
)
from _util import emit  # noqa: E402

# --- RFC 7515 Appendix A.1 published example (rfc-editor.org) --------------
# Header octets: {"typ":"JWT",\r\n "alg":"HS256"}  (the RFC's exact JSON,
# including the CRLF + space line break).
A1_HEADER_OCTETS = b'{"typ":"JWT",\r\n "alg":"HS256"}'
# Payload octets exactly as the RFC lists them (70 octets, incl. 13,10,32):
A1_PAYLOAD_OCTETS = bytes([
    123, 34, 105, 115, 115, 34, 58, 34, 106, 111, 101, 34, 44, 13, 10, 32,
    34, 101, 120, 112, 34, 58, 49, 51, 48, 48, 56, 49, 57, 51, 56, 48, 44,
    13, 10, 32, 34, 104, 116, 116, 112, 58, 47, 47, 101, 120, 97, 109, 112,
    108, 101, 46, 99, 111, 109, 47, 105, 115, 95, 114, 111, 111, 116, 34,
    58, 116, 114, 117, 101, 125])
A1_HEADER_B64 = "eyJ0eXAiOiJKV1QiLA0KICJhbGciOiJIUzI1NiJ9"
A1_PAYLOAD_B64 = ("eyJpc3MiOiJqb2UiLA0KICJleHAiOjEzMDA4MTkzODAsDQogImh0dHA6"
                  "Ly9leGFtcGxlLmNvbS9pc19yb290Ijp0cnVlfQ")
A1_SIGNATURE_B64 = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
A1_TOKEN = A1_HEADER_B64 + "." + A1_PAYLOAD_B64 + "." + A1_SIGNATURE_B64
# The JWK {"kty":"oct"} key's "k" member (base64url of the 64-byte key):
A1_KEY_B64 = ("AyM1SysPpbyDfgZld3umj1qzKObwVMkoqQ-EstJQLr_T-1qS0gZH75aKtMN3"
              "Yj0iPS4hcgUuTwjAzZr1Z9CAow")

# --- RFC 4648 section 10 vectors, unpadded base64url ------------------------
# Published as BASE64("f") = "Zg==" etc.; JWS strips the '=' padding, and no
# input here produces '+'/'/' so the url-safe strings are identical.
RFC4648_VECTORS = [
    (b"", ""),
    (b"f", "Zg"),
    (b"fo", "Zm8"),
    (b"foo", "Zm9v"),
    (b"foob", "Zm9vYg"),
    (b"fooba", "Zm9vYmE"),
    (b"foobar", "Zm9vYmFy"),
]

# Fixed byte inputs for the stdlib oracle cross-check (exercise '-'/'_',
# every byte value, and 0/1/2 mod-3 tail lengths). Deterministic constants.
ORACLE_INPUTS = [
    bytes(range(256)),
    b"\xfb\xef\xbe",       # encodes to '-'/'_'-bearing symbols
    b"\x00",
    b"\x00\xff",
    b"\xab" * 32,           # HS256 digest-sized input
]


def _stdlib_b64url_nopad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def run() -> dict:
    rows = []

    def check(section: str, name: str, ok: bool) -> None:
        rows.append({"section": section, "name": name, "ok": bool(ok)})

    def raises(fn, exc) -> bool:
        try:
            fn()
        except exc:
            return True
        except Exception:
            return False
        return False

    # ---- A. RFC 7515 Appendix A.1 published example (6 checks) ----
    key = b64url_decode(A1_KEY_B64)
    check("rfc7515_a1", "header_octets_encode_to_published_b64",
          b64url_encode(A1_HEADER_OCTETS) == A1_HEADER_B64)
    check("rfc7515_a1", "payload_octets_encode_to_published_b64",
          b64url_encode(A1_PAYLOAD_OCTETS) == A1_PAYLOAD_B64)
    check("rfc7515_a1", "jwk_k_decodes_to_64_byte_key", len(key) == 64)
    check("rfc7515_a1", "sign_bytes_reproduces_published_compact_jws",
          sign_bytes(A1_HEADER_OCTETS, A1_PAYLOAD_OCTETS, key) == A1_TOKEN)
    check("rfc7515_a1", "signature_segment_matches_published",
          sign_bytes(A1_HEADER_OCTETS, A1_PAYLOAD_OCTETS, key).split(".")[2]
          == A1_SIGNATURE_B64)
    hdr, payload = verify(A1_TOKEN, key)
    check("rfc7515_a1", "verify_accepts_published_token_and_returns_octets",
          hdr == {"typ": "JWT", "alg": "HS256"} and payload == A1_PAYLOAD_OCTETS)

    # ---- B. base64url codec vs published vectors + stdlib oracle (12) ----
    for raw, expected in RFC4648_VECTORS:
        ok = (b64url_encode(raw) == expected
              and b64url_decode(expected) == raw
              and _stdlib_b64url_nopad(raw) == expected)
        check("codec", f"rfc4648_s10_{raw.decode('ascii') or 'empty'}", ok)
    for raw in ORACLE_INPUTS:
        enc = b64url_encode(raw)
        ok = (enc == _stdlib_b64url_nopad(raw)
              and b64url_decode(enc) == raw
              and base64.urlsafe_b64decode(enc + "=" * (-len(enc) % 4)) == raw)
        check("codec", f"stdlib_oracle_len_{len(raw)}", ok)

    # ---- C. RFC 7519 exp/nbf boundary semantics (10 checks) ----
    # exp = 1300819380 is the A.1 payload's own expiration claim.
    check("time", "exp_accepts_now_before",
          decode(A1_TOKEN, key, now=1300819379) is not None)
    check("time", "exp_rejects_now_equal_on_or_after",
          raises(lambda: decode(A1_TOKEN, key, now=1300819380),
                 ClaimValidationError))
    check("time", "exp_rejects_now_after",
          raises(lambda: decode(A1_TOKEN, key, now=1300819381),
                 ClaimValidationError))
    check("time", "nbf_rejects_now_before",
          raises(lambda: validate_claims({"nbf": 1300819380}, 1300819379),
                 ClaimValidationError))
    check("time", "nbf_accepts_now_equal",
          validate_claims({"nbf": 1300819380}, 1300819380) is None)
    check("time", "nbf_accepts_now_after",
          validate_claims({"nbf": 1300819380}, 1300819381) is None)
    check("time", "exp_leeway_accepts_within",
          validate_claims({"exp": 1000}, 1059, leeway=60) is None)
    check("time", "exp_leeway_rejects_at_boundary",
          raises(lambda: validate_claims({"exp": 1000}, 1060, leeway=60),
                 ClaimValidationError))
    check("time", "nbf_leeway_accepts_within",
          validate_claims({"nbf": 1000}, 940, leeway=60) is None)
    check("time", "nbf_leeway_rejects_beyond",
          raises(lambda: validate_claims({"nbf": 1000}, 939, leeway=60),
                 ClaimValidationError))

    # ---- D. adversarial rejection battery (8 checks) ----
    tampered_payload = (A1_HEADER_B64 + "."
                        + A1_PAYLOAD_B64[:10]
                        + ("A" if A1_PAYLOAD_B64[10] != "A" else "B")
                        + A1_PAYLOAD_B64[11:] + "." + A1_SIGNATURE_B64)
    check("reject", "tampered_payload_invalid_signature",
          raises(lambda: verify(tampered_payload, key), InvalidSignature))
    tampered_sig = (A1_HEADER_B64 + "." + A1_PAYLOAD_B64 + "."
                    + A1_SIGNATURE_B64[:10]
                    + ("A" if A1_SIGNATURE_B64[10] != "A" else "B")
                    + A1_SIGNATURE_B64[11:])
    check("reject", "tampered_signature_invalid_signature",
          raises(lambda: verify(tampered_sig, key), InvalidSignature))
    none_token = (b64url_encode(b'{"alg":"none"}') + "." + A1_PAYLOAD_B64 + ".")
    check("reject", "alg_none_rejected",
          raises(lambda: verify(none_token, key), InvalidToken))
    hs384_token = sign_bytes(b'{"alg":"HS384"}', A1_PAYLOAD_OCTETS, key)
    check("reject", "alg_hs384_rejected",
          raises(lambda: verify(hs384_token, key), InvalidToken))
    check("reject", "wrong_key_invalid_signature",
          raises(lambda: verify(A1_TOKEN, b"not-the-key"), InvalidSignature))
    padded_token = (A1_HEADER_B64 + "." + A1_PAYLOAD_B64 + "==" + "."
                    + A1_SIGNATURE_B64)
    check("reject", "padded_segment_rejected",
          raises(lambda: verify(padded_token, key), InvalidToken))
    check("reject", "two_part_token_rejected",
          raises(lambda: verify(A1_HEADER_B64 + "." + A1_PAYLOAD_B64, key),
                 InvalidToken))
    crit_token = sign_bytes(b'{"alg":"HS256","crit":["exp"]}',
                            A1_PAYLOAD_OCTETS, key)
    check("reject", "crit_header_rejected",
          raises(lambda: verify(crit_token, key), InvalidToken))

    # ---- E. determinism / roundtrip (1 check) ----
    claims = {"iss": "joe", "exp": 1300819380}
    t1 = sign_claims(claims, key)
    t2 = sign_claims(claims, key)
    check("determinism", "sign_claims_deterministic_and_roundtrips",
          t1 == t2 and decode(t1, key, now=1300819379) == claims)

    sections = sorted({r["section"] for r in rows})
    per_section = {s: sum(1 for r in rows if r["section"] == s and r["ok"])
                   for s in sections}
    checks = len(rows)
    matched = sum(1 for r in rows if r["ok"])
    return {
        "schema": "claimlib_jwt_hs256_v1",
        "module": "jwt_hs256",
        "checks": checks,
        "checks_matched": matched,
        "mismatches": checks - matched,
        "rfc7515_a1_matched": per_section["rfc7515_a1"],
        "codec_matched": per_section["codec"],
        "time_checks_matched": per_section["time"],
        "rejections_correct": per_section["reject"],
        "rfc7515_a1_token": A1_TOKEN,
        "cases": rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "jwt_hs256.json", obj,
         script="python3 claimlib/modules/jwt_hs256/evidence.py")
    # claim:CLAIM-LIB-JWT-HS256-001 checks_matched
    # All 37 checks hold: 6 RFC 7515 A.1 vector checks, 12 codec checks
    # (7 RFC 4648 s10 vectors + 5 stdlib-oracle inputs), 10 RFC 7519 exp/nbf
    # boundary checks, 8 adversarial rejections, 1 determinism roundtrip —
    # so checks_matched = 37 and mismatches = 0.
    print(f"jwt_hs256: {obj['checks_matched']}/{obj['checks']} checks "
          f"(A.1 {obj['rfc7515_a1_matched']}/6, codec {obj['codec_matched']}/12, "
          f"time {obj['time_checks_matched']}/10, "
          f"reject {obj['rejections_correct']}/8); "
          f"mismatches {obj['mismatches']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
