"""Serial device discovery for ENTTEC DMX interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import serial.tools.list_ports


ENTTEC_PRO_VID_PID = (0x0403, 0x6001)
OPEN_DMX_VID_PID = (0x0403, 0x6001)  # same FTDI chip; distinguished by description


@dataclass
class DMXDevice:
    port: str
    description: str
    serial_number: str
    device_type: str  # "pro" or "open"
    score: int  # higher = preferred

    @property
    def label(self) -> str:
        kind = "Pro" if self.device_type == "pro" else "Open DMX"
        serial = f" ({self.serial_number})" if self.serial_number else ""
        return f"{self.port} — {kind}{serial}"


def _score_device(port, desc: str, serial: str, device_type: str) -> int:
    score = 0
    desc_lower = (desc or "").lower()
    serial_upper = (serial or "").upper()
    port_lower = (port or "").lower()

    if device_type == "pro":
        score += 100
    if "dmx usb pro" in desc_lower:
        score += 200
    if serial_upper.startswith("EN"):
        score += 150
    if "/dev/cu.usbserial-en" in port_lower:
        score += 120
    if "open dmx" in desc_lower:
        score -= 50
    return score


def list_dmx_devices() -> List[DMXDevice]:
    devices: List[DMXDevice] = []
    seen_ports = set()

    for info in serial.tools.list_ports.comports():
        port = info.device
        if port in seen_ports:
            continue
        seen_ports.add(port)

        vid = info.vid or 0
        pid = info.pid or 0
        desc = info.description or ""
        serial_num = info.serial_number or ""
        desc_lower = desc.lower()

        device_type: Optional[str] = None
        if vid == ENTTEC_PRO_VID_PID[0] and pid == ENTTEC_PRO_VID_PID[1]:
            if "open dmx" in desc_lower:
                device_type = "open"
            elif "dmx usb pro" in desc_lower or serial_num.upper().startswith("EN"):
                device_type = "pro"
            else:
                # Default FTDI ENTTEC to Pro unless explicitly Open
                device_type = "pro"
        elif "dmx" in desc_lower:
            device_type = "pro" if "pro" in desc_lower else "open"

        if device_type is None:
            continue

        # Prefer cu.* on macOS
        if port.startswith("/dev/tty.") and f"/dev/cu.{port.split('/dev/tty.', 1)[1]}" in seen_ports:
            continue

        devices.append(
            DMXDevice(
                port=port,
                description=desc,
                serial_number=serial_num,
                device_type=device_type,
                score=_score_device(port, desc, serial_num, device_type),
            )
        )

    devices.sort(key=lambda d: (-d.score, d.port))
    return devices


def best_device() -> Optional[DMXDevice]:
    devices = list_dmx_devices()
    return devices[0] if devices else None
