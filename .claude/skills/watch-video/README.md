# watch-video — a Claude Code skill that watches videos

Type `/watch-video <path>` (or say "watch this video <path>") in Claude Code. Claude then understands the video the way a person who watched it would: who says what and when, what is on screen, and what changes over time. After that it can answer questions or cut new videos, for example one person's lines only, the best moments, or a highlight reel.

Code does the heavy work on your Mac, and Claude does the thinking.

| Step | Where it runs | Tool |
|---|---|---|
| Transcript with word times | this Mac | NVIDIA Parakeet-TDT 0.6B v3 (`parakeet-mlx`) |
| Who speaks when (no speaker limit) | this Mac | pyannote `speaker-diarization-community-1` |
| Speech / laughter / applause / music | this Mac | silero-vad + CED-tiny |
| Frames, shot cuts, contact sheets | this Mac | ffmpeg + numpy (every frame scanned) |
| Understanding | Claude | reads sheets + transcript; long videos fan out to parallel sub-agents (Claude Code Workflow) |
| Cuts | this Mac | ffmpeg (one-pass, frame-accurate, A/V-sync tested) |

**Data boundary:** nothing goes to Gemini, OpenAI or any other API. The frames and text that Claude reads go to Anthropic, like any file you open in Claude Code. Library telemetry is off. Web search is used only for videos that you mark as **public**. For private videos an optional hook blocks web tools in that session.

## Requirements

- An Apple Silicon Mac (M1 or later), macOS 14 or later, 16 GB RAM or more (24 GB recommended for long videos).
- `brew install ffmpeg uv`
- About 3 GB of disk for the models, plus about 0.5 GB of cache per hour of video.
- A free Hugging Face account (for the speaker-detection model).

## Install (each teammate, once)

1. Copy the folder to `~/.claude/skills/watch-video/`. Do **not** copy `.venv/` or `.setup_status.json`; they are machine-specific.
2. Open https://huggingface.co/pyannote/speaker-diarization-community-1, log in, and accept the terms.
3. Run `python3 ~/.claude/skills/watch-video/scripts/setup.py` once. It builds the environment and downloads Parakeet and CED, then reports that the speaker model is missing.
4. Create a **Read** token at https://huggingface.co/settings/tokens. In a normal Terminal window (the prompt is interactive, and this keeps the token out of chats) run `~/.claude/skills/watch-video/.venv/bin/hf auth login` and paste it. Then run `setup.py` again to download the speaker model. It builds a Python 3.12 environment in the folder, downloads the three models (about 2.5 GB; this takes several minutes once) and links the parallel-watch workflow into `~/.claude/workflows/watch-video-chunks.js`. Claude Code lists it as a saved workflow after it reloads (a new session); until then the skill passes the script inline. `--check` prints the status without downloading anything.
5. Optional but recommended, the private-video web guard: run `python3 ~/.claude/skills/watch-video/scripts/setup.py --guard` and merge the printed `hooks` block into `~/.claude/settings.json`. It acts only in a session that is watching a video marked private or "not sure"; other sessions are not affected.
6. Optional: to avoid permission prompts for the pipeline, add `"Bash(uv run --project ~/.claude/skills/watch-video*)"` (or the absolute path) to `permissions.allow` in `~/.claude/settings.json`.

## Use

```
/watch-video ~/Movies/friends_s04e03.mkv
/watch-video ~/Downloads/podcast.mp4 find the 3 most viral moments and cut them as separate clips
watch this video ~/Desktop/demo.mov and keep only the parts where Priya talks
```

Claude first asks a few questions (public or private, what the video is, your goal). Processing has already started in the background, so the questions do not add wait time. Output clips go to `<video folder>/<video name>_edits/`.

Measured on an Apple M5 with a 22-min 720p sitcom episode (Friends S07E22):

