# SPDX-License-Identifier: Apache-2.0
"""CRC-16/MODBUS -- the frame check used by Modbus RTU serial fieldbus links.

A pre-verified claimlib code artifact: a reusable, stdlib-only building block
whose key property -- that it reproduces the published CRC catalogue check value
0x4B37 for the ASCII string "123456789" and agrees, byte for byte, with an
independent table-driven implementation -- is registered as a claim and proven
by a committed evidence artifact. Vendoring carries that claim (and caveat).

Modbus RTU appends a 16-bit CRC to every frame: reflected generator polynomial
0xA001 (the reflection of 0x8005), initial value 0xFFFF, input and output
reflected, no final XOR. The two check bytes are transmitted low byte first.

Public API
----------
    crc16_modbus(data: bytes) -> int          # the 16-bit CRC as an int
    crc16_modbus_bytes(data: bytes) -> bytes   # 2-byte little-endian trailer
    append_crc(frame: bytes) -> bytes          # frame + its CRC trailer
    check_frame(frame_with_crc: bytes) -> bool # verify a received frame

    >>> hex(crc16_modbus(b"123456789"))
    '0x4b37'
"""
from __future__ import annotations

_POLY = 0xA001  # reflected 0x8005


class ModbusCRCError(ValueError):
    """The input is not a bytes-like object, or the frame is too short."""


def crc16_modbus(data: bytes) -> int:
    """Return the CRC-16/MODBUS of *data* (bitwise reference implementation)."""
    if not isinstance(data, (bytes, bytearray)):
        raise ModbusCRCError("data must be bytes or bytearray")
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ _POLY
            else:
                crc >>= 1
    return crc & 0xFFFF


def crc16_modbus_bytes(data: bytes) -> bytes:
    """Return the CRC as its 2-byte Modbus wire trailer (low byte first)."""
    return crc16_modbus(data).to_bytes(2, "little")


def append_crc(frame: bytes) -> bytes:
    """Return *frame* with its CRC-16/MODBUS trailer appended."""
    return bytes(frame) + crc16_modbus_bytes(frame)


def check_frame(frame_with_crc: bytes) -> bool:
    """Return True iff *frame_with_crc*'s trailing 2 bytes are its correct CRC."""
    if not isinstance(frame_with_crc, (bytes, bytearray)):
        raise ModbusCRCError("frame must be bytes or bytearray")
    if len(frame_with_crc) < 3:
        raise ModbusCRCError("frame too short to contain payload + CRC")
    payload, trailer = frame_with_crc[:-2], frame_with_crc[-2:]
    return crc16_modbus_bytes(payload) == trailer
