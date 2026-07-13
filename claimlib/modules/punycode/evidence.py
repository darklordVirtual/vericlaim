# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-PUNYCODE-001 — the Punycode codec reproduces every
RFC 3492 section 7.1 sample string, both directions, and agrees with Python's
independent stdlib codec.

The expected encodings are transcribed from RFC 3492 section 7.1 (samples A-S).
Two notes on case, per the module's documented contract (RFC 3492 section 5:
encoders emit lowercase; mixed-case annotation of appendix A is not used by
IDNA): sample (I)'s RFC listing prints one delta digit uppercase ("...baD...")
as a case ANNOTATION — the canonical lowercase form is expected here, and the
decoder is separately checked to accept the RFC's mixed-case spelling. Latin
capitals in samples D/J/K/L/M/N/P are basic code points and survive verbatim.

Independent oracles: (1) the published RFC strings themselves; (2) Python's
stdlib ``punycode`` codec — a separate implementation — must agree on every
sample and on a fixed generated battery. Deterministic: same artifact always.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from punycode import PunycodeError, decode, encode  # noqa: E402
from _util import emit  # noqa: E402

# (label, unicode input, expected Punycode) — RFC 3492 section 7.1.
SAMPLES = [
    ("A Arabic (Egyptian)",
     "ليهمابتكلم"
     "وشعربي؟",
     "egbpdaj6bu4bxfgehfvwxn"),
    ("B Chinese (simplified)",
     "他们为什么不说中文",
     "ihqwcrb4cv8a8dqg056pqjye"),
    ("C Chinese (traditional)",
     "他們爲什麽不說中文",
     "ihqwctvzc91f659drss3x8bo0yb"),
    ("D Czech",
     "Pročprostěnemluvíčesky",
     "Proprostnemluvesky-uyb24dma41a"),
    ("E Hebrew",
     "למההםפשוטל"
     "אמדבריםעבר"
     "ית",
     "4dbcagdahymbxekheh6e0a7fei0b"),
    ("F Hindi (Devanagari)",
     "यहलोगहिन्द"
     "ीक्योंनहीं"
     "बोलसकतेहैं",
     "i1baa7eci9glrd9b2ae1bj0hfcgg6iyaf8o0a1dig0cd"),
    ("G Japanese (kanji + hiragana)",
     "なぜみんな日本語を話"
     "してくれないのか",
     "n8jok5ay5dzabd5bym9f0cm5685rrjetr6pdxa"),
    ("H Korean (Hangul)",
     "세계의모든사람들이한"
     "국어를이해한다면얼마"
     "나좋을까",
     "989aomsvi5e83db1d2a355cv1e0vak1dwrv93d5xbh15a0dt30a5jpsd879ccm6fea98c"),
    ("I Russian (Cyrillic, canonical lowercase)",
     "почемужеон"
     "инеговорят"
     "порусски",
     "b1abfaaepdrnnbgefbadotcwatmq2g4l"),
    ("J Spanish",
     "PorquénopuedensimplementehablarenEspañol",
     "PorqunopuedensimplementehablarenEspaol-fmd56a"),
    ("K Vietnamese",
     "Tạisaohọkhôngthểchỉnóitiếng"
     "Việt",
     "TisaohkhngthchnitingVit-kjcr8268qyxafd2f1b9g"),
    ("L 3<nen>B<gumi><kinpachi><sensei>",
     "3年B組金八先生",
     "3B-ww4c5e180e575a65lsy2b"),
    ("M <amuro><namie>-with-SUPER-MONKEYS",
     "安室奈美恵-with-SUPER-MONKEYS",
     "-with-SUPER-MONKEYS-pc58ag80a8qai00g7n9n"),
    ("N Hello-Another-Way-<sorezore><no><basho>",
     "Hello-Another-Way-それぞれの場所",
     "Hello-Another-Way--fc4qua05auwb3674vfr0b"),
    ("O <hitotsu><yane><no><shita>2",
     "ひとつ屋根の下2",
     "2-u9tlzr9756bt3uc0v"),
    ("P Maji<de>Koi<suru>5<byou><mae>",
     "MajiでKoiする5秒前",
     "MajiKoi5-783gue6qz075azm5e"),
    ("Q <pafii>de<runba>",
     "パフィーdeルンバ",
     "de-jg4avhby1noc0d"),
    ("R <sono><supiido><de>",
     "そのスピードで",
     "d9juau41awczczp"),
    ("S -> $1.00 <-",
     "-> $1.00 <-",
     "-> $1.00 <--"),
]

# The RFC's mixed-case annotated spelling of sample (I): the decoder must
# accept digits in either case (RFC 3492 section 5).
I_MIXED_CASE = "b1abfaaepdrnnbgefbaDotcwatmq2g4l"

# Fixed battery for the stdlib cross-check beyond the samples.
EXTRA_BATTERY = [
    "bücher", "münchen", "æøå",
    "luftfiber-ås", "café", "日本語-dns",
    "a" * 60 + "é", "đđđ", "x",
]


def run() -> dict:
    rows = []
    matched = 0
    for label, text, expected in SAMPLES:
        enc_ok = encode(text) == expected
        dec_ok = decode(expected) == text
        ok = enc_ok and dec_ok
        matched += ok
        rows.append({"sample": label, "expected": expected,
                     "encode_ok": enc_ok, "decode_ok": dec_ok})

    mixed_ok = decode(I_MIXED_CASE) == SAMPLES[8][1]

    stdlib_checks = 0
    stdlib_ok = 0
    for text in [s[1] for s in SAMPLES] + EXTRA_BATTERY:
        stdlib_enc = text.encode("punycode").decode("ascii")
        stdlib_checks += 2
        if encode(text) == stdlib_enc:
            stdlib_ok += 1
        if decode(stdlib_enc) == text:
            stdlib_ok += 1

    rejects = 0
    for bad in ("xyz", "abc-é", "9999999999a"):
        try:
            decode(bad)
        except PunycodeError:
            rejects += 1

    return {
        "schema": "claimlib_evidence_v1",
        "module": "punycode",
        "samples": len(SAMPLES),
        "samples_matched": matched,
        "mismatches": len(SAMPLES) - matched,
        "mixed_case_decode_ok": 1 if mixed_ok else 0,
        "stdlib_checks": stdlib_checks,
        "stdlib_ok": stdlib_ok,
        "reject_cases": 3,
        "rejects_ok": rejects,
        "detail": rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "punycode.json", obj,
         script="python3 claimlib/modules/punycode/evidence.py")
    # claim:CLAIM-LIB-PUNYCODE-001 samples_matched
    # All 19 RFC 3492 section 7.1 samples round-trip exactly, so
    # samples_matched = 19 and mismatches = 0.
    print(f"punycode: {obj['samples_matched']}/{obj['samples']} RFC 3492 "
          f"samples matched both directions; stdlib agreement "
          f"{obj['stdlib_ok']}/{obj['stdlib_checks']}; "
          f"rejects {obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
