---
videomd: 1
part: remake
tokens: 5267
---

## Remake plan

### Step by step

This is a 3D / animation. Do the steps in this order; the detail for each is in the matching subsection below. 34% of the time is a AI story short; its steps are included.

1. **Write the content**: write yours in the same 13 steps as the original (narrative line under “Content and structure”)
2. **Collect material**: one reference image per recurring character to lock appearance across shots: Retriever, Owner
3. **Generate**: 13 calls (109 s), several shots each. Each shot gets one source frame for composition (subtitles erased, in `remake/refs/`), the swapped-in people, animals and products get reference images, and the prompt lists the shots in order
4. **Adapt the prompts to your model**: each unit's draft is already laid out in MiniMax H3 / H3 Max's shot, tag and audio format; refine it against the model's prompt guide before generating (or run `rea-video plan <folder> --rewrite-prompts`)
5. **Voice**: the original is TTS voice-over; record it yourself or use TTS; 27 lines with their pace in the script table under “Sound”
6. **Edit**: follow the order and lengths in the shot list; the original has 14 shots at 7.8s each; 10 transitions under “Edit”
7. **Subtitles and styled text**: import `packaging/subtitles.srt` and replace the words; timing and style under “Packaging layer”
8. **Sound effects**: 48; place similar ones from a library at the times under “Sound”
9. **Put it together and compare**: hand the shots you made to the agent; it places them on the original timeline, keeps the original where yours are missing, and renders a side-by-side comparison with the original

**11 3D render shots + 3 AI video shots → 10 generation units, 13 MiniMax H3 / H3 Max calls**

### Generation units

- **How it is generated**: multi-shot from key frames

| Part | Shots | Time | Length | Prepare |
|---|---|---|---|---|
| G1 | #1 | 0.0–5.4s | generate 6s, trim to 5.4s | reference images |
| G2 | #2 | 5.4–15.8s | generate 11s, trim to 10.4s | reference images |
| G3 | #3 | 15.8–27.0s | generate 12s, trim to 11.2s | reference images |
| G4 | #4 | 27.0–36.9s | 9.9s | reference images |
| G5 | #5 | 36.9–56.9s | 20.0s (2 calls) | reference images |
| G6 | #6, #7 | 56.9–58.8s | generate 4s, trim to 1.8s | reference images |
| G7 | #8 | 58.8–75.1s | generate 9s, trim to 8.2s (2 calls) | reference images |
| G8 | #9–#12 | 75.1–79.8s | 4.8s | reference images |
| G9 | #13 | 79.8–108.8s | generate 15s, trim to 14.5s (2 calls) | reference images |
| G10 | #14 | 108.8–109.2s | generate 4s, trim to 0.4s | reference images |

**Why it is split this way**

- Grouping: consecutive shots share a call where they fit, ≤10s per call, ≤4 shots; a long stretch is cut at a scene change first
- Inputs: the model also takes reference video, but key frames are used here: one key frame per shot fixes composition and look, swapped-in things get their own images
- Audio: the model can generate action sound effects and ambience along with the picture; voice-over is better done as separate TTS and mixed in, so copy and timing stay editable
- Packaging: the text label, subtitle, styled text on the generated shots is post-production packaging: keep it out of the prompts (erased from source references) and lay it back on from the packaging timeline after generation

**Frames to make first (14)**

When swapping people or products, or switching to shot-by-shot image-to-video, prepare each shot's first frame as below:

