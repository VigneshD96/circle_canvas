# 003 — "Forgotten Little Joys of Life" · Episode 2: the TV remote

Made from [`../002-forgotten-little-joys-ep1/THEME.md`](../002-forgotten-little-joys-ep1/THEME.md). Final video: [`episode2.mp4`](episode2.mp4). It's 1080×1920, 24 fps, exactly 59.0 s (1,416 frames), with AAC audio at about −14 LUFS.

**Caption:** "POV / you were your dads tv remote".
**Story:** Dad's cricket match turns to static and he can't reach the dial. The kid turns the dial, then runs up to the roof to twist the antenna. The picture comes back, Dad gives him a kulfi, and they share kulfis on the sofa. The last shot is the kid's first bite. End card: "forgotten / little joys of life" (episode number removed on request).

## Pipeline (all through OpenRouter)
1. **Style references:** 13 frames from episode 1 ([`pipeline/`](pipeline/), refs not committed).
2. **Character sheet + 19 shot stills:** `google/gemini-nano-banana-2.1`, each prompted with the THEME style block plus episode 1 frames as references ([`stills/`](stills/), [`pipeline/shots.py`](pipeline/shots.py)). Shot 5 was regenerated once because one eye was open.
3. **Motion:** each still is the first frame of an image-to-video clip from `heygen/heygen-video-1` at 480p, 9:16 ([`clips/`](clips/), motion prompts in [`pipeline/motions.py`](pipeline/motions.py)). HeyGen Video 1 always renders audio and won't accept `generate_audio: false`, so its audio was **stripped from every clip**.
4. **Edit** ([`pipeline/assemble.py`](pipeline/assemble.py)):
   - Clips are upscaled to 1080×1920 and cut on episode 1's exact cut grid (19 shots).
   - A 3-frame dissolve into the rooftop and a 0.5 s fade into the end card.
   - Overlays: the fixed POV caption boxes at episode 1's pixel positions, two sliding speech bubbles ("aaya papaaa??", "thank youuu"), and the end-card title in Courier Prime with an orange glow.
5. **Audio (current):** user-supplied flute track (YouTube 2ccpTL7VAeU, "Naan Pizhai" flute version, supplied as a file), played from 0:19 for 59 s with no loop, a 1.6 s fade-out over the end card, mixed to −14 LUFS. Music rights belong to the original owners; check licensing before posting.
6. **Original score (earlier version, replaced)** ([`pipeline/score.py`](pipeline/score.py)), synthesised in code:
   - A soft pad and music box until 18.4 s.
   - Then a song at 80 BPM in D major (wavy flute lead, plucked chords, bass, synth tabla) that gets fuller from 46.8 s.
   - Synced comic sounds: static, a sigh slide with a thump, a "?" boing, dial clicks, a whoosh, a picture-snap ding, sparkles, a bite crunch.

**Cost:** about $1.84 of OpenRouter credit: about $0.85 for images and $0.98 for 19 HeyGen clips at $0.05 each, plus one 8 s clip at $0.08.
