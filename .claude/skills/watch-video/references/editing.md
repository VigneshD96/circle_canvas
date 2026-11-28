# Editing recipes (plain cuts)

`W` = `uv run --project "${CLAUDE_SKILL_DIR}" python "${CLAUDE_SKILL_DIR}/scripts/watch.py"`. Outputs go to `<video folder>/<stem>_edits/` (or the run dir if that folder is not writable). The source is never changed.

## The EDL

You choose the segments, and the code does the cutting. Never write ffmpeg commands by hand.

```json
{"mode": "join", "order": "time",
 "segments": [{"start": 754.2, "end": 781.9, "label": "Ross reveals the list", "reason": "big laugh, standalone"}]}
```

- Times are source seconds (from the transcript, timeline or zoom).
- `mode`: `join` (one file) or `separate` (one file per segment). `order`: `time` (default; merges overlaps) or `given` (your order, for a reel).
- Edges are snapped automatically: no word is cut in half (each edge moves up to 0.25 s), and up to 0.15 s of padding is added, but never into another speaker's words. Use `--no-snap` only for pure visual cuts.
- Render: `W cut "<video>" --edl edl.json [--separate] [--order given] [--name my_reel]`. `--fast-copy` is fast but cuts only at keyframes: the cut points are APPROXIMATE, so say so to the user if you use it.

## Recipes

- **"Only X" / "X's portions" / "X's parts" = X's SCENES (default).** Keep every scene X takes part in, complete, with everyone X talks to and everyone who talks to X. Drop every scene without X (other storylines). Only cut X's own lines when the user explicitly asks for "only X's lines / dialogue".
  1. `W scenes "<video>" --who "X"` proposes the segments from the watchers' scene logs: X on screen or speaking, short establishing shots that lead into X's scenes, and adjacent scenes merged. It prints kept and dropped scenes and `edge_check_sheets`.
  2. **Check every edge sheet by eye.** Scene changes are often dissolves, and the logged scene times are about ±1.5 s off. Proposed edges are only a hard cut near the logged time, or the logged time itself. The kept part must start on the first clean frame of X's scene and end on the last clean frame before the next scene, with no flash of another scene and no cut-off first line. If needed, edit `start`/`end` in the proposed EDL file.
  3. `W cut "<video>" --edl <proposed.edl.json> --no-snap` (exact edges, aligned to frames), then report `verify`.
- **Keep one person's lines only** (only when asked for lines/dialogue, for example "only Sheldon's lines"): `W speaker-only "<video>" --speaker "Sheldon"`. First review the proposed EDL and the report: segments, seconds, unsure words, overlap words. Then add `--render` (and `--leakage` to check for other voices).
  - Short lines are kept. Two lines are joined only if nobody else speaks between them.
  - `--overlap drop` removes moments where people talk over each other. `--strict` drops words whose speaker is uncertain.
  - If the name's confidence is not `high`, confirm the mapping with the user before you render.
  - Repeat `--speaker` to keep several people.
- **Best / viral moments**: start from the highlight candidates in `timeline.md`, plus laughter/applause, «loud» and (fast) passages, plus public reception (public videos only). Pick moments that stand alone: a clear setup and a payoff, typically 15–90 s. Show the list (rank, time, title, why) in chat first, then render with `--separate` (one clip each) or `--order given` (a reel).
- **Remove parts** (ads, silences, one topic): write the segments to KEEP (the complement), then `join`.
- **Supercut by topic or word**: find the lines in `transcript.md`, make one segment per line (the snapping adds breathing room), and use `order: time`.

## Check before you report

The render prints `verify`: whether the duration matches the EDL, whether the video and audio streams agree, the words heard at each cut, any word that straddles a cut, and (with `--leakage`) the main-voice share. Report the problems honestly. If a boundary is wrong, change that segment and render again. Tell the user the output paths.