| Shot | Role | How | Reference images | Save as |
|---|---|---|---|---|
| #1 | first frame | text-to-image (also serves as character anchor image) | `shots/shot_001_first.jpg` (source first frame: composition and style reference) | `remake/redrawn/shot001.png` |
| #2 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Retriever look and outfit); `shots/shot_002_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot002.png` |
| #3 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Retriever look and outfit); `shots/shot_003_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot003.png` |
| #4 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Retriever look and outfit); `shots/shot_004_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot004.png` |
| #5 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Retriever look and outfit); `shots/shot_005_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot005.png` |
| #6 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Retriever look and outfit); `shots/shot_006_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot006.png` |
| #7 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Retriever look and outfit); `shots/shot_007_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot007.png` |
| #8 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Retriever look and outfit); `shots/shot_008_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot008.png` |
| #9 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Retriever look and outfit); `shots/shot_009_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot009.png` |
| #10 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Retriever look and outfit); `shots/shot_010_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot010.png` |
| #11 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Retriever look and outfit); `shots/shot_011_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot011.png` |
| #12 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Retriever look and outfit); `shots/shot_012_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot012.png` |
| #13 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Retriever look and outfit); `shots/shot_013_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot013.png` |
| #14 | first frame | image-to-image / reference edit (lock character look) | anchor frame from shot #1 (locks Retriever look and outfit); `shots/shot_014_first.jpg` (source first frame: shot framing and pose reference) | `remake/redrawn/shot014.png` |

- **#1 first frame (text-to-image (also serves as character anchor image))**
  - Image prompt: Vertical 9:16. medium close-up, subject in the upper middle of the frame, camera push-in. Hook: wide high-angle garden; man pushes a big wooden box with a round door into place as the retriever trots past; push-in as the box swings round to face camera
- **#2 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium close-up, subject in the upper middle of the frame, camera pull-out. Push into the box; front wall dissolves into a cutaway; dog curls up shivering on bare boards (breath puff); glowing heat aura around the dog with a green 'room' outline graphic shows the space is too big; box shrinks to a smaller room, dog stands/turns/lies down
- **#3 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium shot, subject in the upper middle of the frame, camera push-in. Dog stands in the smaller box; rain starts, damp rises up the walls (dark wet band); man lifts the box onto bricks
- **#4 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium close-up, subject in the upper middle of the frame, camera push-in. Rain continues; raised floor stays dry, kinetic 'the raised floor' text pops; man lays a striped blue blanket inside
- **#5 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. Soaking-wet dog walks in and shakes; blanket soaks up the water; night, dog shivers on frozen blanket (breath puff); man pulls the blanket out; straw fills the bed; dog steps in and settles; straw gets dragged out; a sill board is added with a '5 in / 13 cm' dimension callout
- **#6 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium close-up, subject in the upper middle of the frame, camera pull-out. Brief beat on the sill/insulation callout; kinetic text pop
- **#7 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium close-up, subject in the upper middle of the frame, camera push-in. Heat shown as orange wavy lines leaking out through the walls
- **#8 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium close-up, subject in the left of the frame, camera push-in. Roof lifts off; walls, floor and ceiling lined with foam then boards; kinetic 'the insulation' text; wide shot of the garden as white wind streaks pick up and blow straight through the centred door onto the bed
- **#9 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium close-up, subject in the lower middle of the frame, camera push-in. Man hangs a fabric flap over the door
- **#10 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. Man walks past the flapped house; camera moves round to a cutaway diagram with a guide line
- **#11 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. Top-down/cutaway of the charity design: a box with the door at one end
- **#12 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. close-up, subject centred in frame, camera push-in. Brief kinetic text beat
- **#13 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium close-up, subject centred in frame, camera push-in. Lid open: hallway + bedroom layout; dog walks in, turns the corner, sleeps behind a partition; dimension callouts '22 in / 56 cm' and '39 in / 99 cm'; white wind streaks hit the wall; kinetic 'the side door'; summer: flap off, two people carry the house into the shade; recap of the fixes; ends inside the house with the dog on a wooden floor
- **#14 first frame (image-to-image / reference edit (lock character look))**
  - Image prompt: Keep the exact facial features and outfit from shot #1's anchor image: Vertical 9:16. medium close-up, subject in the upper middle of the frame, camera pull-out. Final frame, end-card text beat

**G1 · shots #1 · 5.4s**

