from __future__ import annotations

import argparse
import asyncio
from collections.abc import Sequence

from .ble import all_off, connect_check, scan, send_commands
from .protocol import DEVICE, all_off_commands, preset_commands, preset_names


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Control the tested J-Virtuoso2 Joyhub-compatible BLE device.")
    parser.add_argument("--address", default=DEVICE.address, help="BLE address to use.")
    sub = parser.add_subparsers(dest="command", required=True)

    scan_parser = sub.add_parser("scan", help="Scan nearby BLE devices.")
    scan_parser.add_argument("--seconds", type=float, default=8.0)

    sub.add_parser("connect", help="Connect and print discovered GATT services.")

    raw_parser = sub.add_parser("send", help="Send raw hex commands with automatic all-off cleanup by default.")
    raw_parser.add_argument("hex_command", nargs="+")
    raw_parser.add_argument("--hold-seconds", type=float, default=0.0)
    raw_parser.add_argument("--between-command-delay", type=float, default=0.0)
    raw_parser.add_argument("--no-cleanup", action="store_true", help="Disable automatic all-off cleanup.")
    raw_parser.add_argument("--dry-run", action="store_true", help="Print commands without connecting.")

    preset_parser = sub.add_parser("preset", help="Send a verified preset with automatic all-off cleanup by default.")
    preset_parser.add_argument("name", choices=preset_names())
    preset_parser.add_argument("--hold-seconds", type=float, default=0.0)
    preset_parser.add_argument("--between-command-delay", type=float, default=0.0)
    preset_parser.add_argument("--no-cleanup", action="store_true", help="Disable automatic all-off cleanup.")
    preset_parser.add_argument("--dry-run", action="store_true", help="Print commands without connecting.")

    sub.add_parser("all-off", help="Explicitly stop wave and suction/squeeze functions.")
    sub.add_parser("presets", help="List verified preset names.")
    return parser


def _print_commands(commands: Sequence[str], cleanup: bool) -> None:
    for command in commands:
        print(command)
    if cleanup:
        print("# cleanup")
        for command in all_off_commands():
            print(command)


async def run(args: argparse.Namespace) -> int:
    if args.command == "scan":
        for device in await scan(args.seconds):
            print(f"{device['name'] or '(no name)'} [{device['address']}] RSSI={device['rssi']}")
        return 0
    if args.command == "connect":
        for service in await connect_check(args.address):
            print(service["uuid"])
            for characteristic in service["characteristics"]:
                print(f"  {characteristic['uuid']} {','.join(characteristic['properties'])}")
        return 0
    if args.command == "all-off":
        await all_off(args.address)
        return 0
    if args.command == "presets":
        print("\n".join(preset_names()))
        return 0
    if args.command == "send":
        cleanup = not args.no_cleanup
        if args.dry_run:
            _print_commands(args.hex_command, cleanup)
            return 0
        await send_commands(
            args.hex_command,
            address=args.address,
            cleanup=cleanup,
            hold_seconds=args.hold_seconds,
            between_command_delay=args.between_command_delay,
        )
        return 0
    if args.command == "preset":
        commands = preset_commands(args.name)
        cleanup = not args.no_cleanup
        if args.dry_run:
            _print_commands(commands, cleanup)
            return 0
        await send_commands(
            commands,
            address=args.address,
            cleanup=cleanup,
            hold_seconds=args.hold_seconds,
            between_command_delay=args.between_command_delay,
        )
        return 0
    raise SystemExit(f"unknown command: {args.command}")


def main(argv: Sequence[str] | None = None) -> int:
    return asyncio.run(run(build_parser().parse_args(argv)))


if __name__ == "__main__":
    raise SystemExit(main())
