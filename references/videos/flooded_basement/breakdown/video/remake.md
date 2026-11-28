---
videomd: 1
part: remake
tokens: 5225
---

## Remake plan

### Step by step

This is a AI story short. Do the steps in this order; the detail for each is in the matching subsection below.

1. **Write the content**: write yours in the same 13 steps as the original (narrative line under “Content and structure”)
2. **Collect material**: one reference image per recurring character to lock appearance across shots: Hero, Neighbour
3. **Generate**: 10 calls (71 s), several shots each. Each shot gets one source frame for composition (subtitles erased, in `remake/refs/`), the swapped-in people, animals and products get reference images, and the prompt lists the shots in order
4. **Adapt the prompts to your model**: each unit's draft is already laid out in MiniMax H3 / H3 Max's shot, tag and audio format; refine it against the model's prompt guide before generating (or run `rea-video plan <folder> --rewrite-prompts`)
5. **Voice**: the original is TTS voice-over; record it yourself or use TTS; 20 lines with their pace in the script table under “Sound”
6. **Edit**: follow the order and lengths in the shot list; the original has 17 shots at 4.2s each; 11 transitions under “Edit”
7. **Subtitles and styled text**: import `packaging/subtitles.srt` and replace the words; timing and style under “Packaging layer”
8. **Sound effects**: 15; place similar ones from a library at the times under “Sound”
9. **Put it together and compare**: hand the shots you made to the agent; it places them on the original timeline, keeps the original where yours are missing, and renders a side-by-side comparison with the original

**17 AI video shots → 10 generation units, 10 MiniMax H3 / H3 Max calls**

### Generation units

- **How it is generated**: multi-shot from key frames

| Part | Shots | Time | Length | Prepare |
|---|---|---|---|---|
| G1 | #1 | 0.0–7.5s | generate 8s, trim to 7.5s | reference images |
| G2 | #2 | 7.5–13.3s | 5.8s | reference images |
| G3 | #3, #4 | 13.3–21.4s | generate 9s, trim to 8.1s | reference images |
| G4 | #5, #6 | 21.4–27.1s | 5.6s | reference images |
| G5 | #7 | 27.1–34.9s | 7.8s | reference images |
| G6 | #8, #9 | 34.9–44.5s | 9.6s | reference images |
| G7 | #10 | 44.5–49.1s | 4.6s | reference images |
| G8 | #11, #12 | 49.1–55.7s | 6.5s | reference images |
| G9 | #13–#15 | 55.7–63.2s | 7.5s | reference images |
| G10 | #16, #17 | 63.2–71.0s | 7.9s | reference images |

**Why it is split this way**

- Grouping: consecutive shots share a call where they fit, ≤10s per call, ≤4 shots; a long stretch is cut at a scene change first
- Inputs: the model also takes reference video, but key frames are used here: one key frame per shot fixes composition and look, swapped-in things get their own images
- Audio: the model can generate action sound effects and ambience along with the picture; voice-over is better done as separate TTS and mixed in, so copy and timing stay editable
- Packaging: the subtitle, text label on the generated shots is post-production packaging: keep it out of the prompts (erased from source references) and lay it back on from the packaging timeline after generation

**Frames to make first (17)**

When swapping people or products, or switching to shot-by-shot image-to-video, prepare each shot's first frame as below:

