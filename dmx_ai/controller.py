"""DMX output controller with background refresh thread."""

from __future__ import annotations

import threading
import time
from typing import Callable, Dict, Optional

import serial

from dmx_ai.devices import DMXDevice, best_device
from dmx_ai.enttec_pro import EnttecProDriver
from dmx_ai.open_dmx import OpenDMXDriver
from dmx_ai.personalities import PRESETS, ColorMix, mix_to_channels


REFRESH_HZ = 40
REFRESH_INTERVAL = 1.0 / REFRESH_HZ


class DMXController:
    """Manages connection, universe buffer, and ~40 Hz output loop."""

    def __init__(
        self,
        on_status: Optional[Callable[[bool, str], None]] = None,
        on_mix_changed: Optional[Callable[[ColorMix], None]] = None,
    ) -> None:
        self._on_status = on_status
        self._on_mix_changed = on_mix_changed
        self._lock = threading.Lock()
        self._universe = bytearray(513)
        self._mix = ColorMix()
        self._personality = "10CH A001"
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._pro: Optional[EnttecProDriver] = None
        self._open: Optional[OpenDMXDriver] = None
        self._device: Optional[DMXDevice] = None
        self._connected = False
        self._blackout_on_disconnect = True

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def mix(self) -> ColorMix:
        with self._lock:
            return ColorMix(**vars(self._mix))

    @property
    def personality(self) -> str:
        return self._personality

    @property
    def device_label(self) -> str:
        if self._device:
            return self._device.label
        return "Disconnected"

    def _notify(self, connected: bool, message: str) -> None:
        if self._on_status:
            self._on_status(connected, message)

    def _apply_mix_to_universe(self) -> None:
        channels = mix_to_channels(self._personality, self._mix)
        for addr, value in channels.items():
            if 1 <= addr <= 512:
                self._universe[addr] = max(0, min(255, value))

    def _clear_channels_1_16(self) -> None:
        for i in range(1, 17):
            self._universe[i] = 0

    def set_personality(self, personality: str) -> None:
        with self._lock:
            self._personality = personality
            self._clear_channels_1_16()
            self._apply_mix_to_universe()

    def _notify_mix(self) -> None:
        if self._on_mix_changed:
            self._on_mix_changed(self.mix)

    def set_mix(self, mix: ColorMix) -> None:
        with self._lock:
            self._mix = mix
            self._apply_mix_to_universe()
        self._notify_mix()

    def apply_preset(self, name: str) -> ColorMix:
        preset = PRESETS[name]
        self.set_mix(preset)
        return preset

    def _output_loop(self) -> None:
        while self._running:
            try:
                with self._lock:
                    universe = bytes(self._universe)
                    pro = self._pro
                    open_drv = self._open

                if pro is not None:
                    pro.send_universe(bytearray(universe))
                elif open_drv is not None:
                    open_drv.send_universe(bytearray(universe))
            except Exception as exc:
                self._notify(False, f"Output error: {exc}")
                self._connected = False
                self._running = False
                break

            time.sleep(REFRESH_INTERVAL)

    def connect(self, device: Optional[DMXDevice] = None, *, reconnect: bool = False) -> bool:
        if self._connected:
            return True

        dev = device or best_device()
        if dev is None:
            self._notify(False, "No DMX device found")
            return False

        self._blackout_on_disconnect = not reconnect

        try:
            if dev.device_type == "pro":
                port = serial.Serial(
                    port=dev.port,
                    baudrate=57600,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=1,
                    write_timeout=1,
                    rtscts=False,
                )
                self._pro = EnttecProDriver(port)
                self._pro.configure()
                self._open = None
            else:
                if dev.serial_number:
                    url = f"ftdi://ftdi:232h:{dev.serial_number}/1"
                else:
                    url = "ftdi://ftdi:232h/1"
                open_drv = OpenDMXDriver(url)
                open_drv.open()
                self._open = open_drv
                self._pro = None

            self._device = dev
            self._connected = True
            self._running = True
            self._thread = threading.Thread(target=self._output_loop, daemon=True, name="dmx-output")
            self._thread.start()

            # On first connect with no colors set, send Full so user sees light respond
            with self._lock:
                if self._mix.colors_are_zero():
                    self._mix = PRESETS["Full"]
                    self._apply_mix_to_universe()
            self._notify_mix()

            self._notify(True, f"Live — {dev.label}")
            return True

        except Exception as exc:
            self._cleanup_ports()
            self._notify(False, f"Connect failed: {exc}")
            return False

    def disconnect(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None

        if self._blackout_on_disconnect:
            with self._lock:
                self._mix = PRESETS["Blackout"]
                self._apply_mix_to_universe()
                universe = bytes(self._universe)
            try:
                if self._pro is not None:
                    self._pro.send_universe(bytearray(universe))
                elif self._open is not None:
                    self._open.send_universe(bytearray(universe))
            except Exception:
                pass

        self._cleanup_ports()
        self._connected = False
        self._device = None
        self._notify(False, "Disconnected")

    def _cleanup_ports(self) -> None:
        if self._pro is not None:
            try:
                self._pro.close()
            except Exception:
                pass
            self._pro = None
        if self._open is not None:
            try:
                self._open.close()
            except Exception:
                pass
            self._open = None

    def reconnect(self, device: Optional[DMXDevice] = None) -> bool:
        """Reconnect without blackout flash."""
        was_connected = self._connected
        if was_connected:
            self._blackout_on_disconnect = False
            self.disconnect()
        return self.connect(device, reconnect=True)
