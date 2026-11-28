# Theme: "Forgotten Little Joys of Life" (nostalgic POV micro-stories)

The recipe for making new episodes that look, move and sound like the reference ([BREAKDOWN.md](BREAKDOWN.md), [`video.mp4`](video.mp4)). Follow the numbers. Anything marked **(fixed)** is identical in every episode; everything else changes per episode within the rules given.

---

## 1. Series identity (fixed)

- **Premise:** one small, wordless memory from an Indian middle-class childhood, told in about 1 minute from a POV angle, ending on a tiny joy.
- **Tone:** warm, gentle, a little funny, then tender. Nobody is ever mean; the payoff is always small and sweet.
- **Hook caption pattern:** `POV` + one line naming the childhood role through a **modern comparison** (apps, gadgets, services, adult jobs).
  - Reference: *"you were your moms Blinkit and Zepto"*.
- **End card:** `forgotten / little joys of life / ( episode N )` over an illustration of the episode's "joy object".
- **Post caption:** a nostalgic question that invites a reply, plus 1–2 emojis and `#indiannostalgia #indianmemories`.
  - Reference: *"What did you buy with the change? 💰🥹"*.

## 2. Technical format (fixed)

| Item | Value |
|---|---|
| Canvas | 1080 × 1920, 9:16, full bleed (no letterbox) |
| Frame rate | 24 fps. Keyframed moves update on twos (12 fps); "life" loops can run on ones |
| Length | 55–60 s total = 52–57 s story + 2.6 s end card |
| Loudness | −14 LUFS integrated, true peak ≤ −1 dBTP |
| Safe area | Keep key action between y 600 and 1650 (the caption sits at y 324–562; Instagram's UI covers the bottom ~300 px) |

## 3. Art bible (fixed)

### Look
- **Storybook page:** each shot is an illustration on **off-white paper with a fine horizontal grain**, fading at the edges into the paper colour (a soft, irregular vignette).
- A **warm amber glow** sits behind the subject (sunlit, nostalgic).
- **Line:** one even, slightly rough dark-brown brush outline, about 4–5 px at 1080 wide. Never pure black.
- **Fill:** flat colour with soft airbrushed shading.
- **Blush:** a strong red-orange glow on cheeks, ears, nose tip and on fingertips and palms. This blush is the signature look.
- **Faces:** big round heads; huge white eyes with small black pupils (no coloured iris); simple arched brows; tiny mouths. Expressions are read from pupil position and mouth shape.
- **Proportions:** chibi-leaning. Kids about 3.5 heads tall, adults about 5.
- **No camera moves.** Framing comes from the drawing: close-ups are drawn close.

### Palette tokens (sampled from the reference)
| Token | Hex | Use |
|---|---|---|
| `paper` | `#E9E4D7` / `#EFE0C3` | Background and vignette fade |
| `glow` | `#E3BC83` → `#ECCA93` | Warm halo behind subjects |
| `ink` | `#272019` | All outlines |
| `blush` | `#C8553D`-ish, soft airbrush | Cheeks, ears, nose, fingertips |
| `skin` | `#9B5E4A` (shadow) / `#B28163` (mid) | Brown Indian skin tones |
| `mom-kurta` | `#589A92` / `#88B1A7` | Teal salwar kurta |
| `kid-shirt` | warm red ≈ `#C8463A` | Boy's T-shirt |
| `hair` | `#333132` / `#3D3834` | Black hair |
| `steel` | `#605D54`–`#9E9281` | Steel tins, pots |
| `accent` | candy orange `#F5A658`, packet green `#686D01` | Joy objects and products |
| `endcard-text` | warm brown ≈ `#7A3E1E` with an orange glow | End card |

### Character bible (reuse across episodes)
- **Mom ("Amma"):**
  - Long black braid to the waist, red bindi, small gold nose stud
  - Teal salwar kurta, glass bangles on both wrists
  - Kind eyes; her face moves from tired or worried to soft smile
- **The Kid (boy, about 8–10):**
  - Messy black hair, red T-shirt, black shorts, barefoot at home
  - Huge eyes; emotions are curious "?", determined thumbs-up, eyes-closed pride, and wide-eyed wonder
- **Supporting cast (draw one per episode as needed):**
  - Shopkeeper (lilac shirt, moustache)
  - Dad (checked shirt, spectacles)
  - Grandmother (white saree, glasses)
  - Neighbour aunty
- **Hands are characters too:** POV inserts show the kid's open palm with red fingertips, and mom's hand with bangles.

### Prop library (the culture *is* the set dressing)
Steel tins labelled in handwriting (`chai`, `sugar`, `atta`), 2-burner gas stove, steel pot, cup-and-saucer set, door curtain on a rod, ₹1 / ₹2 / ₹5 coins, ₹10 / ₹20 notes, a kirana-shop counter with glass candy jars and hanging snack strips, ration bag, steel tiffin, school bag, Doordarshan-era TV, landline phone, scooter.

**Classic treats as "joy objects":** Eclairs toffee, orange candy slices, Melody, Poppins, Mango Bite, ice gola, Phantom candy sticks, Parle-G, kulfi.

### Image prompt block for style consistency (use for every shot)
```
hand-drawn digital storybook illustration, warm nostalgic Indian childhood, off-white paper texture with fine horizontal grain,
soft irregular vignette fading to paper colour, warm amber glow behind the subject, even rough dark-brown outlines,
flat colours with soft airbrush shading, strong red-orange blush on cheeks, ears, nose and fingertips,
big round heads, huge white eyes with tiny black pupils, simple brows, tiny mouth, chibi proportions,
vertical 9:16 composition, subject centred between 30% and 85% of frame height, empty top band for a caption
```
Add the shot subject after it, for example: *"mom with long black braid, red bindi, teal salwar kurta and bangles, peering into an empty steel tin labelled 'chai'"*.

## 4. Story template: 3 acts, 18–20 shots (fixed structure)

| Act | Time | Shots | Average shot | Purpose | Music |
|---|---|---|---|---|---|
| **1. The problem at home** | 0 → ~18.5 s | 8–9 | **1.5–2.4 s** (fast) | Establish the home, reveal a small problem, bring in the Kid | Quiet bed (−28 dB) + comic sound effects |
| **2. The errand / adventure** | ~18.5 → ~37.5 s | 5 | **2–4.8 s** | The Kid goes out and does the task, one funny or cute obstacle | **The song drops in** about 0.3 s before the first shot of act 2 |
| **3. The tiny joy** | ~37.5 → ~56.5 s | 4 | **4.5–7 s** (long holds) | The small reward and the Kid imagining what it means | Song continues; its fuller, shimmering section starts about 10 s before the end |
| End card | last 2.6 s | 1 | — | Series title + episode number | Song tail |

### Beat sheet to fill in (reference values in brackets)
1. **Establishing still life** of the home task in progress (cooking pot on the stove), 2.4 s.
2. **Hand insert:** an adult hand reaches for something (the chai tin), 2.3 s.
3. **Adult reaction close-up:** looks closely, 1.6 s.
4. **Reveal insert:** the problem (empty tin), 1.5 s.
5. **Comic still:** adult sighs, 1.5 s, held perfectly still, with the "disappointed" sound effect.
6. **Kid enters:** peeks from behind a curtain or door, "?" over his head, 2.3 s.
7. **POV palm insert:** the task is handed over (money placed in his palm), 4.8 s.
8. **Adult instruction:** smile and point, 2.3 s.
9. **Kid accepts:** thumbs-up and dashes off. Song starts, 2.5 s.
10. **Destination:** the Kid struggles a little (too short for the counter), with a cute misspelled speech bubble, 2.5 s.
11. **Over-the-shoulder** at the other person (the shopkeeper shows the item), 2 s.
12. **Triumph:** the item held overhead with action ticks, 2.2 s.
13. **Pride + call back:** eyes shut, proud; the other person calls him back (focus pull), 4.8 s.
14. **POV palm insert #2:** the tiny reward lands (₹1 change) with a sparkle, 4.6 s.
15. **Reaction swap:** puzzled → delighted, "thank you" bubble, 4.6 s.
16. **Return:** back home, full body, 2.5 s.
17. **Adult's gift:** the adult lets him keep the reward, with a smile, 4.7 s.
18. **Wonder close-up:** the reward cross-dissolves into the joy it will buy (coin → Eclairs toffee) and back, 7.1 s.
19. **End card**, 2.6 s.

**Rules**
- Always use **two POV palm inserts**: one when the task is given, one when the reward arrives. They rhyme.
- Shots get longer as the story gets more emotional.
- Never use more than 2 speech bubbles per episode. Keep them short, lower case, with child spelling ("pleeees").
- No narration and no dialogue audio. The story must work with the sound off.

## 5. Animation rules (fixed)
- **Cut-out (puppet) animation on top of illustrations:** draw each element (head, eyes, mouth, arms, hands, props) on its own layer, then **move layers on keyframed paths**. Don't redraw frame by frame.
- **Moves:** hands and props slide in from the frame edge with ease-out, updated on twos (12 fps). Drops (coins, notes) fall about 80–150 px with a tiny settle.
- **Expression changes are instant one-frame swaps** between drawings: fist ↔ open palm, worried ↔ smile, eyes open ↔ shut. Hold each pose at least 0.5 s.
- **Constant small life** in every non-still shot:
  - flame or steam loops
  - a 1–2 px sway or breathing on characters
  - blinking
  - sparkle stars (4-point, white) on shiny objects
- **Comic still:** one shot per episode is held completely still for about 1.5 s (the sigh).
- **Transitions:**
  - Hard cuts by default.
  - One 3-frame dissolve when arriving at a new location (home → shop).
  - An in-shot cross-dissolve of about 0.6 s for "imagination", each way.
  - A 0.5 s fade into the end card.
- **Speech bubbles** slide in from the nearest frame edge in about 0.25 s and stay until the cut.
- **Focus pull:** blur the foreground character (about 10–14 px Gaussian, over about 0.5 s) when the background character calls.

## 6. Text system (fixed)
- **Hook caption** (on screen from 0 to the end-card fade):
  - Two black rectangles (`#000`, no rounding), white serif text (Instagram "Classic" / Times-style), centred.
  - Small box `POV`: about 118 × 89 px at y 324–412, text about 44 px.
  - Main box: about 412 × 139 px at y 424–562, two lines, text about 40 px, 10 px gap above.
  - The text is lower case except proper nouns, and has no apostrophes. The deliberately casual feel is part of the style.
- **Speech bubble:** white rounded pill, 2 px dark outline, a short straight tail toward the speaker, casual handwritten font (e.g. *Patrick Hand* / *Gaegu*), about 30–34 px.
- **Labels inside the art:** handwritten lower case on props ("chai").
- **End card:**
  - Warm-brown typewriter slab serif (e.g. *Courier Prime Bold* / *American Typewriter*), lower case, about 80 px.
  - Soft orange outer glow. `( episode N )` at about 45 px.
  - 3–4 illustrations of the joy object scattered around the text, with crumbs and sparkles on the paper.

## 7. Audio recipe
| Time | Layer | Spec |
|---|---|---|
| 0 → act 2 | **Soft bed** | Quiet sustained instrumental (pad, soft keys, gentle strings or flute), no drums, about 13–15 dB below the song. Key D major in the reference |
| Act 1 | **Comic sound effects**, in sync with the picture | A descending slide-whistle or "aww" with a soft thump on the problem reveal; small bright "ding" hits as money or the reward lands; soft whoosh or patter as the Kid enters |
| Act 2 start (−0.3 s pre-lap) | **The song** | A nostalgic Indian song (vocal or instrumental cover) with a clear melodic lead, bass and light percussion. It enters at full level on the story turn |
| About 10 s before the end | **Song lift** | Its fuller, sparkling section (chorus) under the reward and wonder shots |
| Throughout | **Sparkle sound** | A tiny chime on every sparkle (coin, packet) |
| Master | | −14 LUFS integrated, −1 dBTP; the music tail runs to the very last frame |

Note: the reference's song couldn't be identified or confirmed by listening here. Use music you have the rights to, or Instagram's licensed audio library.

## 8. Production pipeline (how to make an episode)
1. **Write** the hook caption, the problem, the errand and the tiny joy. Fill in the 19-beat sheet (§4) with durations that add up to about 56.5 s.
2. **Draw the stills:** one per shot, plus separate layers for every moving part (hands, eyes, mouth poses, props, bubbles). A hand-drawing app (Procreate, Krita, Photoshop) gives the most faithful result. For AI help, use the prompt block in §3 with the character bible, and keep one approved character sheet as the reference for every shot.
3. **Animate the cut-outs:** After Effects, CapCut keyframes, Rive, or code (canvas + keyframes). Follow §5: slides on twos, one-frame swaps, life loops, sparkles.
4. **Text:** caption boxes, bubbles and end card per §6.
5. **Audio:** bed + sound effects for act 1, the song drop at the act 2 turn, sparkles; master to −14 LUFS per §7.
6. **Export** 1080×1920, 24 fps, H.264 high quality, AAC 44.1 kHz.

## 9. QA checklist
- [ ] 55–60 s; 18–20 shots; act 1 shots average under 2.5 s; act 3 holds longer than 4.5 s
- [ ] Hook caption in POV + modern-comparison form, boxes at the fixed positions, visible until the end card
- [ ] Two POV palm inserts (task given / reward received)
- [ ] Exactly one perfectly still comic shot with its sound effect
- [ ] The song drops in at the act 2 turn (±0.3 s), not before
- [ ] One imagination cross-dissolve to the joy object
- [ ] Paper texture + vignette + amber glow + red blush in every shot; no camera moves
- [ ] At most 2 speech bubbles, lower case, child spelling
- [ ] End card `forgotten / little joys of life / ( episode N )` with joy-object art, 2.6 s, 0.5 s fade in
- [ ] −14 LUFS; works with the sound off

## 10. Episode ideas in the same formula
| Ep | Hook caption (POV …) | Problem → errand | Tiny joy (end-card object) |
|---|---|---|---|
| 2 | you were your dads tv remote | Dad wants the channel changed → kid climbs on a stool and turns the knob, adjusts the antenna | Dad shares his kulfi (kulfi sticks) |
| 3 | you were your familys landline answering machine | Phone rings during lunch → kid answers "hello who's speaking" | Aunty on the phone promises to bring sweets (laddoos) |
| 4 | you were your nanis needle threader | Nani can't thread the needle → kid threads it first try | Nani's secret stash of Poppins (Poppins roll) |
| 5 | you were your moms milk packet pickup service | Morning milk hasn't come → kid runs to the milk booth with the steel can | The milkman gives a free Mango Bite (Mango Bite toffees) |
| 6 | you were your colonys ice gola tracker | Hears the ice-gola cart bell → runs with ₹2 | Rainbow ice gola melting down the arm (ice golas) |