| Shot | Role | How | Reference images | Save as |
|---|---|---|---|---|
| #1 | first frame | text-to-image (also serves as character anchor image) | `shots/shot_001_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot001.png` |
| #2 | first frame | text-to-image (also serves as character anchor image) | `shots/shot_002_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot002.png` |
| #3 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Hero look and outfit); `shots/shot_003_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot003.png` |
| #4 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Hero look and outfit); `shots/shot_004_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot004.png` |
| #5 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_005_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot005.png` |
| #6 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_006_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot006.png` |
| #7 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #2 (locks Neighbour look and outfit); `shots/shot_007_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot007.png` |
| #8 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #2 (locks Neighbour look and outfit); `shots/shot_008_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot008.png` |
| #9 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_009_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot009.png` |
| #10 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_010_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot010.png` |
| #11 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_011_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot011.png` |
| #12 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_012_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot012.png` |
| #13 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_013_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot013.png` |
| #14 | first frame | text-to-image (or low-denoise I2I from source frame) | `shots/shot_014_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot014.png` |
| #15 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Hero look and outfit); `shots/shot_015_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot015.png` |
| #16 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Hero look and outfit); `shots/shot_016_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot016.png` |
| #17 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #2 (locks Neighbour look and outfit); `shots/shot_017_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot017.png` |

- **#1 first frame (text-to-image (also serves as character anchor image))**
  - Image prompt: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. Hook: FPV fly-in to the white house; the hero runs a yellow hose into his own basement window while the street stacks sandbags against the rising river
- **#2 first frame (text-to-image (also serves as character anchor image))**
  - Image prompt: Vertical 9:16. medium close-up, subject in the lower middle of the frame, camera push-in. Fast fly-by to the blue neighbour's house: blue discharge hoses, the neighbour leans on a white picket fence and yells 'Flood's not till tomorrow, pal. You're early!'
- **#3 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium shot, subject in the lower middle of the frame, camera push-in. Whip into the flooding basement; the hero carries a couch up the stairs alone; cut to him shutting off the breaker panel
- **#4 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium shot, subject in the lower middle of the frame. POV down the basement stairs: the water is up to the top step; neighbours gather on the stairs with a life ring, joking
- **#5 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the lower middle of the frame. Night exterior through a window; transition beat
- **#6 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the lower middle of the frame, camera pull-out. River overtops the bank and sandbags; aerial of both houses standing in a brown lake
- **#7 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #2's anchor image: Vertical 9:16. medium shot, subject in the left of the frame, camera push-in. Cutaway of the neighbour's dry basement with pumps winning; neighbour yells 'How's the pool?'; sunset: a hairline crack appears in his basement wall
- **#8 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #2's anchor image: Vertical 9:16. medium shot, subject in the lower middle of the frame, camera pull-out. Midnight: the crack widens to finger width (flashlight close-up); cutaway shows the wall bowing inward under the saturated soil
- **#9 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the upper right of the frame, camera push-in. Cutaway metaphor: a red pickup truck leaning against the basement wall from the soil side
- **#10 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject centred in frame, camera push-in. Workbench close-up: a gloved hand squeezes an empty soda can (crumples) vs a full one (doesn't give)
- **#11 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium close-up, subject in the lower middle of the frame, camera push-in. Side-by-side cutaway: the flooded basement walls with water pushing back equally from inside
- **#12 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the lower middle of the frame. Quick graphic/insert beat for 'flood guides really say'
- **#13 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the left of the frame, camera pull-out. Aerial of the flooded street
- **#14 first frame (text-to-image (or low-denoise I2I from source frame))**
  - Image prompt: Vertical 9:16. medium shot, subject in the upper middle of the frame. Brief zoom/pan frame
- **#15 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium shot, subject in the left of the frame, camera push-in. Aerial as the river recedes, leaving muddy yards; a week later the hero walks a green hose out and drains his basement slowly
- **#16 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium shot, subject in the lower middle of the frame, camera pan / track. Inside the hero's basement: empty, wet floor, four straight walls
- **#17 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #2's anchor image: Vertical 9:16. medium shot, subject centred in frame, camera push-in. Neighbour in rubber boots pumping his basement out, kitchen debris and furniture all over the mud

**G1 · shots #1 · 7.5s**

