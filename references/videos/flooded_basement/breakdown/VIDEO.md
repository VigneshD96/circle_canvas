---
videomd: 1
name: flooded-basement
description: 'A counter-intuitive flood story: the man who floods his own basement on purpose ends up with intact walls, while the neighbour who pumps his dry has his basement wall collapse. Made with (inferred): AI-generated video 100%'
source:
  file: flooded_basement.mp4
  sha256: 03906cbb61849f440662448127113b7f48dd85aeccb218de3b30a8ad819c1bda
  duration: 71.041
  size: 1080x1920
  fps: 23.986
  aspect: '9:16'
shots: 17
tracks:
  transcript: video/transcript.vtt
lang: en
made_mix:
  ai_video: 1.0
confidence: 0.612
readers:
- tools
- agent
open_questions: 17
generator:
  name: rea-video
  version: 0.1.0
---

# flooded_basement.mp4

**Verdict** (inferred): Mixed production: live action or AI, to confirm 93% + AI-generated video 7%; overlays: text labels, static graphics, subtitles, title (composited in code / an editor); audio: voice + 15 sound effects; packaging: 64 subtitle lines, text labels ×2, 10 sound effects land on text / sticker pops
**What it says**: A counter-intuitive flood story: the man who floods his own basement on purpose ends up with intact walls, while the neighbour who pumps his dry has his basement wall collapse.
**Narrative**: #01 grab attention → #02 Neighbour mocks … → #03 He moves valuabl… → #04 'The indoor pool… → #05 Transition → #06-08 turn → #09 Soaked soil push… → #10 Analogy: full ca… → #11 Water inside bal… → #12 Authority beat → #13 Let the water in… → #14 Transition → #15-17 deliver the conclusion
**Made with** (inferred, by duration): AI-generated video 100%
**Remake**: 17 AI video shots → 10 generation units, 10 MiniMax H3 / H3 Max calls

## Next steps

- Remake: Capsule Cinema does the generation, assembly and checks. `rea-video remake <this dir>` hands over to it, does what can be done automatically and keeps the original elsewhere; `remake/status.md` says per shot what is left. Add incoming clips to `remake/mine.json` and run it again
- AI shots: prompts are in the generation units of `video/remake.md`; for automatic generation use Capsule Cinema: `scripts/remake_reference.py prepare <this dir>`, then `run <jobs.json> --dry-run` (paid: ask the user first)

## Open questions

- Shot #1 (0.0–7.5s): Live action / stop motion or AI, to confirm: no AIGC label; 24fps-source marks appear in AI video, stop motion and cinema-camera footage ali…
- Shot #2 (7.5–13.3s): Live action / stop motion or AI, to confirm: no AIGC label; 24fps-source marks appear in AI video, stop motion and cinema-camera footage al…
- Shot #3 (13.3–16.3s): Live action / stop motion or AI, to confirm: no AIGC label; 24fps-source marks appear in AI video, stop motion and cinema-camera footage a…
- Shot #4 (16.3–21.4s): Live action / stop motion or AI, to confirm: no AIGC label; 24fps-source marks appear in AI video, stop motion and cinema-camera footage a…
- Shot #5 (21.4–22.4s): Live action / stop motion or AI, to confirm: no AIGC label; 24fps-source marks appear in AI video, stop motion and cinema-camera footage a…
- Shot #6 (22.4–27.1s): Live action / stop motion or AI, to confirm: no AIGC label; 24fps-source marks appear in AI video, stop motion and cinema-camera footage a…
- Shot #7 (27.1–34.9s): Live action / stop motion or AI, to confirm: no AIGC label; 24fps-source marks appear in AI video, stop motion and cinema-camera footage a…
- Shot #8 (34.9–42.6s): Live action / stop motion or AI, to confirm: no AIGC label; 24fps-source marks appear in AI video, stop motion and cinema-camera footage a…
- 9 more, see the `flag` lines in `video/timeline.md`

## Map

Read this page first; for detail, open only the file you need. Each line is `path | ~tokens | what is in it · when to read it`; paths are relative to this directory.

```videomd-map
video/timeline.md | 1565 | Timeline: one line per shot · what a stretch says, which shots need review, how a shot was made
video/content.md | 1176 | Content and structure · what it says, the narrative line, structure, the script
video/cast.md | 360 | Cast, scenes and props · reference images for characters, first-frame prompts
video/sound.md | 418 | Sound · voice, music, sound effects, beats and sources
video/rhythm.md | 948 | Rhythm and key frames · when cuts and transitions happen, shot lengths, the change curve, key frames of each shot
video/packaging.md | 2655 | Packaging · subtitles, styled text, stickers, picture-in-picture: timing and style
video/remake.md | 5237 | Remake plan · generation units, shoots, code builds, real material to collect, acting and emotion
video/transcript.vtt | 451 | Transcript: who says what, when · quoting speech, subtitles and voice-over
video/shots/*.md | 867 | Per-shot detail, tokens per file on average · checking one shot: what is seen, the inference and its basis, prompts, frames
breakdown.json | 110960 | Full raw data · for programs; a model rarely needs it
shots/ | - | contact sheet, first and last frame of each shot · checking by eye
storyboard.jpg | - | storyboard of the whole video · the whole video at a glance
stems/ | - | voice, music and effects stems · listening, remaking the sound
sfx/ | - | a clip of each sound effect · finding matching effects
packaging/ | - | subtitle files, packaging timeline, sticker frames · remaking subtitles and packaging
audio.png | - | waveform and beat chart · seeing the rhythm
```

## How to read

- One shot per line: `#<n> start-end (s) | key value | …`. A key ending in `~` is the tools' inference; keys without it are visible on screen or measured directly.
- `story` job in the story and the point · `seen` what is on screen · `act` acting (emotion, strength, face) · `camera` camera move · `overlay` overlays · `made~` how it was made (inferred) · `material~` where the material came from (inferred) · `remake` remake route · `flag` needs a second look
- Full detail for a shot is in `video/shots/<n>.md` (e.g. `video/shots/07.md`).
- What is “seen” can be checked against the frames; what is “inferred” is the tools' and image readers' judgement, with the basis in each shot file. When they disagree, trust the frames.
