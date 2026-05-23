# Dust Lord Video Project — launch clip

Status: launch video rendered / X-ready asset included  
Owner/creator framing: Andreas H + Ada Inc  
GitHub preview asset: `media/final/dustlord-launch-x-github-preview.mp4`  
Full-quality final asset: `media/final/dustlord-launch-x-landscape.mp4`  
Creator link: <https://www.linkedin.com/in/andreas-hillborgh-51581371/>  
Related: [[Dust Lord / Lord Dusk]], `README.md`, `docs/ROADMAP.md`, `docs/PUBLICATION_CHECKLIST.md`

## Core idea

Create a short shareable video that introduces **Dust Lord** as a physical household agent: a Roborock S6 MaxV with memory, timing, state transitions, a voice in the room, and a mythological problem with crumbs.

The tone should match the first public X launch post:

> Domestic robotics gets weird when it remembers.

This is not a generic “smart vacuum demo”. It should feel like **domestic robotics becoming folklore**: dock as altar, floor as battlefield, crumbs as entropy, Lord Dusk as the voice layer, Andreas H as creator, Ada Inc as the weirdness field.

## Target formats

Primary:
- X video: 16:9 or 4:5, 15–25 seconds.

Secondary exports:
- Reels/TikTok/Shorts: 9:16, 15–25 seconds.
- Optional GIF/teaser: 5–8 seconds.

## Visual identity

- Dark Nordic domestic product-photography.
- Low angles near floor level so Dust Lord feels like a small embodied character.
- Warm lamp light, black/wood surfaces, cinematic shadows.
- Ada red accent: `#E0001B`, used sparingly for overlays/UI pulses.
- No cheesy AI glow, no brain icons, no corporate SaaS gradient.
- Charging dock can be framed like a tiny altar.
- Text should be sparse, high-contrast, and readable on mobile.

## Shoot list for Andreas

Film short clips, ideally 4K if possible. Keep each clip 3–8 seconds and mostly stable.

Required shots:
1. **Dock/altar establishing shot** — Dust Lord standing in the dock.
2. **Departure** — Dust Lord starts and leaves the dock.
3. **Low tracking shot** — she moves across the floor, camera close to ground.
4. **Detail shot** — wheel, brush, LiDAR/sensor, or side profile moving past camera.
5. **Crumb/entropy shot** — visible crumbs/dust/object on floor before she reaches it.
6. **Domestic obstacle shot** — chair leg, shoe, cable, toy, rug edge, etc.
7. **Return/docking shot** — she returns home or approaches the dock.
8. **Optional voice shot** — room/Nest speaker while Lord Dusk line is audible.

Useful extras:
- A human hand placing crumbs or pressing start.
- A reaction shot from the room: light, speaker, shadows, floor-level POV.
- A top-down shot for UI/map/mission-overlay style.
- A very short “failed pathfinding” or hesitation moment if it happens naturally.

## Suggested clip arc

### Version A — cinematic launch, 20s

0.0–2.0 — Dark dock shot. Text: `MEET DUST LORD`  
2.0–5.0 — Dust Lord leaves dock. Text: `Roborock body.`  
5.0–8.0 — Low movement / brush detail. Text: `Memory. Timing. Voice.`  
8.0–12.0 — Crumbs/obstacle. Text: `A tiny mythological problem with crumbs.`  
12.0–16.0 — Return/docking or strong movement shot. Text: `Created by Andreas H.`  
16.0–20.0 — Final hero frame / dock. Text: `Domestic robotics gets weird when it remembers.`

### Version B — funny/lore, 15s

0.0–2.0 — `THE CRUMBS WERE WARNED.`  
2.0–6.0 — Dust Lord rolls out.  
6.0–10.0 — Crumbs/brush/obstacle. Lord Dusk line if available.  
10.0–13.0 — Docking/return.  
13.0–15.0 — `Meet Dust Lord.` + tags/credits.

### Version C — technical/agentic, 25s

0.0–3.0 — Dock shot. `Roborock body.`  
3.0–7.0 — Movement. `Watcher daemon observes state transitions.`  
7.0–11.0 — Speaker/room. `Lord Dusk speaks through the house.`  
11.0–16.0 — Cleaning/crumbs. `A small embodied agent against entropy.`  
16.0–21.0 — Return/dock. `Created by Andreas H. Raised in Ada Inc weirdness.`  
21.0–25.0 — Final title/tagline.

