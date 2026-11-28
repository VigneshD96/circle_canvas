---
videomd: 1
part: remake
tokens: 5747
---

## Remake plan

### Step by step

This is a 3D / animation. Do the steps in this order; the detail for each is in the matching subsection below.

1. **Write the content**: write yours in the same 17 steps as the original (narrative line under “Content and structure”)
2. **Collect material**: the real material in the picture (live footage) needs the original files, listed under “What to prepare”
3. **Generate**: 7 calls (54 s), several shots each. Each shot gets one source frame for composition (subtitles erased, in `remake/refs/`), the swapped-in people, animals and products get reference images, and the prompt lists the shots in order
4. **Adapt the prompts to your model**: each unit's draft is already laid out in MiniMax H3 / H3 Max's shot, tag and audio format; refine it against the model's prompt guide before generating (or run `rea-video plan <folder> --rewrite-prompts`)
5. **Live shots**: 1 shots to film yourself; camera and light under “Shoot” below
6. **Voice**: the original is TTS voice-over; record it yourself or use TTS; 13 lines with their pace in the script table under “Sound”
7. **Edit**: follow the order and lengths in the shot list; the original has 26 shots at 2.1s each; 8 transitions under “Edit”
8. **Subtitles and styled text**: timing and style under “Packaging layer”
9. **Sound effects**: 18; place similar ones from a library at the times under “Sound”
10. **Put it together and compare**: hand the shots you made to the agent; it places them on the original timeline, keeps the original where yours are missing, and renders a side-by-side comparison with the original

**25 3D render shots → 7 generation units, 7 MiniMax H3 / H3 Max calls; live action 1 shot → 1 scene, 1 camera setup**

### Generation units

- **How it is generated**: multi-shot from key frames

| Part | Shots | Time | Length | Prepare |
|---|---|---|---|---|
| G1 | #1–#4 | 0.0–6.1s | generate 7s, trim to 6.1s | reference images |
| G2 | #5–#8 | 6.1–14.6s | 8.5s | reference images |
| G3 | #9–#12 | 14.6–21.6s | 7.0s | reference images |
| G4 | #13–#15 | 21.6–31.0s | generate 10s, trim to 9.4s | reference images |
| G5 | #16–#19 | 31.0–39.8s | 8.8s | reference images |
| G6 | #21–#24 | 41.7–48.9s | generate 8s, trim to 7.2s | reference images |
| G7 | #25, #26 | 48.9–55.5s | 6.6s | reference images |

**Why it is split this way**

- Grouping: consecutive shots share a call where they fit, ≤10s per call, ≤4 shots; a long stretch is cut at a scene change first
- Inputs: the model also takes reference video, but key frames are used here: one key frame per shot fixes composition and look, swapped-in things get their own images
- Audio: the model can generate action sound effects and ambience along with the picture; voice-over is better done as separate TTS and mixed in, so copy and timing stay editable
- Packaging: the text label, styled text on the generated shots is post-production packaging: keep it out of the prompts (erased from source references) and lay it back on from the packaging timeline after generation

**Frames to make first (25)**

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
| #21 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_021_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot021.png` |
| #22 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_022_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot022.png` |
| #23 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_023_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot023.png` |
| #24 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_024_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot024.png` |
| #25 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_025_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot025.png` |
| #26 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_026_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot026.png` |

- **#1 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. close-up, subject in the lower middle of the frame, camera push-in. You shovel soil onto your flat roof to grow a garden
- **#2 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject in the upper middle of the frame, camera push-in. You shovel soil onto your flat roof to grow a garden
- **#3 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. You shovel soil onto your flat roof to grow a garden
- **#4 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject in the upper middle of the frame, camera push-in. And one storm later, there are tons of wet muds sitting above your bed
- **#5 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the upper middle of the frame, camera push-in. And one storm later, there are tons of wet muds sitting above your bed
- **#6 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject centred in frame, camera pull-out. And one storm later, there are tons of wet muds sitting above your bed
- **#7 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. So the soil comes off and you spread a thin layer of baked clay pebbles that stays light even when it's soaked
- **#8 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject in the upper middle of the frame, camera push-in. So the soil comes off and you spread a thin layer of baked clay pebbles that stays light even when it's soaked
- **#9 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. So the soil comes off and you spread a thin layer of baked clay pebbles that stays light even when it's soaked
- **#10 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. You plant grass, but that thin layer dries out fast and the lawn turns brown
- **#11 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. You plant grass, but that thin layer dries out fast and the lawn turns brown
- **#12 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. So you switch to see them
- **#13 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject in the upper middle of the frame, camera push-in. Tiny succulents that keep water in their fat leaves
- **#14 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject in the lower middle of the frame, camera push-in. Tiny succulents that keep water in their fat leaves
- **#15 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject in the upper middle of the frame, camera push-in. Next spring, the ceiling starts dripping because the roots crept into a seam in the roof looking for water
- **#16 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. Everything comes up again and down goes a rubber sheet that roots can't get through
- **#17 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject in the upper middle of the frame, camera push-in. Everything comes up again and down goes a rubber sheet that roots can't get through
- **#18 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. Then a summer storm floods the roof
- **#19 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the upper middle of the frame, camera push-in. Then a summer storm floods the roof
- **#21 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the upper middle of the frame, camera push-in. So under the pebbles goes a plastic sheet shaped like an egg cartton
- **#22 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject in the upper middle of the frame, camera push-in. So under the pebbles goes a plastic sheet shaped like an egg cartton
- **#23 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. Whose cups hold a little rain and let the rest drain away
- **#24 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject in the upper middle of the frame, camera push-in. Whose cups hold a little rain and let the rest drain away
- **#25 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. Now, the bedroom below stays cooler all summer and your roof is a garden that waters itself
- **#26 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. close-up, subject in the lower middle of the frame, camera push-in. Now, the bedroom below stays cooler all summer and your roof is a garden that waters itself

