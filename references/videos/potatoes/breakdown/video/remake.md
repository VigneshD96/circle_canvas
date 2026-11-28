---
videomd: 1
part: remake
tokens: 4685
---

## Remake plan

### Step by step

This is a 3D / animation. Do the steps in this order; the detail for each is in the matching subsection below.

1. **Write the content**: write yours in the same 10 steps as the original (narrative line under “Content and structure”)
2. **Generate**: 7 calls (52 s), several shots each. Each shot gets one source frame for composition (subtitles erased, in `remake/refs/`), the swapped-in people, animals and products get reference images, and the prompt lists the shots in order
3. **Adapt the prompts to your model**: each unit's draft is already laid out in MiniMax H3 / H3 Max's shot, tag and audio format; refine it against the model's prompt guide before generating (or run `rea-video plan <folder> --rewrite-prompts`)
4. **Voice**: the original is TTS voice-over; record it yourself or use TTS; 12 lines with their pace in the script table under “Sound”
5. **Edit**: follow the order and lengths in the shot list; the original has 21 shots at 2.5s each
6. **Subtitles and styled text**: import `packaging/subtitles.srt` and replace the words; timing and style under “Packaging layer”
7. **Sound effects**: 9; place similar ones from a library at the times under “Sound”
8. **Put it together and compare**: hand the shots you made to the agent; it places them on the original timeline, keeps the original where yours are missing, and renders a side-by-side comparison with the original

**21 3D render shots → 7 generation units, 7 MiniMax H3 / H3 Max calls**

### Generation units

- **How it is generated**: multi-shot from key frames

| Part | Shots | Time | Length | Prepare |
|---|---|---|---|---|
| G1 | #1–#4 | 0.0–8.7s | 8.7s | reference images |
| G2 | #5–#8 | 8.7–17.7s | 9.0s | reference images |
| G3 | #9–#11 | 17.7–26.0s | generate 9s, trim to 8.3s | reference images |
| G4 | #12–#14 | 26.0–33.3s | generate 8s, trim to 7.3s | reference images |
| G5 | #15–#17 | 33.3–41.3s | 8.0s | reference images |
| G6 | #18, #19 | 41.3–46.5s | generate 6s, trim to 5.1s | reference images |
| G7 | #20, #21 | 46.5–51.6s | generate 6s, trim to 5.1s | reference images |

**Why it is split this way**

- Grouping: consecutive shots share a call where they fit, ≤10s per call, ≤4 shots; a long stretch is cut at a scene change first
- Inputs: the model also takes reference video, but key frames are used here: one key frame per shot fixes composition and look, swapped-in things get their own images
- Audio: the model can generate action sound effects and ambience along with the picture; voice-over is better done as separate TTS and mixed in, so copy and timing stay editable
- Packaging: the subtitle, text label, sticker, styled text on the generated shots is post-production packaging: keep it out of the prompts (erased from source references) and lay it back on from the packaging timeline after generation

**Frames to make first (21)**

When swapping people or products, or switching to shot-by-shot image-to-video, prepare each shot's first frame as below:

| Shot | Role | How | Reference images | Save as |
|---|---|---|---|---|
| #1 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_001_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot001.png` |
| #2 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_002_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot002.png` |
| #3 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_003_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot003.png` |
| #4 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_004_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot004.png` |
| #5 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_005_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot005.png` |
| #6 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_006_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot006.png` |
| #7 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_007_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot007.png` |
| #8 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_008_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot008.png` |
| #9 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_009_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot009.png` |
| #10 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_010_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot010.png` |
| #11 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_011_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot011.png` |
| #12 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_012_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot012.png` |
| #13 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_013_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot013.png` |
| #14 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_014_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot014.png` |
| #15 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_015_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot015.png` |
| #16 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_016_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot016.png` |
| #17 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_017_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot017.png` |
| #18 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_018_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot018.png` |
| #19 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_019_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot019.png` |
| #20 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_020_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot020.png` |
| #21 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_021_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot021.png` |

