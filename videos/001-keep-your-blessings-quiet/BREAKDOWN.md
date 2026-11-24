# 001 — "Keep Your Blessings Quiet Until They're Permanent"

| | |
|---|---|
| Source | Instagram reel `DgHUJ3Bhpt3` by **@wealth** (Wealth) |
| Reference copy | [`video.mp4`](video.mp4) |
| Duration | 19.90 s |
| Format | 1080×1920 (9:16), 30 fps, VP9 · AAC stereo 44.1 kHz |
| Genre | Faceless animated "life-lesson" short: cartoon couple, one moral, no dialogue on screen |

Frames: [`frames/`](frames/). The contact sheets sample every 0.5 s; there's one clean still per shot plus a keyframe grid.

---

## 1. The idea in one line

Four "big life wins" (savings, a home, a pregnancy, a car) each end on the same **"shh" beat**: tape over the mouth and a finger to the lips. The fifth win, the baby, ends with the **whole family** doing the shh. The structure *is* the message: celebrate privately.

## 2. Screen layout (constant for all 19.9 s)

```
y=0     ┌──────────────────────────┐
        │                          │  pure black (#000)
y≈513   │  Keep Your Blessings Quiet│  line 1: white + yellow keyword
y≈576   │  Until They're Permanent │  line 2: white + yellow keyword
y=656   ├──────────────────────────┤
        │                          │
        │   16:9 picture band      │  1080×608, vertically centred (centre y=960)
        │                          │
y=1264  ├──────────────────────────┤
        │                          │  pure black
y=1920  └──────────────────────────┘
```

- **Title text never changes or moves.** It's a static overlay for the whole video. Scene-change detection on the title strip returned 0 events.
- Font: heavy, rounded geometric sans (Montserrat/Poppins ExtraBold family, not confirmed), centred, about 36 px cap height on the 1080 canvas, tight line spacing.
- Colours: white `#FFFFFF` with keywords in yellow, measured at about **`#F4EE2C`**. The two yellow words are **Quiet** and **Permanent**.
- The art is made at 16:9 and letterboxed into 9:16. This is a common "horizontal clip + hook title" reel template.

## 3. Shot list (exact cut times from frame-difference detection)

| # | In → Out (s) | Len | Setting / framing | Action | Role |
|---|---|---|---|---|---|
| 1 | 0.00 → 2.67 | 2.67 | Night, dining room, warm lamp. Wide two-shot at a wooden table | Couple counting stacks of cash, smiling, then exchanging a glance (~1.5 s) | **Win #1: savings** |
| 2 | 2.67 → 4.23 | 1.57 | Close two-shot, dark warm background | Each pinches a strip of beige masking tape, sticks it over their mouth (on by ~3.0 s), sly side-eye, finger to lips | **Shh beat** (first time: the tape is applied on screen) |
| 3 | 4.23 → 6.87 | 2.63 | Empty bright apartment, floor-to-ceiling windows, city skyline, daylight | He raises a key ring (~4.5 s), she beams, they hug (~5.6–6.8 s) | **Win #2: new home** |
| 4 | 6.87 → 8.00 | 1.13 | Close two-shot, **daylight window** background | Tape already on, finger to lips, glance | Shh beat |
| 5 | 8.00 → 8.73 | 0.73 | Bedroom, bedside lamp, night | She holds up a pink pregnancy test; he has his back to camera | **Win #3: pregnancy** (setup) |
| 6 | 8.73 → 9.67 | 0.93 | Big close-up of his face | Wide eyes turn into a huge grin (slow push-in) | Reaction |
| 7 | 9.67 → 10.73 | 1.07 | Bedroom, medium | She nuzzles into him, eyes closed, he holds her | Tender beat |
| 8 | 10.73 → 12.00 | 1.27 | Close two-shot, **bedroom** background | Tape pressed on again, then finger to lips | Shh beat |
| 9 | 12.00 → 14.80 | 2.80 | Sunny parking lot, white sedan, trees | She is **visibly pregnant**; he hands her a key fob (~12–13 s), big hug (~14 s) | **Win #4: new car** |
| 10 | 14.80 → 16.20 | 1.40 | Close two-shot, **outdoor/car** background | Tape on, finger to lips | Shh beat |
| 11 | 16.20 → 19.90 | 3.70 | Living room, beige couch, rug, golden light | Baby takes first steps between kneeling parents (16–17 s). All three huddle; **parents and baby** put a finger to their lips (~18.3 s). **Fade to black 19.25 → 19.9 s** | **Win #5: baby + payoff** |

