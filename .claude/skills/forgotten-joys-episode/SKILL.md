---
name: forgotten-joys-episode
description: >
  Make a new episode of the "Forgotten Little Joys of Life" series: a wordless, nostalgic, about-one-minute
  vertical (9:16) storybook-cartoon reel about an Indian middle-class childhood memory, with a fixed
  "POV / you were your ..." caption, a kid, a parent, a tiny joy at the end and a "forgotten / little joys of
  life" end card. Covers the story beats, AI shot stills (OpenRouter image model), image-to-video clips
  (HeyGen Video 1 at 480p), the edit with caption, speech bubbles and end card, music and a checked MP4.
  Use whenever the user asks for a new episode, "another one like the chai / tv remote video", a nostalgic
  Indian POV cartoon reel, or names this series or skill, even without saying "skill".
---

# Forgotten Little Joys: episode maker

One episode is one small childhood memory, told with pictures only, about 55–60 s long:
**a problem at home → the kid does an errand → a tiny joy as the reward → end card.**
Episode 1 (the source reference: chai errand, ₹1 change) and episode 2 (dad's TV remote, kulfi) define the series.
The full creative rules are in [references/THEME.md](references/THEME.md); read it before writing a new episode.
A complete, working episode config is in [references/episode2-example.json](references/episode2-example.json).

## What this costs and needs

- **OpenRouter** account with credit. In a Claude cloud session, ask for the key with the secure credential
  form for host `openrouter.ai` (never in chat); the proxy injects it, so the scripts send a placeholder.
  Run locally, export `OPENROUTER_API_KEY`.
- Measured on episode 2: about **$0.04 per still** (Nano Banana 2.1) and **$0.05 per 5 s clip** (HeyGen Video 1,
  480p; $0.08 for 8 s). **About $2 per episode** including a few retries. Check the balance before starting:
  `GET https://openrouter.ai/api/v1/credits`.
- `ffmpeg`, Python 3 with Pillow, Node with Playwright + Chromium (all present in Claude cloud sessions).
- **Music:** a track the user supplies (file), or none. YouTube downloads are blocked from cloud sessions
  ("confirm you're not a bot"). Ask the user to upload the audio file. Don't try to get around the block.

## Workflow

Work in a new folder per episode (for example `videos/NNN-forgotten-little-joys-epN/`). Copy
`references/episode2-example.json` there as `episode.json` and rewrite it for the new story.

1. **Story (no spend).** From the user's idea, or pick one from THEME.md section 10. Write:
   - the caption: `POV` plus a line naming the kid's role through a modern comparison, lower case, no apostrophes,
     split into two lines (`caption_lines`)
   - 17–19 shots on the THEME beat sheet: home problem (fast shots, about 1.5–2.4 s), errand (2–5 s),
     joy (long holds, 4.5–7 s), end card (2.6 s, `transition_in: "fade12"`)
   - exactly two POV palm shots (task given, reward received), one perfectly still comic shot,
     one `dissolve3` where the location changes, at most two speech bubbles (lower case, kid spelling)
   - per shot: `frames` at 24 fps, `cast`, `image_prompt` (what is in the picture), `refs`, `motion_prompt`
     (one small action, as in the example)
   - the end-card object (the joy) and `end_card.title_lines`. Leave `episode_label` null unless asked.
   Show the shot list to the user if they asked to review; otherwise continue.
2. **New characters.** Any new adult or kid gets a `characters.<name>` entry with `look` (repeated in every
   shot prompt) and a `sheet_prompt`. Run `python3 -I scripts/gen_images.py EP --sheets`, look at the sheet,
   then add `sheets/<name>.png` to the `refs` of that character's shots. The kid and Dad are already
   defined; reuse their `look` text unchanged so they stay the same person.
3. **Stills.** `python3 -I scripts/gen_images.py EP` (parallel). Then look at every still at a readable size
   (contact sheet). Regenerate a single shot with `--only N` after fixing its prompt. Typical faults:
   an eye open when it should be closed, text or letters in the picture, wrong outfit colour, extra hands.
4. **Clips.** `python3 -I scripts/gen_clips.py EP`. It makes each still the first frame of a HeyGen clip
   long enough for the shot and strips the clip's audio. Look at each clip (frames at 1–2 fps). If an action
   starts late, set the shot's `in_offset` (seconds to skip) instead of regenerating. Regenerate only clips
   whose motion is wrong (`--only N`).
5. **Overlays + edit.** `node scripts/overlays.mjs EP` renders the caption, bubbles and end-card title. Then
   `python3 -I scripts/assemble.py EP` cuts each clip to its frames, joins them (hard cuts, the 3-frame
   dissolve, the 0.5 s end fade), lays the caption over everything until the end card, slides the bubbles in,
   and adds the music from `audio.start` with a fade-out, at −14 LUFS (`audio.loop: true` for a short track).
6. **Check.** `bash scripts/check.sh EP` prints frames, duration and loudness and writes a contact sheet.
   Look at the sheet and at frames around each join, bubble and the end card before delivering. Say plainly
   what you could not check (you cannot listen; playback at speed is for the user).

## Rules that matter

- **Never** let generated images contain text; the caption, bubbles and title are added in the edit.
- Same kid in every episode: messy black hair, red T-shirt, black shorts, barefoot. Keep the `look` text.
- Static camera in every clip; motion comes from the characters (the reference is cut-out style, not camera moves).
- HeyGen Video 1 always renders audio and rejects `generate_audio: false`: strip it (the script does).
  It also rejects `frame_images` combined with `input_references`; send only the first frame.
- A video job that times out may still be running: poll its id again before paying for a new one.
- Keep every delivered version (copy the old MP4 aside) before re-rendering after a change.
- Removing a shot later: delete it from `shots` in `episode.json` and re-run `assemble.py`. Bubble times are
  relative to their shot, so they move with it. (Renumber the clip files to match the new order.)
- Music the user supplies may be copyrighted: mention that posting it can get the reel muted or claimed,
  and that Instagram's own music library avoids this.

## Files

- `references/THEME.md`: the series bible: caption formula, art bible, palette, characters, beat sheet,
  animation, text and audio rules, QA checklist, episode ideas.
- `references/style_block.txt`: the style paragraph prepended to every image prompt.
- `references/episode2-example.json`: the full episode 2 config (18 shots, bubbles, audio).
- `assets/style-refs/`: style and character references (episode 2's own generated art).
- `assets/fonts/`: Tinos (caption), Patrick Hand (bubbles), Courier Prime Bold (end card).
- `scripts/`: `gen_images.py`, `gen_clips.py`, `overlays.mjs` + `overlays.html`, `assemble.py`, `check.sh`.