**G1 · shots #1–#4 · 6.1s**

- reference images: source frames of shots #1, #2, #3, #4 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; high key, soft light, warm tones, background clearly blurred.
[Shot 1] You shovel soil onto your flat roof to grow a garden. (composition: <Picture 1>)
[Shot 2] At 00:01.633, the camera cuts to: You shovel soil onto your flat roof to grow a garden. (composition: <Picture 2>)
[Shot 3] At 00:03.000, the camera cuts to: You shovel soil onto your flat roof to grow a garden. (composition: <Picture 3>)
[Shot 4] At 00:04.500, the camera cuts to: And one storm later, there are tons of wet muds sitting above your bed. (composition: <Picture 4>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G2 · shots #5–#8 · 8.5s**

- reference images: source frames of shots #5, #6, #7, #8 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; high key, soft light, warm tones, background clearly blurred.
[Shot 1] And one storm later, there are tons of wet muds sitting above your bed. (composition: <Picture 1>)
[Shot 2] At 00:01.600, the camera cuts to: And one storm later, there are tons of wet muds sitting above your bed. (composition: <Picture 2>)
[Shot 3] At 00:02.633, the camera cuts to: So the soil comes off and you spread a thin layer of baked clay pebbles that stays light even when it's soaked. (composition: <Picture 3>)
[Shot 4] At 00:05.833, the camera cuts to: So the soil comes off and you spread a thin layer of baked clay pebbles that stays light even when it's soaked. (composition: <Picture 4>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G3 · shots #9–#12 · 7.0s**

- reference images: source frames of shots #9, #10, #11, #12 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; high key, soft light, warm tones, background clearly blurred.
[Shot 1] So the soil comes off and you spread a thin layer of baked clay pebbles that stays light even when it's soaked. (composition: <Picture 1>)
[Shot 2] At 00:01.167, the camera cuts to: You plant grass, but that thin layer dries out fast and the lawn turns brown. (composition: <Picture 2>)
[Shot 3] At 00:03.500, the camera cuts to: You plant grass, but that thin layer dries out fast and the lawn turns brown. (composition: <Picture 3>)
[Shot 4] At 00:05.333, the camera cuts to: So you switch to see them. (composition: <Picture 4>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G4 · shots #13–#15 · 9.4s**

- reference images: source frames of shots #13, #14, #15 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; high key, soft light, warm tones, background clearly blurred.
[Shot 1] Tiny succulents that keep water in their fat leaves. (composition: <Picture 1>)
[Shot 2] At 00:03.333, the camera cuts to: Tiny succulents that keep water in their fat leaves. (composition: <Picture 2>)
[Shot 3] At 00:05.766, the camera cuts to: Next spring, the ceiling starts dripping because the roots crept into a seam in the roof looking for water. (composition: <Picture 3>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G5 · shots #16–#19 · 8.8s**

- reference images: source frames of shots #16, #17, #18, #19 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; high key, soft light, warm tones, background clearly blurred.
[Shot 1] Everything comes up again and down goes a rubber sheet that roots can't get through. (composition: <Picture 1>)
[Shot 2] At 00:03.067, the camera cuts to: Everything comes up again and down goes a rubber sheet that roots can't get through. (composition: <Picture 2>)
[Shot 3] At 00:05.000, the camera cuts to: Then a summer storm floods the roof. (composition: <Picture 3>)
[Shot 4] At 00:07.500, the camera cuts to: Then a summer storm floods the roof. (composition: <Picture 4>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G6 · shots #21–#24 · 7.2s**

- reference images: source frames of shots #21, #22, #23, #24 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; high key, soft light, warm tones, background clearly blurred.
[Shot 1] So under the pebbles goes a plastic sheet shaped like an egg cartton. (composition: <Picture 1>)
[Shot 2] At 00:02.333, the camera cuts to: So under the pebbles goes a plastic sheet shaped like an egg cartton. (composition: <Picture 2>)
[Shot 3] At 00:03.833, the camera cuts to: Whose cups hold a little rain and let the rest drain away. (composition: <Picture 3>)
[Shot 4] At 00:05.500, the camera cuts to: Whose cups hold a little rain and let the rest drain away. (composition: <Picture 4>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G7 · shots #25, #26 · 6.6s**

- reference images: source frames of shots #25, #26 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; high key, soft light, warm tones, background clearly blurred.
[Shot 1] Now, the bedroom below stays cooler all summer and your roof is a garden that waters itself. (composition: <Picture 1>)
[Shot 2] At 00:03.033, the camera cuts to: Now, the bedroom below stays cooler all summer and your roof is a garden that waters itself. (composition: <Picture 2>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**Prompt guides for MiniMax H3 / H3 Max**

- https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md
- https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md
- https://platform.minimax.io/docs/api-reference/video-generation-v2-create
- https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide.md

### Shooting scenes

Shoot every shot of one scene before moving to the next; within a scene, shoot the wider sizes first and the close-ups last so the lighting is set only once. Leave about 1s of handle at both ends of every take.

**S1**: shots #20 (1.97s on screen); flat-roofed house, cutaway with bedroom below, pastel daylight, rain
- Lighting: soft frontal light (flat light), key light frontal, warm (about 3000–4000K)
- Setup medium close-up · moving camera (gimbal / handheld pan) · push-in: shots #20, 1.97s on screen, shoot about 4.0s

### Real material in the picture (the original files are needed)

1 shots, 1.97s (4%) contain real material (screen recordings, screenshots, photos, embedded video); a model cannot stand in for them:

- **live footage** (whole frame): shots #20, 2.0s in all