### Rhythm
- Pattern: **WIN (≈2.7 s) → SHH (≈1.1–1.6 s)**, repeated. Win #3 is broken into three quick shots (0.7 / 0.9 / 1.1 s) for a burst of emotion.
- The shh beat appears **4 times**. Only the first shows the tape being applied fully. Later ones start with the tape already on or being pressed on, so the beat gets shorter each time.
- **Continuity detail:** each shh close-up sits in the matching location's lighting (night interior → daylight apartment → bedroom lamp → outdoor sun). It reads as "same moment, closer camera", not a reused clip.
- **Time progression told visually:** pregnancy test → pregnant belly at the car → baby walking. That's about 1.5 years in 20 s with no text.
- **Ending callback:** the baby joins the shh. This is the only shot where the refrain changes, so it lands as the punchline.

### Measured end fade
Picture-band mean luma: 103 at 19.0 s → 87 at 19.4 s → 67 at 19.6 s → 41 at 19.8 s. That's a quick (~0.6 s) fade to black.

## 4. Characters & art direction

- **Him:** short swept brown hair, thick eyebrows, rosy freckled cheeks. Black button-up shirt with white piping (pyjama/lounge style), later a navy shirt in the final scene.
- **Her:** dark brown messy top-bun with loose strands, freckles. Black spaghetti-strap crop top, dark jeans.
- **Baby:** blonde wisps, blue eyes, cream footie onesie.
- Style: modern feature-animation cartoon (Disney/Pixar-adjacent 2D). Big glossy eyes, soft cel shading, painterly warm light, strong rim light, gentle depth of field.
- Palette: warm amber/orange interiors (lamp-lit) alternating with cool, airy daylight exteriors. Skin is rendered very orange-warm throughout.
- Wardrobe and character design stay consistent across every shot.

## 5. Audio

- AAC stereo, about 54 kb/s. Mean −18.4 dB, peak 0.0 dB.
- RMS envelope (0.5 s windows): **quiet ~−29 dB for 0–2.5 s**, then jumps to about −17 dB **exactly at the first shh beat (2.67 s)** and stays there. It dips to −28 dB at 17.5–18.2 s, has a final hit at 18.5 s (−16 dB) on the family shh, and fades out with the picture.
- I measured loudness only. I couldn't listen, so I can't say whether it's music only or has a voice-over. The shape (soft intro, lift on the hook, breath before the final beat) suggests a trending music track edited to the cuts.

## 6. How it was probably made (inference, not confirmed)

1. **Character reference sheet** for the couple (and baby), so the look stays consistent.
2. **One still per shot** made by AI image generation with those references, at 16:9.
3. **Image-to-video** on each still for 1–3 s of motion (hugs forming, tape pressing, the push-in on his face). The soft, morph-like motion inside shots and the lack of camera cuts within a shot point to this.
4. **Edit:** cut to the music, put the 16:9 clips on a black 9:16 canvas, add the static two-line title with the keywords in yellow, then a 0.6 s fade to black at the end.

## 7. Recreating it — shot prompts (template)

Shared style suffix: *"modern 2D feature-animation style, big expressive glossy eyes, freckles, soft cel shading, warm cinematic lighting, shallow depth of field, 16:9"*

1. Couple at a wooden dining table at night counting stacks of cash, warm lamp, smiling at each other.
2. Close-up: couple each sticking a strip of masking tape over their mouth, then finger to lips, mischievous side-glance. *(Re-make in 4 lighting variants: night interior / daylight apartment / bedroom lamp / sunny outdoors.)*
3. Empty sunlit apartment with floor-to-ceiling windows and city view. He holds up house keys, they hug.
4. Bedroom at night: she shows him a positive pregnancy test.
5. Extreme close-up of him: shocked wide eyes turning into a huge grin.
6. Tender hug in the bedroom.
7. Sunny parking lot: pregnant wife receives car keys next to a new white sedan, they hug.
8. Cozy living room: baby's first steps between kneeling parents, then all three put a finger to their lips.

Edit recipe: 9:16 black canvas, clip band 1080×608 centred, title at y≈510–615, cuts at the times in §3, 0.6 s fade out.
