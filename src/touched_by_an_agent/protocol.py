from __future__ import annotations

from dataclasses import dataclass
import re


JOYHUB_SERVICE_UUID = "0000ffa0-0000-1000-8000-00805f9b34fb"
WRITE_CHARACTERISTIC_UUID = "0000ffa1-0000-1000-8000-00805f9b34fb"
NOTIFY_CHARACTERISTIC_UUID = "0000ffa2-0000-1000-8000-00805f9b34fb"


@dataclass(frozen=True)
class DeviceProfile:
    name: str
    address: str
    product_code: str
    ic_code: str
    ability_code: str
    ability_limit: str
    switch_code: str
    service_uuid: str = JOYHUB_SERVICE_UUID
    write_characteristic_uuid: str = WRITE_CHARACTERISTIC_UUID
    notify_characteristic_uuid: str = NOTIFY_CHARACTERISTIC_UUID
    vibration_minimum: int = 60
    tongue_minimum: int = 50


DEVICE = DeviceProfile(
    name="J-Virtuoso2 / Virtuoso 2",
    address="FF:25:07:11:DD:36",
    product_code="3131",
    ic_code="8d",
    ability_code="01100000",
    ability_limit="060050000000",
    switch_code="0803",
)


def _hex_byte(value: int) -> str:
    if not 0 <= value <= 255:
        raise ValueError(f"byte out of range: {value}")
    return f"{value:02x}"


def intensity_byte(level: int, minimum: int, max_level: int = 9) -> int:
    if not 0 <= level <= max_level:
        raise ValueError(f"level must be 0..{max_level}, got {level}")
    if level == 0:
        return 0
    return int(((255 - minimum) * (level / max_level)) + minimum)


def wave_command(vibration_level: int = 0, tongue_level: int = 0, profile: DeviceProfile = DEVICE) -> str:
    """Build the validated wave command: a003 VV LL 00 00 aa."""
    vibration = intensity_byte(vibration_level, profile.vibration_minimum)
    tongue = intensity_byte(tongue_level, profile.tongue_minimum)
    return "a003" + _hex_byte(vibration) + _hex_byte(tongue) + "0000aa"


def suction_command(level: int) -> str:
    """Build the validated suction/squeeze command for P0..P3."""
    if not 0 <= level <= 3:
        raise ValueError(f"suction level must be 0..3, got {level}")
    if level == 0:
        return "a00d00000000"
    return "a00d0000" + _hex_byte(level) + "ff"


def all_off_commands() -> tuple[str, str]:
    return (wave_command(0, 0), suction_command(0))


def all_actuator_commands(vibration_level: int = 9, tongue_level: int = 9, suction_level: int = 3) -> tuple[str, str]:
    """Run suction first, then wave control. The reverse order was not reliable."""
    return (suction_command(suction_level), wave_command(vibration_level, tongue_level))


def preset_commands(name: str) -> tuple[str, ...]:
    normalized = name.strip().lower()
    if normalized == "all-off":
        return all_off_commands()
    if normalized == "all-actuators-max":
        return all_actuator_commands()
    if normalized.startswith("vibration-"):
        return (wave_command(vibration_level=int(normalized.removeprefix("vibration-"))),)
    if normalized.startswith("tongue-") or normalized.startswith("licking-"):
        level = int(normalized.split("-", 1)[1])
        return (wave_command(tongue_level=level),)
    if normalized.startswith("combined-"):
        level = int(normalized.removeprefix("combined-"))
        return (wave_command(vibration_level=level, tongue_level=level),)
    if normalized.startswith("suction-p"):
        return (suction_command(int(normalized.removeprefix("suction-p"))),)
    raise ValueError(f"unknown preset: {name}")


def preset_names() -> list[str]:
    return (
        ["all-off"]
        + [f"vibration-{level}" for level in range(1, 10)]
        + [f"tongue-{level}" for level in range(1, 10)]
        + [f"combined-{level}" for level in range(1, 10)]
        + [f"suction-p{level}" for level in range(1, 4)]
        + ["all-actuators-max"]
    )


def bytes_from_hex(command: str) -> bytes:
    normalized = re.sub(r"\s+", "", command).lower()
    if len(normalized) % 2:
        raise ValueError(f"hex command has odd length: {command!r}")
    return bytes.fromhex(normalized)
