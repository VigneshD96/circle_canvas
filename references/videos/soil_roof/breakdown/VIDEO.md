---
videomd: 1
name: soil-roof
description: 'How a green roof is really built, told as a chain of failed attempts: soil too heavy → light clay pebbles → grass dries → sedum → roots leak → root barrier → flooding → drainage cups. Made with (inferred): 3D render 96%, live action 4%'
source:
  file: soil_roof.mp4
  sha256: db8d292647b4a182351d0e97e4dd8c5b97105ba4fbd62ed3b4cedfc069604eb1
  duration: 55.5
  size: 1080x1920
  fps: 30.0
  aspect: '9:16'
shots: 26
tracks:
  transcript: video/transcript.vtt
lang: en
made_mix:
  cg_3d: 0.9646
  live_action: 0.0354
confidence: 0.725
readers:
- tools
- agent
open_questions: 2
generator:
  name: rea-video
  version: 0.1.0
---

# soil_roof.mp4

**Verdict** (inferred): Mixed production: 3D render 96% + live action 4%; overlays: styled text, text labels, static graphics, subtitles (composited in code / an editor); real material used: live footage (2.0s); audio: voice + 18 sound effects; packaging: styled text ×1, text labels ×95, 12 sound effects land on text / sticker pops
**What it says**: How a green roof is really built, told as a chain of failed attempts: soil too heavy → light clay pebbles → grass dries → sedum → roots leak → root barrier → flooding → drainage cups.
**Narrative**: #01 grab attention → #02-03 add information → #04 grab attention → #05-06 add information → #07 So the soil come… → #08-09 add information → #10 turn → #11 add information → #12 turn → #13-14 add information → #15 turn → #16-17 add information → #18 turn → #19 add information → #20 turn → #21-24 add information → #25-26 deliver the conclusion
**Made with** (inferred, by duration): 3D render 96%, live action 4%
**Remake**: 25 3D render shots → 7 generation units, 7 MiniMax H3 / H3 Max calls; live action 1 shot → 1 scene, 1 camera setup
**Real material to collect**: 1 shots (4% of the duration), list in `video/remake.md`

## Next steps

- Remake: Capsule Cinema does the generation, assembly and checks. `rea-video remake <this dir>` hands over to it, does what can be done automatically and keeps the original elsewhere; `remake/status.md` says per shot what is left. Add incoming clips to `remake/mine.json` and run it again
- AI shots: prompts are in the generation units of `video/remake.md`; for automatic generation use Capsule Cinema: `scripts/remake_reference.py prepare <this dir>`, then `run <jobs.json> --dry-run` (paid: ask the user first)

## Open questions

- Shot #20 (39.8–41.7s): Tools say live action, the image review says 3D render; on the AI / live-action axis the fusion follows the tools (eval-calibrated): chec…
- No AI listened to the soundtrack (the review covered the picture only): real voice versus TTS is inferred from the waveform; the effects were found on the separ…

## Map

Read this page first; for detail, open only the file you need. Each line is `path | ~tokens | what is in it · when to read it`; paths are relative to this directory.

```videomd-map
video/timeline.md | 2335 | Timeline: one line per shot · what a stretch says, which shots need review, how a shot was made
video/content.md | 1165 | Content and structure · what it says, the narrative line, structure, the script
video/cast.md | 168 | Cast, scenes and props · reference images for characters, first-frame prompts
video/sound.md | 483 | Sound · voice, music, sound effects, beats and sources
video/rhythm.md | 1034 | Rhythm and key frames · when cuts and transitions happen, shot lengths, the change curve, key frames of each shot
video/look.md | 760 | Camera, lighting and editing · for filmed shots: framing, camera, lighting, kit
video/packaging.md | 3159 | Packaging · subtitles, styled text, stickers, picture-in-picture: timing and style
video/remake.md | 5759 | Remake plan · generation units, shoots, code builds, real material to collect, acting and emotion
video/transcript.vtt | 328 | Transcript: who says what, when · quoting speech, subtitles and voice-over
video/shots/*.md | 764 | Per-shot detail, tokens per file on average · checking one shot: what is seen, the inference and its basis, prompts, frames
breakdown.json | 125575 | Full raw data · for programs; a model rarely needs it
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