| Step | Time / cost |
|---|---|
| Frame scan (every frame) + selection + sheets | 31 s + 13 s + 6 s |
| Transcription (Parakeet) | 64 s |
| Sound events | 16–30 s |
| Speaker detection (pyannote, MPS) | ~3 min the first time (includes the model download), ~1–2 min after |
| Watch: 4 parallel sub-agents, 76 sheets | 5.7 min, ~484k tokens (the overview's image estimate was 122k: plan for ~4×) |
| Render: 8-min scene cut / six 1-min clips | ~1 min each |

Short videos (up to ~20 sheets) are watched by the main session, which is much cheaper.

## How it decides how much to look at

- Every frame is scanned at a tiny size to find shot cuts and visual change.
- Frames kept: the base rate is 4 fps (≤1 min), 2 fps (≤10 min), 1 fps (≤60 min) or 0.5 fps (longer), plus the first frame of every shot. Repeated frames are dropped, with a heartbeat that keeps slow changes. A frame budget (about 150 frames for 1 min, 510 for 10 min, 1,260 for 1 h) is met by relaxing the change thresholds. Shot cuts are always kept.
- Frames are packed into contact sheets (a 3×3 grid of 480 px tiles with timestamps, about 1,600 tokens per sheet). Up to about 20 sheets, the main session watches them itself. Above that, the chunks are watched in parallel (about 20 sheets per sub-agent).
- `overview.md` shows the token estimate before the watch starts; above about 300k, Claude asks first.

## Commands (what Claude runs)

`uv run --project ~/.claude/skills/watch-video python ~/.claude/skills/watch-video/scripts/watch.py <cmd>`

| Command | What it does |
|---|---|
| `hints <video>` | probe + identity guess (<1 s) |
| `intake <video> --visibility public\|private\|unsure ...` | records your answers; arms the web guard |
| `prepare <video>` | all heavy stages, cached and fingerprinted |
| `name-speakers <video> --map '{...}'` | maps S1, S2 … to names (+ phrase overrides), then rebuilds the transcript and packets |
| `speaker-fixes <video> [--apply]` | reviews and applies the watchers' label fixes |
| `zoom <video> --start --end` | dense full-resolution frames for a close look |
| `validate-log` / `merge` | check the chunk scene logs, then build `timeline.md` |
| `scenes <video> --who NAME [--render]` | every scene a person takes part in (with everyone they talk to) + edge-check sheets |
| `speaker-only <video> --speaker NAME [--render]` | one person's lines only |
| `cut <video> --edl edl.json` | render any segment list |
| `verify-edit` | duration, A/V sync, boundary words, speaker leakage |
| `status`, `release`, `clean --older-than 30` | housekeeping |

The cache is `~/.cache/watch-video/<hash>-<name>/`. Each run folder contains `overview.md`, `transcript.md`, `speakers/`, `sheets/`, `chunks/`, `scene_logs/`, `timeline.md` and `video_understanding.md`.

## Limits

- Scene changes are often dissolves, and the scene times in the watchers' logs are about ±1.5 s off. For scene-based cuts, Claude checks an edge strip for every cut point by eye. This fixed 6 of 10 edges in the test episode; automatic dissolve detection was tried and was not reliable.
- Parakeet on a whole file can drop whole sentences or glue words into one token ("economy.9km"), most often under music, even though it hears them fine in a short window. The transcription stage therefore re-listens to every gap between words and every glued token, and keeps the window's words when they add speech (`asr/words.json` lists each repair under `repaired`; on a 15-min review it recovered 4 sentences, about 100 words, in about 10 s). `verify-edit` also re-listens to a short window at each cut before it reports a boundary as failed. Names are still misheard ("Kiwi" for Kivi, "Ares" for Aeris): the on-screen text wins for wording.
- Diarization often merges minor characters (police officers, a boyfriend, waiters) into main speaker IDs. The watchers flag these with picture evidence, and `speaker-fixes` applies their corrections before any speaker- or scene-based edit.
- Source chapters, subtitles and data streams are never copied into cuts (a copied MKV chapter track once made 1-min clips show as 18 min).
- Speech: the 25 European languages that Parakeet v3 supports. There is no Hindi, Tamil, CJK or Arabic yet.
- When people talk over each other, the transcript mostly follows the loudest voice. These lines are marked `(overlap)`.
- Laugh tracks and music can create a fake "speaker". These are flagged, not hidden.
- Speaker names come from evidence that Claude reads (names said, faces during solo lines, the cast list for public videos). Unclear speakers stay unnamed, and named speaker-only cuts ask first when the confidence is not high.
- URLs: there is no built-in downloader. SKILL.md Step 1 tells Claude to download the video with `yt-dlp` (H.264 ≤1080p mp4) into `~/Downloads` first, so `yt-dlp` must be installed (`brew install yt-dlp`). Tested on a YouTube launch video, 2026-10-06.

## Develop

```
cd ~/.claude/skills/watch-video
uv run python tests/make_fixtures.py tests/fixtures   # synthetic videos with ground truth
uv run pytest -q                                      # unit + A/V sync tests
```
