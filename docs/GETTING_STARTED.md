# Getting started: Hermes → Dust Lord

This guide is intentionally beginner-friendly. It shows the path from installing Hermes Agent to running the Dust Lord local-agent vacuum persona.

Dust Lord is not a one-click product yet. It is a public, hackable reference project for people who already have a robot vacuum, a Mac/Linux machine, and a willingness to wire local automation safely.

## What you need

- A macOS or Linux machine.
- Python 3.11+ recommended.
- A Roborock vacuum that can be controlled locally through your own RPC/helper setup.
- A speaker target if you want the external voice layer, for example Google/Nest Cast.
- Hermes Agent if you want the same agent workflow used in the launch video.

## 1. Install Hermes Agent

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

Then run the setup wizard:

```bash
hermes setup
hermes doctor
```

Useful Hermes docs:

- https://hermes-agent.nousresearch.com/docs/
- https://github.com/NousResearch/hermes-agent

## 2. Clone Dust Lord

```bash
git clone https://github.com/SwedishGold/dustlord.git
cd dustlord
```

## 3. Create local config

```bash
cp .env.example .env
```

Open `.env` and fill in your local paths/targets. Keep all real secrets and local device identifiers out of Git.

Important values are usually:

- `DUSTLORD_HOME` — path to this repo or runtime folder.
- `DUSTLORD_VOICE_LIBRARY` — path to `data/lord-dusk-voice-library.json`.
- `DUSTLORD_RPC_PY` / `DUSTLORD_RPC_SCRIPT` — your local Roborock helper Python/script.
- `DUSTLORD_CAST_HOST` or `DUSTLORD_CAST_UUID` — your speaker target, if using Cast.

## 4. Validate without moving the robot

First check that the persona library is valid:

```bash
DUSTLORD_HOME="$PWD" \
DUSTLORD_VOICE_LIBRARY="$PWD/data/lord-dusk-voice-library.json" \
bin/dustlord library validate --json
```

Then dry-run one Lord Dusk line. This should not move the robot:

```bash
DUSTLORD_HOME="$PWD" \
DUSTLORD_VOICE_LIBRARY="$PWD/data/lord-dusk-voice-library.json" \
python3 scripts/dustlord_say.py --scenario manual_summon --dry-run
```

## 5. Only then connect real hardware

Before any command that can move a vacuum:

1. Confirm your Roborock helper works locally.
2. Confirm the robot is in a safe area.
3. Keep the onboard robot speaker muted if you use external TTS/Cast.
4. Never commit tokens, local keys, account caches, maps, logs, camera images, or home-security data.

Example operator checks once your local integration is wired:

```bash
bin/dustlord health --pretty
bin/dustlord status
bin/dustlord say --text 'Lord Dusk is online.'
```

Example bounded movement test, only when you explicitly intend to move the robot:

```bash
bin/dustlord test-cycle --clean-seconds 20
```

## 6. How Hermes fits in

Hermes is the agent/operator layer. In the launch workflow, Hermes can:

- inspect and edit the Dust Lord codebase;
- run validation/tests;
- trigger safe Dust Lord commands when authorized;
- create voice lines and social/video drafts;
- remember reusable workflows as skills.

Dust Lord itself remains local-first: robot control, speaker output, logs, and device secrets stay on your machine.

## Safety summary

- Dry-run first.
- Move hardware only on purpose.
- Keep secrets out of Git.
- Keep private home data out of demo media.
- Treat any camera/security features as out of scope unless explicitly authorized.