- **#1 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the lower middle of the frame, camera push-in. Hook close-up: a potato racing toward a grid of knives in the cutter housing
- **#2 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject centred in frame, camera pull-out. View through the blade grid as the potato approaches; '~40 mph into the knives' stat card
- **#3 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject centred in frame, camera pull-out. Red X-ray cutaway of a potato jammed in the cutter
- **#4 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the upper left of the frame. Potatoes back up in the pipe; counter card ticks up to '88 potatoes backed up in 10 seconds'
- **#5 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject in the lower middle of the frame, camera push-in. Wide pull-back over the hydrocutter line in the factory hall
- **#6 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. Wide over the line
- **#7 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the lower middle of the frame, camera pan / track. Potatoes poured into a water tank
- **#8 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject in the lower middle of the frame, camera push-in. Teal pump motor and pipework pushing water and potatoes
- **#9 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the lower middle of the frame, camera pan / track. Pipe narrows; yellow highlight glow traces the narrowing section
- **#10 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the lower middle of the frame. Potato speeds up inside the pipe (cutaway)
- **#11 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the lower middle of the frame. Potato being centred by the narrowing pipe
- **#12 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the lower middle of the frame. Potato travelling nose first, dead centre
- **#13 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the lower middle of the frame, camera push-in. Cutter housing; yellow highlight on the grid of thin steel blades
- **#14 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject in the lower middle of the frame, camera pull-out. Macro cutaway: first row of blades slices the potato into slabs
- **#15 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. Crossing row cuts each slab into sticks (exploded view)
- **#16 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the lower middle of the frame, camera push-in. Potato bursts through the grid as a spray of fries
- **#17 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the right of the frame, camera push-in. Pipe widens; fries fan out
- **#18 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. Fries land on a shaking screen
- **#19 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the lower middle of the frame, camera pull-out. Water runs back into the tank
- **#20 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the lower middle of the frame, camera push-in. Static blade grid as potatoes shoot through
- **#21 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the lower middle of the frame. Final burst of fries from the cutter

**G1 · shots #1–#4 · 8.7s**

- reference images: source frames of shots #1, #2, #3, #4 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, cool tones, background clearly blurred.
[Shot 1] Hook close-up: a potato racing toward a grid of knives in the cutter housing. (composition: <Picture 1>)
[Shot 2] At 00:02.200, the camera cuts to: View through the blade grid as the potato approaches; '~40 mph into the knives' stat card. (composition: <Picture 2>)
[Shot 3] At 00:04.500, the camera cuts to: Red X-ray cutaway of a potato jammed in the cutter. (composition: <Picture 3>)
[Shot 4] At 00:06.533, the camera cuts to: Potatoes back up in the pipe; counter card ticks up to '88 potatoes backed up in 10 seconds'. (composition: <Picture 4>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G2 · shots #5–#8 · 9.0s**

- reference images: source frames of shots #5, #6, #7, #8 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, cool tones, background clearly blurred.
[Shot 1] Wide pull-back over the hydrocutter line in the factory hall. (composition: <Picture 1>)
[Shot 2] At 00:02.267, the camera cuts to: Wide over the line. (composition: <Picture 2>)
[Shot 3] At 00:04.200, the camera cuts to: Potatoes poured into a water tank. (composition: <Picture 3>)
[Shot 4] At 00:06.133, the camera cuts to: Teal pump motor and pipework pushing water and potatoes. (composition: <Picture 4>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G3 · shots #9–#11 · 8.3s**

- reference images: source frames of shots #9, #10, #11 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, cool tones, background clearly blurred.
[Shot 1] Pipe narrows; yellow highlight glow traces the narrowing section. (composition: <Picture 1>)
[Shot 2] At 00:02.600, the camera cuts to: Potato speeds up inside the pipe (cutaway). (composition: <Picture 2>)
[Shot 3] At 00:05.933, the camera cuts to: Potato being centred by the narrowing pipe. (composition: <Picture 3>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G4 · shots #12–#14 · 7.3s**

- reference images: source frames of shots #12, #13, #14 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, cool tones, background clearly blurred.
[Shot 1] Potato travelling nose first, dead centre. (composition: <Picture 1>)
[Shot 2] At 00:02.200, the camera cuts to: Cutter housing; yellow highlight on the grid of thin steel blades. (composition: <Picture 2>)
[Shot 3] At 00:05.267, the camera cuts to: Macro cutaway: first row of blades slices the potato into slabs. (composition: <Picture 3>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G5 · shots #15–#17 · 8.0s**

- reference images: source frames of shots #15, #16, #17 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, cool tones, background clearly blurred.
[Shot 1] Crossing row cuts each slab into sticks (exploded view). (composition: <Picture 1>)
[Shot 2] At 00:02.867, the camera cuts to: Potato bursts through the grid as a spray of fries. (composition: <Picture 2>)
[Shot 3] At 00:05.867, the camera cuts to: Pipe widens; fries fan out. (composition: <Picture 3>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G6 · shots #18, #19 · 5.1s**

- reference images: source frames of shots #18, #19 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, cool tones, background clearly blurred.
[Shot 1] Fries land on a shaking screen. (composition: <Picture 1>)
[Shot 2] At 00:03.133, the camera cuts to: Water runs back into the tank. (composition: <Picture 2>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G7 · shots #20, #21 · 5.1s**

- reference images: source frames of shots #20, #21 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, cool tones, background clearly blurred.
[Shot 1] Static blade grid as potatoes shoot through. (composition: <Picture 1>)
[Shot 2] At 00:02.200, the camera cuts to: Final burst of fries from the cutter. (composition: <Picture 2>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**Prompt guides for MiniMax H3 / H3 Max**

- https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md
- https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md
- https://platform.minimax.io/docs/api-reference/video-generation-v2-create
- https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide.md
