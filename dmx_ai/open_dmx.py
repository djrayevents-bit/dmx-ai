"""ENTTEC Open DMX USB fallback via pyftdi (250kbaud 8N2 + break)."""

from __future__ import annotations

import time


class OpenDMXDriver:
    """Host-generated DMX512 timing on FTDI bit-bang / UART."""

    def __init__(self, url: str) -> None:
        self._url = url
        self._device = None

    def open(self) -> None:
        from pyftdi.ftdi import Ftdi

        self._device = Ftdi()
        # 250000 8N2 — Open DMX standard
        self._device.open_from_url(self._url, direction=Ftdi.SERIAL)
        self._device.set_baudrate(250000)
        self._device.set_line_property(Ftdi.Bits.BITS_8, Ftdi.StopBits.STOP_BIT_2, Ftdi.Parity.NONE)

    def send_universe(self, universe: bytearray) -> None:
        if self._device is None:
            raise RuntimeError("Open DMX device not open")

        # DMX512 break (~88µs min) + MAB (~8µs) then start code + slots
        self._device.set_break(True)
        time.sleep(0.0001)  # ~100µs break
        self._device.set_break(False)
        time.sleep(0.000012)  # ~12µs MAB

        # Skip index 0 (start code) — send 513 bytes starting at universe[0]
        self._device.write_data(universe)

    def close(self) -> None:
        if self._device is not None:
            try:
                self._device.close()
            finally:
                self._device = None
