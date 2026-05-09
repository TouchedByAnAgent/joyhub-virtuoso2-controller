from __future__ import annotations

import asyncio
from collections.abc import Sequence

from .protocol import DEVICE, DeviceProfile, all_off_commands, bytes_from_hex


def _load_bleak():
    try:
        from bleak import BleakClient, BleakScanner  # type: ignore
    except ImportError as exc:
        raise SystemExit("Install dependencies first: python -m pip install -r requirements.txt") from exc
    return BleakClient, BleakScanner


async def scan(seconds: float = 8.0) -> list[dict[str, object]]:
    _, scanner = _load_bleak()
    devices = await scanner.discover(timeout=seconds)
    return [
        {
            "name": getattr(device, "name", None),
            "address": getattr(device, "address", None),
            "rssi": getattr(device, "rssi", None),
        }
        for device in devices
    ]


async def connect_check(address: str = DEVICE.address, profile: DeviceProfile = DEVICE) -> list[dict[str, object]]:
    BleakClient, _ = _load_bleak()
    async with BleakClient(address, timeout=20.0) as client:
        services = []
        for service in client.services:
            services.append(
                {
                    "uuid": service.uuid,
                    "characteristics": [
                        {"uuid": characteristic.uuid, "properties": list(characteristic.properties)}
                        for characteristic in service.characteristics
                    ],
                }
            )
        return services


async def send_commands(
    commands: Sequence[str],
    *,
    address: str = DEVICE.address,
    profile: DeviceProfile = DEVICE,
    cleanup: bool = True,
    hold_seconds: float = 0.0,
    between_command_delay: float = 0.0,
) -> None:
    BleakClient, _ = _load_bleak()
    async with BleakClient(address, timeout=20.0) as client:
        try:
            for index, command in enumerate(commands):
                await client.write_gatt_char(profile.write_characteristic_uuid, bytes_from_hex(command), response=False)
                if between_command_delay and index + 1 < len(commands):
                    await asyncio.sleep(between_command_delay)
            if hold_seconds:
                await asyncio.sleep(hold_seconds)
        finally:
            if cleanup:
                for command in all_off_commands():
                    await client.write_gatt_char(profile.write_characteristic_uuid, bytes_from_hex(command), response=False)


async def all_off(address: str = DEVICE.address, profile: DeviceProfile = DEVICE) -> None:
    await send_commands(all_off_commands(), address=address, profile=profile, cleanup=False)
