# Dust Lord / Lord Dusk

A tiny local-agent smart-home project: give a Roborock vacuum a dramatic external voice without flashing firmware.

**Dust Lord** is the robot body. **Lord Dusk** is the persona voice. The robot is controlled through Roborock RPC while Lord Dusk speaks through TTS → local HTTP → Google/Nest Cast.

> I am small, round, and unreasonable.

## Demo

[![Dust Lord launch preview](media/preview/dustlord-launch-preview.gif)](media/final/dustlord-launch-x-github-preview.mp4)

GitHub does not reliably render repository MP4 files inline in README pages, so the README uses an animated GIF preview above. Click it for the GitHub-preview MP4.

- GitHub-preview MP4: [`media/final/dustlord-launch-x-github-preview.mp4`](media/final/dustlord-launch-x-github-preview.mp4)
- Full-quality launch video: [`media/final/dustlord-launch-x-landscape.mp4`](media/final/dustlord-launch-x-landscape.mp4)
- Downloadable release assets: <https://github.com/SwedishGold/dustlord/releases/tag/v0.1.0>

The first public launch clip introduces Dust Lord as a physical household agent: a Roborock S6 MaxV with memory, state transitions, a voice in the room, and a mythological problem with crumbs.

## Creator / links

- Created by **Andreas H** with Ada Inc weirdness.
- LinkedIn: <https://www.linkedin.com/in/andreas-hillborgh-51581371/>
- Launch framing: `@NousResearch` / Hermes in the loop.

## Why this exists

Robot vacuums already have APIs, sensors, state transitions, and physical presence. This project adds an agentic persona layer on top:

```text
robot status/events → watcher → scenario → behavior engine → voice library → TTS → local HTTP → smart speaker
```

The Roborock onboard speaker stays muted. No firmware flashing is required for the current approach.

## Current status

- Roborock body control: working locally
- Lord Dusk TTS/Cast voice: working locally
- Watcher daemon: working on macOS launchd
- CLI: v0.3 operational baseline
- Behavior engine: mood, memory, rarity, safe-silence, mission hooks
- Voice library: 16 scenarios / 111 lines
- Demo video: included under `media/final/`
- Public repo: <https://github.com/SwedishGold/dustlord>

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
bin/dustlord behavior status
```

## Quick local setup

For the full beginner-friendly path from installing Hermes Agent to wiring Dust Lord, see:

[`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md)

Short version:

1. Install Hermes Agent if you want the same agent/operator layer used in the launch workflow:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
   hermes setup
   hermes doctor
   ```
2. Copy the example config:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` with your local Roborock RPC helper, Cast target, and TTS settings.
4. Keep real tokens, local keys, device IDs, home maps, logs, and generated audio out of Git.
5. Validate the voice library:
   ```bash
   DUSTLORD_HOME="$PWD" \
   DUSTLORD_VOICE_LIBRARY="$PWD/data/lord-dusk-voice-library.json" \
   bin/dustlord library validate --json
   ```
6. Test the persona without moving the robot:
   ```bash
   DUSTLORD_HOME="$PWD" \
   DUSTLORD_VOICE_LIBRARY="$PWD/data/lord-dusk-voice-library.json" \
   python3 scripts/dustlord_say.py --scenario manual_summon --dry-run
   ```

## Safety model

- Starting a vacuum has physical side effects. Do not run movement commands unless requested.
- Keep the onboard robot speaker muted if using the external persona layer.
- Do not commit Roborock tokens, local keys, account caches, device IDs, private home maps, or camera/security data.
- Treat camera/home-security features as out of scope unless explicitly authorized.
- Review demo media before publishing; avoid addresses, screens, family photos, QR codes, app screens, and other private details.

## Architecture

```text
Hermes / user
  ↓
dustlord CLI
  ├─ Roborock RPC → vacuum body
  └─ watcher/say → behavior engine → edge-tts → local HTTP → Nest Audio / Cast
```

## Repository layout

```text
bin/dustlord                         # operator CLI
scripts/dustlord_watch.py             # state transition watcher
scripts/dustlord_say.py               # TTS + Cast voice path
scripts/dustlord_behavior.py          # persona behavior/memory/rarity layer
data/lord-dusk-voice-library.json     # persona line library
docs/ROADMAP.md                       # project roadmap
docs/OPERATIONS.md                    # local operations guide
docs/PUBLICATION_CHECKLIST.md         # before publishing to GitHub
docs/DUST_LORD_VIDEO_PROJECT.md       # launch-video idea, shoot list, editing workflow
media/final/dustlord-launch-x-github-preview.mp4 # small preview that GitHub can display
media/final/dustlord-launch-x-landscape.mp4      # full-quality launch clip
.env.example                          # local config template
```

## Notes

This is currently a macOS/Hermes-tailored project. Public hardening focuses on config/env loading, mocked tests, launchd setup docs, and safer installation scripts.

## License

MIT.
