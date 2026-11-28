## Circles using canvas

Using 'arc' in canvas, circles with random radius, speed were created. They float round randomly. 
On hovering mouse over the screen, the circles near the mouse  getting magnified till they pass away from the pointer.
It is a fun project.
[View live demo](https://vigneshd96.github.io/circle_canvas)
## Video breakdowns

Each folder in `videos/` holds a reference copy of a video, extracted frames, and a `BREAKDOWN.md` covering timing, layout, shots, art, audio and how it might be recreated.

| # | Video | Breakdown |
|---|---|---|
| 001 | @wealth reel: "Keep Your Blessings Quiet Until They're Permanent" (19.9 s) | [BREAKDOWN](videos/001-keep-your-blessings-quiet/BREAKDOWN.md) |
| 002 | "Forgotten Little Joys of Life" ep. 1: the chai errand and the ₹1 change (59 s) | [BREAKDOWN](videos/002-forgotten-little-joys-ep1/BREAKDOWN.md) · [THEME (recipe for new episodes)](videos/002-forgotten-little-joys-ep1/THEME.md) |
| 003 | "Forgotten Little Joys of Life" ep. 2: you were your dads tv remote (made from the 002 THEME) | [README](videos/003-forgotten-little-joys-ep2/README.md) · [video](videos/003-forgotten-little-joys-ep2/episode2.mp4) |

## Skills in this repo

| Skill | Where | Use it for |
|---|---|---|
| `watch-video` | [`.claude/skills/watch-video/`](.claude/skills/watch-video/SKILL.md) | Watching and understanding a local video: transcript, speakers, sound events, timestamped frame sheets, and cutting new videos from it. It needs an Apple Silicon Mac (its transcription runs on MLX) and a one-time Hugging Face login for speaker detection. In Linux cloud sessions, the same analysis is done by hand with ffmpeg, as in the 002 breakdown. |
| `storybook-vignette-animation` | [`.claude/skills/storybook-vignette-animation/`](.claude/skills/storybook-vignette-animation/SKILL.md) | Storybook-vignette look with limited 2D animation; default use is new episodes of "Forgotten Little Joys of Life": story beats, AI stills, HeyGen clips, caption, bubbles, end card, music, checked MP4 (about $2 per episode on OpenRouter). Upload package for a claude.ai account: [`skill-packages/storybook-vignette-animation.zip`](skill-packages/storybook-vignette-animation.zip). |
| `vox-motion-graphics` | [`.claude/skills/vox-motion-graphics/`](.claude/skills/vox-motion-graphics/SKILL.md) | Vox-style editorial collage or paper-diorama explainer videos. Use it only when a Vox-style explainer is asked for. |

Notes for this setup: the skill is written around Higgsfield tools. If the Higgsfield account has no credits, the same steps work through OpenRouter (images: `google/gemini-nano-banana-2.1`; video: `heygen/heygen-video-1`, which always renders audio, so strip it), with ffmpeg for assembly, as in [`videos/003-forgotten-little-joys-ep2/pipeline/`](videos/003-forgotten-little-joys-ep2/pipeline/).