## Possible Lord Dusk lines

Use existing voice-library scenarios where possible, or generate a manual line and record/capture it.

Good launch lines:
- “The crumbs are nervous.”
- “I am small, round, and unreasonable.”
- “The altar has received me.”
- “I return with dust in my memory.”
- “Entropy has been reduced.”

Rules:
- Lord Dusk voice remains English-only.
- Keep onboard robot speaker muted; voice is external Cast/TTS.
- Avoid too many lines; one strong line is enough.

## Editing workflow Hermes can use

When Andreas sends source clips:

1. Save all clips under:
   ```text
   ~/Documents/AdaAgents/03_PROJECTS/dustlord/media/raw/YYYY-MM-DD-dustlord-shoot/
   ```
2. Inspect duration/resolution/audio:
   ```bash
   ffprobe -v error -show_entries stream=codec_type,width,height,duration -of json clip.mp4
   ```
3. Select best moments and trim rough cuts with ffmpeg:
   ```bash
   ffmpeg -ss START -to END -i input.mp4 -c:v libx264 -c:a aac clip-trim.mp4
   ```
4. Normalize orientation and frame for target format:
   - X landscape: 1920×1080
   - X portrait/Reels: 1080×1920
   - Use crop/scale, do not distort.
5. Build a motion-graphics composition with HyperFrames when overlays/title cards are needed:
   - HTML/CSS/GSAP is the source of truth.
   - Root `#stage` must span final duration.
   - Use deterministic timelines, no random runtime motion.
   - Add sparse title cards, captions, Ada-red UI pulses, and final credits.
6. Add audio:
   - Prefer captured Lord Dusk line if clean.
   - Otherwise generate/record a short TTS line and mix under music/room audio.
   - Keep captions readable if voice is important.
7. Render draft MP4.
8. Verify before delivery:
   ```bash
   ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 final.mp4
   ffmpeg -i final.mp4 -ss 00:00:05 -vframes 1 preview-frame.png
   ```
   Then visually check representative frames for cropping, readability, and vibe.
9. Export final MP4 variants:
   ```text
   media/final/dustlord-launch-x-github-preview.mp4
   media/final/dustlord-launch-x-landscape.mp4
   media/final/dustlord-launch-vertical.mp4
   ```

## HyperFrames composition plan

Create:

```text
media/video-project/
  DESIGN.md
  index.html
  assets/
    raw/ or symlinks to selected clips
    audio/
    stills/
  output/
```

`DESIGN.md` should define:
- Background: near-black / warm wood / dark Nordic home.
- Accent: Ada red `#E0001B` only for small UI pulses, underline, sensor dot, credits.
- Typography: bold condensed/neo-grotesk for titles; simple sans for small UI labels.
- Motion: slow cinematic entrances, subtle glitch only at scene transitions, no chaotic meme edits unless making Version B.

Overlay copy bank:

```text
MEET DUST LORD
Roborock body.
Lord Dusk voice.
Memory in the loop.
Created by Andreas H.
Raised in Ada Inc weirdness.
@NousResearch in the loop.
@teknium in the family tree.
Domestic robotics gets weird when it remembers.
```

## Publishing copy for video post

Short X caption:

```text
Meet Dust Lord.

A Roborock body, a Lord Dusk voice, and a tiny mythological problem with crumbs.

Created by Andreas H.
Raised in Ada Inc weirdness.
@NousResearch in the loop. @teknium in the family tree.

Domestic robotics gets weird when it remembers.
```

Even shorter:

```text
Meet Dust Lord.

A household robot with memory, timing, and a voice in the room.

Created by Andreas H.
Raised in Ada Inc weirdness.

Domestic robotics gets weird when it remembers.
```

## Safety / privacy checklist

Before posting:
- No private home details visible: family photos, addresses, mail, screens, calendars, kids’ identifying details.
- No Roborock map, device ID, token, local IP, QR code, or app screen secrets visible.
- No embarrassing room details unless intentionally part of the joke.
- Cropping verified for mobile feed.
- Text readable at phone size.
- Audio not painfully loud; voice intelligible.
- If tagging others, verify handles exactly.

## Next action

When source clips arrive, Hermes should:
1. ingest clips into `media/raw/`;
2. create a shot log with filenames, durations, best timestamps, and usable moments;
3. produce a first rough cut;
4. render one X-ready MP4;
5. visually verify frames before sending back to Andreas.
