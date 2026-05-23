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

## Behavior Engine v0.3

Lord Dusk has a behavior layer in `scripts/dustlord_behavior.py` between `dustlord_say.py` and the voice library.

It adds:

- scenario-derived mood
- persistent event/mission memory
- stable `common` / `rare` / `legendary` line rarity
- safe silence for low-value chatter
- mission hooks from `clean_start` to `docked` / `clean_complete`
- recurring-problem “nemesis” counters

Commands:

```bash
bin/dustlord behavior status
bin/dustlord behavior report
bin/dustlord behavior reset
```

Dry-run verification without robot movement:

```bash
bin/dustlord say --scenario manual_summon --dry-run
bin/dustlord say --scenario cleaning_progress --dry-run
bin/dustlord behavior report
```

Config/env:

- `DUSTLORD_BEHAVIOR_SCRIPT` overrides script path.
- `DUSTLORD_BEHAVIOR_STATE_FILE` overrides state file.
- `DUSTLORD_AUDIO_DIR` controls the default behavior state directory.

## Known benign warning

`urllib3 NotOpenSSLWarning` can appear with LibreSSL on macOS even when Cast playback succeeds.
