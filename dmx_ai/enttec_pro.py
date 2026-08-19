"""ENTTEC DMX USB Pro framed serial protocol."""

from __future__ import annotations

import struct
from typing import Iterable

START = 0x7E
END = 0xE7

LABEL_SET_WIDGET_PARAMETERS = 4
LABEL_OUTPUT_ONLY_SEND_DMX = 6

# user config size 0, longer break, MAB 2, 40 fps
WIDGET_PARAMETERS_PAYLOAD = bytes([0, 0, 32, 2, 40])


def _build_packet(label: int, payload: bytes) -> bytes:
    length = len(payload)
    header = struct.pack("<BBH", label, length & 0xFF, (length >> 8) & 0xFF)
    return bytes([START]) + header + payload + bytes([END])


def set_widget_parameters_packet() -> bytes:
    return _build_packet(LABEL_SET_WIDGET_PARAMETERS, WIDGET_PARAMETERS_PAYLOAD)


def send_dmx_packet(universe: Iterable[int]) -> bytes:
    """Build label-6 packet: start code 0 + 512 channel values."""
    values = list(universe)
    if len(values) != 513:
        raise ValueError("DMX universe must be 513 bytes (start code + 512 channels)")
    return _build_packet(LABEL_OUTPUT_ONLY_SEND_DMX, bytes(values))


class EnttecProDriver:
    """Send only label 4 once, then label 6 forever."""

    def __init__(self, serial_port) -> None:
        self._port = serial_port
        self._configured = False

    def configure(self) -> None:
        self._port.write(set_widget_parameters_packet())
        self._port.flush()
        self._configured = True

    def send_universe(self, universe: bytearray) -> None:
        if not self._configured:
            self.configure()
        self._port.write(send_dmx_packet(universe))
        self._port.flush()

    def close(self) -> None:
        self._configured = False
        if self._port and self._port.is_open:
            self._port.close()
