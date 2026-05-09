# TouchedByAnAgent

Use this skill when an agent needs to control the validated Joyhub-compatible `J-Virtuoso2 / Virtuoso 2` device from this repository.

## Device

- BLE address: `FF:25:07:11:DD:36`
- `productCode`: `3131`
- `icCode`: `8d`
- `abilityCode`: `01100000`
- `abilityLimit`: `060050000000`
- `switch_code`: `0803`

## Setup

```bash
python -m pip install -r requirements.txt -e .
```

If Bluetooth access is needed on Windows, run the commands from Windows Python rather than WSL.

## Commands

List presets:

```bash
touched-by-an-agent presets
```

Stop everything:

```bash
touched-by-an-agent all-off
```

Run a verified preset with automatic cleanup:

```bash
touched-by-an-agent preset vibration-9 --hold-seconds 10
touched-by-an-agent preset tongue-9 --hold-seconds 10
touched-by-an-agent preset combined-9 --hold-seconds 10
touched-by-an-agent preset suction-p3 --hold-seconds 10
touched-by-an-agent preset all-actuators-max --hold-seconds 10
```

Raw command sending also performs cleanup by default:

```bash
touched-by-an-agent send a00d000003ff a003ffff0000aa --hold-seconds 10
```

Use `--dry-run` to inspect commands before connecting.

## Protocol

- Vibration/tongue wave control: `a003 VV LL 00 00 aa`
- Wave off: `a00300000000aa`
- Suction/squeeze P1-P3: `a00d000001ff`, `a00d000002ff`, `a00d000003ff`
- Suction/squeeze off: `a00d00000000`
- All-actuator combined control: send suction first, then wave control:

```text
a00d000003ff
a003ffff0000aa
```

The reverse order did not reliably enable suction on the tested unit.

## Safety Rules

- Always prefer `preset` or `send` without `--no-cleanup`; automatic all-off cleanup is on by default.
- After any manual or interrupted run, execute `touched-by-an-agent all-off`.
- Keep the device close to the host and visible during live operation.
- Do not add shopping links, APK artifacts, decompiled source, UI code, scraping, unrelated product research, or broad multi-device work.

## Verification

```bash
python -m unittest discover
touched-by-an-agent preset all-actuators-max --dry-run
```
