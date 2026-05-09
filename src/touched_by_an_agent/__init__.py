"""Minimal controller for the tested J-Virtuoso2 Joyhub-compatible device."""

from .protocol import DEVICE, all_off_commands, preset_commands, suction_command, wave_command

__all__ = [
    "DEVICE",
    "all_off_commands",
    "preset_commands",
    "suction_command",
    "wave_command",
]