- reference images: source frames of shots #1 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, neutral tones, background clearly blurred.
[Shot 1] Hook: FPV fly-in to the white house; the hero runs a yellow hose into his own basement window while the street stacks sandbags against the rising river. (composition: <Picture 1>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G2 · shots #2 · 5.8s**

- reference images: source frames of shots #2 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, neutral tones, background clearly blurred.
[Shot 1] Fast fly-by to the blue neighbour's house: blue discharge hoses, the neighbour leans on a white picket fence and yells 'Flood's not till tomorrow, pal. You're early!' (composition: <Picture 1>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G3 · shots #3, #4 · 8.1s**

- reference images: source frames of shots #3, #4 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, neutral tones, background clearly blurred.
[Shot 1] Whip into the flooding basement; the hero carries a couch up the stairs alone; cut to him shutting off the breaker panel. (composition: <Picture 1>)
[Shot 2] At 00:02.960, the camera cuts to: POV down the basement stairs: the water is up to the top step; neighbours gather on the stairs with a life ring, joking. (composition: <Picture 2>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G4 · shots #5, #6 · 5.6s**

- reference images: source frames of shots #5, #6 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, neutral tones, background clearly blurred.
[Shot 1] Night exterior through a window; transition beat. (composition: <Picture 1>)
[Shot 2] At 00:01.001, the camera cuts to: River overtops the bank and sandbags; aerial of both houses standing in a brown lake. (composition: <Picture 2>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G5 · shots #7 · 7.8s**

- reference images: source frames of shots #7 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, neutral tones, background clearly blurred.
[Shot 1] Cutaway of the neighbour's dry basement with pumps winning; neighbour yells 'How's the pool?'; sunset: a hairline crack appears in his basement wall. (composition: <Picture 1>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G6 · shots #8, #9 · 9.6s**

- reference images: source frames of shots #8, #9 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, neutral tones, background clearly blurred.
[Shot 1] Midnight: the crack widens to finger width (flashlight close-up); cutaway shows the wall bowing inward under the saturated soil. (composition: <Picture 1>)
[Shot 2] At 00:07.754, the camera cuts to: Cutaway metaphor: a red pickup truck leaning against the basement wall from the soil side. (composition: <Picture 2>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G7 · shots #10 · 4.6s**

- reference images: source frames of shots #10 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, neutral tones, background clearly blurred.
[Shot 1] Workbench close-up: a gloved hand squeezes an empty soda can (crumples) vs a full one (doesn't give). (composition: <Picture 1>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G8 · shots #11, #12 · 6.5s**

- reference images: source frames of shots #11, #12 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, neutral tones, background clearly blurred.
[Shot 1] Side-by-side cutaway: the flooded basement walls with water pushing back equally from inside. (composition: <Picture 1>)
[Shot 2] At 00:05.420, the camera cuts to: Quick graphic/insert beat for 'flood guides really say'. (composition: <Picture 2>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G9 · shots #13–#15 · 7.5s**

- reference images: source frames of shots #13, #14, #15 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, neutral tones, background clearly blurred.
[Shot 1] Aerial of the flooded street. (composition: <Picture 1>)
[Shot 2] At 00:01.709, the camera cuts to: Brief zoom/pan frame. (composition: <Picture 2>)
[Shot 3] At 00:02.126, the camera cuts to: Aerial as the river recedes, leaving muddy yards; a week later the hero walks a green hose out and drains his basement slowly. (composition: <Picture 3>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G10 · shots #16, #17 · 7.9s**

- reference images: source frames of shots #16, #17 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, neutral tones, background clearly blurred.
[Shot 1] Inside the hero's basement: empty, wet floor, four straight walls. (composition: <Picture 1>)
[Shot 2] At 00:03.710, the camera cuts to: Neighbour in rubber boots pumping his basement out, kitchen debris and furniture all over the mud. (composition: <Picture 2>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**Prompt guides for MiniMax H3 / H3 Max**

- https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md
- https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md
- https://platform.minimax.io/docs/api-reference/video-generation-v2-create
- https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide.md
