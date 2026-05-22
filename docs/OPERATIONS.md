# Operations

## Local health

```bash
bin/dustlord health --pretty
```

Expected:

- body docked/cleaning/returning is readable
- `error=0`
- robot speaker volume is `0`
- watcher daemon is running

## Full test cycle

```bash
bin/dustlord test-cycle --clean-seconds 20
```

This physically starts the robot, waits for voice, sends it home, waits for docked voice, and verifies final state.

## Speech only

```bash
bin/dustlord say --text 'Lord Dusk is awake. The crumbs are nervous.'
```

Speech-only commands should not move the robot.

## Known benign warning

`urllib3 NotOpenSSLWarning` can appear with LibreSSL on macOS even when Cast playback succeeds.
