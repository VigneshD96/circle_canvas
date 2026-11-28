---
videomd: 1
name: dog-door
description: 'An explainer that ''builds'' the ideal winter dog house one problem at a time: each fix is shown, named, and then broken by the next problem. Made with (inferred): 3D render 66%, AI-generated video 34%'
source:
  file: dog_door.mp4
  sha256: 50e0a78e2dd36c25f002e2d8267753a9ef6378eca0940c44e81cc417aaab95d5
  duration: 109.237
  size: 1080x1920
  fps: 29.999
  aspect: '9:16'
shots: 14
tracks:
  transcript: video/transcript.vtt
lang: en
made_mix:
  cg_3d: 0.6637
  ai_video: 0.3363
confidence: 0.576
readers:
- tools
- agent
open_questions: 15
generator:
  name: rea-video
  version: 0.1.0
---

# dog_door.mp4

**Verdict** (inferred): Mixed production: 3D render 66% + AI-generated video 34% (34% of the duration lacks evidence for live action vs AI, to confirm); overlays: styled text, text labels, static graphics, subtitles, title (composited in code / an editor); audio: voice + 48 sound effects; packaging: 1 subtitle lines, styled text ×2, text labels ×199, 32 sound effects land on text / sticker pops
**What it says**: An explainer that 'builds' the ideal winter dog house one problem at a time: each fix is shown, named, and then broken by the next problem.
**Narrative**: #01 grab attention → #02 Problem 1: too b… → #03 turn → #04 Raised floor wor… → #05 turn → #06 add information → #07-08 turn → #09 add information → #10 turn → #11 Charity design: … → #12 add information → #13 deliver the conclusion → #14 call to action
**Made with** (inferred, by duration): 3D render 66%, AI-generated video 34%
**Remake**: 11 3D render shots + 3 AI video shots → 10 generation units, 13 MiniMax H3 / H3 Max calls

## Next steps

- Remake: Capsule Cinema does the generation, assembly and checks. `rea-video remake <this dir>` hands over to it, does what can be done automatically and keeps the original elsewhere; `remake/status.md` says per shot what is left. Add incoming clips to `remake/mine.json` and run it again
- AI shots: prompts are in the generation units of `video/remake.md`; for automatic generation use Capsule Cinema: `scripts/remake_reference.py prepare <this dir>`, then `run <jobs.json> --dry-run` (paid: ask the user first)

## Open questions

- Shot #1 (0.0–5.4s): Tools say 3D render, the image review says AI-generated video; on the AI / live-action axis the fusion follows the tools (eval-calibrated): …
- Shot #2 (5.4–15.8s): Tools say 3D render, the image review says AI-generated video; on the AI / live-action axis the fusion follows the tools (eval-calibrated):…
- Shot #3 (15.8–27.0s): Tools say 3D render, the image review says AI-generated video; on the AI / live-action axis the fusion follows the tools (eval-calibrated)…
- Shot #4 (27.0–36.9s): Tools say 3D render, the image review says AI-generated video; on the AI / live-action axis the fusion follows the tools (eval-calibrated)…
- Shot #5 (36.9–56.9s): Live action / stop motion or AI, to confirm: no AIGC label; 24fps-source marks appear in AI video, stop motion and cinema-camera footage a…
- Shot #6 (56.9–57.5s): Tools say 3D render, the image review says AI-generated video; on the AI / live-action axis the fusion follows the tools (eval-calibrated)…
- Shot #7 (57.5–58.8s): Tools say 3D render, the image review says AI-generated video; on the AI / live-action axis the fusion follows the tools (eval-calibrated)…
- Shot #8 (58.8–75.1s): Live action / stop motion or AI, to confirm: no AIGC label; 24fps-source marks appear in AI video, stop motion and cinema-camera footage a…
- 7 more, see the `flag` lines in `video/timeline.md`

## Map

Read this page first; for detail, open only the file you need. Each line is `path | ~tokens | what is in it · when to read it`; paths are relative to this directory.

```videomd-map
video/timeline.md | 1406 | Timeline: one line per shot · what a stretch says, which shots need review, how a shot was made
video/content.md | 1402 | Content and structure · what it says, the narrative line, structure, the script
video/cast.md | 365 | Cast, scenes and props · reference images for characters, first-frame prompts
video/sound.md | 956 | Sound · voice, music, sound effects, beats and sources
video/rhythm.md | 697 | Rhythm and key frames · when cuts and transitions happen, shot lengths, the change curve, key frames of each shot
video/packaging.md | 4024 | Packaging · subtitles, styled text, stickers, picture-in-picture: timing and style
video/remake.md | 5279 | Remake plan · generation units, shoots, code builds, real material to collect, acting and emotion
video/transcript.vtt | 692 | Transcript: who says what, when · quoting speech, subtitles and voice-over
video/shots/*.md | 895 | Per-shot detail, tokens per file on average · checking one shot: what is seen, the inference and its basis, prompts, frames
breakdown.json | 133637 | Full raw data · for programs; a model rarely needs it
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
