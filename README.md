# Dust Lord / Lord Dusk

A tiny local-agent smart-home project: give a Roborock vacuum a dramatic external voice without flashing firmware.

**Dust Lord** is the robot body. **Lord Dusk** is the persona voice. The robot is controlled through Roborock RPC while Lord Dusk speaks through TTS → local HTTP → Google/Nest Cast.

> I am small, round, and unreasonable.

## Why this exists

Robot vacuums already have APIs, sensors, state transitions, and physical presence. This project adds an agentic persona layer on top:

```text
robot status/events → watcher → scenario → voice library → TTS → local HTTP → smart speaker
```

The Roborock onboard speaker stays muted. No firmware flashing is required for the current approach.

## Current status

- Roborock body control: working locally
- Lord Dusk TTS/Cast voice: working locally
- Watcher daemon: working on macOS launchd
- CLI: v0.2 operational
- Voice library: 16 scenarios / 111 lines
- Public repo status: local GitHub-ready skeleton, not yet published

## CLI

```bash
bin/dustlord --help
bin/dustlord health --pretty
bin/dustlord status
bin/dustlord say --text 'Lord Dusk is online.'
bin/dustlord test-cycle --clean-seconds 20
bin/dustlord last -n 3
bin/dustlord report
bin/dustlord library list
bin/dustlord library validate
```

## Safety model

- Starting a vacuum has physical side effects. Do not run movement commands unless requested.
- Keep the onboard robot speaker muted if using the external persona layer.
- Do not commit Roborock tokens, local keys, account caches, device IDs, or private home maps.
- Treat camera/home-security features as out of scope unless explicitly authorized.

## Architecture

```text
Hermes / user
  ↓
dustlord CLI
  ├─ Roborock RPC → vacuum body
  └─ watcher/say → edge-tts → local HTTP → Nest Audio / Cast
```

## Repository layout

```text
bin/dustlord                         # operator CLI
scripts/dustlord_watch.py             # state transition watcher
scripts/dustlord_say.py               # TTS + Cast voice path
data/lord-dusk-voice-library.json     # persona line library
docs/ROADMAP.md                       # project roadmap
docs/OPERATIONS.md                    # local operations guide
docs/PUBLICATION_CHECKLIST.md         # before publishing to GitHub
.env.example                          # local config template
```

## Install notes

This is currently a macOS/Hermes-tailored project. The public-friendly next step is replacing local hardcoded paths in scripts with config/env loading everywhere. See `docs/ROADMAP.md`.

## License

MIT.
