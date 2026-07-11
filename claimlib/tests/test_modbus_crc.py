# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``modbus_crc`` library.

Reference: the CRC catalogue value CRC-16/MODBUS("123456789") == 0x4B37.
"""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "modbus_crc"))

from modbus_crc import (  # noqa: E402
    crc16_modbus, crc16_modbus_bytes, append_crc, check_frame, ModbusCRCError)


def test_catalogue_check_value():
    assert crc16_modbus(b"123456789") == 0x4B37


def test_empty_is_init_value():
    assert crc16_modbus(b"") == 0xFFFF


def test_wire_trailer_is_little_endian():
    crc = crc16_modbus(b"123456789")           # 0x4B37
    assert crc16_modbus_bytes(b"123456789") == bytes([crc & 0xFF, crc >> 8])
    assert crc16_modbus_bytes(b"123456789") == b"\x37\x4b"


def test_append_and_check_round_trip():
    frame = b"\x11\x03\x00\x6b\x00\x03"
    framed = append_crc(frame)
    assert check_frame(framed) is True
    # Flip one payload bit -> check must fail.
    corrupted = bytes([framed[0] ^ 0x01]) + framed[1:]
    assert check_frame(corrupted) is False


def test_rejects_bad_input():
    with pytest.raises(ModbusCRCError):
        crc16_modbus("123456789")  # str, not bytes
    with pytest.raises(ModbusCRCError):
        check_frame(b"\x00")       # too short
