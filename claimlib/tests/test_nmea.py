# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``nmea`` library.

Reference: the canonical NMEA 0183 example $GPGGA,...*47 and $GPRMC,...*68.
"""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "nmea"))

from nmea import checksum, checksum_hex, is_valid, build, NMEAError  # noqa: E402

GGA = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
RMC = "$GPRMC,225446,A,4916.45,N,12311.12,W,000.5,054.7,191194,020.3,E*68"


def test_published_checksums():
    assert checksum_hex(GGA) == "47"
    assert checksum_hex(RMC) == "68"
    assert checksum(GGA) == 0x47


def test_published_sentences_validate():
    assert is_valid(GGA) is True
    assert is_valid(RMC) is True


def test_build_round_trip():
    body = "GPVTG,054.7,T,034.4,M,005.5,N,010.2,K"
    sentence = build(body)
    assert sentence.startswith("$" + body + "*")
    assert is_valid(sentence) is True


def test_tamper_breaks_validity():
    corrupted = GGA.replace("123519", "123518")
    assert is_valid(corrupted) is False


def test_checksum_ignores_dollar_and_star():
    # Passing the bare payload or the full sentence yields the same checksum.
    body = "GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,"
    assert checksum_hex(body) == checksum_hex(GGA)


def test_rejects_bad_input():
    assert is_valid("no star here") is False
    assert is_valid("$X*ZZ") is False   # non-hex checksum field
    with pytest.raises(NMEAError):
        build("has*star")