- reference images: source frames of shots #1 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, warm tones, background clearly blurred.
[Shot 1] Hook: wide high-angle garden; man pushes a big wooden box with a round door into place as the retriever trots past; push-in as the box swings round to face camera. (composition: <Picture 1>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G2 · shots #2 · 10.4s**

- reference images: source frames of shots #2 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, warm tones, background clearly blurred.
[Shot 1] Push into the box; front wall dissolves into a cutaway; dog curls up shivering on bare boards (breath puff); glowing heat aura around the dog with a green 'room' outline graphic shows the space is too big; box shrinks to a smaller room, dog stands/turns/lies down. (composition: <Picture 1>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G3 · shots #3 · 11.2s**

- reference images: source frames of shots #3 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, warm tones, background clearly blurred.
[Shot 1] Dog stands in the smaller box; rain starts, damp rises up the walls (dark wet band); man lifts the box onto bricks. (composition: <Picture 1>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G4 · shots #4 · 9.9s**

- reference images: source frames of shots #4 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, warm tones, background clearly blurred.
[Shot 1] Rain continues; raised floor stays dry, kinetic 'the raised floor' text pops; man lays a striped blue blanket inside. (composition: <Picture 1>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G5 · shots #5 · 20.0s**

- reference images: source frames of shots #5 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, warm tones, background clearly blurred.
[Shot 1] Soaking-wet dog walks in and shakes; blanket soaks up the water; night, dog shivers on frozen blanket (breath puff); man pulls the blanket out; straw fills the bed; dog steps in and settles; straw gets dragged out; a sill board is added with a '5 in / 13 cm' dimension callout. (composition: <Picture 1>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G6 · shots #6, #7 · 1.8s**

- reference images: source frames of shots #6, #7 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, warm tones, background clearly blurred.
[Shot 1] Brief beat on the sill/insulation callout; kinetic text pop. (composition: <Picture 1>)
[Shot 2] At 00:00.533, the camera cuts to: Heat shown as orange wavy lines leaking out through the walls. (composition: <Picture 2>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G7 · shots #8 · 16.3s**

- reference images: source frames of shots #8 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, warm tones, background clearly blurred.
[Shot 1] Roof lifts off; walls, floor and ceiling lined with foam then boards; kinetic 'the insulation' text; wide shot of the garden as white wind streaks pick up and blow straight through the centred door onto the bed. (composition: <Picture 1>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G8 · shots #9–#12 · 4.8s**

- reference images: source frames of shots #9, #10, #11, #12 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, warm tones, background clearly blurred.
[Shot 1] Man hangs a fabric flap over the door. (composition: <Picture 1>)
[Shot 2] At 00:01.400, the camera cuts to: Man walks past the flapped house; camera moves round to a cutaway diagram with a guide line. (composition: <Picture 2>)
[Shot 3] At 00:02.967, the camera cuts to: Top-down/cutaway of the charity design: a box with the door at one end. (composition: <Picture 3>)
[Shot 4] At 00:04.300, the camera cuts to: Brief kinetic text beat. (composition: <Picture 4>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G9 · shots #13 · 29.0s**

- reference images: source frames of shots #13 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, warm tones, background clearly blurred.
[Shot 1] Lid open: hallway + bedroom layout; dog walks in, turns the corner, sleeps behind a partition; dimension callouts '22 in / 56 cm' and '39 in / 99 cm'; white wind streaks hit the wall; kinetic 'the side door'; summer: flap off, two people carry the house into the shade; recap of the fixes; ends inside the house with the dog on a wooden floor. (composition: <Picture 1>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**G10 · shots #14 · 0.4s**

- reference images: source frames of shots #14 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, warm tones, background clearly blurred.
[Shot 1] Final frame, end-card text beat. (composition: <Picture 1>)
overall_soundscape: Only the natural sounds of the actions on screen.
non_diegetic_music: N/A
```

**Prompt guides for MiniMax H3 / H3 Max**

- https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md
- https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md
- https://platform.minimax.io/docs/api-reference/video-generation-v2-create
- https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide.md
