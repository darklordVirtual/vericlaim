# SPDX-License-Identifier: Apache-2.0
"""NMEA 0183 sentence checksum -- the integrity field on GPS / marine / SCADA
serial telemetry links.

A pre-verified claimlib code artifact. An NMEA 0183 sentence looks like
``$GPGGA,123519,4807.038,N,...*47``: the two hex digits after ``*`` are the XOR
of every character between ``$`` and ``*`` (exclusive). This module computes and
verifies that checksum; that it reproduces the checksums of the canonical
published example sentences is registered as a claim and proven by a committed
evidence artifact. Vendoring carries that claim (and caveat).

Public API
----------
    checksum(sentence: str) -> int          # XOR of the payload bytes
    checksum_hex(sentence: str) -> str      # two upper-case hex digits
    is_valid(sentence: str) -> bool         # verify a '*HH'-terminated sentence
    build(payload: str) -> str              # '$' + payload + '*HH'

    >>> checksum_hex("GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,")
    '47'
"""
from __future__ import annotations


class NMEAError(ValueError):
    """The sentence is malformed (missing '*', bad checksum field, ...)."""


def _payload(sentence: str) -> str:
    """Return the characters that the checksum covers (between '$' and '*')."""
    s = sentence
    if s.startswith("$"):
        s = s[1:]
    star = s.find("*")
    if star != -1:
        s = s[:star]
    return s


def checksum(sentence: str) -> int:
    """Return the XOR checksum of *sentence*'s payload as an int (0-255)."""
    if not isinstance(sentence, str):
        raise NMEAError("sentence must be a string")
    value = 0
    for ch in _payload(sentence):
        value ^= ord(ch)
    return value & 0xFF


def checksum_hex(sentence: str) -> str:
    """Return the checksum as two upper-case hexadecimal digits."""
    return f"{checksum(sentence):02X}"


def is_valid(sentence: str) -> bool:
    """Return True iff *sentence* carries a correct '*HH' checksum field."""
    if not isinstance(sentence, str):
        return False
    star = sentence.find("*")
    if star == -1 or len(sentence) - star < 3:
        return False
    field = sentence[star + 1:star + 3]
    try:
        stated = int(field, 16)
    except ValueError:
        return False
    return stated == checksum(sentence)


def build(payload: str) -> str:
    """Return a complete sentence: '$' + *payload* + '*' + checksum hex."""
    if "*" in payload or "$" in payload:
        raise NMEAError("payload must not contain '$' or '*'")
    return f"${payload}*{checksum_hex(payload)}"
