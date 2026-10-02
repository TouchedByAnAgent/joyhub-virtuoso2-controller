<p align="center"><img src="assets/banner.jpg" alt="Glowing amber and magenta line-art of a generic handheld gadget emitting radio ripples while a stream of command packets flows toward a stop symbol." width="100%"></p>

# joyhub-virtuoso2-controller

Minimal production handoff repository for controlling the tested Joyhub-compatible device:

- Product link: https://amzn.to/4tpeo5E
- Device: `J-Virtuoso2 / Virtuoso 2`
- BLE address used during validation: `FF:25:07:11:DD:36`
- `productCode`: `3131`
- `icCode`: `8d`
- `abilityCode`: `01100000`
- `abilityLimit`: `060050000000`
- `switch_code`: `0803`

No APK artifacts, decompiled source, UI, scraping, broad product research, or unrelated device support are included.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -e .
```

On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -e .
```

## CLI

Scan:

```bash
touched-by-an-agent scan --seconds 8
```

Connect and print GATT services:

```bash
touched-by-an-agent connect
```

Run an explicit stop:

```bash
touched-by-an-agent all-off
```

Send a verified preset with automatic cleanup:

```bash
touched-by-an-agent preset vibration-9 --hold-seconds 10
touched-by-an-agent preset tongue-9 --hold-seconds 10
touched-by-an-agent preset combined-9 --hold-seconds 10
touched-by-an-agent preset suction-p3 --hold-seconds 10
touched-by-an-agent preset all-actuators-max --hold-seconds 10
```

Send raw commands with automatic cleanup:

```bash
touched-by-an-agent send a00d000003ff a003ffff0000aa --hold-seconds 10
```

Use `--dry-run` to print commands without connecting.

## Validated Protocol

Wave control uses:

```text
a003 VV LL 00 00 aa
```

`VV` is vibration level 1-9 and `LL` is tongue/licking level 1-9. Off is:

```text
a00300000000aa
```

Suction/squeeze uses:

```text
a00d00000Nff
```

where `N` is `1`, `2`, or `3`. Suction/squeeze off is:

```text
a00d00000000
```

All-actuator combined control requires suction/squeeze first, then wave control:

```text
a00d000003ff
a003ffff0000aa
```

The reverse order was not reliable on the tested device.

## Safety

The `send` and `preset` CLI commands perform automatic all-off cleanup by default. The explicit all-off command sends both wave-off and suction-off:

```text
a00300000000aa
a00d00000000
```

Use `--no-cleanup` only for controlled debugging where another process will stop the device.

## Test

```bash
python -m unittest discover
```

The tests use the Python standard library and cover device identity, command generation, preset coverage, safety cleanup behavior in dry-run CLI paths, and raw hex validation.

## Agent Handoff

Use `SKILL.md` as the agent-facing operating instructions. Keep changes focused on this validated device, the specified product link, and protocol. Do not add broad product research, APK-derived files, broad multi-device abstractions, UI code, or unrelated automation.
