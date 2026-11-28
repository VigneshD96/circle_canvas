---
videomd: 1
name: potatoes
description: 'How a hydrocutter turns potatoes into fries: water accelerates each potato through a pipe into a fixed grid of blades. Made with (inferred): 3D render 100%'
source:
  file: potatoes.mp4
  sha256: 98fa8431d2665325442a3aa052875f66b72e886034d76d362f4f28a5a9858b89
  duration: 51.567
  size: 1080x1920
  fps: 30.0
  aspect: '9:16'
shots: 21
tracks:
  transcript: video/transcript.vtt
lang: en
made_mix:
  cg_3d: 1.0
confidence: 0.828
readers:
- tools
- agent
open_questions: 1
generator:
  name: rea-video
  version: 0.1.0
---

# potatoes.mp4

**Verdict** (inferred): Mixed production: 3D render 100%; overlays: animated sticker / GIF, styled text, text labels, subtitles, title (composited in code / an editor); audio: voice + 9 sound effects; packaging: 40 subtitle lines, styled text ×1, text labels ×14, stickers / GIFs ×2, 4 sound effects land on text / sticker pops
**What it says**: How a hydrocutter turns potatoes into fries: water accelerates each potato through a pipe into a fixed grid of blades.
**Narrative**: #01-04 grab attention → #05 It's a hydrocutt… → #06 How factories ma… → #07 Starts in a tank… → #08-13 add information → #14 First row slices → #15 Crossing row cut… → #16 Through faster t… → #17-19 add information → #20-21 deliver the conclusion
**Made with** (inferred, by duration): 3D render 100%
**Remake**: 21 3D render shots → 7 generation units, 7 MiniMax H3 / H3 Max calls

## Next steps

- Remake: Capsule Cinema does the generation, assembly and checks. `rea-video remake <this dir>` hands over to it, does what can be done automatically and keeps the original elsewhere; `remake/status.md` says per shot what is left. Add incoming clips to `remake/mine.json` and run it again
- AI shots: prompts are in the generation units of `video/remake.md`; for automatic generation use Capsule Cinema: `scripts/remake_reference.py prepare <this dir>`, then `run <jobs.json> --dry-run` (paid: ask the user first)

## Open questions

- No AI listened to the soundtrack (the review covered the picture only): real voice versus TTS is inferred from the waveform; the effects were found on the separ…

## Map

Read this page first; for detail, open only the file you need. Each line is `path | ~tokens | what is in it · when to read it`; paths are relative to this directory.

```videomd-map
video/timeline.md | 1843 | Timeline: one line per shot · what a stretch says, which shots need review, how a shot was made
video/content.md | 819 | Content and structure · what it says, the narrative line, structure, the script
video/cast.md | 176 | Cast, scenes and props · reference images for characters, first-frame prompts
video/sound.md | 350 | Sound · voice, music, sound effects, beats and sources
video/rhythm.md | 929 | Rhythm and key frames · when cuts and transitions happen, shot lengths, the change curve, key frames of each shot
video/packaging.md | 2696 | Packaging · subtitles, styled text, stickers, picture-in-picture: timing and style
video/remake.md | 4697 | Remake plan · generation units, shoots, code builds, real material to collect, acting and emotion
video/transcript.vtt | 296 | Transcript: who says what, when · quoting speech, subtitles and voice-over
video/shots/*.md | 707 | Per-shot detail, tokens per file on average · checking one shot: what is seen, the inference and its basis, prompts, frames
breakdown.json | 109632 | Full raw data · for programs; a model rarely needs it
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
