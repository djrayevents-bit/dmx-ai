"""Fixture personality channel maps for Bothlighting 12×18W RGBWA+UV PAR @ address 1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ColorMix:
    master: int = 255
    red: int = 0
    green: int = 0
    blue: int = 0
    white: int = 0
    amber: int = 0
    uv: int = 0
    strobe: int = 0

    def is_all_zero(self) -> bool:
        return (
            self.master == 0
            and self.red == 0
            and self.green == 0
            and self.blue == 0
            and self.white == 0
            and self.amber == 0
            and self.uv == 0
        )

    def colors_are_zero(self) -> bool:
        """True when no color channels are active (ignores master)."""
        return (
            self.red == 0
            and self.green == 0
            and self.blue == 0
            and self.white == 0
            and self.amber == 0
            and self.uv == 0
        )


PERSONALITY_NAMES = ("10CH A001", "6CH D001", "10CH Alt")

# Logical field → DMX channel (1-based, address 1)
PERSONALITY_MAPS: Dict[str, Dict[str, int]] = {
    "10CH A001": {
        "master": 1,
        "strobe": 2,
        "function": 3,
        "program_speed": 4,
        "red": 5,
        "green": 6,
        "blue": 7,
        "white": 8,
        "amber": 9,
        "uv": 10,
    },
    "6CH D001": {
        "red": 1,
        "green": 2,
        "blue": 3,
        "white": 4,
        "amber": 5,
        "uv": 6,
    },
    "10CH Alt": {
        "master": 1,
        "red": 2,
        "green": 3,
        "blue": 4,
        "white": 5,
        "amber": 6,
        "uv": 7,
        "strobe": 8,
        "mode": 9,
        "ch10": 10,
    },
}

# Channels that must stay at 0 for live color mixing
ZERO_CHANNELS: Dict[str, tuple[int, ...]] = {
    "10CH A001": (3, 4),  # function, program speed
    "6CH D001": (),
    "10CH Alt": (9, 10),  # mode, ch10
}


def _scaled(value: int, master: int) -> int:
    return max(0, min(255, int(value * master / 255)))


def mix_to_channels(personality: str, mix: ColorMix) -> Dict[int, int]:
    """Map logical color mix to DMX channel values for the given personality."""
    mapping = PERSONALITY_MAPS[personality]
    channels: Dict[int, int] = {}

    # 6CH D001 has no master channel — scale colors in software
    scale_master = "master" not in mapping

    if "master" in mapping:
        channels[mapping["master"]] = mix.master
    if "strobe" in mapping:
        channels[mapping["strobe"]] = mix.strobe

    m = mix.master if scale_master else 255
    if "red" in mapping:
        channels[mapping["red"]] = _scaled(mix.red, m) if scale_master else mix.red
    if "green" in mapping:
        channels[mapping["green"]] = _scaled(mix.green, m) if scale_master else mix.green
    if "blue" in mapping:
        channels[mapping["blue"]] = _scaled(mix.blue, m) if scale_master else mix.blue
    if "white" in mapping:
        channels[mapping["white"]] = _scaled(mix.white, m) if scale_master else mix.white
    if "amber" in mapping:
        channels[mapping["amber"]] = _scaled(mix.amber, m) if scale_master else mix.amber
    if "uv" in mapping:
        channels[mapping["uv"]] = _scaled(mix.uv, m) if scale_master else mix.uv

    for ch in ZERO_CHANNELS.get(personality, ()):
        channels[ch] = 0

    return channels


PRESETS: Dict[str, ColorMix] = {
    "Red": ColorMix(red=255),
    "Green": ColorMix(green=255),
    "Blue": ColorMix(blue=255),
    "White": ColorMix(white=255),
    "Amber": ColorMix(amber=255),
    "UV": ColorMix(uv=255),
    "Magenta": ColorMix(red=255, blue=255),
    "Cyan": ColorMix(green=255, blue=255),
    "Yellow": ColorMix(red=255, green=180, amber=80),
    "Orange": ColorMix(red=255, green=70, amber=160),
    "Pink": ColorMix(red=255, green=40, blue=120, white=80),
    "Warm": ColorMix(red=80, green=20, white=200, amber=180),
    "Full": ColorMix(red=255, green=255, blue=255, white=255, amber=255, uv=255),
    "Blackout": ColorMix(master=0, red=0, green=0, blue=0, white=0, amber=0, uv=0, strobe=0),
}
